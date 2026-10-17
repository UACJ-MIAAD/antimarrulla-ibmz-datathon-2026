# Reproducible data preparation

These standard-library Python scripts produce the derived `data/` files. Identifiers, comments and operational messages are English; original filenames, columns and source codes remain unchanged for reproducibility.

| Script | Input | Output |
|--------|-------|--------|
| `prepare_raw.py` | Three `datos-2024` release ZIPs in data/raw | Expected source directories, extraction and missing historical DGIS downloads |
| `extract_2024.py` | DGIS 2024 death/SSA archives | Four diabetes extracts under data/defunciones and data/egresos_ssa |
| `history.py` | DGIS historical death/sector ZIPs and 2024 sources | Four aggregates under data/historicos |
| `care_stage_mart.py` | CONAPO, SINAVE, IMSS, historical extracts, SIS and catalogs | data/marts/cascada_entidad_anio.csv |

```bash
gh release download datos-2024 --repo UACJ-MIAAD/antimarrulla-ibmz-datathon-2026 --dir data/raw
python src/data_prep/prepare_raw.py .
python src/data_prep/extract_2024.py .
python src/data_prep/history.py .
python src/data_prep/care_stage_mart.py data
```

Preparation may download approximately 1 GB of historical originals. The 2024/historical extracts and mart have been reproduced byte for byte from the source ZIPs. The English migration repeats this check in a temporary output tree and preserves the originals.

The individual sector extract, catalog conversions and GeoJSON were prepared with separate one-off scripts and are distributed as inputs; their counts can be checked against original sources. Reconciled SINAVE series were prepared before the event. Their reconciliation code is not included as event-built solution code; raw bulletin data and comparison notes remain available in the source documentation. Never rewrite this chronology.
