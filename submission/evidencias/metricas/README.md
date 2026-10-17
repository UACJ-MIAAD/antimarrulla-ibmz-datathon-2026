# Mediciones

Cada corrida deja un `.json` (legible por máquina) y un `.md` (resumen). Desde el 17 oct (auditoría 3) cada archivo trae un bloque `procedencia`: commit, cambios relevantes sin commit, hash del código ejecutado, modelo, particiones e imagen. Se comprueban con `procedencia.verificar(registro)` (en `src/tamizaje/procedencia.py`), que compara los hashes del registro con el estado actual.

| Archivo | Estado |
|---------|--------|
| `medicion_local-darwin-arm64_20261017T094045Z.*` | **Histórica, con procedencia defectuosa.** Declara el commit `dd46ab4` sin cambios, pero ese commit no contenía el código medido (`medir.py`, `hospital.py`, `servicio.py`, `boveda.py` entraron en `ce0d105`) y el detector de entonces ignoraba archivos sin versionar. Las cifras son coherentes con pruebas posteriores, pero **no se pueden reproducir desde el commit que declara**. Se conserva sin editar; la reemplazan las mediciones trazables de abajo. |
| `medicion_proceso_local-darwin-arm64_20261017T130843Z.*` | **Trazable.** Corrida con `make medir FINAL=1` desde un clon limpio del commit `7937f9f` (código `d6f1e9c0…`). Exactitud en 2,000 pacientes del CDC y microbenchmarks en un solo proceso. Local (macOS arm64), **no LinuxONE**. |
| `medicion_api_local-darwin-arm64_20261017T131320Z.*` | **Trazable.** `make demo` y `make medir-api FINAL=1` desde el mismo clon limpio de `7937f9f`; imagen `tamizaje:demo` `sha256:1a106d6c632559361c385235d325aa316c31bfc55290a3c0102ae0cda020b484` (etapa app). Cliente HTTP → API del hospital → mTLS → servicio → descifrado → bóveda, en dos contenedores locales (Linux arm64 en Docker Desktop), **no LinuxONE**; 200 pacientes sintéticos. |
