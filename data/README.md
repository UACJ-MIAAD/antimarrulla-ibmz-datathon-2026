# Public source data

Official public data, anonymized at source where applicable. Tracked individual files are below 50 MB. Larger originals are in the [`datos-2024` release](https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026/releases/tag/datos-2024).

Never publish sensitive or private patient records. `data/raw/` is an ignored local download directory. Original filenames, source columns and codes retain their spelling for reproducibility; explanations and preparation code are in English. Field/relationship details: [DATA_SOURCES.md](../docs/DATA_SOURCES.md) and [DATA_MODEL.md](../docs/DATA_MODEL.md).

## Model input

| File | Description | Rows × columns | Approximate size |
|------|-------------|----------------|------------------|
| `cdc_891/cdc_diabetes_891.csv` | CDC BRFSS 2015 / UCI 891: ID, Diabetes_binary and 21 indicators; 13.93% positive | 253,680 × 23 | 13 MB |

## Mexican diabetes context

| File | Description | Rows | Approximate size |
|------|-------------|-----:|------------------|
| `sinave/boletin/data_raw_Diabetes_T1.csv`, `_T2.csv` | Original epidemiological bulletin: year/week/state, weekly and cumulative cases by sex; 2014 through week 31 of 2026 | 21,024 each | 2 MB |
| `sinave/tipo1/epi_dataset_v2.csv`, `sinave/tipo2/epi_dataset_v2.csv` | *Not included in the submission repository (unused intermediate; [archived](https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026/tree/archive/working-docs-20261018/data/sinave)).* Reconciled weekly state/sex series, Census 2020 exposure and quality flags | 42,048 each | 12 MB |
| `sinave/tipo1/products.csv`, `sinave/tipo2/products.csv` | 111 series/type, 222 total: state/region/national × men/women/all | 72,927 each | 14 MB |
| `defunciones/defunciones_diabetes_2024.csv` | Registered deaths: E10–E14 (112,577) plus O24 (9); 74 EDR columns | 112,586 | 24 MB |
| `egresos_sector/egresos_sector_diabetes_2024.csv` | Reported sector diabetes discharges; institutional code DH, ISSSTE=4 | 120,385 | 8 MB |
| `egresos_sector/descriptor_sectorial_2018_2024.xlsx` | Sector-discharge dictionary/catalogs | — | — |
| `egresos_ssa/egresos_diabetes_2024.csv` | SSA/IMSS-Bienestar diabetes admissions, including anthropometry and coverage | 62,771 | 11 MB |
| `egresos_ssa/afecciones_diabetes_2024.csv`, `procedimientos_diabetes_2024.csv` | Secondary diagnoses and ICD-9 procedures from those admissions | 104,556 / 142,999 | 8 MB |
| `egresos_ssa/descriptor_egresos_2023_2025.xlsx` | SSA-discharge dictionary/catalogs | — | — |
| `sis_cronicas/DA_EC_SIS_2021.zip`, `_2022.zip`, `_2023.zip` | Chronic-disease treatment/control by facility/month | About 50 MB each uncompressed | 16 MB |
| `sis_cronicas/descriptor_servicios_2010_2023.xlsx` | SIS dictionary, sheet Descriptor-ECRON | — | — |
| `imss_detecciones/deteccion_diabetes.csv` | IMSS screening encounters by delegation, 2000–2023 | 840 | 40 KB |

## Historical aggregates

| File | Description | Rows | Approximate size |
|------|-------------|-----:|------------------|
| `historicos/defunciones_diabetes_2017_2024.csv` | E10–E14/O24 deaths by registration/occurrence year, residence, sex, age band and cause | 9,137 | 0.3 MB |
| `historicos/defunciones_todas_causas_2017_2024.csv` | All-cause deaths by year/state/sex | 792 | 12 KB |
| `historicos/egresos_diabetes_2018_2024.csv` | Sector diabetes discharges by year, treatment state, institution, sex, age, reason and condition; includes length of stay | 60,944 | 1.9 MB |
| `historicos/egresos_todas_causas_2018_2024.csv` | All-cause discharges by year/state/institution | 1,026 | 17 KB |

E10–E14 registered-death totals: **151,019 in 2020** and **110,059 in 2023**. Exclude O24 when reproducing these figures. Source age bands are `<20`, `20-59`, `60+`.

## Mart, catalogs and geography

| File | Description | Rows | Approximate size |
|------|-------------|-----:|------------------|
| `marts/cascada_entidad_anio.csv` | State/year care-stage indicators, 2017–2024; population, notified cases, screenings, treatment/control, discharges, deaths and rates | 256 | 30 KB |
| `catalogos/entidades.csv` | INEGI state codes, names, ISO codes, SINAVE region and IMSS delegation crosswalk | 32 | 2 KB |
| `catalogos/clues_202608.csv` | *Not included in the submission repository (unused by the code; download from the source below or the [archive](https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026/tree/archive/working-docs-20261018/data/catalogos)).* DGIS CLUES facility catalog, August 2026, institutions/locations/coordinates | 64,450 | 16 MB |
| `geo/estados_mx.geojson` | Natural Earth state polygons | 32 | 0.4 MB |

The mart combines independent aggregate sources. It is not a linked patient cascade and does not measure case fatality, individual progression or underdiagnosis.

