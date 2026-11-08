# OWASP mapping guide for AI security assessments

**Reviewed:** 2026-11-08  
**Purpose:** provide a controlled, evidence-led mapping from this framework's assurance areas and observed behaviours to relevant OWASP AI/ML risk taxonomies.

This guide is a mapping aid, not a certification, compliance statement, vulnerability verdict, or replacement for the primary OWASP publications. A mapping must be selected from the **demonstrated behaviour and affected system boundary**. Do not assign an OWASP category merely because a test tool or attack algorithm has a similar name.

## Taxonomies and versions

### OWASP Top 10 for Large Language Model Applications — 2026

The OWASP GenAI Security Project's 2026 release is the current LLM application taxonomy as of this review. The 2026 categories are:

| ID | Risk category |
|---|---|
| LLM01:2026 | Prompt Injection |
| LLM02:2026 | Sensitive Information Disclosure |
| LLM03:2026 | Excessive Agency |
| LLM04:2026 | Supply Chain |
| LLM05:2026 | Data and Model Poisoning |
| LLM06:2026 | Unbounded Consumption |
| LLM07:2026 | Misinformation |
| LLM08:2026 | Hidden Context Exposure |
| LLM09:2026 | Vector and Embedding Weaknesses |
| LLM10:2026 | Improper Output Handling |

