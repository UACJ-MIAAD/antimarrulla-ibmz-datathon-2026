# src/datos/ · preparación de datos (reproducible)

Scripts que generaron los datos derivados de `data/`. Solo biblioteca estándar de Python. Escritos durante el evento (17 oct 2026).

| Script | Entrada | Salida |
|--------|---------|--------|
| `recortes_2024.py` | `data/raw/defunciones/` y `data/raw/egresos_ssa/` (Release `datos-2024`) | `data/defunciones/defunciones_diabetes_2024.csv`, `data/egresos_ssa/*_diabetes_2024.csv` |
| `historicos.py` | `data/raw/hist/DEFUN_{2017..2023}.zip`, `sectorial_egresos_{2018..2023}.zip` + 2024 (DGIS) | `data/historicos/*.csv` |
| `mart_cascada.py` | `data/conapo`, `data/sinave`, `data/imss_detecciones`, `data/historicos`, `data/sis_cronicas`, `data/catalogos` | `data/marts/cascada_entidad_anio.csv` |

```bash
# 1. Descargar originales (ver data/README.md) a data/raw/
gh release download datos-2024 --repo UACJ-MIAAD/antimarrulla-ibmz-datathon-2026 --dir data/raw
# 2. Regenerar
python src/datos/recortes_2024.py .
python src/datos/historicos.py .
python src/datos/mart_cascada.py data
```

Verificado: `mart_cascada.py` regenera `data/marts/cascada_entidad_anio.csv` **idéntico byte por byte** (SHA-256 `a481334b6aab00f4…`).

**No incluidos (preparados antes del evento):** las series SINAVE de `data/sinave/` se compilaron y reconciliaron antes del datathon a partir del Boletín Epidemiológico (datos públicos). Su código de reconciliación **no** forma parte de la entrega; el boletín crudo está en `data/sinave/boletin/` y la validación contra él en `docs/FUENTES_DATOS.md §3.1`. Los catálogos `entidades.csv`, el GeoJSON y la conversión del CLUES se generaron con scripts de un solo uso durante el evento.
