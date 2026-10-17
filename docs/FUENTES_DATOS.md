# 📊 Fuentes de datos

Tres fuentes, tres roles: el **CDC** entrena el modelo; **SINAVE** y **EDR** dan el contexto mexicano de incidencia y mortalidad para el pitch y el impacto.

> Ningún dataset se sube al repo. Cómo descargarlos: [data/README.md](../data/README.md).

---

## 1. CDC Diabetes Health Indicators (entrenamiento)

| Campo | Valor |
|-------|-------|
| Fuente | UCI Machine Learning Repository, ID 891 · CDC BRFSS 2015 |
| Link | https://archive.ics.uci.edu/dataset/891/cdc+diabetes+health+indicators |
| Tamaño | 253,680 registros · 21 indicadores |
| Variable objetivo | `Diabetes_binary` (0 = sin diabetes; 1 = prediabetes o diabetes) · 13.9% positivos |
| Ejemplos de indicadores | IMC, presión alta, colesterol alto, actividad física, tabaquismo, edad, sexo, ingreso, acceso a servicios de salud |
| Acceso | `pip install ucimlrepo` → `fetch_ucirepo(id=891)` |
| Licencia | CC BY 4.0 |

## 2. Estadísticas de Defunciones Registradas, EDR (mortalidad · INEGI)

Base anual de registros individuales de defunción, generada a partir del certificado de defunción (Registro Civil y Servicios Médicos Forenses). La causa básica se codifica con CIE-10. La diabetes mellitus es consistentemente una de las dos principales causas de muerte del país.

| Campo | Valor |
|-------|-------|
| Programa | https://www.inegi.org.mx/programas/edr/ (secciones *Microdatos* y *Datos abiertos*) |
| Microdatos (DBF) por año | `https://www.inegi.org.mx/contenidos/programas/edr/microdatos/defunciones/{2020…2024}/defunciones_base_datos_{año}_dbf.zip` |
| Microdatos históricos | `…/microdatos/defunciones/datos/defunciones_generales_base_datos_{1990_1994 … 2015_2019}_dbf.zip` |
| Datos abiertos (CSV) | `…/edr/datosabiertos/conjunto_de_datos_defunciones_registradas_2022_csv.zip` |
| Diccionario 2024 | https://www.inegi.org.mx/rnm/index.php/catalog/1140/data-dictionary |
| Nota de microdatos | https://www.inegi.org.mx/contenidos/programas/edr/microdatos/defunciones_registradas_notas_microdatos.pdf |
| Licencia | Términos de libre uso de la información del INEGI (citar la fuente) |

> ⚠️ INEGI bloquea descargas por script (`curl` recibe HTML). Descargar desde el navegador. Para leer DBF en Python: `dbfread` o `geopandas`/`pyogrio`.

### Variables de `DEFUN24` (74 en total)

| Bloque | Variables |
|--------|-----------|
| Causa | `CAUSA_DEF` (CIE-10 detallada: **E10–E14** diabetes, **O24** diabetes en el embarazo), `LISTA_MEX`, `GR_LISMEX`, `CAPITULO`, `GRUPO`, `LISTA1`, `COD_ADICIO` |
| Persona | `SEXO`, `EDAD`, `EDAD_AGRU`, `ESCOLARIDA`, `OCUPACION`, `COND_ACT`, `EDO_CIVIL`, `CONINDIG`, `LENGUA`, `CVE_LENGUA`, `AFROMEX`, `NACIONALID`, `NACESP_CVE`, `ENT_NAC` |
| Salud | `DERECHOHAB`, `ASIST_MEDI`, `SITIO_OCUR`, `NECROPSIA`, `USONECROPS`, `COND_CERT`, `CIRUGIA`, `ENCEFALICA`, `DONADOR` |
| Lugar | `ENT_/MUN_/LOC_/TLOC_` × `RESID` (residencia), `OCURR` (ocurrencia), `REGIS` (registro); `ENT_/MUN_/LOC_OCULES` (lesión); `AREA_UR`; `DIS_RE_OAX` |
| Fechas | `DIA_/MES_/ANIO_` × `OCUR(R)`, `REGIS`, `NACIM`, `CERT`; `HORAS`, `MINUTOS` |
| Violencia y maternas | `TIPO_DEFUN`, `NATVIOLE`, `LUGAR_OCUR`, `OCURR_TRAB`, `PAR_AGRE`, `VIO_FAMI`, `EMBARAZO`, `REL_EMBA`, `COMPLICARO`, `MATERNAS`, `RAZON_M` |
| Perinatales | `SEM_GEST`, `GRAMOS` |

### Catálogos clave

