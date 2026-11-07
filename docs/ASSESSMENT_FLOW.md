# Assessment flow

This diagram shows how the framework's lifecycle, testing modules, and evidence process connect. It is a reference workflow, not an automated pipeline.

```mermaid
flowchart TD
    A[Authorise assessment] --> B[Define system boundary and intended use]
    B --> C[Threat model and risk prioritisation]
    C --> D[Establish model and system baseline]
    D --> E[Select applicable assurance areas and test modules]
    E --> F{Compatibility and prerequisites met?}
    F -- No --> G[Record not applicable or blocked with rationale]
    F -- Yes --> H[Execute controlled tests]
    H --> I{Execution completed?}
    I -- No --> J[Record failure, exception, and tool version]
    I -- Yes --> K[Capture outputs, parameters, and evidence]
    K --> L[Analyse and reproduce observations]
    L --> M{Security-relevant impact validated?}
    M -- No --> N[Record observation, potential finding, or false positive]
    M -- Yes --> O[Confirm finding and assess severity]
    G --> P[Assessment report]
    J --> P
    N --> P
    O --> Q[Remediation and retest]
    Q --> P
    P --> R[Residual-risk review and continuous monitoring]
```

## Interpretation

- A test can be **not applicable** without being a failure.
- A failed test provides no successful test result.
- An executed test may produce a negative result or an observation; neither automatically constitutes a vulnerability.
- A confirmed finding requires reproducible evidence of security-relevant impact within the documented threat model.
- Remediation should be followed by retesting and residual-risk review.
