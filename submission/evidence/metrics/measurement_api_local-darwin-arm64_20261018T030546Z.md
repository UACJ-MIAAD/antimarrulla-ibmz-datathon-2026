# Hospital API measurement · local-darwin-arm64 · 2026-10-18T03:05:46Z

> ⚠️ LOCAL measurement. This is not LinuxONE performance.

- Commit `be9b27e58cce011804d14124468e46a8c06d7889` (git, clean) · code `db2086ee2fcf99a4` (23 files) · model `e32420ac99fd10d3` · splits `8394d9f07d189298`
- Architecture: arm64 · macOS-27.2-arm64-arm-64bit · 12 CPU · container: False
- Python 3.12.12 · phe 1.5.0 · gmpy2 2.3.2 · cryptography 50.0.2 (OpenSSL 4.0.3 29 Sep 2026) · OpenSSL CLI: OpenSSL 4.0.3 29 Sep 2026 (Library: OpenSSL 4.0.3 29 Sep 2026)
- Comando: `python -m screening.measure --mode api --url http://127.0.0.1:8080 --n 200 --final` · concurrencia 1
- Recorrido: HTTP client → deployed hospital API → mutual TLS 1.3 → risk service → decryption → interpretation → AES-256-GCM vault with fsync (no browser)
- Remote hospital: http://127.0.0.1:8080 · architecture aarch64 (Linux) · model `e32420ac99fd10d3` verified
- Remote code matches client: True

Muestra: 200 deterministic synthetic inputs (seed 2026) · integers matching reference: 200 of 200

| Component | p50 (ms) | p95 (ms) | mean (ms) |
|---|---:|---:|---:|
| Client: complete request | 114.778 | 118.24 | 115.255 |
| Hospital: encrypt | 99.7 | 102.9 | 100.202 |
| Hospital: network_and_service | 9.8 | 10.5 | 9.899 |
| Hospital: decrypt | 1.6 | 1.6 | 1.557 |
| Hospital: interpret | 0.01 | 0.02 | 0.012 |
| Hospital: vault | 1.2 | 1.6 | 1.172 |
| Hospital: total_in_hospital | 112.2 | 115.9 | 112.825 |

Sequential throughput: 520.2 patients/min (n / wall time).
