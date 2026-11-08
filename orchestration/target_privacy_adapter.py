"""Privacy assessment for explicitly instrumented LLM/RAG data-flow events.

The caller supplies an entity detector (for example, a configured Presidio analyzer).
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

    A signal is emitted when disallowed entity types are detected on content marked
    for egress to an external/untrusted destination without redaction.
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
                    "unredacted data-flow event marked for an external or untrusted "
                    "destination. Validate detector accuracy, policy intent and actual "
                    "delivery before confirming impact."
                ),
            })

    return {
        "adapter": "target_event_privacy",
        "adapter_version": "0.2.0",
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


class PrivacyEventRecorder:
    """Incrementally assess events and retain only redacted results.

    Call record_event at each application boundary. The raw event text is passed
    to assess_events synchronously and is not retained by this recorder.
    """

    def __init__(
        self,
        detect_entities: Callable[[str], Iterable[Mapping[str, Any]]],
        result_sink: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self._detect_entities = detect_entities
        self._result_sink = result_sink
        self._seen_ids: set[str] = set()
        self._tests: list[dict[str, Any]] = []
        self._findings: list[dict[str, Any]] = []

    def record_event(self, event: Mapping[str, Any]) -> dict[str, Any]:
        validate_event(event)
        event_id = event["event_id"]
        if event_id in self._seen_ids:
            raise EventContractError(f"Duplicate event_id: {event_id}")
        # assess_events validates again and ensures exactly the same policy path is used.
        assessed = assess_events([event], self._detect_entities)
        self._seen_ids.add(event_id)
        self._tests.extend(assessed["tests"])
        self._findings.extend(assessed["findings"])
        if self._result_sink is not None:
            # Only normalized/redacted data is passed to the caller's persistence hook.
            self._result_sink(assessed)
        return assessed

    def result(self) -> dict[str, Any]:
        """Return the accumulated redacted result; raw event text is not retained."""
        return {
            "adapter": "target_event_privacy",
            "adapter_version": "0.2.0",
            "event_count": len(self._tests),
            "tests": list(self._tests),
            "findings": list(self._findings),
            "limitations": [
                "The caller is responsible for instrumenting the real application data path and supplying complete, truthful policy metadata.",
                "The detector receives raw text in memory; this recorder does not retain it, but caller-side logging may do so.",
                "Entity-type detection is not proof that a value is valid, secret, or attributable to a person.",
                "A signal remains UNCONFIRMED until delivery, authorization, business context and impact are reviewed.",
                "No OWASP mapping or severity is assigned automatically.",
            ],
        }
