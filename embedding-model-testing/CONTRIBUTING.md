# Contributing

1. Open an issue describing the model family, estimator contract, ART version, and proposed attack objective.
2. Keep model-specific adapters isolated and document their input/output shapes and preprocessing.
3. Include a smoke test for model loading, baseline inference, and estimator compatibility.
4. Report attacks as `LISTED`, `COMPATIBLE`, `ATTEMPTED`, `EXECUTED`, or `FAILED`; never silently replace an ART implementation.
5. For retrieval embeddings, report similarity and ranking metrics alongside any classifier-proxy metrics.
6. Do not commit model weights, private data, secrets, or unreviewed logs.
