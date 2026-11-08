"""Build normalized evidence, HTML report and redacted execution log for target privacy runs."""
from __future__ import annotations

import hashlib
import html
import json
import platform
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_evidence_record(
    *,
    assessment_id: str,
    target: dict[str, Any],
    result: dict[str, Any],
    started_at: str,
    finished_at: str,
    artifacts: list[dict[str, Any]],
    detector_version: str,
    run_id: str | None = None,
) -> dict[str, Any]:
    refs = [item["path"] for item in artifacts]
    tests = []
    for item in result["tests"]:
        tests.append({
            "test_id": item["test_id"],
            "test_name": item["test_name"],
            "status": item["status"],
            "category": item.get("category"),
            "observation": item.get("observation"),
            "metrics": item.get("metrics", {}),
            "evidence_refs": refs,
        })
    findings = []
    for item in result["findings"]:
        findings.append({
            **item,
            "evidence_refs": refs,
        })
    return {
        "schema_version": "1.0",
        "assessment_id": assessment_id,
        "run_id": run_id or str(uuid.uuid4()),
        "tool_id": "target_privacy_event_adapter",
        "tool_version": "0.2.0",
        "config_digest": None,
        "target": target,
        "started_at": started_at,
        "finished_at": finished_at,
        "execution_status": "COMPLETED",
        "environment": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "runtime": "local_in_process",
            "detector": "Microsoft Presidio Analyzer",
            "detector_version": detector_version,
        },
        "tests": tests,
        "findings": findings,
        "artifacts": artifacts,
        "limitations": result.get("limitations", []),
        "notes": [
            "Only redacted event metadata and entity-type labels are persisted; raw event text is not included.",
            "Finding verdicts are UNCONFIRMED until application delivery, policy and impact are independently reviewed.",
            "This run covers only events supplied by the caller; completeness of application instrumentation is not established.",
        ],
    }


def render_html_report(record: dict[str, Any]) -> str:
    def esc(value: Any) -> str:
        return html.escape(str(value if value is not None else ""))

    findings = record.get("findings", [])
    tests = record.get("tests", [])
    finding_rows = "".join(
        "<tr>"
        f"<td>{esc(item['title'])}</td>"
        f"<td>{esc(item['category'])}</td>"
        f"<td>{esc(item['severity'])}</td>"
        f"<td>{'Yes' if item['risky_behavior'] else 'No'}</td>"
        f"<td>{esc(item['finding_verdict'])}</td>"
        f"<td>{esc(', '.join(item.get('evidence_refs', [])))}</td>"
        "</tr>"
        for item in findings
    ) or '<tr><td colspan="6">No candidate findings.</td></tr>'
    test_rows = "".join(
        "<tr>"
        f"<td>{esc(item['test_id'])}</td>"
        f"<td>{esc(item['test_name'])}</td>"
        f"<td>{esc(item['status'])}</td>"
        f"<td>{esc(item.get('observation'))}</td>"
        f"<td>{esc(json.dumps(item.get('metrics', {}), sort_keys=True))}</td>"
        "</tr>"
        for item in tests
    ) or '<tr><td colspan="5">No events were assessed.</td></tr>'
    limitations = "".join(f"<li>{esc(item)}</li>" for item in record.get("limitations", []))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Target Privacy Assessment — {esc(record['target']['name'])}</title>
