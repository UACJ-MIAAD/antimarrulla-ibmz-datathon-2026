"""Exploratory external experiment on ENSANUT 2022/2023 (optional US-3.5).
Follow the protocol committed before evaluation in docs/ENSANUT_EXPERIMENT.md.
This REDUCED ten-feature model differs from the MVP. Read untracked local microdata
under data/raw/ensanut/ and export aggregate metrics only.
Run: python -m screening.ensanut
"""
import csv, datetime, json, os
import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score
from . import data, train, schema
from .paths import ARTIFACTS, SPLITS, ROOT

PREDICTORS = ["HighBP", "HighChol", "CholCheck", "BMI", "Smoker", "Stroke", "HeartDiseaseorAttack", "Sex", "Age", "Education"]
FILES = {
    2022: ("ensadul2022_entrega_w.csv", "integrantes_ensanut2022_w.csv", "ensaantro2022_entrega_w.csv"),
    2023: ("adultos_ensanut2023_w_n.csv", "integrantes_ensanut2023_w_n.csv", "antropometria_hta_4mar24.csv"),
}
SENTINELS = {"222.22", "222.2", "999", "999.9", "999.99"}
OUTPUT = os.path.join(ARTIFACTS, "metrics", "ensanut_exploratory_v1.json")


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        rd = csv.DictReader(f)
        return {r["FOLIO_INT"]: {k.lower(): (v or "").strip() for k, v in r.items()} for r in rd}


def integer(v):
    try:
        return int(float(v))
    except ValueError:
        return None


def measurement(r, *ks):
    for k in ks:
        v = r.get(k, "")
        if v and v not in SENTINELS:
            try:
                return float(v)
            except ValueError:
                pass
    return None


def age_group(e):
    return 1 if e < 25 else 13 if e >= 80 else (e - 25) // 5 + 2


EDUCATION = {0: 1, 1: 1, 2: 2, 3: 3, 6: 3, 4: 4, 5: 4, 7: 4, 8: 5, 9: 6, 10: 6, 11: 6, 12: 6}


def map_record(a, i, an):
    "Return a ten-feature row and label, or an exclusion reason."
    y = {"1": 1, "3": 0}.get(a.get("a0301"))
    if y is None:
        return "label"
    hbp = {"1": 1, "2": 0, "3": 0}.get(a.get("a0401"))
    chk = {"1": 1, "2": 0}.get(a.get("a0603"))
    hch = 0 if chk == 0 else {"1": 1, "2": 0}.get(a.get("a0604"))
    s_today, previous_smoking = a.get("a1301"), a.get("a1305")
    smk = 1 if s_today in ("1", "2") or previous_smoking in ("1", "2") else 0 if (s_today == "3" and previous_smoking == "3") else None
    stk = {"1": 1, "2": 0}.get(a.get("a0502d"))
    ai, ib = a.get("a0502a"), a.get("a0502b")
    hrt = 1 if "1" in (ai, ib) else 0 if (ai == "2" and ib == "2") else None
    if None in (hbp, chk, hch, smk, stk, hrt):
        return "health"
    if an is None:
        return "anthropometry"
    weight, height = measurement(an, "an01_1", "an12_1"), measurement(an, "an04_1", "an15_1")
    if not (weight and height and 25 < weight < 250 and 100 < height < 220):
        return "anthropometry"
    bmi = round(weight / (height / 100) ** 2)
    if not 12 <= bmi <= 98:
        return "anthropometry"
    if i is None:
        return "residents"
    sex, age, education = integer(i.get("h0302", "")), integer(i.get("h0303", "")), integer(i.get("h0317a", ""))
    if sex not in (1, 2) or age is None or not 20 <= age <= 110 or education not in EDUCATION:
        return "residents"
    row = {"HighBP": hbp, "HighChol": hch, "CholCheck": chk, "BMI": bmi, "Smoker": smk, "Stroke": stk,
            "HeartDiseaseorAttack": hrt, "Sex": 1 if sex == 1 else 0, "Age": age_group(age), "Education": EDUCATION[education]}
    return [row[p] for p in PREDICTORS], y


def metrics(y, p, w, threshold):
    pred = p >= threshold
    wsum = lambda m: float(w[m].sum())
    tp, fn, tn, fp = wsum(pred & (y == 1)), wsum(~pred & (y == 1)), wsum(~pred & (y == 0)), wsum(pred & (y == 0))
    return {"roc_auc": round(float(roc_auc_score(y, p, sample_weight=w)), 4),
            "average_precision": round(float(average_precision_score(y, p, sample_weight=w)), 4),
            "sensitivity": round(tp / (tp + fn), 4), "specificity": round(tn / (tn + fp), 4),
            "prevalence": round(float(np.average(y, weights=w)), 4), "p_mean": round(float(np.average(p, weights=w)), 4),
            "brier": round(float(np.average((p - y) ** 2, weights=w)), 4)}


def main():
    part = json.load(open(SPLITS))
    ids, X, y = data.load_cdc(features=PREDICTORS)  # Education is outside the protocol schema; load it explicitly
    cols = list(range(len(PREDICTORS)))
    Xtr, ytr, _ = data.load_split(part, "training", ids, X, y)
    Xva, yva, _ = data.load_split(part, "validation", ids, X, y)
    Xte, yte, _ = data.load_split(part, "test", ids, X, y)
    _, _, w, b = train.fit(Xtr[:, cols], ytr)
    threshold = train.threshold_for_sensitivity(yva, train.prob(Xva[:, cols], w, b))
    p_cdc = train.prob(Xte[:, cols], w, b)
    out = {"protocol": "docs/ENSANUT_EXPERIMENT.md", "model": "logistic-reduced-10-v1", "predictors": PREDICTORS,
           "weights_floating": [float(v) for v in w], "intercept_floating": b, "threshold_cdc_validation": round(threshold, 6),
           "cdc_test_reference": metrics(yte, p_cdc, np.ones(len(yte)), threshold),
           "warning": "Separate exploratory experiment: reduced model, a different diagnosed-diabetes label and approximate feature mapping. This does not validate the MVP or establish clinical validity.",
           "date_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "years": {}}
    for year, (fa, fi, fan) in FILES.items():
        d = os.path.join(ROOT, "data", "raw", "ensanut", str(year))
        TO, I, AN = read(os.path.join(d, fa)), read(os.path.join(d, fi)), read(os.path.join(d, fan))
        rows, ys, ws, excl = [], [], [], {}
        for folio, a in TO.items():
            r = map_record(a, I.get(folio), AN.get(folio))
            pw = measurement(a, "ponde_f")
            if isinstance(r, str) or not pw:
                reason = r if isinstance(r, str) else "survey_weight"
                excl[reason] = excl.get(reason, 0) + 1
                continue
            rows.append(r[0]); ys.append(r[1]); ws.append(pw)
        Xe, ye, we = np.array(rows, dtype=float), np.array(ys), np.array(ws)
        p = train.prob(Xe, w, b)
        out["years"][str(year)] = {"adults": len(TO), "included": len(ye), "positives": int(ye.sum()), "exclusions": excl,
                                   "weighted": metrics(ye, p, we, threshold), "without_weighting": metrics(ye, p, np.ones(len(ye)), threshold)}
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ("threshold_cdc_validation", "cdc_test_reference")}, ensure_ascii=False))
    for k, v in out["years"].items():
        print(k, v["adults"], v["included"], v["positives"], v["exclusions"], "\n  weighted", v["weighted"], """
  unweighted""", v["without_weighting"])


if __name__ == "__main__":
    main()
