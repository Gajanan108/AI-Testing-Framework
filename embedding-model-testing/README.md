# Embedding Model Security Testing with IBM ART

> A focused adversarial-robustness testing workstream using the official [Adversarial Robustness Toolbox (ART)](https://github.com/Trusted-AI/adversarial-robustness-toolbox).

This directory contains a Google Colab notebook and an HTML evidence report for a real-model experiment against **MinerU PP-DocLayoutV2**. The experiment is an image-input layout detector evaluation. It is included as the first concrete model adapter in a broader embedding-model testing workstream; it is **not** evidence that OCR embeddings, text embeddings, the VLM, or the end-to-end document pipeline have already been tested.

## What is an embedding model?

An embedding model maps an input (text, image, audio, or another object) to a dense numerical vector. The vector is intended to encode useful semantic or perceptual information. Applications use these vectors for:

- semantic search and nearest-neighbour retrieval;
- document, image, or audio similarity;
- clustering, deduplication, and recommendations;
- retrieval-augmented generation (RAG) candidate selection;
- multimodal matching across different modalities.

A typical retrieval path is: input -> encoder -> vector -> normalization/index -> similarity or distance -> ranking -> downstream application. Security testing should identify which stage is under test. Perturbing the encoder input, manipulating the vector, changing the similarity/ranking stage, and poisoning the indexed corpus are different experiments and should not be conflated.

## What IBM ART does

ART is an open-source Python library initiated by IBM and now maintained as a project of the LF AI & Data Foundation under the Trusted-AI project. It provides estimators and attacks/defences for adversarial ML threats, including evasion, poisoning, extraction, and inference. See the [official project](https://adversarial-robustness-toolbox.org/), [source repository](https://github.com/Trusted-AI/adversarial-robustness-toolbox), and [documentation](https://adversarial-robustness-toolbox.readthedocs.io/en/main/).

ART attacks do not automatically understand an arbitrary embedding vector. An ART estimator/wrapper must expose the model's input/output contract and, for gradient attacks, usable gradients. The objective must represent the application risk. For a retrieval encoder, useful objectives may include target-neighbour attraction/repulsion, rank displacement, nearest-neighbour identity change, or similarity-threshold crossing. A plain vector output without a meaningful objective is not enough to claim a successful attack.

## Repository contents

| Path | Purpose |
|---|---|
| `notebooks/mineru_ibm_art_layout_model_attacks.ipynb` | Colab notebook with ART 1.20.1 pin and source-reviewed constructor corrections; rerun pending |
| `reports/mineru_ibm_art_layout.html` | Uploaded sample HTML report |
| `docs/ATTACK_MATRIX.md` | Attack-family selection and applicability notes |
| `requirements.txt` | Python dependencies for the current notebook |

## Run the notebook

1. Open the notebook in GitHub and choose **Open in Colab**, or download it and upload it to Google Colab.
2. Select a GPU runtime where available (CPU may be slow).
3. Run the cells in order. The notebook uses the official MinerU model manager to obtain the Torch model bundle when the layout weights are absent.
4. It loads the actual PP-DocLayoutV2 model, performs a forward-pass smoke test, wraps its output with ART's `PyTorchClassifier`, and attempts the configured ART attacks.
5. The notebook writes an HTML report and a plain-text execution log under `/content/mineru_ibm_art_layout_attacks/artifacts/` and downloads both.

**Historical run note:** the previously uploaded report records three constructor failures (SpatialTransformation, PixelAttack, ThresholdAttack) because that earlier notebook revision used incorrect constructor keywords. The current notebook pins ART 1.20.1 and corrects these to the official `classifier` argument; ThresholdAttack uses `th`. This is source-reviewed but not yet Colab-executed. The old report remains evidence for the old notebook revision only.

## Historical sample experiment (earlier notebook revision)

The attached report records:

- Model loaded: yes; real local PP-DocLayoutV2 `model.safetensors`;
- forward pass: yes, on CUDA;
- attacks attempted: 9;
- executed: 6;
- failed: 3;
- top-class changed: FastGradientMethod, ProjectedGradientDescent, BasicIterativeMethod, and NewtonFool;
- no top-class change in this run: SquareAttack and ZooAttack.

A changed top class is a **potential robustness signal**, not automatically a confirmed security vulnerability. The report's ART adapter reduces object-query logits to per-class presence scores using max over queries. Therefore, it measures layout-class presence only. It does not directly measure bounding-box geometry, OCR recognition, the separate GGUF VLM, final Markdown output, or end-to-end MinerU behavior. The experiment also uses one synthetic document image; repeat over representative samples and validate downstream impact before severity assignment.

## Attack applicability principles

Use the matrix in [docs/ATTACK_MATRIX.md](docs/ATTACK_MATRIX.md). In short:

- image-space attacks apply to image-input models only when the wrapped task and estimator contract are compatible;
- gradient-based attacks need differentiable input gradients;
- score/query-based attacks need usable model scores and a well-defined objective;
- classifier attacks on embeddings require a deliberate classification proxy, which changes what is being measured;
- direct embedding robustness needs retrieval/metric-learning evaluation (similarity, ranking, neighbour identity, threshold outcomes), not just top-class changes.

The project deliberately separates **listed**, **compatible**, **attempted**, **executed**, **failed**, and **validated finding** states. An attack should be marked executed only after its ART implementation actually generates an adversarial sample and the sample is evaluated.

## Findings and severity

A result should be marked **true finding** only after reproducible evidence shows a security-relevant impact in the intended application. Otherwise use **potential**, **needs validation**, or **false positive**. A class flip or vector drift alone is not sufficient. Record baseline and adversarial outputs, perturbation budget, model/version hashes, input hashes, attack parameters, execution time, exceptions, repeatability, and downstream consequence.

OWASP mapping should be assigned only where the demonstrated application impact supports a specific risk category. Do not force an OWASP mapping onto a raw robustness metric.

## Scope and safe use

Use only models, data, and endpoints you own or are explicitly authorized to test. Do not upload confidential documents, production embeddings, API keys, or proprietary model weights to a public repository. The sample input in the notebook is synthetic. Large model weights are intentionally not committed.

## References

- [ART project site](https://adversarial-robustness-toolbox.org/)
- [ART GitHub repository](https://github.com/Trusted-AI/adversarial-robustness-toolbox)
- [ART documentation](https://adversarial-robustness-toolbox.readthedocs.io/en/main/)
- [ART classifier estimators](https://adversarial-robustness-toolbox.readthedocs.io/en/main/modules/estimators/classification.html)
- [IBM Research: Adversarial Robustness Toolbox](https://research.ibm.com/projects/adversarial-robustness-toolbox)



## MiniLM reranker experiment

A second, separate workstream evaluates a compact text cross-encoder reranker using a pairwise ranking objective and official IBM ART attacks. See [reranker-minilm](reranker-minilm/README.md) for the model explanation, applicability matrix, Colab notebook, and report template.


## HTML report showcase

Open the [model robustness report index](reports/INDEX.html) for the HTML examples. It links the historical MinerU execution report and the illustrative MiniLM report. The MiniLM report is explicitly marked NOT EXECUTED and contains no measured results or findings. See [reports/README.md](reports/README.md) for the evidence-status distinction.
