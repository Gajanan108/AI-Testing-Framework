# MiniLM Cross-Encoder Reranker — IBM ART Security Testing

## Selected model

`cross-encoder/ms-marco-MiniLM-L-6-v2` (approximately 22.7 million parameters). It is a compact, commonly used MS MARCO passage reranker. The Sentence Transformers model comparison reports 74.30 NDCG@10 on TREC DL 2019 and 39.01 MRR@10 on MS MARCO Dev for this model; benchmark values depend on evaluation setup. See the [official Cross-Encoder model table](https://sbert.net/docs/cross_encoder/pretrained_models.html).

Model: https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2

## What a reranker does

A reranker is normally a cross-encoder. It takes a query and a candidate passage together and returns a relevance score. A retrieval system first uses a fast retriever (often a bi-encoder embedding model) to find top-k candidates; the reranker then scores each query-passage pair and reorders those candidates. Cross-encoders are generally more accurate for pairwise relevance but slower because each pair must be processed independently. They do not create a reusable standalone embedding for each text.

## Notebook

Open `notebooks/minilm_reranker_ibm_art_attacks.ipynb` in Google Colab. It downloads the model from Hugging Face, runs a real baseline inference, builds an ART `PyTorchClassifier` adapter for pairwise ranking, smoke-tests the adapter, and attempts official ART attacks:

- FastGradientMethod
- ProjectedGradientDescent
- BasicIterativeMethod
- NewtonFool
- SquareAttack
- ZooAttack

The wrapper defines a pairwise ranking decision: class 0 means the relevant candidate outranks a fixed competitor; class 1 means the ordering is inverted. ART attacks operate on the continuous word-embedding tensor for the candidate pair, not token IDs. The notebook records each attack as EXECUTED or FAILED and generates exactly two downloadable artifacts: an HTML report and a log file.

## Critical threat-model limitation

This is a **latent word-embedding-space** robustness test. A perturbation to a model's internal word embeddings is not necessarily convertible to a valid natural-language text edit. Consequently, a rank inversion here is a potential model robustness issue, not proof that an attacker can cause the same result by submitting modified text to a production search endpoint. A complete follow-on assessment should add discrete token-level attacks, semantic-preservation checks, multiple held-out query/candidate pairs, retrieval ranking metrics (MRR, NDCG@k, Recall@k), and downstream RAG impact testing.

## Applicability

Image-only attacks such as PixelAttack, SpatialTransformation, and image patches are not applicable to this text-pair model input. Classifier attacks can be used only because this notebook explicitly defines a binary pairwise ranking proxy. Attack results must be interpreted against that proxy and not as general-purpose ART support for all rerankers.

## Report semantics

- EXECUTED: ART generated a perturbed embedding and the model was evaluated on it.
- FAILED: the attack raised an exception; no successful attack is claimed.
- ranking_inverted: the attacked relevant passage no longer outranks the fixed competitor.
- Potential finding: repeatable ranking degradation under a realistic threat model.
- Confirmed security finding: requires demonstrated application impact, reproducibility, and a credible attacker capability.

## Dependencies

See `requirements.txt`. The notebook installs ART and Transformers dependencies in Colab.

## References

- [Hugging Face model card](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2)
- [Sentence Transformers Cross-Encoder documentation](https://sbert.net/docs/cross_encoder/usage/usage.html)
- [MS MARCO Cross-Encoder model comparison](https://sbert.net/docs/cross_encoder/pretrained_models.html)
- [Official ART documentation](https://adversarial-robustness-toolbox.readthedocs.io/en/main/)
- [ART evasion attack API](https://adversarial-robustness-toolbox.readthedocs.io/en/main/modules/attacks/evasion.html)
