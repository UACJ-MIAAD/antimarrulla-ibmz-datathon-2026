# In-process measurement · s390x-container · 2026-10-18T05:53:23Z

> Executed on s390x; verify LinuxONE Community Cloud identity using VM/provider evidence.

- Commit `b50f6cc2346d8b5ae2fa22d36f7c67d5ec08c9ed` (environment, clean) · code `59a38c39df3c8741` (24 files) · model `e32420ac99fd10d3` · splits `8394d9f07d189298` · image `sha256:fc4c882858776d3f69652639af62c311fbcfba3564454458e4ca6133634d362c`
- Architecture: s390x · Linux-6.8.0-147-generic-s390x-with-glibc2.39 · 3 CPU · container: True
- Python 3.12.3 · phe 1.5.0 · gmpy2 2.1.5 · cryptography 41.0.7 (OpenSSL 3.0.13 30 Jan 2024) · OpenSSL CLI: OpenSSL 3.0.13 30 Jan 2024 (Library: OpenSSL 3.0.13 30 Jan 2024)
- Comando: `python -m screening.measure --budget-s 600 --max 2000 --patients 20 --https 20 --final` · concurrencia 1

| Sample (stratified CDC test split, seed 2026) | Value |
|---|---|
| Patients | 20 (3 positives, prevalence 0.15) |
| Decrypted integers matching the reference | 20 of 20 |
| Maximum floating-point logit error | 2.227e-08 (bound 5.400e-08) |
| ROC-AUC floating / fixed point / encrypted | 0.980392 / 0.980392 / 0.980392 |
| Sensitivity · specificity (encrypted, threshold 0.1218) | 1.0 · 0.5294 |

| Microbenchmark | p50 (ms) | p95 (ms) | mean (ms) |
|---|---:|---:|---:|
| In process · encrypt 19 features | 242.328 | 245.834 | 242.23 |
| In process · evaluate ciphertexts | 18.136 | 18.675 | 18.19 |
| In process · decrypt | 3.723 | 3.812 | 3.744 |
| Same-process HTTPS + vault (20 requests) | 271.163 | 273.557 | 271.241 |

Sequential throughput: 227.0 patients/min without network; 221.2 with same-process HTTPS (n / wall time). Request 24306 bytes · response 1393 bytes · AES-256-GCM library microbenchmark 6643.8 MB/s.

Plaintext reference on the same 20 patients (10 repetitions, logit only):
floating p50 1.555 µs, p95 1.585 µs;
fixed point p50 3.467 µs, p95 3.602 µs.
Compare with evaluate_service for encrypted logit cost; HTTPS also includes encryption, network and vault.
