# IBM ART benchmark and reproducibility protocol

## Purpose and current status

This protocol defines the evidence required to compare the existing IBM ART experiments without overstating their proxy objectives.

| Experiment | Current evidence | Remaining validation |
|---|---|---|
| MinerU PP-DocLayoutV2 | Historical report: 9 attacks attempted, 6 executed and 3 failed due to incorrect constructor arguments | Rerun corrected ART 1.20.1 notebook; use representative held-out documents; validate downstream layout/OCR impact |
| MiniLM cross-encoder reranker | Notebook and report template committed; no Colab execution claimed | Run pinned notebook; curate multiple held-out query/passage pairs; add discrete text perturbations and downstream retrieval metrics |

Constructor corrections and attack-selection changes are source-reviewed against official ART 1.20.1. This is API review, not runtime compatibility validation. The updated notebooks must be run in Colab before new execution results are reported.

## 1. Environment and provenance

Every run must retain:
- UTC timestamps and unique assessment/run identifier.
- Python, OS, PyTorch, Transformers, CUDA, GPU and IBM ART versions.
- Exact ART release; notebook baseline is `adversarial-robustness-toolbox==1.20.1`.
- Model identifier/revision, configuration and model-weight SHA-256.
- Input fixture identifiers and SHA-256 hashes; do not publish confidential data.
- Python/NumPy/PyTorch/CUDA random seeds.
- Attack class, constructor parameters, threat model, perturbation norm/budget, query/iteration budget and timeout.
- Per-sample execution state, exception, duration, baseline/adversarial outputs and perturbation.
- Notebook Git commit and generated HTML/log hashes.

Do not install an unpinned latest ART release during a run. Change the pin only after reviewing official release notes and constructor signatures.

## 2. MinerU PP-DocLayoutV2

### Objective and boundary

The adapter maps PP-DocLayoutV2 object-query logits to per-class presence scores by taking the maximum logit over queries. ART therefore evaluates a classifier proxy over image inputs.

This proxy does not measure detection-box geometry, OCR text recognition, the separate MinerU VLM/GGUF component, Markdown generation or the complete document workflow.

### Benchmark design

The synthetic document fixture is a smoke test only. A defensible benchmark should use an authorised held-out document set covering forms, invoices, receipts, papers, slides, tables and mixed layouts, with variation in scan quality, resolution, orientation, fonts, whitespace and density. Record ground-truth labels/boxes where available and keep development and evaluation splits separate.

### Metrics

Report per attack and sample:
- Baseline and adversarial class predictions/scores.
- Prediction flip rate, explicitly labelled as prediction consistency when pseudo-labels are used.
- Ground-truth precision/recall only where labelled ground truth exists.
- L-infinity/L2 where meaningful; do not compare spatial/pixel attacks only by an Lp value.
- Attack execution, sample failures, query count, runtime and exception.
- For detector-level validation: class-wise precision/recall, mAP/IoU, box displacement and downstream parser impact.

A class flip against a model-generated pseudo-label is not an accuracy error or a confirmed vulnerability.

## 3. MiniLM cross-encoder reranker

### Objective and boundary

The ART adapter defines a binary pairwise ranking proxy: class 0 means the relevant candidate scores above a fixed competitor; class 1 means the order is inverted. ART perturbs the continuous word-embedding tensor passed to the cross-encoder.

This does not represent an attacker who can only submit text. The perturbed tensor is not guaranteed to correspond to a valid token sequence.

### Benchmark design and metrics

Use held-out query/relevant passage/competitor triplets. Verify baseline ordering first; retain invalid pairs as skipped, not as attack failures or successes. Cover multiple topics and query/passage lengths. Add a separate discrete-token benchmark with semantic-preservation checks. Evaluate the retrieval path with MRR, NDCG@k, Recall@k and downstream RAG impact where applicable.

Report valid baseline pairs, executed/failed pairs, rank inversions divided by executed pairs, baseline/adversarial margins, embedding L-infinity/L2, query/iteration budget, runtime and exceptions. Do not mix latent-space inversion rates with discrete text-attack success rates.

## 4. Repeatability and acceptance gates

For each model and attack configuration:
1. Run a baseline smoke test and verify input/output shapes.
2. Run at least three independent seeds on a fixed evaluation split.
3. Retain failed and skipped samples with reasons.
4. Report mean, spread and sample count across seeds.
5. Confirm attack-specific perturbation budgets and query limits.
6. Reproduce high-impact results independently.
7. Validate against the actual application boundary and downstream task.
8. Have a reviewer classify potential, confirmed or false-positive findings.

Completion gates are separate: API compatibility, actual execution, multi-sample benchmark, downstream impact validation and finding confirmation. Passing one gate does not imply the next has passed.

## 5. Colab run procedure

1. Open the relevant notebook in Colab.
2. Select a compatible runtime; GPU recommended where supported.
3. Run all cells from a clean runtime.
4. Preserve the generated HTML report and log together.
5. Record the notebook Git commit and actual Colab versions.
6. Review failed, skipped and non-applicable rows before interpretation.

Do not replace failed attacks with a different implementation or mark an attack executed unless the official ART method actually generated and evaluated an adversarial sample.

## Official sources

- [ART 1.20.1 PyPI release](https://pypi.org/project/adversarial-robustness-toolbox/1.20.1/)
- [ART official repository](https://github.com/Trusted-AI/adversarial-robustness-toolbox)
- [ART evasion API](https://adversarial-robustness-toolbox.readthedocs.io/en/main/modules/attacks/evasion.html)
- [ART 1.20.1 FastGradientMethod source](https://github.com/Trusted-AI/adversarial-robustness-toolbox/blob/1.20.1/art/attacks/evasion/fast_gradient.py)
- [ART 1.20.1 SpatialTransformation source](https://github.com/Trusted-AI/adversarial-robustness-toolbox/blob/1.20.1/art/attacks/evasion/spatial_transformation.py)
- [ART 1.20.1 PixelThreshold source](https://github.com/Trusted-AI/adversarial-robustness-toolbox/blob/1.20.1/art/attacks/evasion/pixel_threshold.py)
