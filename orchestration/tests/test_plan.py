from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ORCH = Path(__file__).resolve().parents[1]
ROOT = ORCH.parent
sys.path.insert(0, str(ORCH))

import build_assessment_plan as planner  # noqa: E402


class AssessmentPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads((ORCH / "tool_registry.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads(
            (ORCH / "examples" / "mineru_assessment.example.json").read_text(encoding="utf-8")
        )

    def test_example_manifest_selects_colab_and_local_runner_without_execution(self):
        plan = planner.build_plan(self.manifest, self.registry)
        statuses = {item["tool_id"]: item["execution_status"] for item in plan["tools"]}
        self.assertEqual(statuses["ibm_art_mineru_layout"], "MANUAL_COLAB")
        self.assertEqual(statuses["presidio"], "READY_LOCAL")
        self.assertTrue(plan["planning_only"])
        self.assertTrue(all(item["finding_status"] == "NONE" for item in plan["tools"]))

    def test_unmatched_model_archetype_is_not_applicable(self):
        manifest = json.loads(json.dumps(self.manifest))
        manifest["target"]["model_archetype"] = "audio_speech_model"
        manifest["selected_tools"] = ["ibm_art_mineru_layout"]
        plan = planner.build_plan(manifest, self.registry)
        self.assertEqual(plan["tools"][0]["execution_status"], "NOT_APPLICABLE")

    def test_unknown_tool_id_is_rejected(self):
        manifest = json.loads(json.dumps(self.manifest))
        manifest["selected_tools"] = ["not-a-registered-tool"]
        with self.assertRaisesRegex(ValueError, "Unknown tool IDs"):
            planner.build_plan(manifest, self.registry)

    def test_authorisation_is_not_assumed(self):
        plan = planner.build_plan(self.manifest, self.registry)
        self.assertFalse(plan["authorisation_confirmed"])


if __name__ == "__main__":
    unittest.main()
