# 🇲🇽 ENSANUT · evaluación externa exploratoria (extra, US-3.5)

> **Protocolo fijado antes de evaluar** (17 oct 2026). Este archivo se publica en un commit anterior al que trae los resultados. Es un **experimento aparte**: no valida el modelo del MVP ni es validación clínica.

## Pregunta

¿Cuánto discrimina, en adultos mexicanos, un modelo logístico **reducido** entrenado en el CDC solo con las variables que ENSANUT mide de forma comparable?

## Modelo evaluado

- **Modelo reducido**, distinto del MVP: regresión logística con el mismo procedimiento que `src/tamizaje/entrenar.py` (estandarización ajustada en entrenamiento y plegada en los pesos, `C = 1`, sin `class_weight`), entrenada en la **partición de entrenamiento del CDC** y con umbral fijado en la **validación del CDC** (sensibilidad ≥ 0.80 con la mayor especificidad).
- **Predictores (10):** `HighBP`, `HighChol`, `CholCheck`, `BMI`, `Smoker`, `Stroke`, `HeartDiseaseorAttack`, `Sex`, `Age`, `Education`.
- Fuera por no tener equivalente directo verificado: `PhysActivity` (solo en un submódulo), `Fruits`, `Veggies`, `HvyAlcoholConsump`, `AnyHealthcare`, `NoDocbcCost`, `GenHlth`, `MentHlth`, `PhysHlth`, `DiffWalk`, `Income`. No se imputan.

## Datos

ENSANUT Continua 2022 y 2023 (INSP), módulo de adultos (20 años o más), unido por `FOLIO_INT` con residentes y antropometría. Se reporta cada año por separado. Los microdatos no salen de `data/raw/ensanut/` (no se versionan); solo se publican métricas agregadas.

## Etiqueta

`a0301` (¿algún médico le ha dicho que tiene diabetes?): 1 = sí → 1; 3 = no → 0; 2 = solo durante el embarazo → **excluido**. Diferencia conocida: la etiqueta del CDC es prediabetes **o** diabetes declarada; la de ENSANUT es solo diabetes diagnosticada.

## Mapeo de variables

| CDC | ENSANUT | Regla |
|-----|---------|-------|
| `HighBP` | `a0401` | 1 → 1; 2 (solo en el embarazo) y 3 → 0 |
| `CholCheck` | `a0603` | 1 → 1; 2 → 0; 9 → excluido. Diferencia: CDC pregunta por los últimos 5 años; ENSANUT, alguna vez |
| `HighChol` | `a0604` | 1 → 1; 2 → 0; si `a0603` = 2 (nunca medido) → 0 |
| `BMI` | `an01_1`/`an12_1` (peso), `an04_1`/`an15_1` (talla) | Regla de [FUENTES_DATOS.md §8](FUENTES_DATOS.md#8-ensanut-2022-y-2023-insp--evaluación-externa-exploratoria-con-población-mexicana); IMC redondeado al entero; dentro de 12–98 |
| `Smoker` | `a1301`, `a1305` | fuma hoy (1 o 2) o fumó antes (1 o 2) → 1; nunca (3 y 3) → 0; 9 → excluido. Diferencia: CDC pregunta por 100 cigarros en la vida |
| `Stroke` | `a0502d` | 1 → 1; 2 → 0 |
| `HeartDiseaseorAttack` | `a0502a` (infarto), `a0502b` (angina) | alguno = 1 → 1; ambos = 2 → 0 |
| `Sex` | `h0302` | 1 hombre → 1; 2 mujer → 0 |
| `Age` | `h0303` | grupos del CDC: <25 → 1; 25–29 → 2; … 75–79 → 12; 80+ → 13 |
| `Education` | `h0317a` | 0–1 → 1; 2 → 2; 3 y 6 → 3; 4, 5 y 7 → 4; 8 → 5; 9–12 → 6 (aproximado) |

## Exclusiones

Se excluye a quien tenga la etiqueta o cualquier predictor ausente, con código "no sabe / no responde" o fuera de rango. Se reporta cuántos quedan en cada paso.

## Ponderadores y métricas

- Ponderador de expansión `ponde_f`; métricas **ponderadas** (principales) y sin ponderar.
- ROC-AUC, average precision, sensibilidad y especificidad en el umbral del CDC, prevalencia, probabilidad media predicha (calibración en promedio) y Brier.
- Como referencia, las mismas métricas del modelo reducido en la **prueba del CDC**.
- No se ajusta nada con ENSANUT: ni pesos ni umbral.

## Cómo se corre

```bash
make ensanut    # requiere los microdatos locales en data/raw/ensanut/
```

Resultado: `artefactos/metricas/ensanut_exploratorio_v1.json` (solo agregados).

## Resultados (17 oct 2026, corrida después de publicar este protocolo)

Archivo: `artefactos/metricas/ensanut_exploratorio_v1.json`. Umbral del modelo reducido fijado en la validación del CDC: 0.1171.

| Conjunto | Incluidos (positivos) | ROC-AUC | Average precision | Sensibilidad | Especificidad | Prevalencia | p media |
|----------|----------------------:|--------:|------------------:|-------------:|--------------:|------------:|--------:|
| CDC prueba (referencia, sin ponderar) | 38,052 (5,302) | 0.801 | 0.376 | 0.805 | 0.648 | 0.139 | 0.139 |
| ENSANUT 2022, ponderado | 8,414 (1,130) | 0.767 | 0.288 | 0.459 | 0.852 | 0.117 | 0.073 |
| ENSANUT 2023, ponderado | 3,010 (396) | 0.767 | 0.247 | 0.485 | 0.839 | 0.109 | 0.076 |

Sin ponderar: ROC-AUC 0.764 (2022) y 0.739 (2023). Exclusiones 2022: 3,186 sin antropometría válida, 295 con datos de salud incompletos, 18 con etiqueta fuera de la regla; 2023: 3,535, 205 y 22.

**Lectura honesta:**
- El ranking se sostiene a medias: el ROC-AUC baja de 0.80 en el CDC a 0.77 en adultos mexicanos.
- **El modelo subestima el riesgo en México:** predice 7.3–7.6% en promedio frente a 10.9–11.7% de diagnóstico declarado, y con el umbral del CDC la sensibilidad cae a 0.46–0.49. Usarlo en México exigiría recalibrar y fijar el umbral con datos mexicanos, lo que este experimento **no** hace.
- La etiqueta de ENSANUT (solo diabetes diagnosticada) y la del CDC (prediabetes o diabetes) no son iguales, y el mapeo de variables es aproximado.
