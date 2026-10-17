"""Verify artifact hashes, schema, numerical contract and model retraining without changing artifacts.
Run: python -m screening.verify
"""
import json, sys
import numpy as np
from . import contract, data, train, schema
from .paths import MODEL_METRICS, MODEL_JSON, SPLITS


def main():
    errors = []
    ok = lambda cond, msg: print(("  ok  " if cond else "  FALLA ") + msg) or (cond or errors.append(msg))
    m = json.load(open(MODEL_JSON)); met = json.load(open(MODEL_METRICS)); part = json.load(open(SPLITS))
    ok(met["model_sha256"] == data.sha256(MODEL_JSON), "model hash matches the metrics record")
    ok(m["training"]["splits_sha256"] == data.sha256(SPLITS), "split hash matches the model metadata")
    ok(part["source_sha256"] == data.sha256(data.CDC_CSV), "CDC CSV hash matches the split metadata")
    ok(m["variables"] == schema.FEATURE_NAMES and m["schema"]["version"] == schema.VERSION, "schema and feature order match")
    ok((m["weights_integers"], m["intercept_integer"]) == tuple(contract.quantize(m["weights_floating"], m["intercept_floating"])), "quantized weights = round(10^9 * weights)")
    n2048_max_int = (1 << 2047) // 3
    ok(contract.verify_overflow(m["weights_integers"], m["intercept_integer"], n2048_max_int) < n2048_max_int, "2048-bit key overflow bound includes the intercept")
    ids = set(); total = 0
    for k, v in part["ids"].items():
        ids |= set(v); total += len(v)
    ok(len(ids) == total == 253680, "disjoint splits cover all 253,680 rows")

    ids_, X, y = data.load_cdc()
    Xtr, ytr, _ = data.load_split(part, "training", ids_, X, y)
    _, _, w, b = train.fit(Xtr, ytr)
    dif = float(np.max(np.abs(np.array(w) - np.array(m["weights_floating"])))); dif_b = abs(b - m["intercept_floating"])
    Xte, yte, _ = data.load_split(part, "test", ids_, X, y)
    new_auc = train.roc_auc_score(yte, train.prob(Xte, w, b))
    print(f"        maximum weight difference {dif:.2e} · intercept {dif_b:.2e} · retrained ROC-AUC {new_auc:.6f}")
    ok(dif < 1e-3 and dif_b < 1e-3 and abs(new_auc - json.load(open(MODEL_METRICS))["test"]["roc_auc"]) < 1e-3,
       "retraining reproduces the exported model (tolerance 1e-3 allows lbfgs version/architecture variation)")
    if errors:
        sys.exit(f"{len(errors)} checks failed")
    print("verification OK")


if __name__ == "__main__":
    main()
