# Model robustness report showcase

This folder contains HTML reports for the IBM ART model-testing workstream.

| Report | Evidence status | Notes |
|---|---|---|
| [MinerU PP-DocLayoutV2](mineru_ibm_art_layout.html) | Historical execution report | Earlier notebook revision: 9 attacks attempted, 6 executed, 3 failed due to constructor keyword errors. The corrected notebook has not been rerun. |
| [MiniLM cross-encoder reranker](../reranker-minilm/reports/minilm_reranker_sample.html) | Illustrative sample only | Demonstrates the intended report structure. All tests are marked NOT RUN; no measurements or findings are claimed. |
| [MinerU illustrative report](mineru_ibm_art_layout_sample.html) | Illustrative sample only | Corrected notebook output layout; all attacks NOT RUN. |
| [HTML report index](INDEX.html) | Showcase navigation | Explains the evidence status of each report. |

**Important:** The reports have different evidence status. Do not treat the MiniLM sample as execution evidence, and do not treat the historical MinerU report as validation of the corrected notebook. A model score change or class flip is not automatically a confirmed security finding.
