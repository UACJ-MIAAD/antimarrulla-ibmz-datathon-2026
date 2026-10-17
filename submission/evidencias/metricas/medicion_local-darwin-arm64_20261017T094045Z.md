# Medición · local-darwin-arm64 · 2026-10-17T09:40:45Z

> ⚠️ Medición LOCAL: no es LinuxONE. No usar como velocidad de IBM Z.

- Commit: `dd46ab4ed784a9fab29c2fc18e0339be71001db0` · modelo `0455e46245761df6` · particiones `691e273dab9ace2d`
- Máquina: arm64 · macOS-27.2-arm64-arm-64bit · 12 CPU · contenedor: False
- Python 3.12.12 · phe 1.5.0 · gmpy2 2.3.2 · cryptography 50.0.2 (OpenSSL 4.0.3 29 Sep 2026) · OpenSSL CLI: OpenSSL 4.0.3 29 Sep 2026 (Library: OpenSSL 4.0.3 29 Sep 2026)
- Comando: `python -m tamizaje.medir --presupuesto-s 600.0 --max 2000 --https 200` · llave Paillier 2048 bits · concurrencia 1 · calentamiento 5

| Muestra (prueba, estratificada, semilla 2026) | Valor |
|---|---|
| Pacientes | 2000 (279 positivos, prevalencia 0.1395) |
| Enteros descifrados idénticos a la referencia | 2000 de 2000 |
| Error máximo del logit vs. flotante | 4.500e-08 (cota 7.900e-08) |
| ROC-AUC flotante / punto fijo / cifrado | 0.808383 / 0.808383 / 0.808383 |
| Sensibilidad · especificidad (cifrado, umbral 0.1225) | 0.7921 · 0.688 |

| Fase | p50 (ms) | p95 (ms) |
|---|---:|---:|
| Cifrar 21 variables (hospital) | 113.57 | 127.354 |
| Evaluar sobre cifrados (servicio) | 8.33 | 9.827 |
| Descifrar (hospital) | 1.621 | 2.063 |
| Recorrido completo HTTPS + bóveda (200 solicitudes) | 128.168 | 148.069 |

Pacientes por minuto (secuencial, en proceso): 476.9 · por HTTPS: 458.6 · solicitud 26782 bytes · respuesta 1400 bytes · bóveda AES-256-GCM 7060.9 MB/s.
