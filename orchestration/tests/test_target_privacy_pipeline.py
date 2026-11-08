from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ORCH = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ORCH))

from target_privacy_pipeline import write_run_outputs  # noqa: E402
from validate_evidence import validate_record  # noqa: E402


class TargetPrivacyPipelineTests(unittest.TestCase):
    def setUp(self):
        self.result = {
            "adapter": "target_event_privacy",
            "adapter_version": "0.2.0",
            "event_count": 1,
            "tests": [{
                "test_id": "evt-1",
                "test_name": "Privacy inspection: model_output",
                "status": "FAIL",
                "category": "data_flow_privacy",
                "observation": "Disallowed entity types observed on an unredacted external egress path.",
                "metrics": {"event_type": "model_output", "detected_entity_types": ["EMAIL_ADDRESS"]},
            }],
            "findings": [{
                "finding_id": "evt-1-privacy-egress",
                "title": "Potential sensitive-data egress without redaction",
                "category": "sensitive_data_egress",
                "severity": "UNRATED",
                "risky_behavior": True,
                "finding_verdict": "UNCONFIRMED",
                "description": "Synthetic test signal requiring review.",
            }],
            "limitations": ["Synthetic event test only."],
        }

    def test_writes_report_log_and_schema_valid_evidence_with_hashes(self):
        with tempfile.TemporaryDirectory() as temp:
            record = write_run_outputs(
                Path(temp),
                assessment_id="pipeline-test",
                target={"name": "Synthetic target", "model_archetype": "rag_application", "interface": "test"},
                result=self.result,
                started_at="2026-11-08T10:00:00Z",
                finished_at="2026-11-08T10:00:01Z",
                detector_version="test-version",
                run_id="test-run",
            )
            self.assertEqual(validate_record(record), [])
            self.assertEqual({p.name for p in Path(temp).iterdir()}, {
                "target_privacy_report.html",
                "target_privacy_run.log",
                "target_privacy_evidence.json",
            })
            persisted = json.loads((Path(temp) / "target_privacy_evidence.json").read_text())
            self.assertEqual(validate_record(persisted), [])
            self.assertTrue(all(len(item["sha256"]) == 64 for item in persisted["artifacts"]))

    def test_report_and_log_do_not_contain_raw_event_values(self):
        with tempfile.TemporaryDirectory() as temp:
            write_run_outputs(
                Path(temp),
                assessment_id="pipeline-test",
                target={"name": "Synthetic target", "model_archetype": "rag_application"},
                result=self.result,
                started_at="2026-11-08T10:00:00Z",
                finished_at="2026-11-08T10:00:01Z",
                detector_version="test-version",
            )
            for name in ("target_privacy_report.html", "target_privacy_run.log", "target_privacy_evidence.json"):
                content = (Path(temp) / name).read_text()
                self.assertNotIn("person@example.test", content)


if __name__ == "__main__":
    unittest.main()
