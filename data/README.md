# 📁 data/

> ⚠️ **NOTA: no subir datasets grandes ni datos sensibles al repo.**

- Archivos de más de ~5 MB: **fuera** del repo. Se documenta cómo descargarlos.
- Datos personales, clínicos, financieros o de conversaciones reales: **nunca**, aunque estén "anonimizados".
- `.gitignore` ya excluye `data/*.csv`, `data/*.parquet` y similares. Si necesitas subir una muestra mínima para la demo, que sea sintética y pequeña, y avisa en el PR.

## Datasets usados

| Dataset | Fuente (link) | Licencia | Tamaño | Cómo obtenerlo |
|---------|---------------|----------|--------|----------------|
| CDC Diabetes Health Indicators | [UCI ID 891](https://archive.ics.uci.edu/dataset/891/cdc+diabetes+health+indicators) | CC BY 4.0 | 253,680 × 21 | `ucimlrepo.fetch_ucirepo(id=891)` |
| Defunciones registradas (EDR) | [INEGI](https://www.inegi.org.mx/programas/edr/) | Términos de libre uso del INEGI | ~800 mil registros por año | `curl` directo al ZIP (ver abajo) |
| Incidencia de diabetes (SUIVE-1) | [Anuarios de Morbilidad DGE](https://www.gob.mx/salud/acciones-y-programas/anuarios-de-morbilidad-1984-a-2025) | Información pública; citar fuente | Tablas agregadas | Datos de incidencia SINAVE que ya trabaja el equipo |
| Defunciones registradas (CSV) | [datos.gob.mx · Secretaría de Salud](https://www.datos.gob.mx/dataset/registro_defunciones) | CC BY 4.0 | ~206 MB (2023) | `curl` a la DGIS (`DEFUN_{año}.zip`); el CSV de datos.gob.mx solo por navegador |
| Enfermedades crónicas en adultos (SIS) | [datos.gob.mx · Secretaría de Salud](https://www.datos.gob.mx/dataset/registro_enfermedades_cronicas_adultos) | CC BY 4.0 | ~53 MB (2023) | `curl` a la DGIS (`DA_EC_SIS_{año}.zip`) + descriptor |
| Detecciones de diabetes (IMSS) | [datos.gob.mx · IMSS](https://www.datos.gob.mx/dataset/deteccion_padecimientos_delegacion) | CC BY 4.0 | 37 KB | Descarga directa |
| Egresos hospitalarios (ISSSTE) | [datos.gob.mx · ISSSTE](https://www.datos.gob.mx/dataset/datos_egresos_hospitalarios) | CC BY 4.0 | ~58 MB (2024) | Solo navegador |
| Egresos hospitalarios (SSA) | [DGIS](http://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_egresoshosp_gobmx.html) | Información pública; citar fuente | 111 MB (2024) | `curl` a la DGIS (`ssa_egresos_{año}.zip`) |
| Población y marginación | [CONAPO](https://www.datos.gob.mx/dataset/proyecciones-de-poblacion) | CC BY 4.0 | Variable | Descarga directa |

Variables, catálogos y cómo cruzar las fuentes: [docs/FUENTES_DATOS.md](../docs/FUENTES_DATOS.md).

## Descarga

```bash
# Todo cae en data/raw/ (ignorado por git)
mkdir -p data/raw/{cdc_891,defunciones,sis_cronicas,egresos_ssa,imss_detecciones,edr_inegi}

# CDC (entrenamiento)
python -c "from ucimlrepo import fetch_ucirepo; d = fetch_ucirepo(id=891); d.data.original.to_csv('data/raw/cdc_891/cdc_diabetes_891.csv', index=False)"

# Defunciones (DGIS, 2017–2024)
curl -L -o data/raw/defunciones/DEFUN_2024.zip "http://www.dgis.salud.gob.mx/descargas/datosabiertos/defunciones/registro/DEFUN_2024.zip"

# Enfermedades crónicas SIS (DGIS, 2010–2023) + descriptor
curl -L -o data/raw/sis_cronicas/DA_EC_SIS_2023.zip "http://www.dgis.salud.gob.mx/descargas/datosabiertos/serviciosOtorgados/Enfermedades_cronicas_no_transmisibles_en_el_adulto_y_en_el_anciano/DA_EC_SIS_2023.zip"
curl -L -o data/raw/sis_cronicas/descriptor.xlsx "http://www.dgis.salud.gob.mx/descargas/datosabiertos/serviciosOtorgados/Descriptor-Datos_Servicios_2010_2023.xlsx"

# Egresos hospitalarios SSA (DGIS, 2019–2026)
curl -L -o data/raw/egresos_ssa/ssa_egresos_2024.zip "http://www.dgis.salud.gob.mx/descargas/datosabiertos/egresos/ssa_egresos_2024.zip"

# Detecciones de diabetes IMSS
curl -L -o data/raw/imss_detecciones/deteccion_diabetes.csv "https://www.datos.gob.mx/dataset/0ad05edd-1c6b-469e-b52b-a58234b29e65/resource/25261f00-c346-446d-84a4-943691569af9/download/deteccion_diabetes.csv"

# EDR INEGI (DBF)
curl -L -o data/raw/edr_inegi/defunciones_base_datos_2024_dbf.zip "https://www.inegi.org.mx/contenidos/programas/edr/microdatos/defunciones/2024/defunciones_base_datos_2024_dbf.zip"

# Verificar que ningún archivo sea HTML disfrazado
file data/raw/*/*
```
