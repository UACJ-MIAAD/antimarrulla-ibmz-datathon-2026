# Hospital API measurement · s390x-container · 2026-10-18T06:28:39Z

> Executed on s390x; verify LinuxONE Community Cloud identity using VM/provider evidence.

- Commit `b50f6cc2346d8b5ae2fa22d36f7c67d5ec08c9ed` (environment, clean) · code `59a38c39df3c8741` (24 files) · model `e32420ac99fd10d3` · splits `8394d9f07d189298` · image `sha256:efd3103bdbc5fa954515b2e2a67c2fd8f91da53a72bc17002c9ad8ef0be4c1ee`
- Architecture: s390x · Linux-6.8.0-147-generic-s390x-with-glibc2.39 · 3 CPU · container: True
- Python 3.12.3 · phe 1.5.0 · gmpy2 2.1.5 · cryptography 41.0.7 (OpenSSL 3.0.13 30 Jan 2024) · OpenSSL CLI: OpenSSL 3.0.13 30 Jan 2024 (Library: OpenSSL 3.0.13 30 Jan 2024)
- Comando: `python -m screening.measure --mode api --url http://127.0.0.1:8080 --n 200 --final` · concurrencia 1
- Flow: HTTP client → deployed hospital API → mutual TLS 1.3 → risk service → decryption → interpretation → AES-256-GCM vault with fsync (no browser)
- Remote hospital: http://127.0.0.1:8080 · architecture s390x (Linux) · model `e32420ac99fd10d3` verified
- Remote code matches client: True

Sample: 200 deterministic synthetic inputs (seed 2026) · integers matching reference: 200 of 200

| Component | p50 (ms) | p95 (ms) | mean (ms) |
|---|---:|---:|---:|
| Client: complete request | 264.497 | 269.838 | 264.913 |
| Hospital: encrypt | 236.0 | 240.9 | 236.254 |
| Hospital: network_and_service | 21.9 | 23.2 | 22.112 |
| Hospital: decrypt | 3.7 | 3.8 | 3.73 |
| Hospital: interpret | 0.04 | 0.04 | 0.04 |
| Hospital: vault | 1.0 | 1.3 | 1.093 |
| Hospital: total_in_hospital | 262.8 | 268.1 | 263.225 |

Sequential throughput: 226.4 patients/min (n / wall time).
