# Finding taxonomy and reporting semantics

## 1. Test status

| Status | Definition | Reporting rule |
|---|---|---|
| Planned | Test is in the agreed plan but has not started. | Do not imply coverage. |
| Not applicable | The target does not meet the method's prerequisites. | State the technical reason. |
| Attempted | Execution was initiated. | Not equivalent to a completed test. |
| Executed | The method ran and produced an output. | Include evidence and parameters. |
| Failed | The method failed during setup or execution. | Include the exception; do not claim a result. |
| Blocked | An external dependency, permission, or environment prevented execution. | Identify the blocker. |

## 2. Observation and finding status

| Status | Definition | Example |
|---|---|---|
| Observation | A measurable behaviour or deviation was recorded. | A ranking score or model output changed. |
| Potential finding | The observation may have security significance but needs validation. | A reranker reverses a pairwise ranking under a latent embedding perturbation. |
| Confirmed finding | Reproducible evidence demonstrates security-relevant impact within a credible threat model. | An unauthorised user can reliably manipulate a production decision through an exposed input. |
| False positive | Investigation shows the suspected issue is not supported by evidence. | The observed change is expected, non-reproducible, or has no claimed impact. |
| Accepted risk | A validated risk is formally accepted by an authorised owner. | Include approver, rationale, date, and review date. |
| Remediated | A fix has been implemented and verified by retest. | Link the retest evidence. |

Do not use a binary true/false label before validation. If a report requires a binary field, define **true** as a confirmed finding and **false** as an investigated false positive; keep potential findings separate.

## 3. Severity

Severity should be based on demonstrated impact and realistic exploitability in the target context. Consider confidentiality, integrity, availability, privacy, safety, and decision impact; attacker privileges, access, interaction, and required knowledge; scope of affected users, models, data, and downstream systems; repeatability; and existing controls.

Suggested labels are Critical, High, Medium, Low, and Informational. Include a written rationale and the scoring method used. Do not infer severity solely from the attack name or a metric delta.

## 4. OWASP and standards mapping

Map a finding to an OWASP category or external standard only when the demonstrated behaviour fits that category. Record the framework/version and explain the relationship. If no defensible mapping exists, state **Not mapped** rather than forcing a category.

## 5. Required finding fields

Each finding should include a unique ID and title; affected system, component, and version; status and severity with rationale; assurance area and testing module; threat scenario, preconditions, and attacker capability; reproduction steps and evidence references; expected versus observed behaviour; impact and affected assets; applicable OWASP or standards mapping, if justified; remediation; owner, target date, and retest status.

## 6. Example interpretation

A class change under an adversarial image perturbation may demonstrate sensitivity of a model proxy. It is not automatically proof of a production exploit. Confirm whether the changed output affects the actual downstream task, repeat across representative inputs, validate the perturbation budget, and establish that the attacker can submit inputs within the tested threat model.