## Denominators and social determinants

| File | Description | Rows | Approximate size |
|------|-------------|-----:|------------------|
| `conapo/pobproy_quinq1.csv` | Mid-year municipal population by sex/five-year age, 1990–2040 | 252,450 | 35 MB |
| `conapo/indicadores_demograficos_1950_2070.csv` | State demographic indicators | 3,353 | 2 MB |
| `conapo/ime_2020.csv`, `imm_2020.csv` | State/municipal marginalization indices, 2020 | 32 / 2,469 | 0.6 MB |

## Local-only ENSANUT inputs

`raw/ensanut/2022/` and `raw/ensanut/2023/` contain source questionnaires, adults/residents/anthropometry/activity microdata and catalogs. They are not redistributed. Review INSP source terms before any publication; acquisition details are in [DATA_SOURCES.md](../docs/DATA_SOURCES.md). The reduced experiment exports aggregate metrics only.

## Full original release

| Archive | Contents | Size |
|---------|----------|-----:|
| `DEFUN_2024.zip` | Registered deaths, all causes | 31 MB |
| `ssa_egresos_2024.zip` | SSA admissions, secondary conditions, procedures and products | 111 MB |
| `sectorial_egresos_2024.zip` | Reported sector discharge database | 82 MB |

```bash
gh release download datos-2024 --repo UACJ-MIAAD/antimarrulla-ibmz-datathon-2026 --dir data/raw
python src/data_prep/prepare_raw.py .
python src/data_prep/extract_2024.py .
python src/data_prep/history.py .
python src/data_prep/care_stage_mart.py data
```

The four 2024 extracts, four historical CSVs and mart have byte-for-byte reproduction checks. The individual sector extract, catalog conversions and geometry were prepared separately and are distributed as source inputs. SINAVE reconciliation predates the event; its source preparation code is not submitted as event-built solution code. See [preparation details](../src/data_prep/README.md).

## Source terms and attribution recorded by the project

| Source | Institution / source terms | Link |
|--------|----------------------------|------|
| CDC indicators | CDC public-domain source; UCI points to source, Kaggle marks CC0; cite CDC/UCI | https://archive.ics.uci.edu/dataset/891 |
| Epidemiological bulletin | DGE/SINAVE public information; cite source | https://www.gob.mx/salud/acciones-y-programas/direccion-general-de-epidemiologia-boletin-epidemiologico |
| Registered deaths | DGIS/INEGI, use with attribution | http://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_defunciones_gobmx.html |
| Hospital discharges | DGIS, use with attribution | http://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_egresoshosp_gobmx.html |
| SIS chronic diseases | DGIS, CC BY 4.0 | http://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_sis_gobmx.html |
| Screening encounters | IMSS, CC BY 4.0 | https://www.datos.gob.mx/dataset/deteccion_padecimientos_delegacion |
| Population/marginalization | CONAPO, CC BY 4.0 | https://www.datos.gob.mx/dataset/proyecciones-de-poblacion |
| CLUES facilities | DGIS, use with attribution | http://www.dgis.salud.gob.mx/contenidos/intercambio/clues_gobmx.html |
| State boundaries | Natural Earth, public domain | https://www.naturalearthdata.com |

The separate ISSSTE download was unavailable during preparation; ISSSTE is already represented by `DH=4` in the sector extract, with 6,924 diabetes admissions in 2024.

## Why death totals differ

| Count | Definition |
|------:|------------|
| **112,577** | E10–E14 registered in 2024, used in the pitch |
| 112,586 | Above plus nine O24 pregnancy-diabetes deaths |
| 112,641 | Preliminary INEGI press-release figure, not the final microdata count |
| 109,603 | Occurred/registered in 2024, residents of Mexican states, used by the mart indicator |

## Original-source download examples

```bash
mkdir -p data/raw
python -c "from ucimlrepo import fetch_ucirepo; d=fetch_ucirepo(id=891); d.data.original.to_csv('data/raw/cdc_diabetes_891.csv', index=False)"
curl -L -o data/raw/DEFUN_2024.zip "http://www.dgis.salud.gob.mx/descargas/datosabiertos/defunciones/registro/DEFUN_2024.zip"
curl -L -o data/raw/ssa_egresos_2024.zip "http://www.dgis.salud.gob.mx/descargas/datosabiertos/egresos/ssa_egresos_2024.zip"
curl -L -o data/raw/sectorial_egresos_2024.zip "http://www.dgis.salud.gob.mx/descargas/datosabiertos/egresos/sectorial_egresos_2024.zip"
curl -L -o data/raw/DA_EC_SIS_2023.zip "http://www.dgis.salud.gob.mx/descargas/datosabiertos/serviciosOtorgados/Enfermedades_cronicas_no_transmisibles_en_el_adulto_y_en_el_anciano/DA_EC_SIS_2023.zip"
curl -L -o data/raw/defunciones_base_datos_2024_dbf.zip "https://www.inegi.org.mx/contenidos/programas/edr/microdatos/defunciones/2024/defunciones_base_datos_2024_dbf.zip"
file data/raw/*
```

Check archive integrity and reject HTML/error responses masquerading as data files. Do not overwrite a valid original with a failed download.
