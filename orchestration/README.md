# Assessment planning and orchestration MVP

## What this adds

An evidence-aware planning and orchestration layer. It reads an assessment manifest, resolves selected tools against a registry, applies a model-archetype applicability gate and produces a plan.

The MVP has an allowlisted local reference runner: Microsoft Presidio against synthetic fixtures. IBM ART experiments remain Google Colab notebooks and are marked `MANUAL_COLAB`; other external tools require user configuration.

The target privacy adapter is an in-process library for applications that instrument LLM/RAG prompt, response and retrieval boundaries. It accepts a detector callback, evaluates policy metadata and returns redacted observations. `PrivacyEventRecorder` supports incremental capture; `run_target_privacy.py` adds a local JSONL runner, normalized evidence record, HTML report and redacted execution log. The runner is restricted to authorized synthetic data.

This is **not** a unified scanner, automatic attack selector for every tool, or claim that all catalogue tools are integrated.

## Files

- `tool_registry.json`: tool IDs, workstreams, applicability, execution modes and references.
- `assessment_manifest.schema.json`: JSON Schema for assessment inputs.
- `evidence_record.schema.json`: normalized contract for completed tool runs, tests, findings and evidence artifacts.
- `target_privacy_event.schema.json`: event contract for caller-instrumented LLM/RAG data flows.
- `target_privacy_adapter.py`: event validation and incremental `PrivacyEventRecorder`.
- `target_privacy_pipeline.py`: normalized evidence record, artifact hashing, HTML report and log generation.
- `run_target_privacy.py`: authorized synthetic JSONL runner using Microsoft Presidio.
- `validate_evidence.py`: validates evidence JSON against the shared contract.
- `build_assessment_plan.py`: planner with an opt-in Presidio fixture runner.

## Target-interface privacy integration

Instrument the actual application at three boundaries:

1. **Prompt input:** immediately before the prompt is sent to the model/provider.
2. **Retrieved document:** after retrieval and before the document is inserted into model context.
3. **Model output:** after generation and before the response is delivered to its destination.

For each boundary, call `PrivacyEventRecorder.record_event()` with the event schema fields. Set `destination_trust`, `egress_allowed`, `redaction_applied` and `allowed_entity_types` from the application's actual data-handling policy—not from assumptions.

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
    persist_privacy_assessment(recorder.result())  # Redacted result only.
    return {"answer": answer}
```

The adapter emits an unconfirmed candidate when it detects a disallowed entity type on an event marked for egress to an external or untrusted destination without redaction. It checks prompt input, retrieved content and model output. Candidates remain `UNCONFIRMED` and `UNRATED`; no OWASP mapping is inferred. A passing result means only that this rule did not fire for supplied events, not that the application is privacy-safe.

The recorder passes raw text to the detector synchronously but does not retain it. The caller must prevent its own application, detector, tracing, APM and HTTP logs from retaining sensitive content. The adapter does not enforce authorization or verify instrumentation completeness.

## Run the target privacy pipeline

The input is newline-delimited JSON (one event object per line) conforming to `target_privacy_event.schema.json`. Keep the input synthetic for this reference runner.

Install dependencies and the Presidio language model configured for your environment:

```bash
python -m pip install "jsonschema>=4.20,<5" "presidio-analyzer"
python -m spacy download en_core_web_lg
```

Run only after confirming written authorization and using synthetic fixtures:

```bash
python orchestration/run_target_privacy.py \
  --events path/to/synthetic-events.jsonl \
  --output-dir ./target-privacy-output \
  --assessment-id demo-privacy-001 \
  --target-name "Synthetic RAG application" \
  --model-archetype rag_application \
  --authorization-confirmed \
  --synthetic-data-only
```

The runner refuses to start unless both explicit flags are supplied. It does not make network requests or call a target model; it analyzes event text supplied by the caller. The application must instrument and export the events itself.

The output directory contains:

- `target_privacy_report.html` — report with event outcomes, risk indicators and finding verdicts.
- `target_privacy_run.log` — redacted execution summary; no raw event content.
- `target_privacy_evidence.json` — normalized evidence record conforming to the shared schema, with SHA-256 hashes for the HTML report and log.

The evidence JSON is a third output because the framework needs a machine-readable, independently validated record. It does not contain raw event text or detected values. Candidate findings remain unconfirmed; severity is unrated; OWASP mappings are omitted.

## Plan only (default)

```bash
python orchestration/build_assessment_plan.py --manifest orchestration/examples/mineru_assessment.example.json --output-dir ./assessment-plan-output
```

Produces JSON plan, Markdown plan and orchestration log. It does not execute tests.

## Evidence record validation

Install `jsonschema>=4.20,<5` and validate a record:

```bash
python orchestration/validate_evidence.py ./target-privacy-output/target_privacy_evidence.json
```

Test status (`PASS`/`FAIL`) is separate from finding verdict (`CONFIRMED_TRUE`/`CONFIRMED_FALSE`/`UNCONFIRMED`). A failed test is not automatically a confirmed vulnerability. A risky-behaviour flag records an observed risk characteristic; it does not replace severity or finding validation.

## Optional Presidio fixture execution

The companion repository's Presidio runner continues to write `presidio_report.html` and `presidio_run.log` under its own output directory. The planner consumes its redacted stdout summary and writes `presidio_evidence.json` at the orchestration output root. That reference run tests Presidio against synthetic fixtures only; it is not wired to the target model or application data flow.

## Current integration coverage

- Presidio: optional local synthetic-fixture runner.
- Target privacy event adapter: local synthetic JSONL runner and in-process recorder; caller instrumentation required.
- IBM ART MinerU and MiniLM: Colab notebook references; manual execution.
- AIF360, TextAttack, Garak, LIME, InterpretML, JMeter, Locust, Evidently, Giskard, Splunk and Elastic Security: documented upstream configuration; no local adapters claimed.

The CI workflow compiles orchestration modules, validates JSON, checks notebook structure, runs unit tests and builds a plan without executing assessment tools. It does not run the target privacy runner or IBM ART notebooks.
