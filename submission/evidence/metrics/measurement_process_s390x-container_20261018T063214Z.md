# In-process measurement · s390x-container · 2026-10-18T06:32:14Z

> Executed on s390x; verify LinuxONE Community Cloud identity using VM/provider evidence.

- Commit `b50f6cc2346d8b5ae2fa22d36f7c67d5ec08c9ed` (environment, clean) · code `59a38c39df3c8741` (24 files) · model `e32420ac99fd10d3` · splits `8394d9f07d189298` · image `sha256:ed1159ad581754c1f6dfb8b7cccbe8a40d3c27a1e565a6a9cc3e55f3045e4f9d`
- Architecture: s390x · Linux-6.8.0-147-generic-s390x-with-glibc2.39 · 3 CPU · container: True
- Python 3.12.3 · phe 1.5.0 · gmpy2 2.1.5 · cryptography 41.0.7 (OpenSSL 3.0.13 30 Jan 2024) · OpenSSL CLI: OpenSSL 3.0.13 30 Jan 2024 (Library: OpenSSL 3.0.13 30 Jan 2024)
- Comando: `python -m screening.measure --budget-s 600 --max 2000 --patients 2000 --https 200 --final` · concurrencia 1

| Sample (stratified CDC test split, seed 2026) | Value |
|---|---|
| Patients | 2000 (279 positives, prevalence 0.1395) |
| Decrypted integers matching the reference | 2000 of 2000 |
| Maximum floating-point logit error | 3.370e-08 (bound 7.350e-08) |
| ROC-AUC floating / fixed point / encrypted | 0.806525 / 0.806525 / 0.806525 |
| Sensitivity · specificity (encrypted, threshold 0.1218) | 0.7814 · 0.681 |

| Microbenchmark | p50 (ms) | p95 (ms) | mean (ms) |
|---|---:|---:|---:|
| In process · encrypt 19 features | 236.588 | 242.815 | 237.039 |
| In process · evaluate ciphertexts | 17.585 | 18.327 | 17.662 |
| In process · decrypt | 3.718 | 3.927 | 3.756 |
| Same-process HTTPS + vault (200 requests) | 264.996 | 270.712 | 265.631 |

Sequential throughput: 232.0 patients/min without network; 225.9 with same-process HTTPS (n / wall time). Request 24301 bytes · response 1393 bytes · AES-256-GCM library microbenchmark 6442.1 MB/s.

Plaintext reference on the same 2000 patients (10 repetitions, logit only):
floating p50 1.517 µs, p95 1.569 µs;
fixed point p50 3.4 µs, p95 3.537 µs.
Compare with evaluate_service for encrypted logit cost; HTTPS also includes encryption, network and vault.
