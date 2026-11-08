#!/usr/bin/env python3
"""Validate normalized assessment evidence records against the shared JSON Schema."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any
try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:
    raise SystemExit("Missing dependency: install jsonschema>=4.20,<5 to validate evidence records.") from exc

SCHEMA_PATH = Path(__file__).with_name("evidence_record.schema.json")

def validate_record(record: dict[str, Any], schema: dict[str, Any] | None = None) -> list[str]:
    """Return sorted schema violations; an empty list means valid."""
    schema = schema or json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = []
    for error in validator.iter_errors(record):
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        errors.append(f"{location}: {error.message}")
    return sorted(errors)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path, help="Path to a JSON evidence record")
    args = parser.parse_args()
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Could not read evidence record: {exc}", file=sys.stderr)
        return 2
    if not isinstance(record, dict):
        print("Evidence record must be a JSON object.", file=sys.stderr)
        return 2
    errors = validate_record(record)
    if errors:
        print("Evidence record is INVALID:")
        for error in errors: print(f"- {error}")
        return 1
    print("Evidence record is valid.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
