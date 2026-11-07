# Assessment methodology

## 1. Assessment workflow

1. **Authorise** — confirm permission, environment, test window, contacts, and data-handling constraints.
2. **Scope** — identify the system boundary, model components, interfaces, dependencies, and intended use.
3. **Threat model** — identify assets, trust boundaries, attacker profiles, capabilities, entry points, and plausible impacts.
4. **Baseline** — record model identity, version, configuration, input/output contract, baseline performance, and representative test data.
5. **Select tests** — map risks to the seven assurance areas and nine testing modules. Verify each tool's prerequisites and model compatibility.
6. **Execute** — run controlled tests, preserve parameters and logs, and record failures without substituting unapproved methods.
7. **Analyse** — compare results with the baseline and determine whether behaviour is reproducible and security-relevant.
8. **Validate** — confirm impact in the intended application context and threat model.
9. **Report and remediate** — assign status and severity with rationale, recommend controls, and identify an owner.
10. **Retest and close** — verify remediation and record residual risk or accepted exceptions.

## 2. Minimum system record

Capture, where available: system purpose; owner and technical contact; environment and authorisation; model/provider name, architecture, version, revision or hash; tokenizer, preprocessing, postprocessing, and inference configuration; API or application version; data classification and provenance; trust boundaries and exposed interfaces; downstream consumers; threat model; and out-of-scope items.

Do not publish secrets, personal data, production tokens, or proprietary weights in assessment artefacts.

## 3. Test selection and compatibility

Before running a test, document the risk being evaluated; target component and input/output boundary; attacker capability and access assumptions; test method and tool/version; required estimator or adapter contract; differentiability, score access, query budget, or other prerequisites; measurable success criterion; and safety constraints or stop conditions.

A tool supporting an attack family does not mean every model supports it. Image-space attacks are not directly applicable to discrete text inputs. A custom adapter or proxy changes the tested objective and must be described in the report.

## 4. Execution integrity

| Status | Definition |
|---|---|
| PLANNED | Not yet started |
| NOT APPLICABLE | Prerequisites do not match the target |
| ATTEMPTED | Execution was initiated |
| EXECUTED | The test ran and produced an output |
| FAILED | The test raised an error or could not complete |
| BLOCKED | An external dependency or authorisation constraint prevented execution |

Do not count a configured or imported attack as executed. Do not silently replace a failed test with a different implementation. Preserve the exception and exact tool version.

## 5. Evidence requirements

For each executed test, retain timestamp and run ID; test case and objective; target model and application version; input fixture identifier or hash; baseline output and metric; test parameters and random seed where supported; adversarial or modified input or secure reference; output after testing and metric delta; perturbation size or query count where relevant; execution duration, resource use, and exceptions; repeatability results; and analyst interpretation with downstream impact validation.

Use synthetic or approved test data. Keep sensitive raw evidence in access-controlled storage and publish only sanitised summaries.

## 6. Validation and severity

A metric deviation is an observation, not automatically a security vulnerability. Validate whether the behaviour is reproducible; reachable under the stated attacker capability; affects the intended system or decision; violates a security, privacy, safety, fairness, or reliability requirement; and has credible impact and realistic preconditions.

Assign severity only after considering impact, exploitability, scope, and compensating controls. Document the rationale rather than relying on an unexplained label.

## 7. Reporting

Every assessment report should include an executive summary, scope, methodology, model and environment details, coverage, test execution status, findings, limitations, remediation, and retest status. Distinguish test failures from negative results and potential findings from confirmed findings.
