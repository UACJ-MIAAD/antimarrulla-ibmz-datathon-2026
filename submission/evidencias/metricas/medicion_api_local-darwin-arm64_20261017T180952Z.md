# Medición API del hospital · local-darwin-arm64 · 2026-10-17T18:09:52Z

> ⚠️ Medición LOCAL: no es LinuxONE. No usar como velocidad de IBM Z.

- Commit `65ae4ef17c2e180b3d3684d45b7eb4593296bb32` (git, limpio) · código `a947ec104a7d03ef` (22 archivos) · modelo `0455e46245761df6` · particiones `691e273dab9ace2d`
- Máquina: arm64 · macOS-27.2-arm64-arm-64bit · 12 CPU · contenedor: False
- Python 3.12.12 · phe 1.5.0 · gmpy2 2.3.2 · cryptography 50.0.2 (OpenSSL 4.0.3 29 Sep 2026) · OpenSSL CLI: OpenSSL 4.0.3 29 Sep 2026 (Library: OpenSSL 4.0.3 29 Sep 2026)
- Comando: `python -m tamizaje.medir --modo api --url http://127.0.0.1:8080 --n 200 --final` · concurrencia 1
- Recorrido: cliente HTTP → API del hospital desplegado → TLS 1.3 mutuo → servicio de riesgo → descifrado → interpretación → bóveda AES-256-GCM con fsync (sin navegador)
- Hospital remoto: http://127.0.0.1:8080 · máquina aarch64 (Linux) · modelo `0455e46245761df6` verificado
- Código remoto igual al cliente: True

Muestra: 200 pacientes sintéticos deterministas (semilla 2026) · enteros idénticos al esperado: 200 de 200

| Tramo | p50 (ms) | p95 (ms) | media (ms) |
|---|---:|---:|---:|
| Cliente: solicitud completa | 141.29 | 180.039 | 148.56 |
| Hospital: cifrar | 122.5 | 154.0 | 128.434 |
| Hospital: red_y_servicio | 12.6 | 17.2 | 13.496 |
| Hospital: descifrar | 1.7 | 2.4 | 1.831 |
| Hospital: interpretar | 0.03 | 0.05 | 0.035 |
| Hospital: boveda | 1.0 | 2.6 | 1.498 |
| Hospital: total_en_hospital | 138.4 | 176.0 | 145.291 |

Rendimiento secuencial: 403.6 pacientes/min (n / tiempo de pared).
