# Mediciones

Cada corrida deja un `.json` (legible por máquina) y un `.md` (resumen). Desde el 17 oct (auditoría 3) cada archivo trae un bloque `procedencia`: commit, cambios relevantes sin commit, hash del código ejecutado, modelo, particiones e imagen. Se verifican con `python -m tamizaje.procedencia`-style: `procedencia.verificar(registro)` compara los hashes con el estado actual.

| Archivo | Estado |
|---------|--------|
| `medicion_local-darwin-arm64_20261017T094045Z.*` | **Histórica, con procedencia defectuosa.** Declara el commit `dd46ab4` sin cambios, pero ese commit no contenía el código medido (`medir.py`, `hospital.py`, `servicio.py`, `boveda.py` entraron en `ce0d105`) y el detector de entonces ignoraba archivos sin versionar. Las cifras son coherentes con pruebas posteriores, pero **no se pueden reproducir desde el commit que declara**. Se conserva sin editar; la reemplazan las mediciones trazables de abajo. |
