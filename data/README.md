# 📁 data/

> ⚠️ **NOTA: nada de datos sensibles. Datos públicos del equipo sí van en el repo, siempre que cada archivo pese menos de 50 MB; lo más grande va como [Release](https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026/releases/tag/datos-2024).**

## Datos en el repo (listos para usar)

Todo es información pública oficial, anonimizada en origen. Detalle de cada fuente en [docs/FUENTES_DATOS.md](../docs/FUENTES_DATOS.md).

| Carpeta / archivo | Qué es | Filas | Tamaño |
|-------------------|--------|------:|-------:|
| `sinave/boletin/data_raw_Diabetes_T1.csv` · `_T2.csv` | Boletín Epidemiológico SINAVE tal cual: año, semana, entidad, casos de la semana y acumulados por sexo · 2014–2026 (sem. 31) | 21,024 c/u | 2 MB |
| `sinave/tipo1/epi_dataset_v2.csv` · `sinave/tipo2/epi_dataset_v2.csv` | Serie semanal reconciliada: 32 estados × 2 sexos (64 series), con exposición (población Censo 2020) y banderas de calidad | 42,048 c/u | 12 MB |
| `sinave/tipo1/products.csv` · `sinave/tipo2/products.csv` | 111 productos listos para graficar: estado, región y nacional × hombres, mujeres y general | 72,927 c/u | 14 MB |
| `defunciones/defunciones_diabetes_2024.csv` | Defunciones registradas 2024 con causa E10–E14 u O24 (las 80 columnas de la EDR) | 112,586 | 24 MB |
| `egresos_ssa/egresos_diabetes_2024.csv` | Egresos SSA 2024 con afección principal E10–E14 | 62,771 | 11 MB |
| `egresos_ssa/afecciones_diabetes_2024.csv` · `procedimientos_diabetes_2024.csv` | Diagnósticos secundarios y procedimientos (CIE-9) de esos egresos | 104,556 · 142,999 | 8 MB |
| `egresos_ssa/descriptor_egresos_2023_2025.xlsx` | Diccionario de variables y catálogos de egresos (DGIS) | — | — |

**Archivos completos (Release [`datos-2024`](https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026/releases/tag/datos-2024)):** `DEFUN_2024.zip` (todas las causas, 31 MB) y `ssa_egresos_2024.zip` (todos los egresos, 111 MB).

```bash
gh release download datos-2024 --repo UACJ-MIAAD/antimarrulla-ibmz-datathon-2026 --dir data/raw
```

---


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
