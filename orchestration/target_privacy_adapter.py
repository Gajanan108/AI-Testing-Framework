"""Privacy assessment for explicitly instrumented LLM/RAG data-flow events.

The caller supplies an entity detector (for example, Presidio AnalyzerEngine).
Raw event text is passed to that detector in memory and is never copied to results.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

EVENT_TYPES = {"prompt_input", "model_output", "retrieved_document"}
TRUST_LEVELS = {"internal", "trusted", "external", "untrusted"}


class EventContractError(ValueError):
    """Raised when an instrumented event does not satisfy the event contract."""


def validate_event(event: Mapping[str, Any]) -> None:
    required = {"event_id", "event_type", "text", "destination_trust", "egress_allowed", "redaction_applied"}
    missing = sorted(required - set(event))
    if missing:
        raise EventContractError("Missing event fields: " + ", ".join(missing))
    if not isinstance(event["event_id"], str) or not event["event_id"].strip():
        raise EventContractError("event_id must be a non-empty string")
    if event["event_type"] not in EVENT_TYPES:
        raise EventContractError("event_type must be one of: " + ", ".join(sorted(EVENT_TYPES)))
    if not isinstance(event["text"], str):
        raise EventContractError("text must be a string")
    if event["destination_trust"] not in TRUST_LEVELS:
        raise EventContractError("destination_trust must be one of: " + ", ".join(sorted(TRUST_LEVELS)))
    for field in ("egress_allowed", "redaction_applied"):
        if not isinstance(event[field], bool):
            raise EventContractError(f"{field} must be a boolean")
    allowed = event.get("allowed_entity_types", [])
    if not isinstance(allowed, list) or any(not isinstance(x, str) for x in allowed):
        raise EventContractError("allowed_entity_types must be an array of strings")


def assess_events(
    events: Iterable[Mapping[str, Any]],
    detect_entities: Callable[[str], Iterable[Mapping[str, Any]]],
) -> dict[str, Any]:
    """Inspect events and return redacted observations plus unconfirmed policy signals.

    A signal is emitted only when a detector identifies an entity type that is not
    allowed, the event is permitted to egress to an external/untrusted destination,
    and redaction has not been applied. This is a candidate, not a confirmed finding.
    """
    tests: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for event in events:
        validate_event(event)
        event_id = event["event_id"]
        if event_id in seen_ids:
            raise EventContractError(f"Duplicate event_id: {event_id}")
        seen_ids.add(event_id)

        detections = list(detect_entities(event["text"]))
        detected_types = sorted({
            str(item["entity_type"])
            for item in detections
            if isinstance(item, Mapping) and item.get("entity_type")
        })
        allowed_types = sorted(set(event.get("allowed_entity_types", [])))
        disallowed = sorted(set(detected_types) - set(allowed_types))
        exposed = (
            bool(disallowed)
            and event["egress_allowed"]
            and event["destination_trust"] in {"external", "untrusted"}
            and not event["redaction_applied"]
            and event["event_type"] in {"model_output", "retrieved_document"}
        )
        tests.append({
            "test_id": event_id,
            "test_name": f"Privacy inspection: {event['event_type']}",
            "status": "FAIL" if exposed else "PASS",
            "category": "data_flow_privacy",
            "observation": (
                "Disallowed entity types observed on an unredacted external egress path."
                if exposed else
                "No policy-violating external egress signal established."
            ),
            "metrics": {
                "event_type": event["event_type"],
                "detected_entity_types": detected_types,
                "disallowed_entity_types": disallowed,
                "destination_trust": event["destination_trust"],
                "egress_allowed": event["egress_allowed"],
                "redaction_applied": event["redaction_applied"],
            },
        })
        if exposed:
            findings.append({
                "finding_id": f"{event_id}-privacy-egress",
                "title": "Potential sensitive-data egress without redaction",
                "category": "sensitive_data_egress",
                "severity": "UNRATED",
                "risky_behavior": True,
                "finding_verdict": "UNCONFIRMED",
                "description": (
                    "A detector identified entity types outside the event policy on an "
                    "unredacted output/retrieval path marked for an external or untrusted "
                    "destination. Validate detector accuracy, policy intent and actual "
                    "delivery before confirming impact."
                ),
            })

    return {
        "adapter": "target_event_privacy",
        "adapter_version": "0.1.0",
        "event_count": len(tests),
        "tests": tests,
        "findings": findings,
        "limitations": [
            "The caller is responsible for instrumenting the real application data path and supplying complete, truthful policy metadata.",
            "The detector receives raw text in memory; this adapter does not persist it, but caller-side logging may do so.",
            "Entity-type detection is not proof that a value is valid, secret, or attributable to a person.",
            "A signal remains UNCONFIRMED until delivery, authorization, business context and impact are reviewed.",
            "No OWASP mapping or severity is assigned automatically.",
        ],
    }
