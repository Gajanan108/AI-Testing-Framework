# AI Security Testing Framework

A modular framework for assessing the **security, robustness, privacy, fairness, reliability, and operational behaviour of machine-learning (ML) and large-language-model (LLM) systems**.

The framework combines a lifecycle-based assurance model, reusable assessment modules, and model-specific technical experiments. It is intended to help security, engineering, data-science, and governance teams identify risks, execute proportionate tests, and retain evidence for remediation and release decisions.

> **Project scope:** This repository contains framework guidance and selected model-specific experiments. It is not yet a single automated platform implementing every assessment area. Capabilities are described according to their actual implementation and validation status.

## At a glance

- **Assessment coverage:** seven high-level assurance areas and nine modular testing activities.
- **Lifecycle coverage:** planning and design through development, validation, deployment, and continuous monitoring.
- **Model coverage:** conventional ML, embedding and retrieval components, document/vision models, LLM applications, and agentic workflows where suitable methods exist.
- **Evidence-led results:** distinguish planned, attempted, executed, failed, observed, potential, and confirmed outcomes.
- **Technical workstreams:** IBM Adversarial Robustness Toolbox (ART) experiments for a document-layout model and a MiniLM cross-encoder reranker.

## Framework at a glance

The framework uses two complementary views: **seven assurance areas** describe the outcomes to assess; **nine testing modules** describe the activities used to gather evidence. The lifecycle model determines when assurance activities should take place.

### Seven assurance areas

| # | Assurance area | Assessment objective | Example tooling / references |
|---|---|---|---|
| 1 | Data privacy and governance | Assess sensitive-data handling, privacy controls, data governance, and compliance obligations. | Microsoft Presidio; NIST AI RMF; applicable privacy and sector requirements |
| 2 | Bias and fairness | Identify disparate outcomes, data imbalance, and unfair model behaviour. | AI Fairness 360; TextAttack; OECD AI Principles |
| 3 | Adversarial robustness | Evaluate resistance to malicious or unexpected inputs and model manipulation. | IBM Adversarial Robustness Toolbox (ART); Garak; OWASP guidance |
| 4 | Explainability and interpretability | Assess whether model behaviour and decisions can be understood and investigated. | LIME; InterpretML; NIST AI RMF |
| 5 | Performance and scalability | Measure latency, throughput, resource consumption, and behaviour under load. | Apache JMeter; Locust |
| 6 | Operational monitoring and drift | Detect changes in input data, model behaviour, and operational performance. | Evidently AI; Giskard |
| 7 | Incident response and security monitoring | Support detection, triage, investigation, and response to AI-related security events. | SIEM platforms such as Splunk and Elastic/Kibana; NIST Cybersecurity Framework |

Tool names are examples of possible implementation choices, not a claim that every tool is integrated or suitable for every model. Select tools according to the model boundary, threat model, available interfaces, and evidence requirements.

### Nine modular testing activities

1. Data and input validation
2. Model functionality testing
3. Bias and fairness testing
4. Explainability and transparency
5. Robustness and adversarial testing
6. Performance and efficiency testing
7. Integration and system testing
8. User acceptance and ethical review
9. Continuous monitoring and improvement

See [Framework overview](docs/FRAMEWORK_OVERVIEW.md), [Assessment methodology](docs/ASSESSMENT_METHODOLOGY.md), and the [assessment flow diagram](docs/ASSESSMENT_FLOW.md).

## Continuous defensive assurance lifecycle

| Lifecycle phase | Primary focus | Typical evidence |
|---|---|---|
| Planning and design | Intended use, system boundaries, risk classification, threat modelling, privacy and security requirements | System description, data-flow diagram, threat model, assessment plan |
| Data collection and preparation | Data quality, provenance, sensitive data, representativeness, permissions | Dataset inventory, data-quality checks, privacy review |
| Model development and training | Model behaviour, robustness, fairness, explainability, training-data risks | Experiment records, evaluation results, model/version identifiers |
| Validation and verification | Functional, security, adversarial, fairness, and performance testing | Test results, reproducible findings, acceptance criteria |
| Operational readiness | Deployment controls, access, logging, monitoring, incident response, rollback | Readiness checklist, runbooks, alert tests |
| Deployment | Secure configuration, integrations, release controls, production verification | Release record, configuration evidence, smoke tests |
| Monitoring and continuous assurance | Drift, incidents, regressions, feedback, model or data changes | Monitoring results, incident records, periodic reassessments |

