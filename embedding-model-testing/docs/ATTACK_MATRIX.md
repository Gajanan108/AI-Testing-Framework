# IBM ART attack selection and applicability

This matrix is a selection guide, not a promise that every attack applies to every model. Confirm the installed ART version and the estimator's declared capabilities before execution. The official source of truth is the [ART repository](https://github.com/Trusted-AI/adversarial-robustness-toolbox) and [documentation](https://adversarial-robustness-toolbox.readthedocs.io/en/main/).

## Estimator / model contract first

| Model or task | Typical ART estimator family | What must be exposed | Key caveat |
|---|---|---|---|
| Image classifier | Classification estimator (e.g. PyTorchClassifier) | Image tensor input, class scores/logits, labels, gradients for white-box attacks | Image-space perturbations; preprocessing and clipping must match production |
| Text classifier | Framework classifier estimator | Token/text preprocessing and class scores; gradient path depends on tokenization/model | Discrete tokens are not continuous pixels; pixel attacks are not applicable |
| Embedding encoder | Encoding/feature estimator where supported, or carefully designed custom estimator/objective | Input -> embedding vector; differentiable input gradients if using gradient attacks; explicit similarity/ranking objective | A vector alone has no class label or attack success criterion |
| Object detector | Object-detection estimator or a task-specific supported wrapper | Boxes, labels, scores and the output format expected by the attack | Do not collapse detections to a class proxy and then claim full detector robustness |
| Audio model | Audio/task-specific estimator or supported classifier wrapper | Waveform/features, task scores and appropriate gradients | Image-specific attacks do not transfer to audio |
| Generator / VLM | Generation estimator or a separate task-specific evaluation harness | Generation outputs plus measurable task-specific success criterion | ART estimator coverage does not equal complete LLM/VLM safety red teaming |

## Attacks configured in the MinerU notebook

| Attack | Family / requirements | Current notebook status | Interpretation |
|---|---|---|---|
| FastGradientMethod | Gradient-based evasion; classifier gradients | Executed | Image perturbation against the layout-class presence proxy |
| ProjectedGradientDescent | Iterative gradient-based evasion; classifier gradients | Executed | Same proxy task; bounded iterative perturbation |
| BasicIterativeMethod | Iterative gradient-based evasion; classifier gradients | Executed | Same proxy task |
| SquareAttack | Score/query-based evasion; classifier scores | Executed | No top-class change in the sample run |
| ZooAttack | Zeroth-order / query-based evasion; classifier score/loss contract | Executed | No top-class change in the sample run; recorded perturbation was zero |
| NewtonFool | Gradient-based evasion; classifier gradients | Executed | Top-class changed; reported L-infinity perturbation was 1.0, so inspect budget and input normalization before interpreting |
| SpatialTransformation | Spatial/image transformation | Constructor corrected for ART 1.20.1; rerun pending | Official constructor expects `classifier`; image-space transformation only |
| PixelAttack | Pixel-level image attack | Constructor corrected for ART 1.20.1; rerun pending | Official constructor expects `classifier`; `th` is the threshold parameter |
| ThresholdAttack | Threshold/image transformation | Constructor corrected for ART 1.20.1; rerun pending | Official constructor expects `classifier` and `th`, not `estimator` and `threshold` |

## How to select attacks for embedding models

1. **Identify the actual model boundary.** Is the model a text encoder, image encoder, audio encoder, multimodal encoder, or an entire retrieval service?
2. **Define the task objective.** For retrieval, measure top-k neighbour identity, rank movement, cosine similarity to a target, false match rate, or threshold crossing.
3. **Choose an estimator contract.** Confirm that ART's estimator family supports the model framework and required methods. Do not pretend a generic embedding output is a classifier.
4. **Check attack prerequisites.** White-box attacks need gradients; score-based attacks need queryable scores; poisoning attacks need a training/data pipeline; extraction attacks need an exposed query interface.
5. **Check input domain.** Image transformations are for image inputs; they are not text-token attacks. Discrete token inputs require discrete/text-specific methods or a carefully justified relaxation.
6. **Run a smoke test.** Verify model load, deterministic baseline output, estimator prediction, gradients (when required), generated sample shape/range, and post-attack inference.
7. **Validate application impact.** Re-run on a held-out sample set and confirm that the changed embedding changes retrieval or downstream decisions.

## What this sample does not establish

The MinerU notebook adapts PP-DocLayoutV2 object-query logits into per-class presence scores using max over queries. This is a classifier proxy over an image-input detector. It is not a direct vector-embedding evaluation and it does not cover OCR recognition, the GGUF VLM, bounding-box geometry, or the complete document-to-Markdown pipeline.


## MiniLM reranker applicability update

The MiniLM notebook selects FastGradientMethod, ProjectedGradientDescent, BasicIterativeMethod, NewtonFool and ZooAttack against its pairwise ranking proxy. SquareAttack is not applicable to the 2D token-embedding sequence representation: the official implementation uses spatial/image-shaped perturbation logic. Image-only attacks such as PixelAttack, ThresholdAttack and SpatialTransformation are also not applicable to this text model.

The notebooks now pin ART 1.20.1. Constructor corrections are source-reviewed against the official release, but the updated notebooks have not yet been executed in Colab. The historical MinerU report (six executed, three failed) remains evidence for the earlier notebook revision only.
