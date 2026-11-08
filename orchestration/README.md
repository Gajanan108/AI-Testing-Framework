# Assessment planning and orchestration MVP

## What this adds

A small evidence-aware planning/orchestration layer. It reads an assessment manifest, resolves selected tools against a registry, applies a model-archetype applicability gate and produces a plan.

The MVP has one allowlisted local reference runner: Microsoft Presidio against synthetic fixtures. It can optionally invoke that runner. IBM ART experiments remain Google Colab notebooks and are marked `MANUAL_COLAB`; other external tools require user configuration and are not falsely represented as executable adapters.

The target privacy adapter is an in-process library for applications that instrument LLM/RAG prompt, response and retrieval boundaries. It accepts a detector callback, evaluates policy metadata and returns redacted observations. `PrivacyEventRecorder` supports incremental capture: each event is assessed synchronously, and only normalized results are retained. It does not connect to an application, endpoint, model, or telemetry platform by itself.

This is **not** a unified scanner, automatic attack selector for every tool, or claim that all catalogue tools are integrated.

## Files

- `tool_registry.json`: tool IDs, workstreams, applicability, execution modes and references.
- `assessment_manifest.schema.json`: JSON Schema for assessment inputs.
- `evidence_record.schema.json`: normalized contract for completed tool runs, tests, findings and evidence artifacts.
- `target_privacy_event.schema.json`: event contract for caller-instrumented LLM/RAG data flows.
- `target_privacy_adapter.py`: validates and assesses instrumented privacy events; includes incremental `PrivacyEventRecorder`.
- `validate_evidence.py`: validates an evidence JSON file against the evidence contract.
- `examples/mineru_assessment.example.json`: sample manifest; authorisation is deliberately false.
- `build_assessment_plan.py`: standard-library planner with an opt-in Presidio runner.

## Target-interface privacy integration

Instrument the actual application at three boundaries:

1. **Prompt input:** immediately before the prompt is sent to the model/provider.
2. **Retrieved document:** after retrieval and before the document is inserted into model context.
3. **Model output:** after generation and before the response is delivered to its destination.

For each boundary, call `PrivacyEventRecorder.record_event()` with the event schema fields. Set `destination_trust`, `egress_allowed`, `redaction_applied` and `allowed_entity_types` from the application's actual data-handling policy—not from assumptions. For example, a prompt sent to a hosted model provider may have an external destination; a response delivered to an authenticated internal user may have a trusted destination.

Example using a configured Presidio detector and a FastAPI route (illustrative integration points; replace the retrieval, model and response-policy functions with the application's real implementations):

```python
from fastapi import FastAPI
from presidio_analyzer import AnalyzerEngine

from orchestration.target_privacy_adapter import PrivacyEventRecorder

app = FastAPI()
analyzer = AnalyzerEngine()

def detect_entities(text):
    return [
        {"entity_type": item.entity_type, "score": item.score}
        for item in analyzer.analyze(text=text, language="en")
    ]

@app.post("/chat")
async def chat(payload: dict):
    # Create one recorder per request/trace; persist only its redacted result.
    recorder = PrivacyEventRecorder(detect_entities=detect_entities)

    prompt = build_prompt(payload)
    recorder.record_event({
        "event_id": "prompt-1",
        "event_type": "prompt_input",
        "text": prompt,
        "destination_trust": model_provider_trust(),
        "egress_allowed": model_provider_egress_is_allowed(),
        "redaction_applied": prompt_was_redacted(),
        "allowed_entity_types": policy_allowed_entity_types(),
    })

    documents = retrieve_documents(payload)
    for index, document in enumerate(documents):
        recorder.record_event({
            "event_id": f"retrieval-{index}",
            "event_type": "retrieved_document",
            "text": document.text,
            "destination_trust": model_provider_trust(),
            "egress_allowed": model_provider_egress_is_allowed(),
            "redaction_applied": document_was_redacted(document),
            "allowed_entity_types": policy_allowed_entity_types(),
        })

    answer = await call_model(prompt, documents)
    recorder.record_event({
        "event_id": "output-1",
        "event_type": "model_output",
        "text": answer,
        "destination_trust": response_destination_trust(payload),
        "egress_allowed": response_egress_is_allowed(payload),
        "redaction_applied": answer_was_redacted(answer),
        "allowed_entity_types": policy_allowed_entity_types(),
    })

    redacted_assessment = recorder.result()
    persist_privacy_assessment(redacted_assessment)  # Never persist raw event text.
    return {"answer": answer}
```

The adapter only emits a risky-behaviour candidate when it detects a disallowed entity type on an event marked for egress to an external or untrusted destination without redaction. This includes prompt input sent to a hosted provider, retrieved content sent into a model context, and output sent to a destination. The candidate remains `UNCONFIRMED` and `UNRATED`; the adapter does not infer an OWASP mapping. A passing result means only that this rule did not fire for the supplied events, not that the application is privacy-safe.

The recorder passes raw text to the detector synchronously but does not retain it. A result sink, if configured, receives only normalized/redacted observations. The caller must still prevent its own application, detector, tracing, APM and HTTP logs from retaining sensitive content. Use synthetic data by default and run against real data only under documented authorization and an approved data-handling policy. The adapter does not enforce authorization, verify instrumentation completeness, or write a full evidence record with artifact hashes.

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

A missed expected entity is recorded as a failed test and an **UNCONFIRMED** candidate with severity **UNRATED**. An unexpected entity type is recorded as a possible false-positive candidate, also **UNCONFIRMED**. Neither is promoted to a confirmed vulnerability: this fixture-only runner evaluates Presidio against the fixture set and is not wired to the target model or application data flow. It does not assess production exposure or application-level impact. No OWASP mapping is assigned.

If the runner fails, the orchestrator records a failed/partial execution and returns a non-zero exit code. A failure is not a security finding.

## Status semantics

| Status | Meaning |
|---|---|
| NOT_APPLICABLE | Registry does not map the selected model archetype to the tool |
| REVIEW_REQUIRED | Conditional fit; verify component/interface |
| MANUAL_COLAB | Open and run the referenced notebook in Colab |
| READY_LOCAL | An allowlisted local runner exists; execution remains opt-in |
| UPSTREAM_CONFIGURATION_REQUIRED | Documentation exists; configure and run the upstream tool |
| EXECUTED / FAILED | Allowlisted runner completed or failed |

Finding status is independent. This MVP never promotes a tool result to a confirmed finding.

## Current integration coverage

- Presidio: optional local synthetic-fixture runner.
- Target privacy event adapter: in-process recorder library; application instrumentation and detector wiring required.
- IBM ART MinerU and MiniLM: Colab notebook references; manual execution.
- AIF360, TextAttack, Garak, LIME, InterpretML, JMeter, Locust, Evidently, Giskard, Splunk and Elastic Security: documented upstream configuration; no local adapters claimed.

Add adapters only when their input contract, authentication, invocation, timeout, output contract, failure handling and evidence provenance are documented. Do not accept arbitrary shell commands from manifests.

## Automated validation

The `.github/workflows/orchestration-validation.yml` workflow checks Python syntax, registry/manifest JSON, notebook JSON structure, planner and evidence-schema unit tests, evidence schema JSON validity and plan generation in plan-only mode. It does not run Colab notebooks or execute assessment tools.
