# Assessment planning and orchestration MVP

## What this adds

A small evidence-aware planning/orchestration layer. It reads an assessment manifest, resolves selected tools against a registry, applies a model-archetype applicability gate and produces a plan.

The MVP has one allowlisted local reference runner: Microsoft Presidio against synthetic fixtures. It can optionally invoke that runner. IBM ART experiments remain Google Colab notebooks and are marked `MANUAL_COLAB`; other external tools require user configuration and are not falsely represented as executable adapters.

This is **not** a unified scanner, automatic attack selector for every tool, or claim that all catalogue tools are integrated.

## Files

- `tool_registry.json`: tool IDs, workstreams, applicability, execution modes and references.
- `assessment_manifest.schema.json`: JSON Schema for assessment inputs.
- `evidence_record.schema.json`: normalized contract for completed tool runs, tests, findings and evidence artifacts.
- `validate_evidence.py`: validates an evidence JSON file against that contract.
- `examples/mineru_assessment.example.json`: sample manifest; authorisation is deliberately false.
- `build_assessment_plan.py`: standard-library planner with an opt-in Presidio runner.

## Plan only (default)

From the repository root:

```bash
python orchestration/build_assessment_plan.py --manifest orchestration/examples/mineru_assessment.example.json --output-dir ./assessment-plan-output
```

Produces JSON plan, Markdown plan and orchestration log. It does not execute tests.

## Evidence record validation

Install the validator dependency:

```bash
python -m pip install "jsonschema>=4.20,<5"
```

Validate a tool-produced record:

```bash
python orchestration/validate_evidence.py path/to/evidence-record.json
```

The schema requires run identity, target, timestamps, execution status, test outcomes and artifact hashes. Finding verdicts are independent from test outcomes:

| Field | Meaning |
|---|---|
| Test status `PASS` / `FAIL` / `ERROR` | Outcome of an individual test case |
| Finding verdict `CONFIRMED_TRUE` | Evidence and review support a true finding |
| Finding verdict `CONFIRMED_FALSE` | Review determined the suspected issue is a false positive |
| Finding verdict `UNCONFIRMED` | Signal requires further validation |

A failed test is not automatically a confirmed vulnerability. A risky-behaviour flag records the observed risk characteristic; it does not replace severity or finding validation. Evidence artifacts require SHA-256 hashes so downstream reports can identify the exact collected files.

The schema defines the interchange contract; it does not execute tools, attest that a tool ran, or independently validate the truth of a finding.

## Optional Presidio execution

1. Review the target and scope.
2. Set `authorisation.confirmed` to true only after written authorisation.
3. Keep `data_policy.synthetic_data_only` true.
4. Ensure the companion `AI-Testing-Tool-Samples` repository is checked out beside this repository so the registered relative runner and fixture paths resolve.
5. Install dependencies from the companion Presidio requirements file and the NLP model required by your Presidio configuration.
6. Run the planner with `--execute-presidio`.

Example:

```bash
python orchestration/build_assessment_plan.py \
  --manifest path/to/authorised-synthetic-manifest.json \
  --output-dir ./assessment-output \
  --execute-presidio
```

The adapter invokes only the fixed, registry-allowlisted Presidio script with an argument list (not a shell command) and a bounded 900-second timeout. It refuses execution when authorisation, synthetic-data policy or model-archetype applicability gates do not pass.

The companion runner continues to write exactly two files in `assessment-output/presidio/`:

- `presidio_report.html`
- `presidio_run.log`

With `--emit-evidence-summary`, the runner also emits one redacted `PRESIDIO_EVIDENCE_SUMMARY=` JSON line on stdout. This line contains fixture IDs, entity-type labels and confidence scores, but no raw fixture text or detected values. The orchestrator consumes it and writes `assessment-output/presidio_evidence.json`, including normalized test outcomes, unconfirmed candidate observations, execution metadata and SHA-256 hashes of the two runner artifacts. Raw stdout/stderr are not copied into the orchestration log.

A missed expected entity is recorded as a failed test and an **UNCONFIRMED** candidate with severity **UNRATED**. An unexpected entity type is recorded as a possible false-positive candidate, also **UNCONFIRMED**. Neither is promoted to a confirmed vulnerability: this fixture-only run does not assess a production data flow or application-level impact. No OWASP mapping is assigned.

If the runner fails, the orchestrator records a failed/partial execution and returns a non-zero exit code. A failure is not a security finding.

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

The `.github/workflows/orchestration-validation.yml` workflow checks Python syntax, registry/manifest JSON, notebook JSON structure, planner and evidence-schema unit tests, evidence schema JSON validity and plan generation in plan-only mode. It does not run Colab notebooks or execute assessment tools.
