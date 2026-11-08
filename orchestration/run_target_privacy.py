#!/usr/bin/env python3
"""Run the target privacy event pipeline over caller-instrumented JSONL events."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from target_privacy_adapter import PrivacyEventRecorder  # noqa: E402
from target_privacy_pipeline import utc_now, write_run_outputs  # noqa: E402


def load_events(path: Path) -> list[dict[str, Any]]:
    events = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on input line {line_number}.") from exc
        if not isinstance(event, dict):
            raise ValueError(f"Input line {line_number} must be a JSON object.")
        events.append(event)
    if not events:
        raise ValueError("Input contains no events.")
    return events


def make_presidio_detector():
    try:
        from presidio_analyzer import AnalyzerEngine
        detector_version = version("presidio-analyzer")
    except (ImportError, PackageNotFoundError) as exc:
        raise RuntimeError("Install presidio-analyzer and its configured NLP model before running.") from exc
    analyzer = AnalyzerEngine()

    def detect(text: str):
        return [
            {"entity_type": item.entity_type, "score": item.score}
            for item in analyzer.analyze(text=text, language="en")
        ]
    return detect, detector_version


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", required=True, type=Path, help="JSONL file of instrumented events")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--assessment-id", required=True)
    parser.add_argument("--target-name", required=True)
    parser.add_argument("--model-archetype", required=True)
    parser.add_argument("--interface", default="instrumented-application")
    parser.add_argument("--authorization-confirmed", action="store_true")
    parser.add_argument("--synthetic-data-only", action="store_true")
    args = parser.parse_args()

    if not args.authorization_confirmed:
        print("Refusing to run: pass --authorization-confirmed after verifying written authorization.", file=sys.stderr)
        return 2
    if not args.synthetic_data_only:
        print("Refusing to run: this reference runner is restricted to synthetic data; pass --synthetic-data-only.", file=sys.stderr)
        return 2

    started_at = utc_now()
    try:
        events = load_events(args.events)
        detector, detector_version = make_presidio_detector()
        recorder = PrivacyEventRecorder(detector)
        for event in events:
            recorder.record_event(event)
        result = recorder.result()
        finished_at = utc_now()
        record = write_run_outputs(
            args.output_dir,
            assessment_id=args.assessment_id,
            target={
                "name": args.target_name,
                "model_archetype": args.model_archetype,
                "interface": args.interface,
            },
            result=result,
            started_at=started_at,
            finished_at=finished_at,
            detector_version=detector_version,
        )

        # Validate against the shared evidence schema before reporting success.
        from validate_evidence import validate_record
        errors = validate_record(record)
        if errors:
            raise RuntimeError("Generated evidence record failed schema validation: " + "; ".join(errors))
    except Exception as exc:
        # Error messages are restricted to exception type; input content is never logged.
        print(f"Assessment failed: {type(exc).__name__}. No event content was logged.", file=sys.stderr)
        return 1

    print(f"Assessment complete: {result['event_count']} events; {len(result['findings'])} unconfirmed candidate findings.")
    print(f"HTML report: {args.output_dir / 'target_privacy_report.html'}")
    print(f"Execution log: {args.output_dir / 'target_privacy_run.log'}")
    print(f"Evidence record: {args.output_dir / 'target_privacy_evidence.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
