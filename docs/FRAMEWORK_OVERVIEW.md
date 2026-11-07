# Framework overview

## 1. Purpose

The AI Security Testing Framework provides a structured approach to assessing machine-learning and AI-enabled systems across security, privacy, fairness, robustness, transparency, performance, and operational assurance.

It combines a lifecycle-based assurance model with modular testing activities. It is a framework and a collection of evolving technical workstreams; it should not be described as a unified automated scanner unless and until the individual modules are integrated and validated.

## 2. Scope

The framework can be tailored to conventional ML models; text and image embedding encoders; retrieval and reranking components; document-understanding and computer-vision models; LLM-powered applications and RAG pipelines; and agentic workflows where tools, permissions, and autonomy can be assessed.

The relevant test method depends on the system boundary and exposed interface. A model-only test does not establish the security of the surrounding application, APIs, data stores, orchestration, or user experience.

## 3. Seven assurance areas

### 3.1 Data privacy and governance
Assess data collection, provenance, retention, access, consent or other lawful basis where applicable, sensitive-data exposure, and governance controls. Include training/evaluation data and runtime inputs or outputs.

### 3.2 Bias and fairness
Evaluate dataset representation and model outcomes across relevant populations and use contexts. Select fairness metrics with domain stakeholders; no single metric is appropriate for every decision system.

### 3.3 Adversarial robustness
Assess model behaviour under malicious, malformed, unexpected, or distribution-shifted inputs. Define attacker capability and perturbation constraints before choosing attacks. Keep model-level robustness distinct from application-level exploitability.

### 3.4 Explainability and interpretability
Assess whether relevant stakeholders can understand model behaviour sufficiently to review, challenge, debug, or govern it. Explanations are supporting evidence, not proof that a model is correct or fair.

### 3.5 Performance and scalability
Measure latency, throughput, resource use, concurrency behaviour, and graceful degradation under expected and peak load. Include model inference and surrounding service dependencies.

### 3.6 Operational monitoring and drift
Monitor input-data changes, output distributions, performance, model versions, and relevant feedback signals. Define thresholds, owners, alert routes, and reassessment triggers.

### 3.7 Incident response and security monitoring
Ensure AI-related events can be logged, detected, triaged, investigated, contained, and recovered from. Include prompt injection, data exposure, model misuse, abnormal tool invocation, and supply-chain events where relevant.

## 4. Nine testing modules

| Module | Core questions | Example evidence |
|---|---|---|
| Data and input validation | Are inputs valid, bounded, expected, and handled safely? | Schema tests, malformed-input results, data-quality checks |
| Model functionality | Does the model meet its intended functional requirements? | Baseline metrics, test fixtures, regression results |
| Bias and fairness | Are outcomes acceptably fair for the intended context? | Group metrics, dataset analysis, review decisions |
| Explainability and transparency | Can behaviour be interpreted and communicated appropriately? | Explanations, feature analyses, model cards |
| Robustness and adversarial testing | How does the system respond to hostile or perturbed inputs? | Attack logs, perturbation budgets, baseline/adversarial comparisons |
| Performance and efficiency | Does it meet operational performance objectives? | Latency percentiles, throughput, resource metrics |
| Integration and system testing | Are interfaces, permissions, dependencies, and data flows secure? | API tests, access-control results, integration traces |
| User acceptance and ethical review | Is use appropriate, understandable, accessible, and accountable? | UAT records, human review, ethical assessment |
| Continuous monitoring and improvement | Are degradation and incidents detected and acted on? | Drift reports, alerts, incident and remediation records |

## 5. How the views fit together

The seven assurance areas describe **what outcomes matter**. The nine modules describe **how evidence is gathered**. The lifecycle model describes **when the work should happen**. One test may support several assurance areas, and one assurance area may require multiple modules.

## 6. Tailoring

Select test depth based on impact of an incorrect or harmful outcome; sensitivity and volume of data processed; exposure to untrusted users or external inputs; model autonomy and ability to take actions; downstream decisions and integrations; attacker capability and access; and regulatory, contractual, or sector-specific obligations.

Record exclusions and residual risks. A test omitted because it is not applicable is different from a test that has not yet been implemented.
