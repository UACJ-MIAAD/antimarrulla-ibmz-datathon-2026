# Data sources and definitions

CDC trains the model. SINAVE, EDR, SIS, IMSS, hospital discharges and CONAPO support Mexican context. Public curated inputs are tracked; large originals and ENSANUT microdata remain local or in the release. See [data inventory](../data/README.md). Original names/column codes are retained for reproducibility; explanations are English.

## 0. Direct acquisition routes

These routes were recorded/tested during October 17 preparation; availability is not guaranteed indefinitely. Replace YEAR with the source year. Validate the response and ZIP CRC rather than accept an HTML error page as a dataset.

| Source | Recorded coverage | Direct route | Example size |
|--------|-------------------|--------------|--------------|
| DGIS deaths | 2017–2024 | http://www.dgis.salud.gob.mx/descargas/datosabiertos/defunciones/registro/DEFUN_YEAR.zip | 31 MB, 2024 |
| DGIS SSA discharges | 2019–2026 | http://www.dgis.salud.gob.mx/descargas/datosabiertos/egresos/ssa_egresos_YEAR.zip | 111 MB, 2024 |
| DGIS emergencies | 2019–2026 | http://www.dgis.salud.gob.mx/descargas/datosabiertos/urgencias/Urgencias_YEAR.zip | — |
| DGIS SIS chronic disease | 2010–2023 | http://www.dgis.salud.gob.mx/descargas/datosabiertos/serviciosOtorgados/Enfermedades_cronicas_no_transmisibles_en_el_adulto_y_en_el_anciano/DA_EC_SIS_YEAR.zip | Varies by year |
| SIS dictionary | Descriptor-ECRON sheet | http://www.dgis.salud.gob.mx/descargas/datosabiertos/serviciosOtorgados/Descriptor-Datos_Servicios_2010_2023.xlsx | 209 KB |
| INEGI EDR DBF | Annual 2020–2024 | https://www.inegi.org.mx/contenidos/programas/edr/microdatos/defunciones/YEAR/defunciones_base_datos_YEAR_dbf.zip | — |
| INEGI historical DBF | Five-year blocks, 1990–2019 | https://www.inegi.org.mx/contenidos/programas/edr/microdatos/defunciones/datos/defunciones_generales_base_datos_2015_2019_dbf.zip | Example block |
| IMSS screening | 2000–2023 | https://www.datos.gob.mx/dataset/0ad05edd-1c6b-469e-b52b-a58234b29e65/resource/25261f00-c346-446d-84a4-943691569af9/download/deteccion_diabetes.csv | 37 KB |
| CDC UCI 891 | BRFSS 2015 | `ucimlrepo.fetch_ucirepo(id=891)` | 253,680 records |

