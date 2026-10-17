# Hospital API measurement · local-darwin-arm64 · 2026-10-17T19:40:52Z

> ⚠️ LOCAL measurement. This is not LinuxONE performance.

- Commit `5412abe7ed82efdf91b5afba846079f0f58584b1` (git, clean) · code `fa44bfe5f31989c2` (22 files) · model `9747116760f938ae` · splits `8394d9f07d189298`
- Architecture: arm64 · macOS-27.2-arm64-arm-64bit · 12 CPU · container: False
- Python 3.12.12 · phe 1.5.0 · gmpy2 2.3.2 · cryptography 50.0.2 (OpenSSL 4.0.3 29 Sep 2026) · OpenSSL CLI: OpenSSL 4.0.3 29 Sep 2026 (Library: OpenSSL 4.0.3 29 Sep 2026)
- Comando: `python -m screening.measure --mode api --url http://127.0.0.1:18080 --n 200 --final` · concurrencia 1
- Recorrido: HTTP client → deployed hospital API → mutual TLS 1.3 → risk service → decryption → interpretation → AES-256-GCM vault with fsync (no browser)
- Remote hospital: http://127.0.0.1:18080 · architecture aarch64 (Linux) · model `9747116760f938ae` verified
- Remote code matches client: True

Muestra: 200 deterministic synthetic inputs (seed 2026) · integers matching reference: 200 of 200

| Component | p50 (ms) | p95 (ms) | mean (ms) |
|---|---:|---:|---:|
| Client: complete request | 149.015 | 183.317 | 153.094 |
| Hospital: encrypt | 128.9 | 161.2 | 132.569 |
| Hospital: network_and_service | 13.1 | 17.4 | 13.826 |
| Hospital: decrypt | 1.7 | 2.9 | 1.87 |
| Hospital: interpret | 0.04 | 0.07 | 0.039 |
| Hospital: vault | 1.1 | 2.4 | 1.38 |
| Hospital: total_in_hospital | 146.0 | 179.5 | 149.682 |

Sequential throughput: 391.7 patients/min (n / wall time).
