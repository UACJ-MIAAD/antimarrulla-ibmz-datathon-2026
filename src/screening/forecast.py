"""Optional E5 weekly diabetes T1/T2 forecasting and budget scenarios.
Use 222 series (111 per type), fitting complete weekly observations from 2022 onward. Reject missing/non-finite values
until fold-local imputation is implemented; global interpolation could leak future values.
Publish 11 bridge weeks plus 52 forecast weeks: 63 steps after the last July 27, 2026 observation.
Select seasonal naive versus damped additive ETS using rolling origins, >=104 training weeks,
up to four 52-week validation origins, SMAPE then MAE for a 5% tie. Derive exploratory
80/95 bands from horizon-segment errors. Use regional fallback below five annual cases,
and reconcile national → region → state totals proportionally.
Evaluate the complete pipeline on separate outer origins using only past data; report actual
out-of-sample SMAPE, band coverage and width. Marginal upper-bound sums are scenarios,
not joint intervals. Budget requires a sourced cost; never invent one.
Run: python -m screening.forecast [--today 2026-10-17] [--cost-mxn N --source-cost URL]
"""
import argparse, csv, datetime, json, os, warnings
import numpy as np
from .paths import ARTIFACTS, ROOT

FIT_START = "2022-01-01"
S = 52
SEGMENTS = [(1, 13), (14, 26), (27, 52)]
EVALUATION_SEGMENTS = [(1, 13), (14, 26), (27, 52), (53, 63), (12, 63)]
PUBLISHED_HORIZON = 63
OUTPUT = os.path.join(ARTIFACTS, "forecast", "e5_forecast_v1.json")
FIELDS = ("f", "lo95", "lo80", "hi80", "hi95")


def load():
    series = {}
    for kind in ("tipo1", "tipo2"):
        with open(os.path.join(ROOT, "data", "sinave", kind, "products.csv"), newline="") as f:
            for r in csv.DictReader(f):
                k = (r["disease_id"], {"estado": "state", "nacional": "national"}.get(r["geography_level"], r["geography_level"]), r["geography_id"], {"general": "all", "hombres": "men", "mujeres": "women"}.get(r["sex"], r["sex"]))
                series.setdefault(k, []).append((r["ds"], float(r["y_cases"]) if r["observed"] == "True" else np.nan))
    for k in series:
        series[k].sort()
    return series


def prepare_observations(y):
    "Reject gaps before splitting: global interpolation can leak future holdout values."
    y = np.array(y, dtype=float)
    if not np.all(np.isfinite(y)):
        raise ValueError("complete finite weekly observations required; missing weeks need fold-local imputation")
    return y, 0


def snaive(y, h):
    last = y[-S:]
    return np.array([last[i % S] for i in range(h)])


def ets(y, h):
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = ExponentialSmoothing(y, trend="add", damped_trend=True, seasonal="add", seasonal_periods=S,
                                 initialization_method="estimated").fit()
    f = np.asarray(m.forecast(h))
    if not np.all(np.isfinite(f)):
        raise ValueError("non-finite ETS forecast")
    return np.clip(f, 0, None)


MODELS = {"naive_seasonal": snaive, "ets": ets}


def smape(a, f):
    d = np.abs(a) + np.abs(f)
    return float(np.mean(np.where(d == 0, 0.0, 2 * np.abs(a - f) / np.where(d == 0, 1, d)))) * 100