DGIS optional version query strings may be omitted. [DGIS database index](http://www.dgis.salud.gob.mx/contenidos/basesdedatos/Datos_Abiertos_gobmx.html). During preparation, repodatos.atdt.gob.mx blocked scripted downloads; use equivalent DGIS sources where available or the original browser workflow. Catalog metadata can be requested from `https://www.datos.gob.mx/api/3/action/package_show?id=DATASET_ID`.

## 1. CDC Diabetes Health Indicators

[UCI dataset 891](https://archive.ics.uci.edu/dataset/891/cdc+diabetes+health+indicators), CDC BRFSS 2015. 253,680 records, 21 predictors, ID and binary label; 35,346 positives (13.9333%). Indicators cover BMI, blood pressure/cholesterol, physical activity, smoking, demographics and healthcare access. `ID` is excluded from the model.

The project's recorded source attribution treats CDC/BRFSS as public-domain material; UCI points to the source and Kaggle labels its copy CC0. Do not conflate the license of a dataset copy, website text or software dependency; retain the original source attribution. The source target denotes reported prediabetes/diabetes, not future disease or a laboratory-verified diagnosis.

## 2. INEGI registered deaths (EDR)

Annual death-certificate records from civil registration and forensic/medical reporting, with ICD-10 underlying cause. Diabetes filtering uses E10–E14, keeping pregnancy-diabetes O24 separately.

| Reference | Link |
|-----------|------|
| Program and microdata | https://www.inegi.org.mx/programas/edr/ |
| 2024 dictionary | https://www.inegi.org.mx/rnm/index.php/catalog/1140/data-dictionary |
| Microdata notes | https://www.inegi.org.mx/contenidos/programas/edr/microdatos/defunciones_registradas_notas_microdatos.pdf |
| Aggregate indicator API | https://www.inegi.org.mx/servicios/api_indicadores.html |

Direct DBF ZIPs worked during preparation; scraping the program page is a different task because links are assembled in JavaScript. Read DBF using dbfread or compatible geospatial tools. The indicator API is not the microdata source. DGIS also provides CSV death archives, including the 2024 input used here. Retain INEGI attribution/source terms.

### Source fields: 74-column DEFUN24

| Group | Source identifiers |
|-------|--------------------|
| Cause | CAUSA_DEF, LISTA_MEX, GR_LISMEX, CAPITULO, GRUPO, LISTA1, COD_ADICIO |
| Person | SEXO, EDAD, EDAD_AGRU, ESCOLARIDA, OCUPACION, COND_ACT, EDO_CIVIL, CONINDIG, LENGUA, CVE_LENGUA, AFROMEX, NACIONALID, NACESP_CVE, ENT_NAC |
| Health | DERECHOHAB, ASIST_MEDI, SITIO_OCUR, NECROPSIA, USONECROPS, COND_CERT, CIRUGIA, ENCEFALICA, DONADOR |
| Geography | ENT/MUN/LOC/TLOC residence, occurrence and registration fields; injury geography; AREA_UR and DIS_RE_OAX |
| Dates | Day/month/year of occurrence, registration, birth and certification; HORAS/MINUTOS |
| Violence/maternal | TIPO_DEFUN, NATVIOLE, LUGAR_OCUR, OCURR_TRAB, PAR_AGRE, VIO_FAMI, EMBARAZO, REL_EMBA, COMPLICARO, MATERNAS, RAZON_M |
| Perinatal | SEM_GEST, GRAMOS |

### Important source codebooks

| Field | English meaning of source codes |
|-------|---------------------------------|
| SEXO | 1 male; 2 female; 9 unspecified |
| ESCOLARIDA | 1 none; 2 preschool; 3/4 incomplete/complete primary; 5/6 secondary; 7/8 upper secondary; 9 professional; 10 postgraduate; 88 not applicable under age 3; 99 unspecified |
| EDO_CIVIL | 1 single; 2 divorced; 3 widowed; 4 cohabiting; 5 married; 6 separated; 8 not applicable under 12; 9 unspecified |
| DERECHOHAB | 1 none; 2 IMSS; 3 ISSSTE; 4 PEMEX; 5 SEDENA; 6 SEMAR; 7 Seguro Popular equivalent; 8 other; 9 IMSS-Bienestar; 10 ISSFAM; 12 OPD IMSS-Bienestar; 99 unspecified |
| SITIO_OCUR | 1 SSA; 2 IMSS-Bienestar; 3 IMSS; 4 ISSSTE; 5 PEMEX; 6 SEDENA; 7 SEMAR; 8 other public; 9 private; 10 public road; 11 home; 12 other; 13 OPD IMSS-Bienestar; 99 unspecified |
| ASIST_MEDI | 1 assisted; 2 unassisted; 9 unspecified |
| AREA_UR | 1 urban, >=2,500 residents; 2 rural; 9 unspecified |
| COND_ACT | 1 worked; 2 did not work; 8 not applicable under 5; 9 unspecified |
| TIPO_DEFUN | 4 natural disease death; other specified categories include accidents/violence |

EDAD's first digit encodes the unit; 4xxx denotes years. Verify against the descriptor for the source year rather than treating all values as plain years.

## 3. SINAVE incidence (SUIVE-1)

Weekly aggregated newly notified cases, not individual records. [Manual](https://epidemiologia.salud.gob.mx/gobmx/salud/documentos/manuales/32_ManualSuive.pdf), [annual morbidity tables](https://www.gob.mx/salud/acciones-y-programas/anuarios-de-morbilidad-1984-a-2025), [weekly bulletin](https://www.gob.mx/salud/acciones-y-programas/direccion-general-de-epidemiologia-boletin-epidemiologico).

Source dimensions: CLUES/notifying institution/municipality/state; epidemiological week/start/end dates; E10 type 1, E11–E14 type 2 and O24.4 gestational diabetes. Source age bands: under one, 1–4, 5–9, 10–14, 15–19, 20–24, 25–44, 45–49, 50–59, 60–64, 65+, unknown. Annual tables add incidence rates, reporting source and cause rankings.

### 3.1 Team-prepared series

| Layer | File | Contents |
|-------|------|----------|
| Raw bulletin | data/sinave/boletin/data_raw_Diabetes_T1.csv and T2 | Anio, Semana, Entidad, Padecimiento, Casos_semana and cumulative sex/previous-year counts |
| Reconciled (archived, not in the submission repository) | tipo1/epi_dataset_v2.csv and tipo2 | 64 state/sex series; dates, cases, exposure, observed and quality flags |
| Products | tipo1/products.csv and tipo2 | 111 series/type, 222 total; state/region/national × men/women/all |

These series were compiled/reconciled **before the event** as prepared data. Their reconciliation code is not submitted as event-built solution code. Preserve that disclosure and raw-bulletin comparison.

| Recorded check, October 17 | Type 1 | Type 2 |
|---------------------------|--------|--------|
| Annual weekly sum versus bulletin cumulative | −2.5% to +7.8%, most below 3% | −3.3% to +1.7%, most about −1% |
| Negative values | 0 | 0 |
| Imputed weeks, observed=False | 9, about 0.0% | 120, about 0.2% |
| National cases, 2024 | 3,938 | 494,049 |
| Male/female split, 2024 | 1,639 /2,299 | 205,270 /288,779 |

Exposure is fixed Census 2020 population; use year-specific CONAPO for rates. T1 sex splits often use sex_fallback_state_13w imputation, so prefer general. T2 has sex_delta_total_mismatch adjustments; do not assume the raw male/female sums always equal the bulletin total. 2026 is partial, and the product's last observed week starts July 27. Notifications depend on detection/reporting and are not all underlying cases.

### 3.2 Exploratory deaths per 100 notified cases, 2024

The numerator is **109,603 E10–E14 deaths occurring and registered in 2024 among residents of Mexican states**. The 112,577 registered-year total includes earlier occurrences and foreign residence; substituting it would yield about 22.6 rather than the mart's 22.0.

| Geography | Newly notified cases | Deaths | Deaths/100 cases |
|-----------|---------------------:|-------:|-----------------:|
| National | 497,987 | 109,603 | 22.0 |
| Michoacán | 9,330 | 4,129 | 44.3 |
| Oaxaca | 11,891 | 4,577 | 38.5 |
| Puebla | 18,887 | 7,042 | 37.3 |
| Estado de México | 53,776 | 17,081 | 31.8 |
| Veracruz | 33,819 | 10,473 | 31.0 |
| Chihuahua | 12,552 | 2,649 | 21.1 |
| Baja California | 27,751 | 2,504 | 9.0 |
| Sinaloa | 17,681 | 1,537 | 8.7 |

State notified-case and mortality rates per 100,000 CONAPO residents have Pearson correlation −0.12. The ratio is not case fatality, underdiagnosis or evidence of late detection. Deaths arise from earlier diagnosed cohorts; age, prior prevalence, reporting coverage, referrals and registration affect it. Always show numerator/denominator and the exploratory label.

## 4. Other Mexican sources

The preparation record used source attribution/CC BY 4.0 where the catalog specifies it. Preserve each actual dataset's terms and source, rather than generalizing one license to all files. Browser/script restrictions are observations from acquisition, not permanent guarantees.

| Source | Coverage/grain | Use |
|--------|----------------|-----|
| [Registered deaths](https://www.datos.gob.mx/dataset/registro_defunciones) | 1998–2023 catalog CSV; individual | Same EDR concepts; DGIS direct equivalent used |
| [Chronic disease](https://www.datos.gob.mx/dataset/registro_enfermedades_cronicas_adultos) | SIS 2010–2023; facility/month | Treatment, control, HbA1c and foot-related counts |
| [Screening](https://www.datos.gob.mx/dataset/deteccion_padecimientos_delegacion) | IMSS 2000–2023; delegation/year | Screening encounters |
| [ISSSTE discharges](https://www.datos.gob.mx/dataset/datos_egresos_hospitalarios) | 2020/2024; individual | Hospitalization context |
| [Population projections](https://www.datos.gob.mx/dataset/proyecciones-de-poblacion), [marginalization](https://www.datos.gob.mx/dataset/indices_marginacion) | State/municipality; 1950–2070 /2010–2020 catalog coverage | Denominators/social context |

### 4.1 Additional death CSV

Recorded route: `https://repodatos.atdt.gob.mx/all_data/secretaria_salud/6fecbbb3-afd9-44a1-8665-679a80ce4a15/defunciones_registradas_YEAR.csv`. EDR fields plus FECHA_OCURR/NACIM/REGIS/CERT and fn_LISTA_MEX/fn_GR_LISMEX. Filter CAUSA_DEF E10–E14; keep O24 separate. Direct DGIS DEFUN archives are the automated route.

### 4.2 SIS chronic disease

Recorded route: `https://repodatos.atdt.gob.mx/s_salud/enf_cronicas_adultos/DA_EC_SIS_YEAR.csv`; DGIS ZIP/dictionary equivalents are listed above. Keys: CLAVE_ENTIDAD, ENTIDAD, CLAVE_MUNICIPIO, MUNICIPIO, CLUES, NOMBRE_CLUES, MES, ANIO, FECHA. NULL means no recorded value.

| Prefix | Meaning | Important suffixes |
|--------|---------|--------------------|
| ADM | Diabetes treatment/control | 02/03/05/06 entering treatment; 08/09/11/12 in treatment; 14/15/17/18 controlled; 20–22 insulin treatment; 23 controlled with insulin |
| AHA | Hypertension | Similar age/sex structure |
| AOB | Obesity | Similar structure |
| ADL | Dyslipidemia | Similar structure |
| AEC | Metabolic syndrome | Similar structure |
| HBA | HbA1c | 01 tests; 02 controlled; 03 coverage |
| PDM | Diabetes foot examination | 02 examinations; 03 foot-condition count |
| PMA | Microalbuminuria | 01 diabetes tests; 02 hypertension tests |
| FRS | Overweight risk | 01 women20–59, 02 women60+, 03 men20–59, 04 men60+ |
| RUN | Referral to UNEME-EC | 01 |

ADM treatment/control suffixes represent women20–59, women60+, men20–59, men60+. SIS covers reporting facilities, mainly SSA/IMSS-Bienestar, not the entire health system. Use monthly averages for patient-stock indicators and annual sums for test/event counts.

### 4.3 IMSS screening

Columns: delegacion, ano, detecciones, fecha, fn_ano. Trim delegation whitespace. Parse the first four year characters because annotations include `2004*`, `2008 (1)` and `2012 (2)`. Other conditions exist in the catalog; the selected file is diabetes screening.

### 4.4 ISSSTE-specific discharge CSV

Recorded URL: `https://repodatos.atdt.gob.mx/api_update/issste/datos_egresos_hospitalarios/egresos_hospitalarios_issste2024.csv`. Fields: entidad, unidad, clues, edad_anios, sexo, servicio_troncal, tipo_derechohabiente, fecha_ingreso, fecha_egreso, diagnostico_principal_cie10, descripcion_cie_010. Filter principal diagnosis E10–E14. Length of stay is discharge minus admission date. The separate source was unavailable during preparation; use the reported sector source's DH=4 for the included ISSSTE count.

### 4.5 Reported sector discharge database

`http://www.dgis.salud.gob.mx/descargas/datosabiertos/egresos/sectorial_egresos_YEAR.zip`; 2024 archive about 82 MB. Dictionary: sectorial_Descriptores_Base_de_Datos_EGRESOS_2018_2024.xlsx. Source fields, pipe-delimited: ID, DH, CEDOCVE, CLUES, MOTIVO_EGRESO, SEXO, GPO_EDAD, CLAVE_EDAD, EDAD1, DIAS_ESTA, AFECPRIN4, AFECPRIN3, GBDAFECPRIN, ANOCAP, MES, GPODIAS, PRINPRIN. It has no procedure table; use SSA for amputation counts.

| Institution | Diabetes discharges, 2024 | Share of its discharges |
|-------------|--------------------------:|------------------------:|
| IMSS | 46,755 | 1.8% |
| Servicios de Salud IMSS-Bienestar | 42,620 | 2.6% |
| Secretaría de Salud | 15,598 | 1.9% |
| ISSSTE, DH=4 | 6,924 | 2.0% |
| IMSS-Bienestar | 4,417 | 2.6% |
| SEDENA/PEMEX/SEMAR/others | 4,071 | — |
| **Total** | **120,385** | **2.0%** |

All-cause sector discharges: 5,877,537. Diabetes discharge deaths: 5,707 (4.7%). DH1/3/13 sum to 62,635, versus 62,771 in the separate SSA file. The discrepancy is **unreconciled**; do not invent a coverage/cutoff explanation or present them as identical subsets. “Reported sector database” does not guarantee every hospitalization nationally.

The transparency/budget data at data.buengobierno.gob.mx was reviewed as possible financial context, not clinical training data. The selected individual-level training data remains CDC; local ENSANUT was obtained directly from INSP.

## 5. Care-stage context, not a linked cascade

| Stage | Source/field | Grain |
|-------|--------------|-------|
| Screening | IMSS detecciones | Delegation/year |
| New cases | SINAVE E10/E11–E14 | Notifying state/week |
| In treatment | SIS ADM08+09+11+12 | Facility/month |
| Controlled | SIS ADM14+15+17+18, HBA02 | Facility/month |
| Complications | Discharge records/procedures, SIS PDM03 | Admission/facility-month |
| Deaths | EDR CAUSA_DEF E10–E14 | Death record |
| Denominator | CONAPO population | State/year/sex/age |

National 2024 context: 497,987 notified cases; 120,385 sector diabetes discharges; separate SSA file 62,771; 11,550 SSA admissions with amputation (11,759 procedures); 112,577 registered deaths. Different sources/populations/periods mean arrows do not measure losses between stages. The purpose is to describe burden and motivate private inference, not claim a measured intervention effect.

## 6. Harmonizing SINAVE and EDR

| Dimension | SINAVE | EDR / interpretation |
|-----------|--------|----------------------|
| Geography | Notifying unit | ENT_RESID/MUN_RESID residence; disclose distinction |
| Time | Epidemiological year/week | ANIO_OCUR/MES_OCURR/DIA_OCURR; use a consistent week definition |
| Sex | Source men/women codes | SEXO mapping |
| Age | SUIVE age bands | Recode exact EDAD; EDAD_AGRU does not directly supply the 25–44 group |
| Diagnosis | E10, E11–E14, O24.4 | CAUSA_DEF E10–E14, O24 separately |
| Institution | Reporting source | DERECHOHAB affiliation or SITIO_OCUR location; these differ |

EDR also supports education, occupation, marital status, affiliation, Indigenous identity and urban/rural context. CONAPO supplies matching rate denominators. These are aggregate comparisons, not individual joins to CDC.

### 6.1 Reproducible initial counts

2024 registered-death input: **819,672 records**. Diabetes 112,577 (13.7%): E11 85,395; E14 22,537; E10 4,323. Male/female counts 56,131/56,442. Largest residence counts: Estado de México 17,155, Veracruz 10,585, CDMX 8,565, Puebla 7,065; Chihuahua 2,768.

SSA all-cause input: **2,649,236 admissions**, Egresos.txt, pipe-delimited Latin-1. Principal diabetes 62,771 (2.4%); lower-limb amputation 11,550 (18.4%) and 11,759 procedures; hemodialysis ICD-9 39.95 in 1,719 admissions (2.7%); MOTEGRE=5 in 2,976 (4.7%); mean stay 5.1 days. Residence counts: Estado de México 6,697, Veracruz 5,491, Guanajuato 4,215, CDMX 3,891; Chihuahua 1,332. Descriptor: ssa_Descriptores_Bases_de_Datos_EGRESOS_2023_2025.xlsx.

## 7. Pitch figures

ENSANUT 2022: 18.3% total diabetes, 12.6% diagnosed and 5.8% undiagnosed (rounded estimates do not sum exactly). Source: Basto-Abreu et al., Salud Pública de México 2023;65 supplement 1:S163–S168.

Use **112,577 final microdata registered deaths**, not the preliminary INEGI press total 112,641. Of the registered E10–E14 deaths, 109,698 occurred in 2024 before restricting residence; the mart's Mexican-state-resident same-year total is 109,603. Admission/procedure counts above are events, not unique people.

## 8. ENSANUT 2022/2023 acquisition and checks

Selected Mexican individual-level source for an exploratory reduced experiment. [2022 downloads](https://ensanut.insp.mx/encuestas/ensanutcontinua2022/descargas.php), [2023 downloads](https://ensanut.insp.mx/encuestas/ensanutcontinua2023/descargas.php). Original browser forms used POST rather than a stable direct file URL. Modules: residents, household, adults 20+, anthropometry/blood pressure and physical activity, plus XLSX catalogs/PDF questionnaires.

Local-only directories: data/raw/ensanut/2022 and /2023. The acquisition/integrity record remains local. Review INSP redistribution terms before publication.

2022 stems: integrantes_ensanut2022_w, hogar_ensanut2022_w, ensadul2022_entrega_w, ensaantro2022_entrega_w, ensafisica2022_adultos_entrega_w. 2023 stems: integrantes_ensanut2023_w_n, hogar_ensanut2023_w_n, adultos_ensanut2023_w_n, antropometria_hta_4mar24, actividad_fisica_w_adultos. Household/person IDs: FOLIO_I/FOLIO_INT, stored as text. Expansion weight: ponde_f; survey cluster field: upm.

| Recorded acquisition check | 2022 | 2023 |
|----------------------------|-----:|-----:|
| Valid ZIP CRC / CSV bytes match archive | 5/5 | 5/5 |
| Adult rows and unique FOLIO_INT | 11,913 | 6,772 |
| Adults missing a resident join | 0 | 0 |
| Prior diabetes diagnosis a0301=1 | 1,544 | 857 |
| Weighted prior-diagnosis prevalence | 10.9% | 11.0% |
| Represented adults | 85.5 million | 86.0 million |
| Valid BMI and yes/no diagnosis base | 8,628 (13.4% unweighted positive) | 3,089 (13.1%) |

Exact base rule: join adults/anthropometry on FOLIO_INT; use an01_1 weight, falling back to an12_1 if missing or 222.22; use an04_1 height, falling back to an15_1 if missing or 222.2. Exclude 222.22/222.2/999. Require **25<weight<250 kg**, **100<height<220 cm**, a0301 in 1/3. Other exclusion rules can shift a count by one, such as 8,629 for 2022. Further predictor/weight exclusions define the reduced experiment's smaller sample.

The weighted 2022 10.9% matches the reported prior-diagnosis estimate; its unweighted prevalence is 13.0%. Use ponde_f for population estimates. a0301 is reported diagnosis, not laboratory diabetes. These 2022 modules do not supply glucose/HbA1c. Exclude measurement sentinel codes before BMI; filter age using resident records because anthropometry includes minors and an anomalous 869 age. Prediabetes a0301a exists only in 2023. Out-of-pocket fields such as a03061c may inform a future sourced cost study, but no valid E5 unit cost has been established.
