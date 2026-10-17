# ENSANUT exploratory external experiment — optional US-3.5

The original protocol was committed before its results on October 17, 2026. This English translation preserves the experiment's definitions and chronology. It is a separate reduced-model experiment, not clinical validation or validation of the 21-feature MVP.

## Question and model

How well does a reduced CDC-trained logistic model discriminate reported diagnosed diabetes in Mexican adults using approximately comparable ENSANUT variables?

Use the same training-only standardization/folded-weight procedure, C=1 and no class weighting. Train on CDC training data and select the threshold on CDC validation for sensitivity >=0.80. Do not fit weights, calibrators or thresholds on ENSANUT.

Ten predictors: HighBP, HighChol, CholCheck, BMI, Smoker, Stroke, HeartDiseaseorAttack, Sex, Age, Education. Exclude PhysActivity, Fruits, Veggies, HvyAlcoholConsump, AnyHealthcare, NoDocbcCost, GenHlth, MentHlth, PhysHlth, DiffWalk and Income because a direct comparable mapping was not verified. Do not impute them.

ENSANUT Continua 2022/2023 adults age 20+, joined by FOLIO_INT to residents/anthropometry. Report years separately. Local microdata remains under ignored data/raw/ensanut; publish aggregate metrics only.

## Label and feature mapping

`a0301`: clinician-reported diagnosis, 1=yes →1; 3=no →0; 2=pregnancy only →exclude. The CDC source label includes reported prediabetes/diabetes; this target is diagnosed diabetes only.

| CDC feature | ENSANUT source | Fixed mapping |
|-------------|----------------|---------------|
| HighBP | a0401 | 1→1; 2 pregnancy only and 3→0 |
| CholCheck | a0603 | 1→1; 2→0; 9 excluded. CDC uses the last five years; ENSANUT asks ever. |
| HighChol | a0604 | 1→1; 2→0; never checked (a0603=2)→0 |
| BMI | an01_1/an12_1 weight; an04_1/an15_1 height | Reject sentinel/implausible measurements; integer-rounded BMI in 12–98; source rules in DATA_SOURCES.md |
| Smoker | a1301/a1305 | Current or former smoking code 1/2→1; both 3→0; unknown excluded. CDC asks about 100 lifetime cigarettes. |
| Stroke | a0502d | 1→1; 2→0 |
| HeartDiseaseorAttack | a0502a infarction/a0502b angina | Either 1→1; both 2→0 |
| Sex | h0302 | 1 male→1; 2 female→0 |
| Age | h0303 | CDC categories: under 25→1; 25–29→2; … 75–79→12; 80+→13 |
| Education | h0317a | 0/1→1; 2→2; 3/6→3; 4/5/7→4; 8→5; 9–12→6; approximate mapping |

Exclude records with missing, unknown/nonresponse or out-of-range label/predictors and report exclusion counts. Use survey expansion weight `ponde_f`; report weighted primary metrics and unweighted references. Metrics: ROC-AUC, AP, sensitivity/specificity at the CDC threshold, prevalence, mean predicted probability and Brier. Also report the reduced model on the CDC test split.

```bash
make ensanut
```

Requires local microdata; output `artifacts/metrics/ensanut_exploratory_v1.json` contains aggregates only.

## Recorded results

Reduced-model CDC-validation threshold: 0.1171.

| Dataset | Included (positive) | AUC | AP | Sensitivity | Specificity | Prevalence | Mean probability |
|---------|--------------------:|----:|---:|------------:|------------:|-----------:|-----------------:|
| CDC test, unweighted | 38,052 (5,302) | 0.801 | 0.376 | 0.805 | 0.648 | 0.139 | 0.139 |
| ENSANUT 2022, weighted | 8,414 (1,130) | 0.767 | 0.288 | 0.459 | 0.852 | 0.117 | 0.073 |
| ENSANUT 2023, weighted | 3,010 (396) | 0.767 | 0.247 | 0.485 | 0.839 | 0.109 | 0.076 |

Unweighted AUC: 0.764 (2022), 0.739 (2023). Exclusions 2022: 3,186 invalid anthropometry, 295 incomplete health variables, 18 invalid labels; 2023: 3,535 /205 /22 respectively.

Ranking falls from CDC AUC about 0.80 to about 0.77. The reduced model **underestimates risk**: predicted averages 7.3–7.6% versus diagnosed prevalence 10.9–11.7%; sensitivity falls to 0.46–0.49 at the CDC threshold. Mexican deployment would require its own evaluation, recalibration and threshold selection, none of which this experiment performs. Target differences and approximate mapping limit interpretation.
