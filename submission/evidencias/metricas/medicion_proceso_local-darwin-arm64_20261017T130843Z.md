# Medición en proceso · local-darwin-arm64 · 2026-10-17T13:08:43Z

> ⚠️ Medición LOCAL: no es LinuxONE. No usar como velocidad de IBM Z.

- Commit `7937f9f55db9d5f81fad698256440bb78cd271eb` (git, limpio) · código `d6f1e9c03f57d57d` (21 archivos) · modelo `0455e46245761df6` · particiones `691e273dab9ace2d`
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
| En proceso · cifrar 21 variables | 105.219 | 109.966 | 105.7 |
| En proceso · evaluar sobre cifrados | 7.728 | 8.108 | 7.776 |
| En proceso · descifrar | 1.515 | 1.591 | 1.516 |
| HTTPS en el mismo proceso + bóveda (100 solicitudes) | 118.409 | 123.225 | 119.012 |

Rendimiento secuencial: 521.3 pacientes/min sin red; 504.1 con HTTPS en el mismo proceso (n / tiempo de pared). Solicitud 26778 bytes · respuesta 1400 bytes · AES-256-GCM (microbenchmark de la biblioteca) 5964.5 MB/s.
