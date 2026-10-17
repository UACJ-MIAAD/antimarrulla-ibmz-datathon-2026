"""Load CDC UCI 891 and shared stratified 70/15/15 splits with a fixed seed.
Store split IDs and hashes once; training, encrypted evaluation and benchmarks use the same artifact.
Run: python -m screening.data [--force]
"""
import csv, hashlib, json, os, sys
import numpy as np
from sklearn.model_selection import train_test_split
from . import schema
from .paths import CDC_CSV, SPLITS, SCHEMA_JSON, ensure_dirs

SEED = 2026


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load_cdc(path=CDC_CSV):
    "Return IDs, integer feature matrix in schema order and labels; exclude ID from predictors."
    with open(path, newline="") as f:
        rd = csv.DictReader(f)
        rows = list(rd)
    ids = np.array([int(r["ID"]) for r in rows], dtype=np.int64)
    X = np.array([[schema.to_integer(n, int(float(r[n]))) for n in schema.FEATURE_NAMES] for r in rows], dtype=np.int64)
    y = np.array([int(float(r[schema.TARGET])) for r in rows], dtype=np.int64)
    return ids, X, y


def create_splits(ids, y):
    tr, tmp = train_test_split(ids, test_size=0.30, stratify=y, random_state=SEED)
    pos = {int(i): k for k, i in enumerate(ids)}
    and_tmp = y[[pos[int(i)] for i in tmp]]
    va, te = train_test_split(tmp, test_size=0.50, stratify=and_tmp, random_state=SEED)
    return {"training": sorted(int(i) for i in tr), "validation": sorted(int(i) for i in va), "test": sorted(int(i) for i in te)}


def save_splits(force=False):
    ensure_dirs()
    with open(SCHEMA_JSON, "w") as f:
        json.dump(schema.as_dict(), f, ensure_ascii=False, indent=2)
    if os.path.exists(SPLITS) and not force:
        print("splits already exist:", SPLITS)
        return json.load(open(SPLITS))
    ids, X, y = load_cdc()
    p = create_splits(ids, y)
    pos = {k: int(y[np.isin(ids, v)].sum()) for k, v in p.items()}
    art = {
        "version": "cdc891-splits-v1", "seed": SEED, "proportions": "70/15/15 stratified by Diabetes_binary",
        "source": os.path.relpath(CDC_CSV), "source_sha256": sha256(CDC_CSV), "schema": schema.VERSION,
        "sizes": {k: len(v) for k, v in p.items()}, "positives": pos, "ids": p,
    }
    with open(SPLITS, "w") as f:
        json.dump(art, f, separators=(",", ":"))
    print("particiones:", art["sizes"], "positivos:", pos)
    return art


def load_split(art, name, ids, X, y):
    m = np.isin(ids, np.array(art["ids"][name]))
    return X[m], y[m], ids[m]


if __name__ == "__main__":
    save_splits(force="--force" in sys.argv)