def selection(y):
    "Selection backtest: up to four 52-week origins, each with at least 104 training weeks."
    n = len(y)
    origins = [n - S - 13 * k for k in range(4) if n - S - 13 * k >= 2 * S]
    if not origins:
        raise ValueError("series is too short for model selection")
    result = {m: {"err": [], "smape": [], "mae": []} for m in MODELS}
    for o in origins:
        tr, te = y[:o], y[o:o + S]
        for name, fn in MODELS.items():
            try:
                f = fn(tr, S)
            except Exception:
                f = snaive(tr, S)
            result[name]["err"].append(te - f)
            result[name]["smape"].append([smape(te[a - 1:b], f[a - 1:b]) for a, b in SEGMENTS] + [smape(te, f)])
            result[name]["mae"].append(float(np.mean(np.abs(te - f))))
    out = {}
    for name, r in result.items():
        sm = np.mean(np.array(r["smape"]), axis=0)
        out[name] = {"smape_by_segment": {f"h{a}-{b}": round(float(v), 2) for (a, b), v in zip(SEGMENTS, sm[:3])},
                       "smape_1_52": round(float(sm[3]), 2), "mae": round(float(np.mean(r["mae"])), 3),
                       "origins": len(origins), "errors": np.array(r["err"])}
    return out


def choose(bt):
    a, b = bt["ets"], bt["naive_seasonal"]
    if abs(a["smape_1_52"] - b["smape_1_52"]) <= 0.05 * max(a["smape_1_52"], b["smape_1_52"], 1e-9):
        return "ets" if a["mae"] <= b["mae"] else "naive_seasonal"
    return "ets" if a["smape_1_52"] < b["smape_1_52"] else "naive_seasonal"


def bands(errors, h_total):
    "Empirical error quantiles by horizon segment; horizons beyond 52 use the last segment."
    q = {(a, b): np.quantile(errors[:, a - 1:b].ravel(), [0.025, 0.10, 0.90, 0.975]) for a, b in SEGMENTS}
    return np.array([q[next(((a, b) for a, b in SEGMENTS if a <= h <= b), SEGMENTS[-1])] for h in range(1, h_total + 1)])


def system(ys, h_total, region_of):
    "Run the full pipeline on the supplied series only, without future observations."
    raw = {}
    for k, y in ys.items():
        bt = selection(y)
        model = choose(bt)
        try:
            f = MODELS[model](y, h_total)
        except Exception:
            model, f = "naive_seasonal", snaive(y, h_total)
        b = bands(bt[model]["errors"], h_total)
        raw[k] = {"y": y, "model": model, "f": f,
                    "lo95": np.clip(f + b[:, 0], 0, None), "lo80": np.clip(f + b[:, 1], 0, None),
                    "hi80": np.clip(f + b[:, 2], 0, None), "hi95": np.clip(f + b[:, 3], 0, None),
                    "selection": {m: {kk: vv for kk, vv in r.items() if kk != "errors"} for m, r in bt.items()},
                    "cases_52": float(y[-S:].sum())}
    for k, c in raw.items():  # Regional fallback
        if k[1] == "state" and c["cases_52"] < 5:
            reg = raw[(k[0], "region", region_of[k[2]], k[3])]
            siblings = [kk for kk in raw if kk[0] == k[0] and kk[1] == "state" and kk[3] == k[3] and region_of[kk[2]] == region_of[k[2]]]
            tot = sum(raw[kk]["y"][-2 * S:].sum() for kk in siblings)
            prop = c["y"][-2 * S:].sum() / tot if tot else 0.0
            for field in FIELDS:
                c[field] = reg[field] * prop
            c["model"] = f"regional_fallback ({prop:.4f} of its region)"
    for kind in {k[0] for k in raw}:  # Top-down reconciliation
        for sex in {k[3] for k in raw if k[0] == kind}:
            national = raw[(kind, "national", "mx", sex)]
            for field in FIELDS:
                national[field + "_rec"] = national[field]
            regions = [k for k in raw if k[0] == kind and k[1] == "region" and k[3] == sex]
            region_sum = sum(raw[k]["f"] for k in regions)
            fac_r = np.divide(national["f"], region_sum, out=np.ones_like(region_sum), where=region_sum > 0)
            for kr in regions:
                rc = raw[kr]
                for field in FIELDS:
                    rc[field + "_rec"] = rc[field] * fac_r
                states = [k for k in raw if k[0] == kind and k[1] == "state" and k[3] == sex and region_of[k[2]] == kr[2]]
                state_sum = sum(raw[k]["f"] for k in states)
                fac_and = np.divide(rc["f_rec"], state_sum, out=np.ones_like(state_sum), where=state_sum > 0)
                for ke in states:
                    for field in FIELDS:
                        raw[ke][field + "_rec"] = raw[ke][field] * fac_and
    return raw


