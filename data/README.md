# 📁 data/

> ⚠️ **NOTA: no subir datasets grandes ni datos sensibles al repo.**

- Archivos de más de ~5 MB: **fuera** del repo. Se documenta cómo descargarlos.
- Datos personales, clínicos, financieros o de conversaciones reales: **nunca**, aunque estén "anonimizados".
- `.gitignore` ya excluye `data/*.csv`, `data/*.parquet` y similares. Si necesitas subir una muestra mínima para la demo, que sea sintética y pequeña, y avisa en el PR.

## Datasets usados

| Dataset | Fuente (link) | Licencia | Tamaño | Cómo obtenerlo |
|---------|---------------|----------|--------|----------------|
| CDC Diabetes Health Indicators | [UCI ID 891](https://archive.ics.uci.edu/dataset/891/cdc+diabetes+health+indicators) | CC BY 4.0 | 253,680 × 21 | `ucimlrepo.fetch_ucirepo(id=891)` |
| Defunciones registradas (EDR) | [INEGI](https://www.inegi.org.mx/programas/edr/) | Términos de libre uso del INEGI | ~800 mil registros por año | Descarga manual del DBF desde el navegador (INEGI bloquea scripts) |
| Incidencia de diabetes (SUIVE-1) | [Anuarios de Morbilidad DGE](https://www.gob.mx/salud/acciones-y-programas/anuarios-de-morbilidad-1984-a-2025) | Información pública; citar fuente | Tablas agregadas | Datos de incidencia SINAVE que ya trabaja el equipo |
| Defunciones registradas (CSV) | [datos.gob.mx · Secretaría de Salud](https://www.datos.gob.mx/dataset/registro_defunciones) | CC BY 4.0 | ~206 MB (2023) | Navegador (repodatos bloquea `curl`) |
| Enfermedades crónicas en adultos (SIS) | [datos.gob.mx · Secretaría de Salud](https://www.datos.gob.mx/dataset/registro_enfermedades_cronicas_adultos) | CC BY 4.0 | ~53 MB (2023) | Navegador; descriptor en la DGIS |
| Detecciones de diabetes (IMSS) | [datos.gob.mx · IMSS](https://www.datos.gob.mx/dataset/deteccion_padecimientos_delegacion) | CC BY 4.0 | 37 KB | Descarga directa |
| Egresos hospitalarios (ISSSTE) | [datos.gob.mx · ISSSTE](https://www.datos.gob.mx/dataset/datos_egresos_hospitalarios) | CC BY 4.0 | ~58 MB (2024) | Navegador |
| Población y marginación | [CONAPO](https://www.datos.gob.mx/dataset/proyecciones-de-poblacion) | CC BY 4.0 | Variable | Descarga directa |

Variables, catálogos y cómo cruzar las fuentes: [docs/FUENTES_DATOS.md](../docs/FUENTES_DATOS.md).

## Descarga

```bash
# CDC (entrenamiento):
python -c "from ucimlrepo import fetch_ucirepo; d = fetch_ucirepo(id=891); print(d.data.features.shape)"
# EDR INEGI: descargar en el navegador y descomprimir en data/raw/ (ignorado por git)
```
