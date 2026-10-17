"""Evaluación externa exploratoria con ENSANUT 2022 y 2023 (extra, US-3.5).

Sigue el protocolo fijado antes de evaluar en docs/ENSANUT_EXPERIMENTO.md. Modelo REDUCIDO (10 variables), distinto del MVP.
Lee microdatos locales (data/raw/ensanut/, no versionados) y guarda solo métricas agregadas.

Uso: python -m tamizaje.ensanut
"""
import csv, datetime, json, os
import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score
from . import datos, entrenar, esquema
from .rutas import ARTEFACTOS, PARTICIONES, RAIZ

PREDICTORES = ["HighBP", "HighChol", "CholCheck", "BMI", "Smoker", "Stroke", "HeartDiseaseorAttack", "Sex", "Age", "Education"]
ARCHIVOS = {
    2022: ("ensadul2022_entrega_w.csv", "integrantes_ensanut2022_w.csv", "ensaantro2022_entrega_w.csv"),
    2023: ("adultos_ensanut2023_w_n.csv", "integrantes_ensanut2023_w_n.csv", "antropometria_hta_4mar24.csv"),
}
SENTINELAS = {"222.22", "222.2", "999", "999.9", "999.99"}
SALIDA = os.path.join(ARTEFACTOS, "metricas", "ensanut_exploratorio_v1.json")


def leer(path):
    with open(path, encoding="utf-8", newline="") as f:
        rd = csv.DictReader(f)
        return {r["FOLIO_INT"]: {k.lower(): (v or "").strip() for k, v in r.items()} for r in rd}


def entero(v):
    try:
        return int(float(v))
    except ValueError:
        return None


def medida(r, *ks):
    for k in ks:
        v = r.get(k, "")
        if v and v not in SENTINELAS:
            try:
                return float(v)
            except ValueError:
                pass
    return None


def grupo_edad(e):
    return 1 if e < 25 else 13 if e >= 80 else (e - 25) // 5 + 2


EDUCACION = {0: 1, 1: 1, 2: 2, 3: 3, 6: 3, 4: 4, 5: 4, 7: 4, 8: 5, 9: 6, 10: 6, 11: 6, 12: 6}


def mapear(a, i, an):
    """Regresa (fila de 10 predictores, etiqueta) o el motivo de exclusión."""
    y = {"1": 1, "3": 0}.get(a.get("a0301"))
    if y is None:
        return "etiqueta"
    hbp = {"1": 1, "2": 0, "3": 0}.get(a.get("a0401"))
    chk = {"1": 1, "2": 0}.get(a.get("a0603"))
    hch = 0 if chk == 0 else {"1": 1, "2": 0}.get(a.get("a0604"))
    s_hoy, s_antes = a.get("a1301"), a.get("a1305")
    smk = 1 if s_hoy in ("1", "2") or s_antes in ("1", "2") else 0 if (s_hoy == "3" and s_antes == "3") else None
    stk = {"1": 1, "2": 0}.get(a.get("a0502d"))
    ia, ib = a.get("a0502a"), a.get("a0502b")
    hrt = 1 if "1" in (ia, ib) else 0 if (ia == "2" and ib == "2") else None
    if None in (hbp, chk, hch, smk, stk, hrt):
        return "salud"
    if an is None:
        return "antropometría"
    peso, talla = medida(an, "an01_1", "an12_1"), medida(an, "an04_1", "an15_1")
    if not (peso and talla and 25 < peso < 250 and 100 < talla < 220):
        return "antropometría"
    imc = round(peso / (talla / 100) ** 2)
    if not 12 <= imc <= 98:
        return "antropometría"
    if i is None:
        return "residentes"
    sexo, edad, esc = entero(i.get("h0302", "")), entero(i.get("h0303", "")), entero(i.get("h0317a", ""))
    if sexo not in (1, 2) or edad is None or not 20 <= edad <= 110 or esc not in EDUCACION:
        return "residentes"
    fila = {"HighBP": hbp, "HighChol": hch, "CholCheck": chk, "BMI": imc, "Smoker": smk, "Stroke": stk,
            "HeartDiseaseorAttack": hrt, "Sex": 1 if sexo == 1 else 0, "Age": grupo_edad(edad), "Education": EDUCACION[esc]}
    return [fila[p] for p in PREDICTORES], y


