# Medición API del hospital · local-darwin-arm64 · 2026-10-17T13:38:44Z

> ⚠️ Medición LOCAL: no es LinuxONE. No usar como velocidad de IBM Z.

- Commit `655763fb6fd9be8cf20cb24b8405aa0095789b8a` (git, limpio) · código `dca22a07d5f34d2f` (21 archivos) · modelo `0455e46245761df6` · particiones `691e273dab9ace2d`
- Máquina: arm64 · macOS-27.2-arm64-arm-64bit · 12 CPU · contenedor: False
- Python 3.12.12 · phe 1.5.0 · gmpy2 2.3.2 · cryptography 50.0.2 (OpenSSL 4.0.3 29 Sep 2026) · OpenSSL CLI: OpenSSL 4.0.3 29 Sep 2026 (Library: OpenSSL 4.0.3 29 Sep 2026)
- Comando: `python -m tamizaje.medir --modo api --url http://127.0.0.1:8080 --n 200 --final` · concurrencia 1
- Recorrido: cliente HTTP → API del hospital desplegado → TLS 1.3 mutuo → servicio de riesgo → descifrado → interpretación → bóveda AES-256-GCM con fsync (sin navegador)
- Hospital remoto: http://127.0.0.1:8080 · máquina aarch64 (Linux) · modelo `0455e46245761df6` verificado

Muestra: 200 pacientes sintéticos deterministas (semilla 2026) · enteros idénticos al esperado: 200 de 200

| Tramo | p50 (ms) | p95 (ms) | media (ms) |
|---|---:|---:|---:|
| Cliente: solicitud completa | 131.766 | 145.484 | 133.59 |
| Hospital: cifrar | 115.4 | 125.7 | 116.409 |
| Hospital: red_y_servicio | 11.3 | 12.9 | 11.713 |
| Hospital: descifrar | 1.6 | 1.8 | 1.679 |
| Hospital: interpretar | 0.02 | 0.03 | 0.024 |
| Hospital: boveda | 0.8 | 1.7 | 1.113 |
| Hospital: total_en_hospital | 129.8 | 141.3 | 130.933 |

Rendimiento secuencial: 448.9 pacientes/min (n / tiempo de pared).
