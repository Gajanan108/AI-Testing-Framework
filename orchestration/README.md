# Assessment planning and orchestration MVP

## What this adds

A small evidence-aware planning/orchestration layer. It reads an assessment manifest, resolves selected tools against a registry, applies a model-archetype applicability gate and produces a plan.

The MVP has one allowlisted local reference runner: Microsoft Presidio against synthetic fixtures. It can optionally invoke that runner. IBM ART experiments remain Google Colab notebooks and are marked `MANUAL_COLAB`; other external tools require user configuration and are not falsely represented as executable adapters.

This is **not** a unified scanner, automatic attack selector for every tool, or claim that all catalogue tools are integrated.

## Files

- `tool_registry.json`: tool IDs, workstreams, applicability, execution modes and references.
- `assessment_manifest.schema.json`: JSON Schema for assessment inputs.
- `examples/mineru_assessment.example.json`: sample manifest; authorisation is deliberately false.
- `build_assessment_plan.py`: standard-library planner with an opt-in Presidio runner.

## Plan only (default)

From the repository root:

```bash
python orchestration/build_assessment_plan.py --manifest orchestration/examples/mineru_assessment.example.json --output-dir ./assessment-plan-output
```

Produces JSON plan, Markdown plan and orchestration log. It does not execute tests.

## Optional Presidio execution

1. Review the target and scope.
2. Set `authorisation.confirmed` to true only after written authorisation.
3. Keep `data_policy.synthetic_data_only` true.
4. Install dependencies from the companion Presidio requirements file.
5. Run the planner with `--execute-presidio`.

The adapter uses an argument list (not a shell command), a fixed registry entry and a bounded timeout. It invokes only the synthetic Presidio fixture script. It does not send data to an external endpoint.

## Status semantics

| Status | Meaning |
|---|---|
| NOT_APPLICABLE | Registry does not map the selected model archetype to the tool |
| REVIEW_REQUIRED | Conditional fit; verify component/interface |
| MANUAL_COLAB | Open and run the referenced notebook in Colab |
| READY_LOCAL | An allowlisted local runner exists; execution remains opt-in |
| UPSTREAM_CONFIGURATION_REQUIRED | Documentation exists; configure and run upstream tool |
| EXECUTED / FAILED | Allowlisted runner completed or failed |

Finding status is independent. This MVP never promotes a tool result to a confirmed finding.

## Current integration coverage

- Presidio: optional local synthetic-fixture runner.
- IBM ART MinerU and MiniLM: Colab notebook references; manual execution.
- AIF360, TextAttack, Garak, LIME, InterpretML, JMeter, Locust, Evidently, Giskard, Splunk and Elastic Security: documented upstream configuration; no local adapters claimed.

Add adapters only when their input contract, authentication, invocation, timeout, output contract, failure handling and evidence provenance are documented. Do not accept arbitrary shell commands from manifests.

## Automated validation

The `.github/workflows/orchestration-validation.yml` workflow checks Python syntax, registry/manifest JSON, notebook JSON structure, planner unit tests and plan generation in plan-only mode. It does not run Colab notebooks or execute assessment tools.
