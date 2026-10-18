# In-process measurement · local-darwin-arm64 · 2026-10-18T03:01:42Z

> ⚠️ LOCAL measurement. This is not LinuxONE performance.

- Commit `be9b27e58cce011804d14124468e46a8c06d7889` (git, clean) · code `db2086ee2fcf99a4` (23 files) · model `e32420ac99fd10d3` · splits `8394d9f07d189298`
- Architecture: arm64 · macOS-27.2-arm64-arm-64bit · 12 CPU · container: False
- Python 3.12.12 · phe 1.5.0 · gmpy2 2.3.2 · cryptography 50.0.2 (OpenSSL 4.0.3 29 Sep 2026) · OpenSSL CLI: OpenSSL 4.0.3 29 Sep 2026 (Library: OpenSSL 4.0.3 29 Sep 2026)
- Comando: `python -m screening.measure --budget-s 600 --max 2000 --https 100 --final` · concurrencia 1

| Sample (stratified CDC test split, seed 2026) | Value |
|---|---|
| Patients | 2000 (279 positives, prevalence 0.1395) |
| Decrypted integers matching the reference | 2000 of 2000 |
| Maximum floating-point logit error | 3.370e-08 (bound 7.350e-08) |
| ROC-AUC floating / fixed point / encrypted | 0.806525 / 0.806525 / 0.806525 |
| Sensitivity · specificity (encrypted, threshold 0.1218) | 0.7814 · 0.681 |

| Microbenchmark | p50 (ms) | p95 (ms) | mean (ms) |
|---|---:|---:|---:|
| In process · encrypt 19 features | 97.116 | 99.829 | 97.453 |
| In process · evaluate ciphertexts | 7.536 | 7.806 | 7.558 |
| In process · decrypt | 1.492 | 1.54 | 1.491 |
| Same-process HTTPS + vault (100 requests) | 110.1 | 112.811 | 110.488 |

Sequential throughput: 562.9 patients/min without network; 543.0 with same-process HTTPS (n / wall time). Request 24301 bytes · response 1393 bytes · AES-256-GCM library microbenchmark 2858.1 MB/s.

Plaintext reference on the same 2000 patients (10 repetitions, logit only):
floating p50 0.916 µs, p95 0.958 µs;
fixed point p50 1.833 µs, p95 1.958 µs.
Compare with evaluate_service for encrypted logit cost; HTTPS also includes encryption, network and vault.
