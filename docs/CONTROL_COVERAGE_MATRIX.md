# Assurance-to-testing coverage matrix

This matrix connects the framework's **seven assurance areas** to its **nine testing modules**. It is a planning aid, not a claim that every cell is implemented or automated. Select and tailor tests based on the system boundary, intended use, threat model, and available evidence.

**Legend:** P = primary relationship; S = supporting relationship; — = not normally a direct relationship. A dash does not prohibit a test where the system context justifies it.

| Assurance area ↓ / Testing module → | Data & input validation | Model functionality | Bias & fairness | Explainability | Robustness & adversarial | Performance & efficiency | Integration & system | User acceptance & ethics | Monitoring & improvement |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Data privacy and governance | P | S | S | — | S | — | P | S | S |
| Bias and fairness | S | P | P | S | S | — | S | P | S |
| Adversarial robustness | P | S | — | — | P | S | P | — | S |
| Explainability and interpretability | — | S | S | P | S | — | — | P | S |
| Performance and scalability | S | P | — | — | S | P | P | S | P |
| Operational monitoring and drift | S | S | S | — | S | P | P | — | P |
| Incident response and security monitoring | S | — | — | — | P | S | P | S | P |

## How to use the matrix

1. Start with the system's risks and intended use; do not select tests solely because a cell is marked P.
2. Select primary relationships first, then supporting activities where they produce useful evidence.
3. Record the selected test cases, owner, tool/version, prerequisites, and acceptance criteria in the assessment plan.
4. Mark each test as Planned, Not applicable, Attempted, Executed, Failed, or Blocked.
5. Link observations and findings to the relevant assurance area and testing module.
6. Explain exclusions. Not applicable means the test does not fit the target; it does not mean the risk is absent.

## Important distinctions

- Data privacy and governance includes dataset governance and runtime data handling; the actual control surface may sit in the application or platform rather than the model.
- Bias and fairness requires context-appropriate cohorts, metrics, and stakeholder review. A generic model accuracy score is insufficient.
- Adversarial robustness must specify attacker access, input constraints, perturbation budget, and downstream success criterion.
- Explainability is not a substitute for correctness, fairness, or security testing.
- Monitoring requires operational telemetry, thresholds, ownership, and response procedures—not just a drift library.
- Incident response requires tested people, processes, and technical controls; the presence of a SIEM product alone is not evidence of readiness.
