# 📁 data/

Datos públicos oficiales, anonimizados en origen, listos para usar. Cada archivo pesa menos de 50 MB; los archivos completos más grandes están en el Release [`datos-2024`](https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026/releases/tag/datos-2024).

> ⚠️ **Nunca** subir datos personales, clínicos reales ni nada sensible. `data/raw/` es para descargas locales y está ignorada por git.

Detalle de variables, catálogos y cruces entre fuentes: [docs/FUENTES_DATOS.md](../docs/FUENTES_DATOS.md).

---

## Inventario

### Entrenamiento del modelo

| Archivo | Qué es | Filas × columnas | Tamaño |
|---------|--------|------------------|-------:|
| `cdc_891/cdc_diabetes_891.csv` | CDC Diabetes Health Indicators (UCI 891, BRFSS 2015): `ID` + `Diabetes_binary` + 21 indicadores · 13.93% positivos | 253,680 × 23 | 13 MB |

### Contexto mexicano de la diabetes

| Archivo | Qué es | Filas | Tamaño |
|---------|--------|------:|-------:|
| `sinave/boletin/data_raw_Diabetes_T1.csv` · `_T2.csv` | Boletín Epidemiológico SINAVE tal cual: año, semana, entidad, casos de la semana y acumulados por sexo · 2014 → 2026 sem. 31 | 21,024 c/u | 2 MB |
| `sinave/tipo1/epi_dataset_v2.csv` · `sinave/tipo2/epi_dataset_v2.csv` | Serie semanal reconciliada: 32 estados × 2 sexos (64 series), con exposición (Censo 2020) y banderas de calidad | 42,048 c/u | 12 MB |
| `sinave/tipo1/products.csv` · `sinave/tipo2/products.csv` | 111 series listas para graficar: estado · región · nacional × hombres · mujeres · general | 72,927 c/u | 14 MB |
| `defunciones/defunciones_diabetes_2024.csv` | Defunciones registradas 2024 con causa E10–E14 (112,577) u O24 (9); las 74 columnas de la EDR | 112,586 | 24 MB |
| `egresos_sector/egresos_sector_diabetes_2024.csv` | Hospitalizaciones por diabetes 2024 de **todo el sector** (IMSS, ISSSTE, SSA, IMSS-Bienestar, PEMEX, SEDENA, SEMAR…); `DH` = institución, ISSSTE = 4 | 120,385 | 8 MB |
| `egresos_sector/descriptor_sectorial_2018_2024.xlsx` | Diccionario y catálogos de egresos sectoriales | — | — |
| `egresos_ssa/egresos_diabetes_2024.csv` | Hospitalizaciones por diabetes 2024 en SSA / IMSS-Bienestar, con más variables (peso, talla, derechohabiencia…) | 62,771 | 11 MB |
| `egresos_ssa/afecciones_diabetes_2024.csv` · `procedimientos_diabetes_2024.csv` | Diagnósticos secundarios y procedimientos CIE-9 de esos egresos (amputaciones, hemodiálisis) | 104,556 · 142,999 | 8 MB |
| `egresos_ssa/descriptor_egresos_2023_2025.xlsx` | Diccionario y catálogos de egresos SSA | — | — |
| `sis_cronicas/DA_EC_SIS_{2021,2022,2023}.zip` | Control de diabetes, hipertensión, obesidad… por unidad médica y mes (SIS) | ~50 MB c/u descomprimido | 16 MB |
| `sis_cronicas/descriptor_servicios_2010_2023.xlsx` | Diccionario del SIS (hoja `Descriptor-ECRON`) | — | — |
| `imss_detecciones/deteccion_diabetes.csv` | Detecciones (tamizajes) de diabetes del IMSS por delegación, 2000–2023 | 840 | 40 KB |

### Denominadores y determinantes sociales

| Archivo | Qué es | Filas | Tamaño |
|---------|--------|------:|-------:|
| `conapo/pobproy_quinq1.csv` | Población a mitad de año por municipio, sexo y edad quinquenal, 1990–2040 | 252,450 | 35 MB |
| `conapo/indicadores_demograficos_1950_2070.csv` | Indicadores demográficos por entidad (población, nacimientos, defunciones, esperanza de vida…) | 3,353 | 2 MB |
| `conapo/ime_2020.csv` · `imm_2020.csv` | Índice de marginación 2020, estatal y municipal | 32 · 2,469 | 0.6 MB |

### Archivos completos (Release `datos-2024`)

