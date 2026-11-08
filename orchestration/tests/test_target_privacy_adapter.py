from __future__ import annotations

import sys
import unittest
from pathlib import Path

ORCH = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ORCH))

from target_privacy_adapter import EventContractError, PrivacyEventRecorder, assess_events  # noqa: E402


def detector(_text):
    return [{"entity_type": "EMAIL_ADDRESS", "score": 0.99}]


def event(**overrides):
    value = {
        "event_id": "evt-1",
        "event_type": "model_output",
        "text": "synthetic person@example.test",
        "destination_trust": "external",
        "egress_allowed": True,
        "redaction_applied": False,
        "allowed_entity_types": [],
    }
    value.update(overrides)
    return value


class TargetPrivacyAdapterTests(unittest.TestCase):
    def test_unredacted_disallowed_entity_on_external_output_is_unconfirmed_risk(self):
        result = assess_events([event()], detector)
        self.assertEqual(result["tests"][0]["status"], "FAIL")
        self.assertEqual(result["findings"][0]["finding_verdict"], "UNCONFIRMED")
        self.assertTrue(result["findings"][0]["risky_behavior"])
        self.assertNotIn("person@example.test", str(result))

    def test_redaction_prevents_egress_signal(self):
        result = assess_events([event(redaction_applied=True)], detector)
        self.assertEqual(result["tests"][0]["status"], "PASS")
        self.assertEqual(result["findings"], [])

    def test_internal_prompt_input_is_not_classified_as_egress(self):
        result = assess_events([event(event_type="prompt_input", destination_trust="internal")], detector)
        self.assertEqual(result["findings"], [])

    def test_external_prompt_input_is_checked_as_egress(self):
        result = assess_events([event(event_type="prompt_input")], detector)
        self.assertEqual(len(result["findings"]), 1)

    def test_allowed_entity_type_is_not_a_policy_violation(self):
        result = assess_events([event(allowed_entity_types=["EMAIL_ADDRESS"])], detector)
        self.assertEqual(result["findings"], [])

    def test_duplicate_event_ids_are_rejected(self):
        with self.assertRaises(EventContractError):
            assess_events([event(), event()], detector)

    def test_missing_policy_field_is_rejected(self):
        invalid = event()
        del invalid["egress_allowed"]
        with self.assertRaises(EventContractError):
            assess_events([invalid], detector)

    def test_recorder_retains_only_redacted_results(self):
        persisted = []
        recorder = PrivacyEventRecorder(detector, result_sink=persisted.append)
        recorder.record_event(event())
        result = recorder.result()
        self.assertEqual(result["event_count"], 1)
        self.assertNotIn("person@example.test", str(result))
        self.assertNotIn("person@example.test", str(persisted))
        self.assertEqual(len(result["findings"]), 1)

    def test_recorder_rejects_duplicate_event_ids(self):
        recorder = PrivacyEventRecorder(detector)
        recorder.record_event(event())
        with self.assertRaises(EventContractError):
            recorder.record_event(event())

    def test_recorder_handles_multiple_application_boundaries(self):
        recorder = PrivacyEventRecorder(detector)
        recorder.record_event(event(event_id="prompt", event_type="prompt_input"))
        recorder.record_event(event(event_id="retrieval", event_type="retrieved_document"))
        self.assertEqual(recorder.result()["event_count"], 2)


if __name__ == "__main__":
    unittest.main()
