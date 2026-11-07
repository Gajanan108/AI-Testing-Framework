# Risk rating methodology

## 1. Purpose and use

This method provides a consistent, transparent starting point for prioritising validated AI/ML security findings. It is a project-defined qualitative/semi-quantitative method, not a claim of alignment with a particular external scoring standard.

Rate **likelihood** and **impact** separately on a 1–5 scale. Calculate the inherent risk score as:

**Inherent risk = Likelihood × Impact**

Use the score band as a prioritisation aid, then document the rationale and any context-specific override. Do not assign a score to a raw observation that has not been validated as a finding; label it Observation or Potential finding instead.

## 2. Likelihood scale

| Score | Label | Guidance |
|---:|---|---|
| 1 | Rare | Requires highly unusual conditions, privileged access, or an impractical chain of prerequisites. |
| 2 | Unlikely | Exploitation is possible but requires significant access, expertise, or favourable conditions. |
| 3 | Possible | A realistic attacker could exploit the issue with moderate effort or access. |
| 4 | Likely | The attack path is practical, repeatable, and available to a plausible attacker. |
| 5 | Almost certain | The weakness is readily exploitable, repeatable, and broadly accessible in the assessed context. |

Assess likelihood using attacker access, required privileges, complexity, user interaction, exposure, repeatability, and the reliability of the exploit path.

## 3. Impact scale

| Score | Label | Guidance |
|---:|---|---|
| 1 | Negligible | Minimal, localised effect with no material security or business consequence. |
| 2 | Minor | Limited and recoverable impact affecting a small scope. |
| 3 | Moderate | Meaningful degradation, exposure, or incorrect outcomes requiring operational response. |
| 4 | Major | Significant confidentiality, integrity, availability, privacy, safety, or business impact. |
| 5 | Severe | Critical or widespread impact, such as large-scale sensitive-data exposure, material unauthorised actions, or serious safety consequences. |

Consider confidentiality, integrity, availability, privacy, safety, fairness, financial impact, regulatory obligations, affected population, and downstream decisions. Use the highest credible impact supported by evidence, not a speculative worst case.

## 4. Score bands

| Score | Suggested rating | Default handling |
|---:|---|---|
| 1–4 | Low | Track and remediate through normal engineering prioritisation. |
| 5–9 | Medium | Assign an owner and target date; consider compensating controls. |
| 10–16 | High | Prioritised remediation and explicit risk-owner review. |
| 17–25 | Critical | Urgent containment and escalation to the designated security/risk authority. |

## 5. Inherent and residual risk

- **Inherent risk** describes risk before considering existing controls.
- **Residual risk** describes risk remaining after verified controls and mitigations are considered.

Do not reduce the numeric score merely because a control is documented. Consider whether the control is deployed, correctly configured, monitored, and tested. Record control evidence and reassess likelihood and/or impact with a clear rationale.

## 6. Override and escalation criteria

A numeric band must not suppress escalation where credible evidence indicates severe safety consequences, active exploitation, broad sensitive-data exposure, unauthorised high-impact actions, or material regulatory obligations. Record the reason for any rating override and who approved it.

## 7. Required report fields

Every rated finding should state:

- likelihood score and rationale;
- impact score and rationale;
- inherent score and band;
- relevant existing controls and evidence;
- residual score and band, if assessed;
- severity override, if any, and rationale;
- remediation owner, target date, and acceptance authority.

## 8. Limitations

This method is a consistent internal prioritisation rubric. It does not replace a mandated organisational risk methodology, regulatory assessment, safety case, privacy impact assessment, or a sector-specific scoring process. Where an organisation has an approved method, use that method and document any mapping.