def evaluate(ys, region_of, h=PUBLISHED_HORIZON):
    "Nested evaluation of the reconciled pipeline through h steps using separate evaluation origins."
    n = len(next(iter(ys.values())))
    origins = [o for o in (n - h - 13 * k for k in range(4)) if o - S >= 2 * S]
    rows, forecasts = [], {}
    for o in origins:
        c = system({k: y[:o] for k, y in ys.items()}, h, region_of)
        forecasts[o] = {k: v["f_rec"] for k, v in c.items()}
        for k, y in ys.items():
            current, v = y[o:o + h], c[k]
            rows.append({"key": k, "source": o, "current": current, "f": v["f_rec"], "lo80": v["lo80_rec"], "hi80": v["hi80_rec"],
                          "lo95": v["lo95_rec"], "hi95": v["hi95_rec"]})
    summary = {}
    for level in ("national", "region", "state"):
        sel = [r for r in rows if r["key"][1] == level]
        if not sel:
            continue
        summary[level] = {}
        for a, b in EVALUATION_SEGMENTS:
            sl = slice(a - 1, b)
            sm = [smape(r["current"][sl], r["f"][sl]) for r in sel]
            cob80 = np.mean(np.concatenate([(r["current"][sl] >= r["lo80"][sl]) & (r["current"][sl] <= r["hi80"][sl]) for r in sel]))
            cob95 = np.mean(np.concatenate([(r["current"][sl] >= r["lo95"][sl]) & (r["current"][sl] <= r["hi95"][sl]) for r in sel]))
            width80 = np.mean(np.concatenate([(r["hi80"][sl] - r["lo80"][sl]) / np.maximum(np.mean(r["current"][sl]), 1) for r in sel]))
            summary[level][f"h{a}-{b}"] = {"smape": round(float(np.mean(sm)), 2), "coverage_80": round(float(cob80), 3),
                                           "coverage_95": round(float(cob95), 3), "relative_width_80": round(float(width80), 3)}
    by_series = {}
    for r in rows:
        d = by_series.setdefault(r["key"], {f"h{a}-{b}": [] for a, b in EVALUATION_SEGMENTS})
        for a, b in EVALUATION_SEGMENTS:
            d[f"h{a}-{b}"].append(smape(r["current"][a - 1:b], r["f"][a - 1:b]))
    by_series = {k: {t: round(float(np.mean(v)), 2) for t, v in d.items()} for k, d in by_series.items()}
    return {"origins": origins, "horizon": h, "by_level": summary, "by_series": by_series, "forecasts": forecasts}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", default="2026-10-17", help="fixed reference date for reproducibility")
    ap.add_argument("--cost-mxn", type=float, default=None)
    ap.add_argument("--source-cost", default=None)
    a = ap.parse_args()
    if (a.cost_mxn is None) != (a.source_cost is None):
        raise SystemExit("a unit cost requires its source (--source-cost)")

    if a.cost_mxn is not None and (not np.isfinite(a.cost_mxn) or a.cost_mxn <= 0 or not a.source_cost.strip()):
        raise SystemExit("unit cost must be positive and finite, with a nonblank source")

    series = load()
    region_of = {r["cve_ent"]: r["region_sinave"] for r in csv.DictReader(open(os.path.join(ROOT, "data", "catalogos", "entidades.csv"), encoding="utf-8"))}
    last = max(d for v in series.values() for d, _ in v)
    monday_ref = datetime.date.fromisoformat(a.today) - datetime.timedelta(days=datetime.date.fromisoformat(a.today).weekday())
    nowcast = (monday_ref - datetime.date.fromisoformat(last)).days // 7
    h_total = nowcast + S
    dates = [(datetime.date.fromisoformat(last) + datetime.timedelta(weeks=i)).isoformat() for i in range(1, h_total + 1)]

    ys, dates_hist, missing = {}, {}, {}
    for k, v in series.items():
        v = [(d, y) for d, y in v if d >= FIT_START]
        if any(datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a) != datetime.timedelta(weeks=1)
               for (a, _), (b, _) in zip(v, v[1:])):
            raise ValueError(f"nonweekly or missing calendar rows in series {k}")
        ys[k], missing[k] = prepare_observations([y for _, y in v])
        dates_hist[k] = [d for d, _ in v]

    raw = system(ys, h_total, region_of)
    ev = evaluate(ys, region_of, h=h_total)

    ini = nowcast
    output = {"version": "e5-forecast-v2", "reference_date": a.today, "last_observation": last, "weeks_nowcast": nowcast,
              "steps_since_last_observation": h_total,
              "horizon": {"from": dates[ini], "through": dates[-1], "weeks": S}, "fit_start": FIT_START,
              "unit_cost_mxn": a.cost_mxn, "source_cost": a.source_cost,
              "nested_evaluation": {"origins": [dates_hist[next(iter(ys))][o] for o in ev["origins"]], "horizon_steps": ev["horizon"],
                                     "by_level": ev["by_level"],
                                     "note": "The complete selection/bands/fallback/reconciliation pipeline uses only observations before each origin and is evaluated on subsequent actual weeks. Few origins limit the evidence."},
              "warnings": ["80/95 bands are exploratory: actual out-of-sample coverage is reported in nested evaluation; nominal coverage is not guaranteed.",
                               "Bands are marginal by series/week. Conservative and stress scenarios sum weekly upper bounds; they are not joint total intervals.",
                               "SINAVE-notified cases, not all underlying cases."],
              "series": []}
    summary_models = {}
    for k, c in sorted(raw.items()):
        r = lambda v: [int(round(max(x, 0))) for x in v]
        f52 = c["f_rec"][ini:]
        series = {"kind": k[0], "level": k[1], "id": k[2], "sex": k[3], "model": c["model"], "interpolated_weeks": missing[k],
                 "selection": c["selection"], "evaluation_smape": ev["by_series"][k],
                 "history": {"dates": dates_hist[k][-2 * S:], "cases": r(c["y"][-2 * S:])},
                 "forecast": {"dates": dates, "point": r(c["f_rec"]), "lo80": r(c["lo80_rec"]), "hi80": r(c["hi80_rec"]),
                                "lo95": r(c["lo95_rec"]), "hi95": r(c["hi95_rec"])},
                 "total_52": {"point": int(round(f52.sum())), "conservative_scenario_total_hi80": int(round(c["hi80_rec"][ini:].sum())),
                              "stress_scenario_total_hi95": int(round(c["hi95_rec"][ini:].sum()))}}
        if a.cost_mxn is not None:
            series["budget_52_mxn"] = {kk: round(v * a.cost_mxn, 2) for kk, v in series["total_52"].items()}
        summary_models[c["model"].split(" ")[0]] = summary_models.get(c["model"].split(" ")[0], 0) + 1
        output["series"].append(series)
    output["models_selected"] = summary_models
    output["names"] = {r["cve_ent"]: r["nombre_corto"] for r in csv.DictReader(open(os.path.join(ROOT, "data", "catalogos", "entidades.csv"), encoding="utf-8"))}
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as fo:
        json.dump(output, fo, ensure_ascii=False, separators=(",", ":"))
    for t in ("diabetes_t1", "diabetes_t2"):
        n_ = next(s for s in output["series"] if s["kind"] == t and s["level"] == "national" and s["sex"] == "all")
        print(f"{t} national all · {n_['model']} · evaluation h1-63 {n_['evaluation_smape']} · total 52 weeks {n_['total_52']}")
    print("selected models:", summary_models, "· steps", h_total, "· evaluation origins", output["nested_evaluation"]["origins"])
    print(json.dumps(output["nested_evaluation"]["by_level"], ensure_ascii=False))


if __name__ == "__main__":
    main()
