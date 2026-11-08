#!/usr/bin/env python3
"""Build an evidence-aware plan; optionally invoke the allowlisted Presidio synthetic-fixture runner."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DEFAULT = Path(__file__).with_name("tool_registry.json")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_json(path: Path):
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def safe_path(relative: str) -> Path:
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT.parent):
        raise ValueError(f"Registry path escapes workspace: {relative}")
    return path


def build_plan(manifest: dict[str, Any], registry: dict[str, Any]):
    for key in ("assessment_id", "target", "authorisation", "data_policy", "selected_tools"):
        if key not in manifest:
            raise ValueError(f"Missing manifest field: {key}")
    if not isinstance(manifest["selected_tools"], list) or not manifest["selected_tools"]:
        raise ValueError("selected_tools must be a non-empty array")
    tools = {item["id"]: item for item in registry.get("tools", [])}
    unknown = sorted(set(manifest["selected_tools"]) - set(tools))
    if unknown:
        raise ValueError("Unknown tool IDs: " + ", ".join(unknown))
    archetype = manifest["target"]["model_archetype"]
    entries = []
    for tool_id in manifest["selected_tools"]:
        tool = tools[tool_id]
        applicable = tool.get("applicable_archetypes", [])
        conditional = tool.get("conditional_archetypes", [])
        if "all" not in applicable and archetype not in applicable and archetype not in conditional:
            status, reason = "NOT_APPLICABLE", "Registry does not map this model archetype to the tool."
        elif archetype in conditional:
            status, reason = "REVIEW_REQUIRED", "Conditional fit; verify the component/interface before execution."
        elif tool["execution_mode"] == "colab_notebook":
            status, reason = "MANUAL_COLAB", "Open the referenced notebook in Colab; this planner does not execute notebooks."
        elif tool["execution_mode"] == "python_script":
            status, reason = "READY_LOCAL", "An allowlisted local runner exists; execution is opt-in."
        else:
            status, reason = "UPSTREAM_CONFIGURATION_REQUIRED", "Configure and execute the upstream tool in your environment."
        entries.append({
            "tool_id": tool_id,
            "tool": tool["name"],
            "workstream": tool["workstream"],
            "execution_mode": tool["execution_mode"],
            "reference": tool.get("path"),
            "execution_status": status,
            "finding_status": "NONE",
            "reason": reason,
            "limitations": tool.get("limitations", "Review workstream documentation."),
        })
    return {
        "assessment_id": manifest["assessment_id"],
        "generated_utc": utc_now(),
        "target": manifest["target"],
        "authorisation_confirmed": bool(manifest["authorisation"].get("confirmed")),
        "synthetic_data_only": bool(manifest["data_policy"].get("synthetic_data_only")),
        "planning_only": True,
        "tools": entries,
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_presidio_evidence(
    manifest: dict[str, Any],
    summary: dict[str, Any],
    *,
    started_at: str,
    finished_at: str,
    artifacts: list[dict[str, Any]],
    run_id: str | None = None,
) -> dict[str, Any]:
    """Normalize the runner's redacted stdout summary; never infer a confirmed vulnerability."""
    artifact_refs = [item["path"] for item in artifacts]
    evidence_tests = []
    findings = []
    for item in summary.get("tests", []):
        missed = sorted(set(item.get("missed_entities", [])))
        unexpected = sorted(set(item.get("unexpected_entities", [])))
        detected = sorted(set(item.get("detected_entities", [])))
        expected = sorted(set(item.get("expected_entities", [])))
        status = "FAIL" if missed or unexpected else "PASS"
        observations = []
        if missed:
            observations.append("Missed expected entity types: " + ", ".join(missed))
        if unexpected:
            observations.append("Unexpected entity types: " + ", ".join(unexpected))
        if not observations:
            observations.append("Expected entity types detected; no unexpected types.")
        evidence_tests.append({
            "test_id": str(item["test_id"]),
            "test_name": str(item["test_name"]),
            "status": status,
            "category": "privacy_detection",
            "observation": "; ".join(observations),
            "metrics": {
                "expected_entity_types": expected,
                "detected_entity_types": detected,
                "missed_entity_types": missed,
                "unexpected_entity_types": unexpected,
                "confidence_scores": item.get("scores", []),
            },
            "evidence_refs": artifact_refs,
        })
        if missed:
            findings.append({
                "finding_id": f"{item['test_id']}-missed-entity-type",
                "title": "Expected PII entity type not detected",
                "category": "privacy_detection_gap",
                "severity": "UNRATED",
                "risky_behavior": False,
                "finding_verdict": "UNCONFIRMED",
                "description": (
                    "A labelled synthetic fixture contained an expected entity type that the "
                    "configured Presidio run did not detect. This is a test signal only; no "
                    "production data flow or application-level exposure was assessed."
                ),
                "evidence_refs": artifact_refs,
            })
        if unexpected:
            findings.append({
                "finding_id": f"{item['test_id']}-unexpected-entity-type",
                "title": "Unexpected PII entity type detected",
                "category": "possible_false_positive",
                "severity": "UNRATED",
                "risky_behavior": False,
                "finding_verdict": "UNCONFIRMED",
                "description": (
                    "The detector returned entity types outside the fixture's expected labels. "
                    "This is a fixture-level false-positive candidate requiring review."
                ),
                "evidence_refs": artifact_refs,
            })

    runner_status = summary.get("execution_status")
    if runner_status == "EXECUTED":
        execution_status = "COMPLETED"
    elif evidence_tests:
        execution_status = "PARTIAL"
    else:
        execution_status = "FAILED"

    return {
        "schema_version": "1.0",
        "assessment_id": manifest["assessment_id"],
        "run_id": run_id or str(uuid.uuid4()),
        "tool_id": "presidio",
        "tool_version": summary.get("tool_version"),
        "config_digest": None,
        "target": manifest["target"],
        "started_at": started_at,
        "finished_at": finished_at,
        "execution_status": execution_status,
        "environment": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "runtime": "local_subprocess",
        },
        "tests": evidence_tests,
        "findings": findings,
        "artifacts": artifacts,
        "limitations": [
            "Synthetic fixtures only; no production or personal data was processed.",
            "Entity-type comparison only; this is not a span-level precision/recall benchmark.",
            "A detector miss or unexpected entity type is not automatically a confirmed security finding.",
            "No application-level data flow, exposure, impact, severity or OWASP mapping was established.",
        ],
        "notes": [
            "Raw fixture text and detected values are intentionally excluded from normalized evidence.",
            "Finding verdicts remain UNCONFIRMED pending application-context review.",
        ],
    }


