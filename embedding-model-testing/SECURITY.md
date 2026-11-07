# Security and responsible testing

This project is for authorized robustness testing of models and systems you own or have explicit permission to assess.

- Do not commit API keys, credentials, private datasets, production embeddings, proprietary weights, or confidential documents.
- Keep model weights and generated logs out of Git unless they have been reviewed and intentionally approved for publication.
- Use synthetic or approved test inputs in public examples.
- Treat class flips, score changes, and embedding drift as observations until reproducibility and application impact are established.
- Report suspected vulnerabilities privately to the affected model or service owner before public disclosure.
