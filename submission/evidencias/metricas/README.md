# Mediciones

Cada corrida deja un `.json` (legible por máquina) y un `.md` (resumen). Desde el 17 oct (auditoría 3) cada archivo trae un bloque `procedencia`: commit, cambios relevantes sin commit, hash del código ejecutado, modelo, particiones e imagen. Se comprueban con `procedencia.verificar(registro)` (en `src/tamizaje/procedencia.py`), que compara los hashes del registro con el estado actual.

| Archivo | Estado |
|---------|--------|
| `medicion_local-darwin-arm64_20261017T094045Z.*` | **Histórica, con procedencia defectuosa.** Declara el commit `dd46ab4` sin cambios, pero ese commit no contenía el código medido (`medir.py`, `hospital.py`, `servicio.py`, `boveda.py` entraron en `ce0d105`) y el detector de entonces ignoraba archivos sin versionar. Las cifras son coherentes con pruebas posteriores, pero **no se pueden reproducir desde el commit que declara**. Se conserva sin editar; la reemplazan las mediciones trazables de abajo. |
| `medicion_proceso_local-darwin-arm64_20261017T130843Z.*` | **Trazable.** Corrida con `make medir FINAL=1` desde un clon limpio del commit `7937f9f` (código `d6f1e9c0…`). Exactitud en 2,000 pacientes del CDC y microbenchmarks en un solo proceso. Local (macOS arm64), **no LinuxONE**. |
| `medicion_api_local-darwin-arm64_20261017T131320Z.*` | **Trazable.** `make demo` y `make medir-api FINAL=1` desde el mismo clon limpio de `7937f9f`; imagen `tamizaje:demo` `sha256:1a106d6c632559361c385235d325aa316c31bfc55290a3c0102ae0cda020b484` (etapa app). Cliente HTTP → API del hospital → mTLS → servicio → descifrado → bóveda, en dos contenedores locales (Linux arm64 en Docker Desktop), **no LinuxONE**; 200 pacientes sintéticos. |

Para reproducir las cifras de `7937f9f`, usar ese commit: el código cambió después y el hash de la rama actual ya es otro. Una modificación de documentación no altera los cálculos, pero los cambios del servicio o medidor sí exigen identificar su propia versión.

## Mediciones de la versión `655763f`

| Archivo | Estado |
|---------|--------|
| `medicion_proceso_local-darwin-arm64_20261017T133429Z.*` | **Trazable para `655763f`.** `make medir FINAL=1` desde un clon limpio de `655763f` (código `dca22a07…`). 2,000/2,000 enteros, ROC-AUC 0.808 en las tres variantes. Local, no LinuxONE. |
| `medicion_api_local-darwin-arm64_20261017T133844Z.*` | **Trazable para `655763f`.** `make demo` + `make medir-api FINAL=1` desde el mismo clon; imagen `tamizaje:demo` `sha256:77477fa44b55543bf057d162d542d8dc4df2b23c195500493ac3479df9310775`; el hospital reporta el mismo hash de código que el cliente (`codigo_igual_al_cliente: true`). 200/200 enteros, p50 131.8 ms. Dos contenedores locales, no LinuxONE. |

Las de `7937f9f` siguen siendo válidas para ese commit (`git checkout 7937f9f`).

## Medición de la auditoría de equipo (`65ae4ef`)

- `medicion_proceso_local-darwin-arm64_20261017T181050Z.json`: 2,000/2,000 enteros idénticos; AUC 0.808383 en claro, punto fijo y cifrado. Añade tiempos del logit en claro sobre la misma muestra: p50 1.0 µs; punto fijo 2.083 µs; evaluación cifrada 8.691 ms (sin red). No son la misma operación que el recorrido HTTPS completo.
- `medicion_api_local-darwin-arm64_20261017T180952Z.json`: 200/200 sintéticos por la API de dos contenedores, código remoto igual al cliente, p50 141.29 ms y p95 180.039 ms; 403.6 pacientes/min en secuencia. Demo temporal con secretos/volumen propios, retirada al terminar.

Ambas corridas registran procedencia limpia de `65ae4ef` y son **locales, no LinuxONE**. No se ajustaron los resultados para que repitieran latencias anteriores. Los cambios de empaquetado/documentación posteriores no son otra medición; para reproducir exactamente el código medido, usar ese commit.
