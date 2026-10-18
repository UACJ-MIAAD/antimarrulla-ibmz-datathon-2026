# Schema cdc19-v1: Education and Income removed

**Decision (team-approved, October 17, 2026):** the protocol schema drops `Education` and `Income`. The model, the form and the
encrypted protocol now use 19 CDC variables instead of 21.

## Why

Both variables contribute almost nothing to discrimination, and removing them means the hospital collects two fewer
sensitive socioeconomic answers and encrypts two fewer values per patient.

Ablation on the CDC validation split (trained on the training split with the exported model's `train.fit`; test split untouched). Reproduce with `make ablation`; the result is recorded in `artifacts/metrics/ablation_cdc19_v1.json`:

| Features | ROC-AUC | Average precision |
|---|---:|---:|
| All 21 | 0.8186 | 0.3979 |
| Without Education | 0.8187 | 0.3980 |
| Without Income | 0.8180 | 0.3975 |
| Without both (19) | 0.8180 | 0.3975 |

Exported model on the untouched test split (n = 38,052, threshold chosen for sensitivity ≥ 0.80 on validation):

| Model | ROC-AUC | Sensitivity | Specificity | Brier |
|---|---:|---:|---:|---:|
| `logistic-cdc21-v1` (21 features) | 0.8260 | 0.805 | 0.691 | — |
| `logistic-cdc19-v1` (19 features) | 0.8252 | 0.807 | 0.689 | 0.0983 |

Fixed-point and encrypted scoring remain exact: the decrypted integer equals the plaintext reference, and the maximum
quantization error is 3.8 × 10⁻⁸ in the logit.

## What changed

- `schema.VERSION` is `cdc19-v1`; the model is `logistic-cdc19-v1` (artifact paths keep their file names except
  `artifacts/model/cdc19_schema_v1.json`). The data splits are unchanged.
- Requests carry 19 ciphertexts (≈ 24 KB instead of ≈ 27 KB). Sending `Education` or `Income` is rejected as an
  unknown field.
- The ENSANUT exploratory model still uses `Education`; it now loads that column explicitly instead of through the
  protocol schema, so its artifact is unaffected.
- The two-host audit detects leaked plaintext vectors of the current schema size.

## Consequences

Every measurement and audit recorded before this change used the 21-feature model and code hashes. They remain valid
history but do not describe the release: rerun `make verify-docker`, `make measure-docker FINAL=1`,
`make measure-api-docker FINAL=1` and the two-host audit on the release commit. Both containers must be rebuilt
together; a 21-feature peer is rejected as an incompatible schema.
