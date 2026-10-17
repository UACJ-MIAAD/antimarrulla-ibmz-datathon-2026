"""Carga del CDC (UCI 891) y particiones estratificadas 70/15/15 con semilla fija.

Las particiones se guardan una sola vez como artefacto compartido (IDs por partición + hashes);
entrenamiento, evaluación cifrada y mediciones leen ese mismo archivo.

Uso: python -m tamizaje.datos [--forzar]
"""
import csv, hashlib, json, os, sys
import numpy as np
from sklearn.model_selection import train_test_split
from . import esquema
from .rutas import CDC_CSV, PARTICIONES, ESQUEMA_JSON, asegurar_dirs

SEMILLA = 2026


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def cargar_cdc(path=CDC_CSV):
    """Regresa (ids, X enteros en el orden del esquema, y). Excluye ID de las variables."""
    with open(path, newline="") as f:
        rd = csv.DictReader(f)
        filas = list(rd)
    ids = np.array([int(r["ID"]) for r in filas], dtype=np.int64)
    X = np.array([[esquema.a_entero(n, int(float(r[n]))) for n in esquema.NOMBRES] for r in filas], dtype=np.int64)
    y = np.array([int(float(r[esquema.OBJETIVO])) for r in filas], dtype=np.int64)
    return ids, X, y


def crear_particiones(ids, y):
    tr, tmp = train_test_split(ids, test_size=0.30, stratify=y, random_state=SEMILLA)
    pos = {int(i): k for k, i in enumerate(ids)}
    y_tmp = y[[pos[int(i)] for i in tmp]]
    va, te = train_test_split(tmp, test_size=0.50, stratify=y_tmp, random_state=SEMILLA)
    return {"entrenamiento": sorted(int(i) for i in tr), "validacion": sorted(int(i) for i in va), "prueba": sorted(int(i) for i in te)}


def guardar_particiones(forzar=False):
    asegurar_dirs()
    with open(ESQUEMA_JSON, "w") as f:
        json.dump(esquema.como_dict(), f, ensure_ascii=False, indent=2)
    if os.path.exists(PARTICIONES) and not forzar:
        print("particiones ya existen:", PARTICIONES)
        return json.load(open(PARTICIONES))
    ids, X, y = cargar_cdc()
    p = crear_particiones(ids, y)
    pos = {k: int(y[np.isin(ids, v)].sum()) for k, v in p.items()}
    art = {
        "version": "cdc891-particiones-v1", "semilla": SEMILLA, "proporciones": "70/15/15 estratificado por Diabetes_binary",
        "fuente": os.path.relpath(CDC_CSV), "fuente_sha256": sha256(CDC_CSV), "esquema": esquema.VERSION,
        "tamanos": {k: len(v) for k, v in p.items()}, "positivos": pos, "ids": p,
    }
    with open(PARTICIONES, "w") as f:
        json.dump(art, f, separators=(",", ":"))
    print("particiones:", art["tamanos"], "positivos:", pos)
    return art


def cargar_particion(art, nombre, ids, X, y):
    m = np.isin(ids, np.array(art["ids"][nombre]))
    return X[m], y[m], ids[m]


if __name__ == "__main__":
    guardar_particiones(forzar="--forzar" in sys.argv)