Apply the framework proportionately to system impact, exposure, autonomy, data sensitivity, and credible attacker capabilities.

## Technical experiments and artefacts

### Embedding and document-model testing — IBM ART

The [embedding-model-testing workstream](embedding-model-testing/README.md) contains a MinerU PP-DocLayoutV2 experiment, attack applicability guidance, and an HTML report. The current experiment uses an ART classifier adapter over layout-class presence scores. It does **not** establish robustness of OCR, bounding-box geometry, the separate VLM, or the end-to-end document pipeline.

### MiniLM cross-encoder reranker — IBM ART

The [MiniLM reranker workstream](embedding-model-testing/reranker-minilm/README.md) evaluates cross-encoder/ms-marco-MiniLM-L6-v2 using a pairwise ranking proxy and selected official ART attacks. Its attack surface is continuous internal word-embedding space; this is not equivalent to an attacker changing natural-language text at an application endpoint.

Both workstreams document attack applicability, execution status, and limitations. The reranker notebook and report template are committed, but the experiment has not yet been executed in Colab. A notebook or sample template is not completed test evidence.

## Results and finding quality

| State | Meaning |
|---|---|
| Planned | Included in the assessment scope but not run |
| Not applicable | The model or interface does not satisfy the test prerequisites |
| Attempted | Execution was initiated |
| Executed | The test method ran and produced an output |
| Failed | Execution failed; no successful test result is claimed |
| Observed behaviour | A measurable change or unexpected response was recorded |
| Potential finding | An observation may have security relevance but needs validation |
| Confirmed finding | Reproducible evidence demonstrates security-relevant impact in the stated threat model |
| False positive | The suspected issue was investigated and evidence does not support the finding |

A model score change, class flip, prompt response, or metric deviation is not automatically a vulnerability. A finding should include reproducible evidence, the affected system boundary, attacker prerequisites, impact, severity rationale, and remediation guidance. See [Finding taxonomy](docs/FINDING_TAXONOMY.md), the [finding report template](templates/FINDING_REPORT.md), and the [test case template](templates/TEST_CASE.md).

## Repository structure

- **docs/** — framework overview, assessment methodology, and finding taxonomy.
- **templates/** — reusable assessment-plan and finding-report templates.
- **embedding-model-testing/** — existing IBM ART workstream, attack matrix, notebooks, reports, and dependencies.
- **embedding-model-testing/reranker-minilm/** — separate MiniLM reranker experiment.

Existing notebooks, reports, and workstream documentation are retained.

## Getting started

1. Read the [Framework overview](docs/FRAMEWORK_OVERVIEW.md) and [assessment flow](docs/ASSESSMENT_FLOW.md).
2. Define the system boundary, intended use, data flows, deployment context, and threat model.
3. Select proportionate assessment activities using the [Assessment methodology](docs/ASSESSMENT_METHODOLOGY.md).
4. Record scope and acceptance criteria with the [Assessment plan template](templates/ASSESSMENT_PLAN.md), then define individual checks using the [Test case template](templates/TEST_CASE.md).
5. Execute only tests compatible with the model and interface. Record failures and non-applicable tests explicitly.
6. Document observations using the [Finding report template](templates/FINDING_REPORT.md).
7. Validate security impact before assigning confirmed status or severity.

## Safety and responsible use

Use the framework only against systems, models, datasets, and endpoints that you own or are explicitly authorised to assess. Use synthetic or approved test data. Do not commit secrets, customer data, proprietary model weights, or confidential reports to a public repository. See [SECURITY.md](SECURITY.md).

## Project-reported metrics

Earlier project descriptions referenced **95% drift-detection precision** and **99% PII-detection accuracy across 10GB+ of data**. These figures are retained as project-reported claims, not independently verified benchmark results in this repository. Before using them as performance claims, publish the evaluation dataset description, ground-truth method, metric definitions, test conditions, and reproducible results.

## Contributing

Contributions that improve test coverage, model adapters, reproducibility, documentation, and evidence quality are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

The repository has historically described the project as MIT-licensed. A licence file is not currently present at the repository root; add the actual licence text before treating the repository as formally licensed under MIT.