def metricas(y, p, w, umbral):
    pred = p >= umbral
    wsum = lambda m: float(w[m].sum())
    tp, fn, tn, fp = wsum(pred & (y == 1)), wsum(~pred & (y == 1)), wsum(~pred & (y == 0)), wsum(pred & (y == 0))
    return {"roc_auc": round(float(roc_auc_score(y, p, sample_weight=w)), 4),
            "average_precision": round(float(average_precision_score(y, p, sample_weight=w)), 4),
            "sensibilidad": round(tp / (tp + fn), 4), "especificidad": round(tn / (tn + fp), 4),
            "prevalencia": round(float(np.average(y, weights=w)), 4), "p_media": round(float(np.average(p, weights=w)), 4),
            "brier": round(float(np.average((p - y) ** 2, weights=w)), 4)}


def main():
    part = json.load(open(PARTICIONES))
    ids, X, y = datos.cargar_cdc()
    cols = [esquema.NOMBRES.index(p) for p in PREDICTORES]
    Xtr, ytr, _ = datos.cargar_particion(part, "entrenamiento", ids, X, y)
    Xva, yva, _ = datos.cargar_particion(part, "validacion", ids, X, y)
    Xte, yte, _ = datos.cargar_particion(part, "prueba", ids, X, y)
    _, _, w, b = entrenar.ajustar(Xtr[:, cols], ytr)
    umbral = entrenar.umbral_por_sensibilidad(yva, entrenar.prob(Xva[:, cols], w, b))
    p_cdc = entrenar.prob(Xte[:, cols], w, b)
    out = {"protocolo": "docs/ENSANUT_EXPERIMENTO.md", "modelo": "logistico-reducido-10-v1", "predictores": PREDICTORES,
           "pesos_flotantes": [float(v) for v in w], "intercepto_flotante": b, "umbral_cdc_validacion": round(umbral, 6),
           "referencia_cdc_prueba": metricas(yte, p_cdc, np.ones(len(yte)), umbral),
           "advertencia": "Experimento exploratorio aparte: modelo reducido, etiqueta distinta (solo diabetes diagnosticada) y mapeo aproximado. No valida el MVP ni es validación clínica.",
           "fecha_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "anios": {}}
    for anio, (fa, fi, fan) in ARCHIVOS.items():
        d = os.path.join(RAIZ, "data", "raw", "ensanut", str(anio))
        A, I, AN = leer(os.path.join(d, fa)), leer(os.path.join(d, fi)), leer(os.path.join(d, fan))
        filas, ys, ws, excl = [], [], [], {}
        for folio, a in A.items():
            r = mapear(a, I.get(folio), AN.get(folio))
            pw = medida(a, "ponde_f")
            if isinstance(r, str) or not pw:
                motivo = r if isinstance(r, str) else "ponderador"
                excl[motivo] = excl.get(motivo, 0) + 1
                continue
            filas.append(r[0]); ys.append(r[1]); ws.append(pw)
        Xe, ye, we = np.array(filas, dtype=float), np.array(ys), np.array(ws)
        p = entrenar.prob(Xe, w, b)
        out["anios"][str(anio)] = {"adultos": len(A), "incluidos": len(ye), "positivos": int(ye.sum()), "exclusiones": excl,
                                   "ponderado": metricas(ye, p, we, umbral), "sin_ponderar": metricas(ye, p, np.ones(len(ye)), umbral)}
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ("umbral_cdc_validacion", "referencia_cdc_prueba")}, ensure_ascii=False))
    for k, v in out["anios"].items():
        print(k, v["adultos"], v["incluidos"], v["positivos"], v["exclusiones"], "\n  ponderado", v["ponderado"], "\n  sin ponderar", v["sin_ponderar"])


if __name__ == "__main__":
    main()
