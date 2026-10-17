# Medición en proceso · local-darwin-arm64 · 2026-10-17T18:10:50Z

> ⚠️ Medición LOCAL: no es LinuxONE. No usar como velocidad de IBM Z.

- Commit `65ae4ef17c2e180b3d3684d45b7eb4593296bb32` (git, limpio) · código `a947ec104a7d03ef` (22 archivos) · modelo `0455e46245761df6` · particiones `691e273dab9ace2d`
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
| En proceso · cifrar 21 variables | 118.059 | 159.865 | 127.614 |
| En proceso · evaluar sobre cifrados | 8.691 | 12.018 | 9.488 |
| En proceso · descifrar | 1.668 | 2.597 | 1.827 |
| HTTPS en el mismo proceso + bóveda (100 solicitudes) | 145.226 | 205.052 | 150.639 |

Rendimiento secuencial: 431.3 pacientes/min sin red; 398.3 con HTTPS en el mismo proceso (n / tiempo de pared). Solicitud 26783 bytes · respuesta 1400 bytes · AES-256-GCM (microbenchmark de la biblioteca) 1769.3 MB/s.

Referencia en claro sobre los mismos 2000 pacientes (10 repeticiones, solo logit):
flotante p50 1.0 µs, p95 1.25 µs;
punto fijo p50 2.083 µs, p95 2.666 µs.
Comparar con evaluar_servicio para el costo del logit cifrado; el recorrido HTTPS además incluye cifrado, red y bóveda.
