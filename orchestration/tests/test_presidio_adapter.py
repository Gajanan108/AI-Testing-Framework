from __future__ import annotations

import sys
import unittest
from pathlib import Path

ORCH = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ORCH))

from build_assessment_plan import build_presidio_evidence  # noqa: E402
from validate_evidence import validate_record  # noqa: E402


class PresidioEvidenceAdapterTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {
            "assessment_id": "presidio-adapter-test",
            "target": {
                "name": "Synthetic fixture target",
                "model_archetype": "llm_application",
                "interface": "text",
            },
        }
        self.artifacts = [
            {
                "path": "presidio/presidio_report.html",
                "sha256": "a" * 64,
                "media_type": "text/html",
                "description": "Synthetic test report",
            },
            {
                "path": "presidio/presidio_run.log",
                "sha256": "b" * 64,
                "media_type": "text/plain",
                "description": "Synthetic test log",
            },
        ]
        self.times = {
            "started_at": "2026-01-01T10:00:00Z",
            "finished_at": "2026-01-01T10:01:00Z",
            "artifacts": self.artifacts,
            "run_id": "unit-test-run",
        }

    def test_missed_entity_is_unconfirmed_not_a_true_finding(self):
        summary = {
            "execution_status": "EXECUTED",
            "tool_version": "test-version",
            "tests": [{
                "test_id": "PII-EMAIL-001",
                "test_name": "Synthetic email address",
                "expected_entities": ["EMAIL_ADDRESS"],
                "detected_entities": [],
                "missed_entities": ["EMAIL_ADDRESS"],
                "unexpected_entities": [],
                "scores": [],
            }],
        }
        record = build_presidio_evidence(self.manifest, summary, **self.times)
        self.assertEqual(record["execution_status"], "COMPLETED")
        self.assertEqual(record["tests"][0]["status"], "FAIL")
        self.assertEqual(record["findings"][0]["finding_verdict"], "UNCONFIRMED")
        self.assertFalse(record["findings"][0]["risky_behavior"])
        self.assertEqual(validate_record(record), [])

    def test_unexpected_entity_is_not_automatically_a_confirmed_false_positive(self):
        summary = {
            "execution_status": "EXECUTED",
            "tool_version": "test-version",
            "tests": [{
                "test_id": "PII-PHONE-001",
                "test_name": "Synthetic telephone number",
                "expected_entities": ["PHONE_NUMBER"],
                "detected_entities": ["EMAIL_ADDRESS", "PHONE_NUMBER"],
                "missed_entities": [],
                "unexpected_entities": ["EMAIL_ADDRESS"],
                "scores": [{"entity_type": "PHONE_NUMBER", "score": 0.9}],
            }],
        }
        record = build_presidio_evidence(self.manifest, summary, **self.times)
        self.assertEqual(record["findings"][0]["category"], "possible_false_positive")
        self.assertEqual(record["findings"][0]["finding_verdict"], "UNCONFIRMED")
        self.assertEqual(validate_record(record), [])

    def test_clean_fixture_is_pass_without_findings(self):
        summary = {
            "execution_status": "EXECUTED",
            "tool_version": "test-version",
            "tests": [{
                "test_id": "PII-CARD-001",
                "test_name": "Synthetic payment card",
                "expected_entities": ["CREDIT_CARD"],
                "detected_entities": ["CREDIT_CARD"],
                "missed_entities": [],
                "unexpected_entities": [],
                "scores": [{"entity_type": "CREDIT_CARD", "score": 0.95}],
            }],
        }
        record = build_presidio_evidence(self.manifest, summary, **self.times)
        self.assertEqual(record["tests"][0]["status"], "PASS")
        self.assertEqual(record["findings"], [])
        self.assertEqual(validate_record(record), [])

    def test_partial_runner_execution_is_not_marked_complete(self):
        summary = {"execution_status": "FAILED", "tool_version": "test-version", "tests": []}
        record = build_presidio_evidence(self.manifest, summary, **self.times)
        self.assertEqual(record["execution_status"], "FAILED")
        self.assertEqual(validate_record(record), [])

    def test_no_artifacts_does_not_create_unreferenced_findings(self):
        summary = {
            "execution_status": "EXECUTED",
            "tool_version": "test-version",
            "tests": [{
                "test_id": "PII-EMAIL-001",
                "test_name": "Synthetic email",
                "expected_entities": ["EMAIL_ADDRESS"],
                "detected_entities": [],
                "missed_entities": ["EMAIL_ADDRESS"],
                "unexpected_entities": [],
                "scores": [],
            }],
        }
        record = build_presidio_evidence(
            self.manifest,
            summary,
            started_at=self.times["started_at"],
            finished_at=self.times["finished_at"],
            artifacts=[],
            run_id="unit-test-no-artifacts",
        )
        self.assertEqual(record["findings"], [])
        self.assertEqual(validate_record(record), [])


if __name__ == "__main__":
    unittest.main()