| Archivo | Qué es | Tamaño |
|---------|--------|-------:|
| `DEFUN_2024.zip` | Defunciones registradas 2024, todas las causas | 31 MB |
| `ssa_egresos_2024.zip` | Egresos SSA 2024 completos (Egresos, Afecciones, Procedimientos, Productos) | 111 MB |
| `sectorial_egresos_2024.zip` | Egresos de todo el sector 2024 | 82 MB |

```bash
gh release download datos-2024 --repo UACJ-MIAAD/antimarrulla-ibmz-datathon-2026 --dir data/raw
```

---

## Fuentes y licencias

| Fuente | Institución | Licencia | Origen |
|--------|-------------|----------|--------|
| CDC Diabetes Health Indicators | CDC vía UCI ML Repository | CC BY 4.0 | https://archive.ics.uci.edu/dataset/891 |
| Boletín Epidemiológico (diabetes T1 y T2) | DGE · SINAVE | Información pública; citar fuente | https://www.gob.mx/salud/acciones-y-programas/direccion-general-de-epidemiologia-boletin-epidemiologico |
| Defunciones registradas | DGIS / INEGI | Libre uso con cita | http://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_defunciones_gobmx.html |
| Egresos hospitalarios (SSA y sector) | DGIS | Libre uso con cita | http://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_egresoshosp_gobmx.html |
| Enfermedades crónicas (SIS) | DGIS | CC BY 4.0 | http://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_sis_gobmx.html |
| Detecciones de padecimientos | IMSS | CC BY 4.0 | https://www.datos.gob.mx/dataset/deteccion_padecimientos_delegacion |
| Proyecciones de población · marginación | CONAPO | CC BY 4.0 | https://www.datos.gob.mx/dataset/proyecciones-de-poblacion |

> **ISSSTE:** el CSV de egresos del ISSSTE en datos.gob.mx (`repodatos.atdt.gob.mx`) no se puede descargar ni por script ni, a veces, por navegador. **No hace falta:** el ISSSTE viene completo en los egresos del sector (`DH = 4`, 6,924 hospitalizaciones por diabetes en 2024).

## Cifras: por qué no coinciden exactamente

| Cifra | Qué cuenta | Dónde |
|-------|-----------|-------|
| **112,577** | Muertes registradas en 2024 con causa E10–E14 (la que usamos en el pitch) | Microdatos DGIS |
| 112,586 | Las mismas + 9 por diabetes en el embarazo (O24) | `defunciones/defunciones_diabetes_2024.csv` |
| 112,641 | Cifra preliminar del boletín de prensa de INEGI | Comunicado INEGI |
| 109,603 | Solo las ocurridas en 2024 con residencia en México (usada en la brecha por estado) | Cálculo del equipo |

## Descarga desde las fuentes originales

```bash
# Descargas locales en data/raw/ (ignorado por git)
mkdir -p data/raw

# CDC (entrenamiento)
python -c "from ucimlrepo import fetch_ucirepo; d = fetch_ucirepo(id=891); d.data.original.to_csv('data/raw/cdc_diabetes_891.csv', index=False)"

# DGIS: defunciones (2017–2024), egresos SSA (2019–2026), egresos del sector (2004–2024), SIS (2010–2023)
curl -L -o data/raw/DEFUN_2024.zip "http://www.dgis.salud.gob.mx/descargas/datosabiertos/defunciones/registro/DEFUN_2024.zip"
curl -L -o data/raw/ssa_egresos_2024.zip "http://www.dgis.salud.gob.mx/descargas/datosabiertos/egresos/ssa_egresos_2024.zip"
curl -L -o data/raw/sectorial_egresos_2024.zip "http://www.dgis.salud.gob.mx/descargas/datosabiertos/egresos/sectorial_egresos_2024.zip"
curl -L -o data/raw/DA_EC_SIS_2023.zip "http://www.dgis.salud.gob.mx/descargas/datosabiertos/serviciosOtorgados/Enfermedades_cronicas_no_transmisibles_en_el_adulto_y_en_el_anciano/DA_EC_SIS_2023.zip"

# INEGI EDR (DBF)
curl -L -o data/raw/defunciones_base_datos_2024_dbf.zip "https://www.inegi.org.mx/contenidos/programas/edr/microdatos/defunciones/2024/defunciones_base_datos_2024_dbf.zip"

# Verificar que ningún archivo sea HTML disfrazado
file data/raw/*
```
