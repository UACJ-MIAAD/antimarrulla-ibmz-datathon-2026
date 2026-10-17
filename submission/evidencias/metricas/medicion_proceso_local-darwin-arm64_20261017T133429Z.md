# Medición en proceso · local-darwin-arm64 · 2026-10-17T13:34:29Z

> ⚠️ Medición LOCAL: no es LinuxONE. No usar como velocidad de IBM Z.

- Commit `655763fb6fd9be8cf20cb24b8405aa0095789b8a` (git, limpio) · código `dca22a07d5f34d2f` (21 archivos) · modelo `0455e46245761df6` · particiones `691e273dab9ace2d`
- Máquina: arm64 · macOS-27.2-arm64-arm-64bit · 12 CPU · contenedor: False
- Python 3.12.12 · phe 1.5.0 · gmpy2 2.3.2 · cryptography 50.0.2 (OpenSSL 4.0.3 29 Sep 2026) · OpenSSL CLI: OpenSSL 4.0.3 29 Sep 2026 (Library: OpenSSL 4.0.3 29 Sep 2026)
- Comando: `python -m tamizaje.medir --presupuesto-s 600 --max 2000 --https 100 --final` · concurrencia 1

| Muestra (prueba del CDC, estratificada, semilla 2026) | Valor |
|---|---|
| Pacientes | 2000 (279 positivos, prevalencia 0.1395) |
| Enteros descifrados idénticos a la referencia | 2000 de 2000 |
| Error máximo del logit vs. flotante | 4.500e-08 (cota 7.900e-08) |
| ROC-AUC flotante / punto fijo / cifrado | 0.808383 / 0.808383 / 0.808383 |
| Sensibilidad · especificidad (cifrado, umbral 0.1225) | 0.7921 · 0.688 |

| Microbenchmark | p50 (ms) | p95 (ms) | media (ms) |
|---|---:|---:|---:|
| En proceso · cifrar 21 variables | 105.817 | 112.345 | 106.616 |
| En proceso · evaluar sobre cifrados | 7.793 | 8.211 | 7.857 |
| En proceso · descifrar | 1.523 | 1.623 | 1.538 |
| HTTPS en el mismo proceso + bóveda (100 solicitudes) | 127.244 | 152.245 | 129.424 |

Rendimiento secuencial: 516.6 pacientes/min sin red; 463.6 con HTTPS en el mismo proceso (n / tiempo de pared). Solicitud 26779 bytes · respuesta 1400 bytes · AES-256-GCM (microbenchmark de la biblioteca) 6634.3 MB/s.
