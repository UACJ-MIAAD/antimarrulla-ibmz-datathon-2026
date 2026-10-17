# In-process measurement · local-darwin-arm64 · 2026-10-17T19:35:17Z

> ⚠️ LOCAL measurement. This is not LinuxONE performance.

- Commit `5412abe7ed82efdf91b5afba846079f0f58584b1` (git, clean) · code `fa44bfe5f31989c2` (22 files) · model `9747116760f938ae` · splits `8394d9f07d189298`
- Architecture: arm64 · macOS-27.2-arm64-arm-64bit · 12 CPU · container: False
- Python 3.12.12 · phe 1.5.0 · gmpy2 2.3.2 · cryptography 50.0.2 (OpenSSL 4.0.3 29 Sep 2026) · OpenSSL CLI: OpenSSL 4.0.3 29 Sep 2026 (Library: OpenSSL 4.0.3 29 Sep 2026)
- Comando: `python -m screening.measure --budget-s 600.0 --max 2000 --https 100 --final` · concurrencia 1

| Sample (stratified CDC test split, seed 2026) | Value |
|---|---|
| Patients | 2000 (279 positives, prevalence 0.1395) |
| Decrypted integers matching the reference | 2000 of 2000 |
| Maximum floating-point logit error | 4.500e-08 (bound 7.900e-08) |
| ROC-AUC floating / fixed point / encrypted | 0.808383 / 0.808383 / 0.808383 |
| Sensitivity · specificity (encrypted, threshold 0.1225) | 0.7921 · 0.688 |

| Microbenchmark | p50 (ms) | p95 (ms) | mean (ms) |
|---|---:|---:|---:|
| In process · encrypt 21 features | 127.723 | 164.608 | 132.69 |
| In process · evaluate ciphertexts | 9.11 | 12.068 | 9.685 |
| In process · decrypt | 1.644 | 2.423 | 1.803 |
| Same-process HTTPS + vault (100 requests) | 144.065 | 177.682 | 149.398 |

Sequential throughput: 415.6 patients/min without network; 401.6 with same-process HTTPS (n / wall time). Request 26775 bytes · response 1393 bytes · AES-256-GCM library microbenchmark 7022.1 MB/s.

Plaintext reference on the same 2000 patients (10 repetitions, logit only):
floating p50 0.959 µs, p95 1.208 µs;
fixed point p50 2.084 µs, p95 2.625 µs.
Compare with evaluate_service for encrypted logit cost; HTTPS also includes encryption, network and vault.
