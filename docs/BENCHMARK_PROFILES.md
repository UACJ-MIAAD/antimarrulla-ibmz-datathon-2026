# Benchmark profiles: 20, 200, 2,000 and 16,000

Pin the reviewed release on a named branch before measuring. This configuration builds on the evidence preflight fix; both PRs must be reviewed and merged before the VM run. Reserve a measurement window on the VM and avoid other benchmarks in parallel. The model weights and 19-feature schema are unchanged. Executable source changes require rebuilding both endpoints and the client together.

## Prepared profiles

| `PROFILE` | Labeled CDC process comparison | Synthetic deployed API requests | Intended use |
|---|---:|---:|---|
| `20` | 20 | 20 | Diagnostic / short rehearsal |
| `200` | 200 | 200 | Diagnostic / short comparison |
| `2000` (default) | 2,000 | 200 | Standard release-sized measurement |
| `16000` | 16,000 | 200 | Extended release-sized numerical comparison |

The CDC process comparison computes floating, fixed-point and Paillier predictions on the same deterministic stratified test sample. Its same-process HTTPS microbenchmark uses up to 200 requests and is labeled separately. The API measurement uses deterministic synthetic inputs through the deployed Hospital → mTLS service → Hospital → encrypted vault flow. API inputs have no clinical labels or AUC. A 16,000-record process run is **not** 16,000 deployed API requests.

Each profile declares its exact process/API counts in `manifest.json`, command logs, summary and run/branch name. The checker rejects smaller or larger actual samples, missing/inexact results and inconsistent declarations. Small runs can pass diagnostic checks but do not satisfy the final package. Release-size eligibility requires a configured process count of 2,000 or 16,000 and API count of at least 200; host/provider and all other release gates remain separate.

## Ready-to-run commands on the VM

Run only after independent review and pinning the approved commit:

```bash
make test-profiles PY=python3                  # Prints configuration; runs no measurements.
make evidence-run PROFILE=20 PY=python3        # Recorded diagnostic.
make evidence-run PROFILE=200 PY=python3       # Recorded diagnostic.
make evidence-run PROFILE=2000 PY=python3      # Standard.
make evidence-run PROFILE=16000 PY=python3     # Extended CDC comparison + 200 API requests.
```

One command runs all four profiles **sequentially**, stopping on the first failed step/check/upload:

```bash
make evidence-suite PY=python3
```

This repeats verification and the smoke test for each profile and publishes four separate evidence branches. It does not automatically merge or promote evidence. Keep the printed branch names. `NO_PUSH=1` keeps all runs local; do not mistake that for uploaded evidence. Run valid diagnostics through the new profile-aware checker; a previously failed run remains failed and must stay on its diagnostic branch.

If the team also wants **16,000 full deployed API round trips**, request them explicitly:

```bash
make evidence-run PROFILE=16000 API_N=16000 PY=python3
```

The suite's default already includes separate 200-request API measurements at the larger sizes. Avoid repeating a 16,000-request API run at every size unless that additional runtime is intentional.

## Live pitch: use an already running demo

Before recording, run `make demo-docker` and prepare the development image with `make image-dev`. The pitch only needs a single synthetic UI evaluation and/or a short terminal demonstration. For 20 end-to-end synthetic requests:

```bash
make demo-test N=20 FINAL=1
```

For a 200-request short benchmark:

```bash
make demo-test N=200 FINAL=1
```

These commands measure the deployed API and write the usual JSON/Markdown output, but do not retrain/reverify the model, execute a CDC process experiment or publish an evidence branch. They require a running matching Hospital/service. Twenty API requests cannot replace final CDC/provider evidence. A 200-request run may exceed the pitch time budget; record it beforehand and show its summary. Do not promise that verification/build plus measurements fit inside the three-minute video.

## Exact counts and runtime

Profile commands use `--patients N`: the requested CDC count overrides the old adaptive `--max`/`--budget-s` behavior and is never silently reduced. An out-of-range request fails. Direct manual runs without `--patients` retain the previous adaptive budget. Pilot and warmup requests are excluded from reported sample counts and consume extra time.

The pilot reports an estimate for the process loop. That estimate excludes build, verification, key generation, API measurements, warmups and publication; it is not an SLA. The team's chat report of a previous 16,000-record run taking 27 minutes is **not verified evidence of this release or either measurement scope**. Do not schedule a 16,000-record run inside the pitch. Do not infer throughput, patient capacity or concurrency from free disk space divided by request size.

Process/API measurement summaries preserve separate scopes, counts, timings, hashes and environment labels. Compare per-patient p50/p95/mean and exactness under the same architecture/version/concurrency; total time naturally increases with sample size. Sample-size changes alone are not a concurrent-load benchmark. The CDC stratified samples are reproducible but are not guaranteed to be nested across sizes; compare float/fixed/encrypted values within each sample.

## Configuration verification

Native `make verify`: **178 passed**, model reproduced. Ubuntu arm64 `make verify-docker`: **126 passed, 7 skipped**, model reproduced. The native suite includes **91 targeted profile/runner/measurement/package cases**. The two suite orchestration tests use a fake Make command; they do not run long measurements. A temporary local process rehearsal requested 20 records with `--max 8 --budget-s 1`, still measured **20/20 exact** and made three same-process HTTPS requests. It is not a deployed 20-request API test or a VM measurement. The model weights remain unchanged. [Validation record](../submission/evidence/local/benchmark_profiles_validation.json).
