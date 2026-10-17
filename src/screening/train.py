"""Train CDC UCI 891 logistic regression and export the protocol model.
Use the shared stratified 70/15/15 split artifact. Fit standardization on training data only,
then fold it into weights/intercept so the hospital sends original integer feature codes.
Choose the validation threshold for sensitivity >=0.80 with maximum specificity; report test metrics separately.
Export floating/fixed-point weights (scale 10^9), schema, threshold, versions and hashes.
Run: python -m screening.train
"""
import datetime, hashlib, json, math, platform, sys
import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, confusion_matrix, roc_auc_score, roc_curve
from sklearn.preprocessing import StandardScaler
from . import contract, data, schema
from .paths import MODEL_METRICS, MODEL_JSON, SPLITS, ensure_dirs

TARGET_SENSITIVITY = 0.80
MODEL_NAME = "logistic-cdc21-v1"


def fit(Xtr, ytr, class_weight=None):
    sc = StandardScaler().fit(Xtr.astype(float))
    lr = LogisticRegression(C=1.0, max_iter=5000, class_weight=class_weight)
    lr.fit(sc.transform(Xtr.astype(float)), ytr)
    coef = lr.coef_[0]
    w = coef / sc.scale_
    b = float(lr.intercept_[0] - np.sum(coef * sc.mean_ / sc.scale_))
    return sc, lr, w, b


def prob(X, w, b):
    z = X.astype(float) @ w + b
    return 1.0 / (1.0 + np.exp(-z))


def threshold_for_sensitivity(y, p, target=TARGET_SENSITIVITY):
    fpr, tpr, thr = roc_curve(y, p)
    i = int(np.argmax(tpr >= target))
    return float(thr[i])


def ece(y, p, bins=10):
    "Expected calibration error in ten equal-sized probability-quantile bins."
    order = np.argsort(p)
    table, total = [], 0.0
    for g in np.array_split(order, bins):
        mp, oy = float(p[g].mean()), float(y[g].mean())
        table.append({"n": int(len(g)), "p_mean": round(mp, 4), "observed": round(oy, 4)})
        total += len(g) / len(p) * abs(mp - oy)
    return total, table