def run_presidio(
    manifest: dict[str, Any],
    plan: dict[str, Any],
    out_dir: Path,
    log_lines: list[str],
    registry: dict[str, Any],
) -> int:
    if "presidio" not in manifest["selected_tools"]:
        return 0
    entry = next(item for item in plan["tools"] if item["tool_id"] == "presidio")
    if entry["execution_status"] != "READY_LOCAL":
        log_lines.append(f"Presidio not run: applicability gate status is {entry['execution_status']}.")
        return 0
    if not manifest["authorisation"].get("confirmed"):
        log_lines.append("Presidio not run: authorisation.confirmed is false.")
        return 0
    if not manifest["data_policy"].get("synthetic_data_only"):
        log_lines.append("Presidio not run: this adapter is restricted to synthetic fixtures.")
        return 0

    item = next(tool for tool in registry["tools"] if tool["id"] == "presidio")
    script = safe_path(item["path"])
    fixture_rel = manifest.get("tool_config", {}).get("presidio", {}).get("fixtures", item["fixtures"])
    fixtures = safe_path(fixture_rel)
    if not script.is_file() or not fixtures.is_file():
        raise FileNotFoundError("Presidio runner/fixtures missing.")
    tool_out = out_dir / "presidio"
    tool_out.mkdir(parents=True, exist_ok=True)
    report = tool_out / "presidio_report.html"
    run_log = tool_out / "presidio_run.log"
    command = [
        sys.executable, str(script), "--fixtures", str(fixtures),
        "--output-dir", str(tool_out), "--emit-evidence-summary",
    ]
    started_at = utc_now()
    log_lines.append("Presidio runner invoked; raw stdout/stderr are not copied into orchestration.log.")
    summary = None
    return_code = 1
    failure_note = None
    try:
        result = subprocess.run(
            command, cwd=ROOT.parent, capture_output=True, text=True, timeout=900, check=False
        )
        return_code = result.returncode
        for line in result.stdout.splitlines():
            if line.startswith("PRESIDIO_EVIDENCE_SUMMARY="):
                summary = json.loads(line.split("=", 1)[1])
                break
        if result.returncode != 0:
            failure_note = f"Runner exited with code {result.returncode}."
        elif summary is None:
            failure_note = "Runner completed without the required redacted evidence summary."
    except subprocess.TimeoutExpired:
        failure_note = "Runner timed out after 900 seconds."
    except OSError as exc:
        failure_note = f"Runner could not be started: {type(exc).__name__}."
    finished_at = utc_now()

    artifacts = []
    for path, media_type, description in (
        (report, "text/html", "Presidio HTML assessment report"),
        (run_log, "text/plain", "Presidio execution log"),
    ):
        if path.is_file():
            artifacts.append({
                "path": path.relative_to(out_dir).as_posix(),
                "sha256": sha256_file(path),
                "media_type": media_type,
                "description": description,
            })

    if summary is None:
        summary = {"execution_status": "FAILED", "tool_version": None, "tests": []}
    record = build_presidio_evidence(
        manifest, summary, started_at=started_at, finished_at=finished_at, artifacts=artifacts
    )
    if failure_note:
        record["notes"].append(failure_note)
    evidence_path = out_dir / "presidio_evidence.json"
    evidence_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    if return_code == 0 and record["execution_status"] == "COMPLETED" and len(artifacts) == 2:
        entry["execution_status"] = "EXECUTED"
        entry["reason"] = "Allowlisted Presidio runner completed; normalized evidence and artifact hashes were collected."
    else:
        entry["execution_status"] = "FAILED"
        entry["reason"] = failure_note or "Runner did not produce both expected artifacts and a complete evidence summary."
        entry["exception"] = failure_note or f"exit_code={return_code}"
    entry["evidence_record"] = str(evidence_path)
    entry["artifacts"] = artifacts
    plan["planning_only"] = False
    log_lines.append(f"Presidio execution status: {record['execution_status']}.")
    log_lines.append(f"Normalized evidence record: {evidence_path.name}.")
    log_lines.append(f"Hashed artifacts: {len(artifacts)}.")
    return 0 if entry["execution_status"] == "EXECUTED" else 1


