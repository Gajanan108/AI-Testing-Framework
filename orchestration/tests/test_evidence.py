from __future__ import annotations
import sys, unittest
from pathlib import Path
ORCH=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ORCH))
from validate_evidence import validate_record

def valid_record():
    return {
      "schema_version":"1.0","assessment_id":"unit-test-assessment","run_id":"unit-test-run-001","tool_id":"test-tool",
      "target":{"name":"Synthetic test model","model_archetype":"text_classifier"},
      "started_at":"2026-01-01T10:00:00Z","finished_at":"2026-01-01T10:01:00Z","execution_status":"COMPLETED",
      "tests":[{"test_id":"case-001","test_name":"Synthetic control check","status":"FAIL","observation":"Control did not behave as expected.","evidence_refs":["artifact-001"]}],
      "findings":[{"finding_id":"finding-001","title":"Unverified test signal","category":"robustness","severity":"UNRATED","risky_behavior":True,"finding_verdict":"UNCONFIRMED","evidence_refs":["artifact-001"]}],
      "artifacts":[{"path":"artifacts/raw-output.json","sha256":"a"*64,"media_type":"application/json","description":"Synthetic unit-test fixture"}]
    }

class EvidenceSchemaTests(unittest.TestCase):
    def test_valid_record_passes(self): self.assertEqual(validate_record(valid_record()),[])
    def test_test_failure_can_remain_unconfirmed(self):
        record=valid_record()
        self.assertEqual(validate_record(record),[])
    def test_missing_artifact_hash_is_rejected(self):
        record=valid_record(); del record["artifacts"][0]["sha256"]
        self.assertTrue(any("sha256" in error for error in validate_record(record)))
    def test_unknown_finding_verdict_is_rejected(self):
        record=valid_record(); record["findings"][0]["finding_verdict"]="TRUE"
        self.assertTrue(any("finding_verdict" in error for error in validate_record(record)))
    def test_false_positive_is_distinct_from_failed_test(self):
        record=valid_record(); record["findings"][0]["finding_verdict"]="CONFIRMED_FALSE"
        self.assertEqual(validate_record(record),[])

if __name__=="__main__": unittest.main()