Primary source: [OWASP GenAI Security Project — official Top 10 repository](https://github.com/GenAI-Security-Project/GenAI-LLM-Top10). The repository identifies the 2026 release and links to the canonical publication. Use the release-specific primary material when preparing a formal report.

### OWASP Machine Learning Security Top 10 — 2023 draft project

The OWASP Machine Learning Security Top 10 project lists the following risk categories:

| ID | Risk category |
|---|---|
| ML01:2023 | Input Manipulation Attack |
| ML02:2023 | Data Poisoning Attack |
| ML03:2023 | Model Inversion Attack |
| ML04:2023 | Membership Inference Attack |
| ML05:2023 | Model Theft |
| ML06:2023 | AI Supply Chain Attacks |
| ML07:2023 | Transfer Learning Attack |
| ML08:2023 | Model Skewing |
| ML09:2023 | Output Integrity Attack |
| ML10:2023 | Model Poisoning |

**Status caveat:** OWASP describes this Machine Learning Security Top 10 work as a draft that is being modified. Verify its current status and wording before using it as a formal control baseline. Source: [OWASP Machine Learning Security Top 10 project](https://owasp.org/projects/machine-learning-security-top-ten/).

## Framework assurance-area mapping

The relationships below are **candidate mappings**, not automatic assignments. "Direct candidate" means the taxonomy category may directly describe the observed risk if the required behaviour is demonstrated. "Conditional" means the mapping depends on system architecture, attacker capability, and impact. "Adjacent" means the taxonomy can inform the assessment but does not itself define the assurance outcome.

| Framework assurance area | Candidate OWASP mappings | Relationship and evidence needed |
|---|---|---|
| Data privacy and governance | LLM02:2026 Sensitive Information Disclosure; LLM08:2026 Hidden Context Exposure; LLM09:2026 Vector and Embedding Weaknesses; ML03:2023 Model Inversion; ML04:2023 Membership Inference | Direct candidate where sensitive information is disclosed or inferred from a model/application, hidden context is exposed, or vector/embedding controls expose protected data. Demonstrate the data class, access boundary, attacker prerequisites, and reproducible disclosure. |
| Bias and fairness | LLM05:2026 Data and Model Poisoning; LLM07:2026 Misinformation; ML02:2023 Data Poisoning; ML08:2023 Model Skewing; ML10:2023 Model Poisoning | Conditional/adjacent. These categories may explain malicious manipulation or skewed model behaviour, but they are not fairness metrics or a fairness standard. Demonstrate cohort-level outcome disparity separately using suitable fairness measures and context. |
| Adversarial robustness | LLM01:2026 Prompt Injection; LLM05:2026 Data and Model Poisoning; LLM07:2026 Misinformation; LLM09:2026 Vector and Embedding Weaknesses; LLM10:2026 Improper Output Handling; ML01:2023 Input Manipulation; ML02:2023 Data Poisoning; ML09:2023 Output Integrity | Direct candidate only when an attacker-controlled input, data source, vector/embedding path, or model output causes a security-relevant effect. Record the attacker model, perturbation constraints, objective, repeatability, and downstream impact. |
| Explainability and interpretability | LLM07:2026 Misinformation; ML09:2023 Output Integrity | Adjacent/conditional. An explanation-quality defect is not automatically an OWASP vulnerability. Map only where misleading outputs or compromised output integrity cause a demonstrated security or business impact. Explainability metrics should be reported separately. |
| Performance and scalability | LLM06:2026 Unbounded Consumption | Direct candidate for uncontrolled inference or resource use causing service degradation, denial of service, or material cost impact. Include request rates, resource/cost telemetry, rate limits, concurrency, and recovery evidence. |
| Operational monitoring and drift | LLM04:2026 Supply Chain; LLM05:2026 Data and Model Poisoning; LLM06:2026 Unbounded Consumption; LLM07:2026 Misinformation; ML06:2023 AI Supply Chain Attacks; ML10:2023 Model Poisoning | Conditional. These are risks that monitoring may help detect; drift detection alone does not prove any of them. Show the relevant signal, detection latency, alert quality, response owner, and tested response path. |
| Incident response and security monitoring | Relevant LLM01–LLM10 and ML01–ML10 categories, selected by the incident scenario | Use the taxonomy category describing the underlying incident, not "incident response" as a vulnerability category. Assess telemetry, triage, containment, recovery, evidence preservation, and lessons learned as operational capabilities. |

## Model and application archetype guidance

| Target under test | Candidate mapping focus | Do not overclaim |
|---|---|---|
| Image/layout detector (e.g. PP-DocLayoutV2) | ML01 input manipulation; ML09 output integrity; ML06 supply chain where model/dependency provenance is implicated | A class flip in a layout-class proxy does not establish OCR failure, document extraction compromise, or a production exploit. LLM Top 10 mappings are generally not appropriate for a standalone layout detector. |
| OCR pipeline | ML01 input manipulation; ML09 output integrity; ML06 supply chain; LLM10 improper output handling only if extracted text is consumed unsafely by an LLM/application boundary | OCR character errors alone are not prompt injection or sensitive-data disclosure. Show downstream effect and trust-boundary crossing. |
| Text embedding / retrieval / RAG | LLM09 vector and embedding weaknesses; LLM02 sensitive information disclosure; LLM08 hidden context exposure; LLM05 data and model poisoning; ML01 input manipulation | Vector distance changes or embedding drift alone do not prove data leakage, retrieval compromise, or user-visible exploitability. |
| LLM application / agent | LLM01 prompt injection; LLM02 sensitive information disclosure; LLM03 excessive agency; LLM04 supply chain; LLM05 poisoning; LLM06 unbounded consumption; LLM07 misinformation; LLM08 hidden context exposure; LLM09 vector and embedding weaknesses; LLM10 improper output handling | A model-only test may not exercise tools, permissions, retrieval, memory, plugins, output consumers, or deployment controls. State exactly which layers were tested. |
| Cross-encoder reranker | LLM09 vector and embedding weaknesses only when part of an embedding/RAG application and the relevant weakness is demonstrated; ML01 input manipulation; ML09 output integrity | A perturbation to internal word embeddings is not necessarily a valid text edit. A pairwise ranking proxy result is not proof of a production query attack. |

## Finding-level mapping procedure

For every proposed mapping:

1. **Identify the affected asset and boundary.** Name the model, application component, API, data store, tool, or downstream consumer.
2. **Describe the observed behaviour.** Record baseline, attacked/abused behaviour, raw evidence, and the exact test objective.
3. **State attacker prerequisites.** Distinguish white-box access, score/query access, authenticated user access, untrusted document ingestion, and privileged access.
4. **Demonstrate impact.** Explain confidentiality, integrity, availability, safety, privacy, or business impact. A metric shift alone is not impact.
5. **Choose the narrowest supported category.** If no category accurately describes the behaviour, write "No direct OWASP mapping identified" rather than forcing one.
6. **Record taxonomy and version.** For example, `LLM09:2026` or `ML01:2023`; never write only "OWASP LLM".
7. **Separate mapping from status.** A taxonomy label does not make an observation a confirmed finding and does not determine severity.
8. **Review the primary source.** Taxonomies change. Confirm category names and definitions at report publication time.

### Recommended report fields

| Field | Required content |
|---|---|
| OWASP taxonomy | Exact taxonomy name and release |
| OWASP category ID | Exact identifier and year |
| Mapping rationale | One or two sentences connecting observed evidence to the category |
| Evidence reference | Test case, run ID, log, output, request/response, or trace |
| Mapping confidence | Direct / Conditional / Adjacent / No direct mapping |
| Finding status | Observation / Potential / Confirmed / False positive / Accepted / Remediated |
| Severity | Determined by the framework risk methodology, not by OWASP category |

## Important interpretation rules

- OWASP Top 10 lists are awareness and risk-taxonomy resources; they are not complete security test plans, exhaustive vulnerability catalogues, or compliance certifications.
- The OWASP LLM Top 10 applies to LLM applications and their surrounding systems. Do not apply it indiscriminately to standalone classical ML models.
- The OWASP ML Top 10 project currently describes its content as draft. Treat its category mapping as provisional.
- OWASP category selection and severity are separate decisions. One category can contain findings of different severities; a single finding may also relate to more than one category when evidence supports each mapping.
- A failed attack, a not-run test, a synthetic sample, or a static illustrative report cannot support a confirmed finding.
- Do not label a finding "true" solely because a tool reports an anomaly. Validate reproducibility and security-relevant impact under the stated threat model.

## References

- [OWASP GenAI Security Project — 2026 Top 10 source repository](https://github.com/GenAI-Security-Project/GenAI-LLM-Top10)
- [OWASP Top 10 for LLM Applications — project page](https://owasp.org/projects/top-10-for-large-language-model-applications)
- [OWASP Machine Learning Security Top 10 — project page and draft status](https://owasp.org/projects/machine-learning-security-top-ten/)
- [OWASP Developer Guide — Top 10 projects](https://devguide.owasp.org/en/02-foundations/05-top-ten/)