| Variable | Códigos |
|----------|---------|
| `SEXO` | 1 Hombre · 2 Mujer · 9 No especificado |
| `ESCOLARIDA` | 1 Sin escolaridad · 2 Preescolar · 3 Primaria incompleta · 4 Primaria completa · 5 Secundaria incompleta · 6 Secundaria completa · 7 Bachillerato incompleto · 8 Bachillerato completo · 9 Profesional · 10 Posgrado · 88 No aplica (<3 años) · 99 No especificada |
| `EDO_CIVIL` | 1 Soltero · 2 Divorciado · 3 Viudo · 4 Unión libre · 5 Casado · 6 Separado · 8 No aplica (<12 años) · 9 No especificado |
| `DERECHOHAB` | 1 Ninguna · 2 IMSS · 3 ISSSTE · 4 PEMEX · 5 SEDENA · 6 SEMAR · 7 Equivalente a Seguro Popular · 8 Otra · 9 IMSS-Bienestar · 10 ISSFAM · 12 OPD IMSS-Bienestar · 99 No especificada |
| `SITIO_OCUR` | 1 SSA · 2 IMSS-Bienestar · 3 IMSS · 4 ISSSTE · 5 PEMEX · 6 SEDENA · 7 SEMAR · 8 Otra pública · 9 Privada · 10 Vía pública · 11 Hogar · 12 Otro · 13 OPD IMSS-Bienestar · 99 No especificado |
| `ASIST_MEDI` | 1 Con asistencia · 2 Sin asistencia · 9 No especificado |
| `AREA_UR` | 1 Urbana (≥2,500 hab.) · 2 Rural · 9 No especificada |
| `COND_ACT` | 1 Sí trabajó · 2 No trabajó · 8 No aplica (<5 años) · 9 No especificado |
| `TIPO_DEFUN` | 4 Enfermedad (muerte natural); 1–3 y 5 accidentes y violencias |

> `EDAD` no trae catálogo en el diccionario. Convención INEGI (verificar en el descriptor del año): el primer dígito indica la unidad (4xxx = años).

## 3. SINAVE · incidencia (vigilancia convencional SUIVE-1)

Notificación **semanal y agregada** de casos nuevos por unidad médica. No es base individual.

| Campo | Valor |
|-------|-------|
| Formato | SUIVE-1 · Informe semanal de casos nuevos de enfermedades |
| Manual | https://epidemiologia.salud.gob.mx/gobmx/salud/documentos/manuales/32_ManualSuive.pdf |
| Publicación anual | Anuarios de Morbilidad 1984–2025: https://www.gob.mx/salud/acciones-y-programas/anuarios-de-morbilidad-1984-a-2025 (tablas PDF por entidad, institución, enfermedad, edad y mes) |
| Semanal | Boletín Epidemiológico: https://www.gob.mx/salud/acciones-y-programas/direccion-general-de-epidemiologia-boletin-epidemiologico |

### Variables del SUIVE-1

| Bloque | Variables |
|--------|-----------|
| Unidad notificante | CLUES · municipio (clave INEGI) · jurisdicción sanitaria · entidad (clave INEGI) · institución |
| Tiempo | Semana epidemiológica · fecha de inicio · fecha de término |
| Diagnóstico | **E10** Diabetes tipo 1 · **E11–E14** Diabetes tipo 2 · **O24.4** Diabetes en el embarazo |
| Casos nuevos por sexo y grupo de edad | <1 · 1-4 · 5-9 · 10-14 · 15-19 · 20-24 · **25-44** · 45-49 · 50-59 · 60-64 · 65+ · Ign. |
| Derivadas (anuario) | Tasa de incidencia por 100,000 habitantes · fuente de notificación · principales causas |

## 4. Cómo cruzar SINAVE (incidencia) con EDR (mortalidad)

| Llave | SINAVE | EDR | Nota |
|-------|--------|-----|------|
| Entidad / municipio | Clave INEGI de la unidad notificante | `ENT_RESID`, `MUN_RESID` | ⚠️ SINAVE ubica por **unidad**; EDR por **residencia**. Para tasas, usar residencia |
| Tiempo | Semana epidemiológica | `ANIO_OCUR`, `MES_OCURR`, `DIA_OCURR` | Convertir la fecha de defunción a semana epidemiológica |
| Sexo | Hombre / mujer | `SEXO` | Directo |
| Edad | 12 grupos SUIVE | `EDAD` | Recodificar `EDAD` a grupos SUIVE; `EDAD_AGRU` es quinquenal y no tiene 25-44 |
| Diagnóstico | E10, E11–E14, O24.4 | `CAUSA_DEF` | Filtrar `CAUSA_DEF` por E10–E14 y O24 |
| Institución | Fuente de notificación | `DERECHOHAB` o `SITIO_OCUR` | Elegir una; no son equivalentes |

**Lo que solo da la EDR:** escolaridad, ocupación, estado civil, afiliación, autoadscripción indígena y área urbana o rural. Sirve para hablar de **determinantes sociales** de la mortalidad por diabetes, que la incidencia del SINAVE no permite.

**Denominadores para tasas:** proyecciones de población de CONAPO por entidad, sexo y edad.

## 5. Cifras de contexto usadas en el pitch

| Cifra | Fuente |
|-------|--------|
| 18.3% de adultos con diabetes; 12.6% diagnosticada y 5.8% sin diagnóstico | ENSANUT 2022, Basto-Abreu et al., *Salud Pública de México* 2023;65(supl 1):S163-S168 |
| 112,641 defunciones por diabetes en 2024; 2.ª causa de muerte | INEGI, EDR 2024 (preliminar) |
