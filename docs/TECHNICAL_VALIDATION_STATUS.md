# Technical validation status

**Last documentation/code review:** 7 November 2026  
**Status:** source-reviewed corrections committed; Colab model execution remains pending.

## 1. IBM ART experiments

| Workstream | Code/configuration state | Runtime evidence |
|---|---|---|
| MinerU PP-DocLayoutV2 | ART pinned to 1.20.1; notebook now installs MinerU dependencies before imports; SpatialTransformation and PixelAttack use `classifier`; ThresholdAttack uses `classifier` and `th`; seed and runtime metadata are logged | Historical report only: 9 attacks attempted, 6 executed and 3 failed under the previous constructor revision. Corrected notebook has not been rerun in Colab |
| MiniLM reranker | ART pinned to 1.20.1; SquareAttack removed as an image/spatial attack not suitable for the token-embedding sequence proxy; seed and runtime metadata are logged | Notebook is not yet executed in Colab; report remains a template |

The constructor corrections are checked against official ART 1.20.1 source signatures. This is source-level API review, not proof that all attack generation paths work against the target model and installed runtime.

## 2. Orchestration validation

The assessment planner and registry are committed. The planner is intentionally conservative:
- Default operation generates a plan and does not execute tests.
- ART notebooks are marked `MANUAL_COLAB`.
- Presidio is the only allowlisted local runner and is restricted to synthetic fixtures with explicit opt-in and an authorisation gate.
- Other external tools remain documented/configuration-led; no integrations are claimed where no adapter exists.

The GitHub Actions validation workflow completed successfully on commit `4510280896fa8cc5ea9ad941bb3dec60e168cea2`. It compiled the planner, validated JSON files, parsed the notebook JSON structures, ran planner unit tests and generated a plan without executing assessment tools.

[View the successful validation workflow](https://github.com/Gajanan108/AI-Testing-Framework/actions/runs/42392337583).

## 3. Benchmark evidence

The benchmark protocol is committed in [BENCHMARK_AND_REPRODUCIBILITY_PROTOCOL.md](BENCHMARK_AND_REPRODUCIBILITY_PROTOCOL.md). It defines provenance, model/input hashes, version pinning, repeatability, per-sample status, metrics and acceptance gates.

No new benchmark result is claimed. The existing MinerU report is historical evidence for the earlier notebook revision. The MiniLM notebook remains unexecuted. Neither notebook currently establishes a representative, held-out, multi-run benchmark or production security impact.

## 4. What is required to close runtime validation

1. Open each notebook in Google Colab using the committed Git revision.
2. Run from a clean runtime with the pinned ART version and compatible dependencies.
3. Preserve the generated HTML report and log.
4. Review every executed, failed and skipped attack; verify perturbation budgets and outputs.
5. Repeat against an authorised held-out sample set and record model/input hashes.
6. Validate downstream application impact before confirming findings or assigning severity.

A passing planner CI run does not validate the model notebooks. A successful ART call does not, by itself, establish a vulnerability.