def markdown(plan):
    lines = [
        f"# Assessment plan — {plan['assessment_id']}", "",
        f"- Generated UTC: {plan['generated_utc']}",
        f"- Target: {plan['target'].get('name')}",
        f"- Archetype: {plan['target'].get('model_archetype')}",
        f"- Authorisation confirmed: {plan['authorisation_confirmed']}",
        f"- Synthetic data only: {plan['synthetic_data_only']}", "",
        "| Tool | Workstream | Mode | Execution status | Finding status |",
        "|---|---|---|---|---|",
    ]
    for tool in plan["tools"]:
        lines.append(
            f"| {tool['tool']} | {tool['workstream']} | {tool['execution_mode']} | "
            f"{tool['execution_status']} | {tool['finding_status']} |"
        )
    lines.extend(["", "## Notes", ""])
    for tool in plan["tools"]:
        lines.append(f"- **{tool['tool']}** — {tool['reason']} Limitations: {tool['limitations']}")
        if tool.get("evidence_record"):
            lines.append(f"  - Evidence record: `{tool['evidence_record']}`")
    lines.extend([
        "",
        "Execution and finding statuses are independent. A planned, manual or failed test is not a finding.",
    ])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--registry", type=Path, default=REGISTRY_DEFAULT)
    parser.add_argument("--output-dir", type=Path, default=Path("assessment-plan-output"))
    parser.add_argument(
        "--execute-presidio", action="store_true",
        help="Opt in to the allowlisted synthetic Presidio runner.",
    )
    args = parser.parse_args()
    manifest = read_json(args.manifest)
    registry = read_json(args.registry)
    plan = build_plan(manifest, registry)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_dir = args.output_dir.resolve()
    log_lines = [f"Generated UTC: {utc_now()}", f"Assessment: {manifest['assessment_id']}"]
    execution_exit_code = 0
    if args.execute_presidio:
        execution_exit_code = run_presidio(manifest, plan, output_dir, log_lines, registry)
    (output_dir / "assessment_plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    (output_dir / "assessment_plan.md").write_text(markdown(plan), encoding="utf-8")
    (output_dir / "orchestration.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    print(f"Plan: {output_dir / 'assessment_plan.md'}")
    print(f"JSON: {output_dir / 'assessment_plan.json'}")
    print(f"Log: {output_dir / 'orchestration.log'}")
    return execution_exit_code


if __name__ == "__main__":
    raise SystemExit(main())