def metrics(y, p, threshold):
    pred = (p >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    e, table = ece(y, p)
    return {
        "n": int(len(y)), "positives": int(y.sum()), "prevalence": round(float(y.mean()), 4),
        "roc_auc": round(float(roc_auc_score(y, p)), 4),
        "average_precision": round(float(average_precision_score(y, p)), 4),
        "sensitivity": round(tp / (tp + fn), 4), "specificity": round(tn / (tn + fp), 4),
        "ppv": round(tp / (tp + fp), 4) if tp + fp else None,
        "matrix_confusion": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "brier": round(float(brier_score_loss(y, p)), 4), "p_mean": round(float(p.mean()), 4),
        "ece_10_quantiles": round(e, 4), "calibration_by_decile": table,
    }


def main():
    ensure_dirs()
    part = data.save_splits()
    ids, X, y = data.load_cdc()
    Xtr, ytr, _ = data.load_split(part, "training", ids, X, y)
    Xva, yva, _ = data.load_split(part, "validation", ids, X, y)
    Xte, yte, _ = data.load_split(part, "test", ids, X, y)

    sc, lr, w, b = fit(Xtr, ytr)
    # Folded weights must reproduce sklearn predictions on standardized inputs.
    p_sk = lr.predict_proba(sc.transform(Xte.astype(float)))[:, 1]
    assert np.allclose(p_sk, prob(Xte, w, b), atol=1e-12), "folded standardization does not reproduce sklearn predictions"

    p_va, p_te = prob(Xva, w, b), prob(Xte, w, b)
    threshold = threshold_for_sensitivity(yva, p_va)
    W, B = contract.quantize(w.tolist(), b)

    # Floating point versus exact integer fixed point over the full test split.
    z_int = np.array([contract.logit_integer(W, B, x) for x in Xte.tolist()], dtype=object)
    logit_q = np.array([int(z) / contract.S_W for z in z_int], dtype=float)
    logit_f = Xte.astype(float) @ w + b
    err = np.abs(logit_q - logit_f)
    bounds = np.array([contract.logit_error_bound(x) for x in Xte.tolist()])
    p_q = 1.0 / (1.0 + np.exp(-logit_q))

    # Calibration effect of class_weight="balanced"; not used by the exported model.
    _, _, wb, bb = fit(Xtr, ytr, class_weight="balanced")
    p_te_bal = prob(Xte, wb, bb)
    threshold_bal = threshold_for_sensitivity(yva, prob(Xva, wb, bb))

    # Identical feature rows without ID; sensitivity after deduplicating training rows.
    rows = np.hstack([X, y[:, None]])
    _, count = np.unique(rows, axis=0, return_counts=True)
    dup_total = int((count - 1).sum())
    tr_set = {tuple(r) for r in np.hstack([Xtr, ytr[:, None]]).tolist()}
    te_in_tr = int(sum(tuple(r) in tr_set for r in np.hstack([Xte, yte[:, None]]).tolist()))
    Xtr_u, idx = np.unique(np.hstack([Xtr, ytr[:, None]]), axis=0, return_index=True)
    _, _, wd, bd = fit(Xtr[np.sort(idx)], ytr[np.sort(idx)])
    p_te_dedup = prob(Xte, wd, bd)

    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    model = {
        "model": MODEL_NAME, "schema": schema.as_dict(), "variables": schema.FEATURE_NAMES,
        "weights_floating": [float(v) for v in w], "intercept_floating": b,
        "weight_scale": contract.S_W, "weights_integers": W, "intercept_integer": B, "exponent": contract.EXPONENT,
        "threshold": {"probability": threshold, "logit": math.log(threshold / (1 - threshold)),
                   "criterion": f"sensitivity >= {TARGET_SENSITIVITY} on validation with maximum specificity"},
        "means_training": [float(v) for v in sc.mean_],
        "training": {
            "data": "CDC Diabetes Health Indicators (UCI 891)", "data_sha256": part["source_sha256"],
            "splits": "artifacts/splits/cdc891_splits_v1.json", "splits_sha256": data.sha256(SPLITS),
            "seed": data.SEED, "algorithm": "LogisticRegression(lbfgs, C=1.0, max_iter=5000, class_weight=None) on standardized inputs; standardization folded into weights and intercept",
            "python": platform.python_version(), "numpy": np.__version__, "scikit_learn": sklearn.__version__,
            "platform": f"{platform.system()} {platform.machine()}", "date_utc": now,
        },
    }
    with open(MODEL_JSON, "w") as f:
        json.dump(model, f, ensure_ascii=False, indent=1)
    model_sha = data.sha256(MODEL_JSON)

    met = {
        "model": MODEL_NAME, "model_sha256": model_sha, "date_utc": now, "environment": model["training"]["platform"],
        "definitions": {
            "average_precision": "sklearn.metrics.average_precision_score: precision weighted by recall increments, not trapezoidal PR area",
            "threshold": model["threshold"]["criterion"], "ece": "expected calibration error in ten equal-sized bins",
        },
        "threshold_probability": round(threshold, 6),
        "validation": metrics(yva, p_va, threshold), "test": metrics(yte, p_te, threshold),
        "quantization_in_test": {
            "n": int(len(yte)), "weight_scale": contract.S_W,
            "error_max_logit": float(err.max()), "error_mean_logit": float(err.mean()),
            "applicable_max_bound": float(bounds.max()), "all_within_bound": bool(np.all(err <= bounds)),
            "error_max_probability": float(np.abs(p_q - p_te).max()),
            "roc_auc_floating": round(float(roc_auc_score(yte, p_te)), 6), "roc_auc_point_fijo": round(float(roc_auc_score(yte, p_q)), 6),
            "decisions_different_in_threshold": int(np.sum((p_q >= threshold) != (p_te >= threshold))),
        },
        "class_weight_balanced": {
            "note": "class_weight='balanced' increases positive-class probabilities while changing ranking little. The exported model omits class weighting and chooses its threshold on validation; this does not guarantee external calibration.",
            "test": metrics(yte, p_te_bal, threshold_bal), "threshold_validation": round(threshold_bal, 6),
        },
        "duplicates": {
            "rows_repeated_without_id_in_all_the_cdc": dup_total,
            "rows_of_test_with_copy_identical_in_training": te_in_tr,
            "note": "Identical categorical responses can belong to different people; identical rows do not establish duplicate participants.",
            "sensitivity_training_without_duplicates": {"rows_training": int(len(idx)), "test": metrics(yte, p_te_dedup, threshold_for_sensitivity(yva, prob(Xva, wd, bd)))},
        },
        "xgboost": "not trained: optional after logistic regression is completed and verified",
    }
    with open(MODEL_METRICS, "w") as f:
        json.dump(met, f, ensure_ascii=False, indent=1)
    t = met["test"]
    print(f"model {model_sha[:12]} · test: ROC-AUC {t['roc_auc']} · AP {t['average_precision']} · sens {t['sensitivity']} · specificity {t['specificity']} · Brier {t['brier']} · threshold {threshold:.4f}")
    print("quantization:", met["quantization_in_test"])


if __name__ == "__main__":
    main()
