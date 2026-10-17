# Medición API del hospital · local-darwin-arm64 · 2026-10-17T13:13:20Z

> ⚠️ Medición LOCAL: no es LinuxONE. No usar como velocidad de IBM Z.

- Commit `7937f9f55db9d5f81fad698256440bb78cd271eb` (git, limpio) · código `d6f1e9c03f57d57d` (21 archivos) · modelo `0455e46245761df6` · particiones `691e273dab9ace2d`
- Máquina: arm64 · macOS-27.2-arm64-arm-64bit · 12 CPU · contenedor: False
- Python 3.12.12 · phe 1.5.0 · gmpy2 2.3.2 · cryptography 50.0.2 (OpenSSL 4.0.3 29 Sep 2026) · OpenSSL CLI: OpenSSL 4.0.3 29 Sep 2026 (Library: OpenSSL 4.0.3 29 Sep 2026)
- Comando: `python -m tamizaje.medir --modo api --url http://127.0.0.1:8080 --n 200 --final` · concurrencia 1
- Recorrido: cliente HTTP → API del hospital desplegado → TLS 1.3 mutuo → servicio de riesgo → descifrado → interpretación → bóveda AES-256-GCM con fsync (sin navegador)
- Hospital remoto: http://127.0.0.1:8080 · máquina aarch64 (Linux) · modelo `0455e46245761df6` verificado

Muestra: 200 pacientes sintéticos deterministas (semilla 2026) · enteros idénticos al esperado: 200 de 200

| Tramo | p50 (ms) | p95 (ms) | media (ms) |
|---|---:|---:|---:|
| Cliente: solicitud completa | 129.221 | 136.821 | 129.966 |
| Hospital: cifrar | 112.9 | 118.6 | 113.417 |
| Hospital: red_y_servicio | 10.9 | 12.3 | 11.017 |
| Hospital: descifrar | 1.6 | 1.7 | 1.609 |
| Hospital: interpretar | 0.02 | 0.03 | 0.019 |
| Hospital: boveda | 0.7 | 1.4 | 1.042 |
| Hospital: total_en_hospital | 126.2 | 133.7 | 127.105 |

Rendimiento secuencial: 461.3 pacientes/min (n / tiempo de pared).
