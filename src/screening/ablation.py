"""Ablation evidence for schema cdc19-v1: does removing Education and/or Income change discrimination?

Same procedure as the exported model (train.fit: standardized logistic regression), trained on the TRAINING split and
scored on the VALIDATION split; the test split is not used. Education and Income are loaded explicitly because they
are no longer part of the protocol schema.

Run: python -m screening.ablation        → artifacts/metrics/ablation_cdc19_v1.json
"""
import datetime, json, os, platform
import numpy as np
import sklearn
from sklearn.metrics import average_precision_score, roc_auc_score
from . import data, schema, train
from .paths import ARTIFACTS, SPLITS

REMOVED = ["Education", "Income"]
OUTPUT = os.path.join(ARTIFACTS, "metrics", "ablation_cdc19_v1.json")


def run():
    names = schema.FEATURE_NAMES + REMOVED  # the 19 protocol features plus the two candidates for removal
    part = json.load(open(SPLITS))
    ids, X, y = data.load_cdc(features=names)
    Xtr, ytr, _ = data.load_split(part, "training", ids, X, y)
    Xva, yva, _ = data.load_split(part, "validation", ids, X, y)
    variants = {"all_21": names, "without_Education": [n for n in names if n != "Education"],
                "without_Income": [n for n in names if n != "Income"], "without_both_19": schema.FEATURE_NAMES}
    results = {}
    for key, cols in variants.items():
        ix = [names.index(n) for n in cols]
        _, _, w, b = train.fit(Xtr[:, ix], ytr)
        p = train.prob(Xva[:, ix], w, b)
        results[key] = {"features": len(cols), "roc_auc": round(float(roc_auc_score(yva, p)), 4),
                        "average_precision": round(float(average_precision_score(yva, p)), 4)}
    base = results["all_21"]["roc_auc"]
    for r in results.values():
        r["delta_roc_auc_vs_21"] = round(r["roc_auc"] - base, 4)
    out = {"question": "Does removing Education and/or Income reduce discrimination?",
           "procedure": "train.fit (standardized logistic regression) on the training split; scored on the validation split; test split unused",
           "splits_sha256": data.sha256(SPLITS), "source_sha256": part["source_sha256"],
           "n_training": int(len(ytr)), "n_validation": int(len(yva)), "validation_positives": int(yva.sum()),
           "results": results, "date_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
           "environment": f"{platform.system()} {platform.machine()} · Python {platform.python_version()} · scikit-learn {sklearn.__version__} · numpy {np.__version__}"}
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(out, f, indent=1)
    print(f"Validation split (n={out['n_validation']:,}, positives={out['validation_positives']:,}); trained on {out['n_training']:,}")
    print(f"{'variant':<20} {'features':>8} {'ROC-AUC':>8} {'AP':>8} {'ΔAUC vs 21':>11}")
    for k, r in results.items():
        print(f"{k:<20} {r['features']:>8} {r['roc_auc']:>8} {r['average_precision']:>8} {r['delta_roc_auc_vs_21']:>+11.4f}")
    print("saved to", os.path.relpath(OUTPUT))
    return out


if __name__ == "__main__":
    run()