<style>
:root{{--ink:#172033;--muted:#657087;--line:#dce2eb;--panel:#f5f7fa;--accent:#254b7a}}
*{{box-sizing:border-box}}body{{margin:0;background:#f2f4f8;color:var(--ink);font:14px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}}
main{{max-width:1180px;margin:32px auto;padding:0 20px}}header,.panel{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:22px;margin-bottom:18px}}
h1{{font-size:25px;margin:0 0 5px}}h2{{font-size:17px;margin:0 0 14px}}p,.muted{{color:var(--muted)}}
.meta{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-top:18px}}
.meta div{{background:var(--panel);padding:12px;border-radius:8px}}.meta strong{{display:block;font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}}
.statrow{{display:flex;gap:12px;flex-wrap:wrap}}.stat{{background:var(--panel);padding:14px 18px;border-radius:8px;min-width:140px}}.stat b{{display:block;font-size:23px}}
table{{width:100%;border-collapse:collapse;font-size:12px}}th,td{{padding:10px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}}th{{background:var(--panel);font-weight:650}}td{{overflow-wrap:anywhere}}
.notice{{border-left:4px solid #bd8730;background:#fff8e9;padding:12px 14px;border-radius:5px}}
footer{{color:var(--muted);font-size:12px;padding:10px 2px}}
@media(max-width:700px){{main{{padding:0 10px}}header,.panel{{padding:15px}}}}
</style></head><body><main>
<header><h1>Target Privacy Assessment</h1><div class="muted">{esc(record['target']['name'])} · {esc(record['target']['model_archetype'])}</div>
<div class="meta">
<div><strong>Assessment ID</strong>{esc(record['assessment_id'])}</div>
<div><strong>Run ID</strong>{esc(record['run_id'])}</div>
<div><strong>Execution</strong>{esc(record['execution_status'])}</div>
<div><strong>Detector</strong>Microsoft Presidio {esc(record.get('environment',{}).get('detector_version'))}</div>
<div><strong>Started</strong>{esc(record['started_at'])}</div>
<div><strong>Finished</strong>{esc(record['finished_at'])}</div>
</div></header>
<section class="panel"><h2>Assessment summary</h2><div class="statrow">
<div class="stat"><b>{len(tests)}</b>Events assessed</div><div class="stat"><b>{sum(1 for x in tests if x['status']=='PASS')}</b>Passed</div>
<div class="stat"><b>{sum(1 for x in tests if x['status']=='FAIL')}</b>Failed</div><div class="stat"><b>{len(findings)}</b>Candidate findings</div></div>
<p class="notice">Candidate findings are not confirmed vulnerabilities. Severity remains UNRATED and verdict remains UNCONFIRMED pending review of actual delivery, authorization, policy intent and impact.</p></section>
<section class="panel"><h2>Findings</h2><table><thead><tr><th>Finding</th><th>Category</th><th>Severity</th><th>Risky behavior</th><th>Verdict</th><th>Evidence</th></tr></thead><tbody>{finding_rows}</tbody></table></section>
<section class="panel"><h2>Event test results</h2><table><thead><tr><th>Event ID</th><th>Test</th><th>Status</th><th>Observation</th><th>Redacted metrics</th></tr></thead><tbody>{test_rows}</tbody></table></section>
<section class="panel"><h2>Limitations and review notes</h2><ul>{limitations}</ul><p>Raw event text and detected values are excluded from this report. Entity-type detection does not prove that a value is valid, secret, or attributable to a person. No OWASP mapping is automatically assigned.</p></section>
<footer>Generated by AI Testing Framework · {esc(record['tool_id'])} · Evidence schema {esc(record['schema_version'])}</footer>
</main></body></html>"""


def write_run_outputs(
    output_dir: Path,
    *,
    assessment_id: str,
    target: dict[str, Any],
    result: dict[str, Any],
    started_at: str,
    finished_at: str,
    detector_version: str,
    run_id: str | None = None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "target_privacy_report.html"
    log_path = output_dir / "target_privacy_run.log"
    evidence_path = output_dir / "target_privacy_evidence.json"

    log_lines = [
        "AI Testing Framework — Target Privacy Event Assessment",
        f"Assessment ID: {assessment_id}",
        f"Run ID: {run_id or 'generated'}",
        f"Started: {started_at}",
        f"Finished: {finished_at}",
        f"Events assessed: {result['event_count']}",
        f"Tests failed: {sum(1 for item in result['tests'] if item['status'] == 'FAIL')}",
        f"Candidate findings: {len(result['findings'])}",
        "Raw event text and detected values were not written to this log.",
        "Finding verdicts remain UNCONFIRMED; severity remains UNRATED.",
    ]
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    artifacts = [
        {
            "path": report_path.name,
            "sha256": "0" * 64,
            "media_type": "text/html",
            "description": "Target privacy HTML assessment report",
        },
        {
            "path": log_path.name,
            "sha256": sha256_file(log_path),
            "media_type": "text/plain",
            "description": "Redacted target privacy execution log",
        },
    ]
    record = build_evidence_record(
        assessment_id=assessment_id,
        target=target,
        result=result,
        started_at=started_at,
        finished_at=finished_at,
        artifacts=artifacts,
        detector_version=detector_version,
        run_id=run_id,
    )
    report_path.write_text(render_html_report(record), encoding="utf-8")
    artifacts[0]["sha256"] = sha256_file(report_path)
    record["artifacts"] = artifacts
    evidence_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record
