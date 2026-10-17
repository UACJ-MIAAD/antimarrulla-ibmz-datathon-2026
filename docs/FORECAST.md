# Optional E5: weekly forecasts and budget scenarios

Priority **Plus**. Owners: Yazmin (data/planning), Carlos (modeling), Javier (dashboard). Pause extensions if H12 encrypted flow or H18 demo is at risk. Do not trade required evidence, English release review or submission time for E5.

## Purpose and inputs

Explore the next 52 weeks of newly notified T1/T2 diabetes cases by state and sex. This is a planning experiment, not a demonstrated effect of screening on incident disease. Inputs: `data/sinave/tipo1/products.csv` and `tipo2/products.csv`; 111 weekly series per type, 222 total.

| Geography × men/women/all | Series per type |
|---------------------------|----------------:|
| 32 states | 96 |
| Four SINAVE regions | 12 |
| National | 3 |

Source region IDs centro/norte/occidente/sureste and original source column names remain exact. The UI displays English labels. State/region/national and sex aggregates are not independent series.

Last observation: week of July 27, 2026. At the fixed October 17 reference, eleven bridge/nowcast weeks precede 52 published forecast weeks (October 19, 2026 through October 11, 2027), totaling **63 steps** after the last observation.

## Original design and implemented scope

The original candidate plan included seasonal naive, ETS, SARIMA and Prophet if available, a map, T1+T2 totals and LinuxONE training. **Implemented:** seasonal naive and damped additive Holt-Winters ETS, charts, filters, quarterly totals, evaluation and sourced-cost scenarios. SARIMA, Prophet, map, combined T1+T2 and LinuxONE forecasting execution remain unimplemented. Existing fitting/results were local.

## Forecasting pipeline

1. Fit from 2022 onward; exclude COVID 2020–2021. Count linearly interpolated missing weeks.
2. Compare seasonal naive (repeat the previous 52 weeks) with ETS, period 52, damped additive trend and additive seasonality.
3. Per-series selection: up to four 52-week origins, thirteen weeks apart, each with >=104 prior fitting weeks. Minimize h1–52 SMAPE; within 5% relative SMAPE, break ties with MAE. Selection error is not independent evaluation.
4. Estimate exploratory 80/95 bands from selection errors by h1–13, h14–26 and h27–52 segments; h>52 uses the last segment.
5. Below five observed cases in 52 weeks, use the state's historical regional share against the regional forecast. No existing series needed this fallback.
6. Reconcile proportionally top-down by type and sex: national → region → state. Do not force the all-sex series to equal men+women.
7. Clip negative predictions and round published counts to integers. Rounding can produce small aggregation differences.

## Separate nested evaluation

At two outer origins (February 17 and May 19, 2025), run the complete selection/bands/fallback/reconciliation pipeline using only pre-origin observations and compare with the next 63 actual weeks. Report horizon-segment SMAPE, actual coverage and relative band width. A thirteen-week backtest cannot alone establish a 52-week horizon.

| Level | SMAPE h1–13 | h14–26 | h27–52 | h53–63 | h12–63 | Actual 80% coverage, h12–63 | Actual 95% coverage |
|-------|------------:|-------:|-------:|-------:|-------:|----------------------------:|--------------------:|
| National | 14.6% | 13.7% | 12.9% | 13.3% | 13.1% | 64% | 87% |
| Region | 23.2% | 23.7% | 25.6% | 26.4% | 25.0% | 65% | 81% |
| State | 59.0% | 58.1% | 60.0% | 61.3% | 59.7% | 63% | 79% |

These average all types/sexes/series and origins at each level, not each individual series. For example, T2 all-sex 80% coverage is 52.9% nationally and 55.8% at state level; state SMAPE is 21.7%. Sparse T1 series contribute large errors. Two outer origins provide limited evidence.

The bands are **too narrow relative to nominal coverage**: nominal 80% covers about 63–65%, nominal 95% about 79–87%. Keep them labeled exploratory. Do not substitute model-selection SMAPE for this out-of-sample evaluation.

## Budget and dashboard

`budget = forecast_cases * sourced_unit_cost`. The cost is editable, must have a literature/official tariff source and must be shown with that source. No documented cost means no budget result.

Base = point forecast. Conservative/stress scenarios sum weekly marginal 80/95 upper bounds; **they are not joint confidence intervals for the annual total**. Show quarterly and 52-week case/cost totals by geography and sex.

Implemented controls: T1/T2, national/region/state, men/women/all, cost and required source. Chart: last 104 observed weeks plus forecast/bridge period and exploratory bands. Evaluation table shows independent error and actual coverage; model-selection details are separate. No forecast map or combined type total is implemented.

```bash
make forecast
```

Code: `src/screening/forecast.py`. Artifact: `artifacts/forecast/e5_forecast_v1.json`; website copy: `site/assets/forecast.json`; dashboard: `site/forecast.html`. The English migration preserves numerical forecasts and converts authored keys/labels. Running a new forecast records a new output rather than modifying historical evidence.

Recorded selections: 148 ETS, 74 seasonal naive. National 52-week points: T2 all-sex 574,746 cases versus 555,474 in the last observed 52 weeks; T1 all-sex 3,834 versus 3,857. These are **notified cases**, not all underlying cases.

Ideas about horizons/SMAPE/regional fallback may come from prior team research; solution code must follow the event rules. Prepared SINAVE data and its earlier chronology remain disclosed.
