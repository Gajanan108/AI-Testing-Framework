#!/usr/bin/env python3
"""Build an evidence-aware plan; optionally invoke the allowlisted Presidio synthetic-fixture runner."""
from __future__ import annotations
import argparse, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
REGISTRY_DEFAULT=Path(__file__).with_name("tool_registry.json")

def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")

def read_json(path: Path):
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict): raise ValueError(f"Expected JSON object: {path}")
    return value

def safe_path(relative: str) -> Path:
    path=(ROOT/relative).resolve()
    if not path.is_relative_to(ROOT.parent): raise ValueError(f"Registry path escapes workspace: {relative}")
    return path

def build_plan(manifest: dict[str,Any], registry: dict[str,Any]):
    for key in ("assessment_id","target","authorisation","data_policy","selected_tools"):
        if key not in manifest: raise ValueError(f"Missing manifest field: {key}")
    if not isinstance(manifest["selected_tools"],list) or not manifest["selected_tools"]:
        raise ValueError("selected_tools must be a non-empty array")
    tools={item["id"]:item for item in registry.get("tools",[])}
    unknown=sorted(set(manifest["selected_tools"])-set(tools))
    if unknown: raise ValueError("Unknown tool IDs: "+", ".join(unknown))
    archetype=manifest["target"]["model_archetype"]
    entries=[]
    for tool_id in manifest["selected_tools"]:
        tool=tools[tool_id]
        applicable=tool.get("applicable_archetypes",[])
        conditional=tool.get("conditional_archetypes",[])
        if "all" not in applicable and archetype not in applicable and archetype not in conditional:
            status,reason="NOT_APPLICABLE","Registry does not map this model archetype to the tool."
        elif archetype in conditional:
            status,reason="REVIEW_REQUIRED","Conditional fit; verify the component/interface before execution."
        elif tool["execution_mode"]=="colab_notebook":
            status,reason="MANUAL_COLAB","Open the referenced notebook in Colab; this planner does not execute notebooks."
        elif tool["execution_mode"]=="python_script":
            status,reason="READY_LOCAL","An allowlisted local runner exists; execution is opt-in."
        else:
            status,reason="UPSTREAM_CONFIGURATION_REQUIRED","Configure and execute the upstream tool in your environment."
        entries.append({"tool_id":tool_id,"tool":tool["name"],"workstream":tool["workstream"],
            "execution_mode":tool["execution_mode"],"reference":tool.get("path"),
            "execution_status":status,"finding_status":"NONE","reason":reason,
            "limitations":tool.get("limitations","Review workstream documentation.")})
    return {"assessment_id":manifest["assessment_id"],"generated_utc":utc_now(),
        "target":manifest["target"],"authorisation_confirmed":bool(manifest["authorisation"].get("confirmed")),
        "synthetic_data_only":bool(manifest["data_policy"].get("synthetic_data_only")),
        "planning_only":True,"tools":entries}

def run_presidio(manifest, plan, out_dir, log_lines):
    if "presidio" not in manifest["selected_tools"]: return
    if not manifest["authorisation"].get("confirmed"):
        log_lines.append("Presidio not run: authorisation.confirmed is false."); return
    if not manifest["data_policy"].get("synthetic_data_only"):
        log_lines.append("Presidio not run: this adapter is restricted to synthetic fixtures."); return
    registry=read_json(REGISTRY_DEFAULT)
    item=next(t for t in registry["tools"] if t["id"]=="presidio")
    script=safe_path(item["path"])
    fixture_rel=manifest.get("tool_config",{}).get("presidio",{}).get("fixtures",item["fixtures"])
    fixtures=safe_path(fixture_rel)
    if not script.is_file() or not fixtures.is_file(): raise FileNotFoundError("Presidio runner/fixtures missing.")
    tool_out=out_dir/"presidio"; tool_out.mkdir(parents=True,exist_ok=True)
    command=[sys.executable,str(script),"--fixtures",str(fixtures),"--output-dir",str(tool_out)]
    log_lines.append("Presidio command: "+" ".join(command))
    result=subprocess.run(command,cwd=ROOT.parent,capture_output=True,text=True,timeout=900,check=False)
    log_lines.extend(["Presidio stdout:",result.stdout,"Presidio stderr:",result.stderr])
    report=tool_out/"presidio_report.html"; run_log=tool_out/"presidio_run.log"
    entry=next(t for t in plan["tools"] if t["tool_id"]=="presidio")
    if result.returncode==0 and report.is_file() and run_log.is_file():
        entry["execution_status"]="EXECUTED"; entry["artifacts"]=[str(report),str(run_log)]
        entry["reason"]="Allowlisted Presidio reference runner completed on synthetic fixtures."
    else:
        entry["execution_status"]="FAILED"; entry["exception"]=f"exit_code={result.returncode}"
        entry["reason"]="Runner failed; inspect orchestration and tool logs."
    plan["planning_only"]=False

def markdown(plan):
    lines=[f"# Assessment plan — {plan['assessment_id']}","",
        f"- Generated UTC: {plan['generated_utc']}",
        f"- Target: {plan['target'].get('name')}",
        f"- Archetype: {plan['target'].get('model_archetype')}",
        f"- Authorisation confirmed: {plan['authorisation_confirmed']}",
        f"- Synthetic data only: {plan['synthetic_data_only']}","",
        "| Tool | Workstream | Mode | Execution status | Finding status |","|---|---|---|---|---|"]
    for t in plan["tools"]:
        lines.append(f"| {t['tool']} | {t['workstream']} | {t['execution_mode']} | {t['execution_status']} | {t['finding_status']} |")
    lines.extend(["","## Notes",""])
    for t in plan["tools"]: lines.append(f"- **{t['tool']}** — {t['reason']} Limitations: {t['limitations']}")
    lines.extend(["","Execution and finding statuses are independent. A planned, manual or failed test is not a finding."])
    return "\n".join(lines)+"\n"

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",type=Path,required=True)
    parser.add_argument("--registry",type=Path,default=REGISTRY_DEFAULT)
    parser.add_argument("--output-dir",type=Path,default=Path("assessment-plan-output"))
    parser.add_argument("--execute-presidio",action="store_true",help="Opt in to the allowlisted synthetic Presidio runner.")
    args=parser.parse_args()
    manifest=read_json(args.manifest); registry=read_json(args.registry)
    plan=build_plan(manifest,registry)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    log_lines=[f"Generated UTC: {utc_now()}",f"Assessment: {manifest['assessment_id']}"]
    if args.execute_presidio: run_presidio(manifest,plan,args.output_dir.resolve(),log_lines)
    (args.output_dir/"assessment_plan.json").write_text(json.dumps(plan,indent=2),encoding="utf-8")
    (args.output_dir/"assessment_plan.md").write_text(markdown(plan),encoding="utf-8")
    (args.output_dir/"orchestration.log").write_text("\n".join(log_lines)+"\n",encoding="utf-8")
    print(f"Plan: {args.output_dir/'assessment_plan.md'}")
    print(f"JSON: {args.output_dir/'assessment_plan.json'}")
    print(f"Log: {args.output_dir/'orchestration.log'}")
    return 0

if __name__=="__main__": raise SystemExit(main())
