# src/datos/ · preparación de datos (reproducible)

Scripts que generaron los datos derivados de `data/`. Solo biblioteca estándar de Python. Escritos durante el evento (17 oct 2026).

| Script | Entrada | Salida |
|--------|---------|--------|
| `preparar_raw.py` | ZIP del Release `datos-2024` descargados en `data/raw/` | Los acomoda en `data/raw/{defunciones,egresos_ssa,egresos_sector}/`, extrae los que se leen como texto y descarga de la DGIS los históricos que falten a `data/raw/hist/` |
| `recortes_2024.py` | `data/raw/defunciones/` y `data/raw/egresos_ssa/` (Release `datos-2024`) | `data/defunciones/defunciones_diabetes_2024.csv`, `data/egresos_ssa/*_diabetes_2024.csv` |
| `historicos.py` | `data/raw/hist/DEFUN_{2017..2023}.zip`, `sectorial_egresos_{2018..2023}.zip` + 2024 (DGIS) | `data/historicos/*.csv` |
| `mart_cascada.py` | `data/conapo`, `data/sinave`, `data/imss_detecciones`, `data/historicos`, `data/sis_cronicas`, `data/catalogos` | `data/marts/cascada_entidad_anio.csv` |

```bash
# 1. Descargar los originales 2024 del Release a data/raw/
gh release download datos-2024 --repo UACJ-MIAAD/antimarrulla-ibmz-datathon-2026 --dir data/raw
# 2. Acomodar, extraer y bajar los históricos 2017–2023 de la DGIS (~1 GB)
python src/datos/preparar_raw.py .
# 3. Regenerar
python src/datos/recortes_2024.py .
python src/datos/historicos.py .
python src/datos/mart_cascada.py data
```

Verificado (17 oct 2026), en una carpeta vacía partiendo solo de los tres ZIP del Release y los ZIP históricos de la DGIS:

- `recortes_2024.py` e `historicos.py` regeneran **idénticos byte por byte** los 4 recortes 2024 (`data/defunciones/`, `data/egresos_ssa/`) y los 4 CSV de `data/historicos/`.
- `mart_cascada.py` regenera `data/marts/cascada_entidad_anio.csv` **idéntico byte por byte** (SHA-256 `a481334b6aab00f4…`).

**Insumos preparados (no se regeneran aquí):** el recorte individual `data/egresos_sector/egresos_sector_diabetes_2024.csv`, las conversiones de catálogos (`entidades.csv`, CLUES) y el GeoJSON se hicieron con scripts de un solo uso; se distribuyen tal cual y sus conteos se pueden comprobar contra los originales.

**No incluidos (preparados antes del evento):** las series SINAVE de `data/sinave/` se compilaron y reconciliaron antes del datathon a partir del Boletín Epidemiológico (datos públicos). Su código de reconciliación **no** forma parte de la entrega; el boletín crudo está en `data/sinave/boletin/` y la validación contra él en `docs/FUENTES_DATOS.md §3.1`.
