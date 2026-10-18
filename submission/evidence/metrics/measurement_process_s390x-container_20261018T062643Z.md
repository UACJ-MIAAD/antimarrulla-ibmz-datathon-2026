# In-process measurement · s390x-container · 2026-10-18T06:26:43Z

> Executed on s390x; verify LinuxONE Community Cloud identity using VM/provider evidence.

- Commit `b50f6cc2346d8b5ae2fa22d36f7c67d5ec08c9ed` (environment, clean) · code `59a38c39df3c8741` (24 files) · model `e32420ac99fd10d3` · splits `8394d9f07d189298` · image `sha256:a951d209aa441b8b7e907a89eb101a9923da61ddd27afbde61744ef5b429f205`
- Architecture: s390x · Linux-6.8.0-147-generic-s390x-with-glibc2.39 · 3 CPU · container: True
- Python 3.12.3 · phe 1.5.0 · gmpy2 2.1.5 · cryptography 41.0.7 (OpenSSL 3.0.13 30 Jan 2024) · OpenSSL CLI: OpenSSL 3.0.13 30 Jan 2024 (Library: OpenSSL 3.0.13 30 Jan 2024)
- Comando: `python -m screening.measure --budget-s 600 --max 2000 --patients 200 --https 200 --final` · concurrencia 1

| Sample (stratified CDC test split, seed 2026) | Value |
|---|---|
| Patients | 200 (28 positives, prevalence 0.14) |
| Decrypted integers matching the reference | 200 of 200 |
| Maximum floating-point logit error | 2.404e-08 (bound 5.650e-08) |
| ROC-AUC floating / fixed point / encrypted | 0.841362 / 0.841362 / 0.841362 |
| Sensitivity · specificity (encrypted, threshold 0.1218) | 0.8571 · 0.6802 |

| Microbenchmark | p50 (ms) | p95 (ms) | mean (ms) |
|---|---:|---:|---:|
| In process · encrypt 19 features | 235.091 | 239.204 | 235.371 |
| In process · evaluate ciphertexts | 17.45 | 17.924 | 17.501 |
| In process · decrypt | 3.613 | 3.737 | 3.632 |
| Same-process HTTPS + vault (200 requests) | 262.764 | 269.158 | 263.204 |

Sequential throughput: 233.7 patients/min without network; 228.0 with same-process HTTPS (n / wall time). Request 24301 bytes · response 1393 bytes · AES-256-GCM library microbenchmark 6635.2 MB/s.

Plaintext reference on the same 200 patients (10 repetitions, logit only):
floating p50 1.5 µs, p95 1.531 µs;
fixed point p50 3.393 µs, p95 3.481 µs.
Compare with evaluate_service for encrypted logit cost; HTTPS also includes encryption, network and vault.
