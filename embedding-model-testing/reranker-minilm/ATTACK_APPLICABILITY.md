# MiniLM reranker — ART attack applicability

This experiment exposes a **pairwise ranking classifier proxy** to ART. It is not a native ART reranker estimator. The proxy uses the margin between a candidate's reranker score and a fixed competitor's score.

| ART attack | Applicability in this notebook | Reason |
|---|---|---|
| FastGradientMethod | Selected | Differentiable PyTorch classifier proxy; perturbs continuous input word embeddings |
| ProjectedGradientDescent | Selected | Iterative gradient-based perturbation of the same continuous input |
| BasicIterativeMethod | Selected | Iterative gradient-based perturbation |
| NewtonFool | Selected | Gradient-based classifier evasion against the pairwise decision |
| SquareAttack | Selected | Score-based black-box classifier attack; expensive in high-dimensional embedding input |
| ZooAttack | Selected | Zeroth-order score-based attack; query cost can be high |
| PixelAttack | Not applicable | Assumes pixel/image feature semantics |
| SpatialTransformation | Not applicable | Translation/rotation attack for image-like inputs |
| AdversarialPatch | Not applicable | Image/video patch threat model |
| Audio ASR attacks | Not applicable | Model does not accept audio |
| Object detector attacks | Not applicable | Model returns relevance scores, not boxes/classes for object detection |

## Limitations

The ART wrapper's input is a continuous tensor of token embeddings. This allows gradient-based perturbations but does not create valid token sequences. To assess an attacker who can only submit text, add discrete text transformations and verify semantic preservation and actual tokenizer/model reranking. The notebook's one query and two passages are a smoke-test fixture, not a benchmark dataset.
