"""Épica E5 (extra): pronóstico semanal de casos nuevos de diabetes T1 y T2 y planeación financiera.

Decisiones (ver docs/PRONOSTICO.md):
- 222 series SINAVE (111 por tipo: nacional, 4 regiones y 32 estados × general, hombres y mujeres).
- Ajuste solo con 2022 en adelante (COVID 2020–2021 fuera); semanas no observadas → interpolación lineal (se cuentan).
- Horizonte explícito: la última observación es la semana del 27 jul 2026; se pronostican 11 semanas de puente hasta la
  semana de referencia (nowcast) y las 52 semanas siguientes: 63 pasos desde la última observación.
- SISTEMA DE PRONÓSTICO (el mismo para publicar y para evaluar):
  1. Selección por serie: backtest con hasta 4 orígenes de 52 semanas (cada 13 semanas, con al menos 104 semanas de
     ajuste) entre ingenuo estacional y ETS (Holt-Winters aditivo, tendencia amortiguada, s = 52); SMAPE en h1–52,
     empate a 5% → MAE.
  2. Bandas 80/95 exploratorias: cuantiles de los errores de esa selección por tramo de horizonte (h > 52 usa el último).
  3. Series con < 5 casos en 52 semanas: proporción dentro de su región aplicada al pronóstico regional.
  4. Coherencia proporcional de arriba abajo por tipo y sexo (nacional → regiones → estados).
- EVALUACIÓN ANIDADA (separada de la selección): orígenes externos cada 13 semanas con 63 semanas reales después;
  en cada uno el sistema completo (selección, bandas, respaldo y reconciliación) se corre SOLO con datos anteriores al
  origen y se compara contra las 63 semanas siguientes. Reporta SMAPE, cobertura y anchura de bandas por nivel y tramo.
- Presupuesto = casos × costo unitario, solo si se da un costo con su fuente (no se inventa). Los escenarios con
  límites superiores suman límites semanales marginales: NO son un intervalo conjunto del total.

Uso: python -m tamizaje.pronostico [--hoy 2026-10-17] [--costo-mxn N --fuente-costo "..."]
"""
import argparse, csv, datetime, json, os, warnings
import numpy as np
from .rutas import ARTEFACTOS, RAIZ

INICIO_AJUSTE = "2022-01-01"
S = 52
TRAMOS = [(1, 13), (14, 26), (27, 52)]
TRAMOS_EVAL = [(1, 13), (14, 26), (27, 52), (53, 63), (12, 63)]
H_PUBLICADO = 63
SALIDA = os.path.join(ARTEFACTOS, "pronostico", "e5_pronostico_v1.json")
CAMPOS = ("f", "lo95", "lo80", "hi80", "hi95")


def cargar():
    series = {}
    for tipo in ("tipo1", "tipo2"):
        with open(os.path.join(RAIZ, "data", "sinave", tipo, "products.csv"), newline="") as f:
            for r in csv.DictReader(f):
                k = (r["disease_id"], r["geography_level"], r["geography_id"], r["sex"])
                series.setdefault(k, []).append((r["ds"], float(r["y_cases"]) if r["observed"] == "True" else np.nan))
    for k in series:
        series[k].sort()
    return series


def interpolar(y):
    y = np.array(y, dtype=float); m = np.isnan(y)
    if m.any():
        idx = np.arange(len(y)); y[m] = np.interp(idx[m], idx[~m], y[~m])
    return y, int(m.sum())


def snaive(y, h):
    ult = y[-S:]
    return np.array([ult[i % S] for i in range(h)])


def ets(y, h):
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = ExponentialSmoothing(y, trend="add", damped_trend=True, seasonal="add", seasonal_periods=S,
                                 initialization_method="estimated").fit()
    f = np.asarray(m.forecast(h))
    if not np.all(np.isfinite(f)):
        raise ValueError("ETS no finito")
    return np.clip(f, 0, None)


MODELOS = {"ingenuo_estacional": snaive, "ets": ets}


def smape(a, f):
    d = np.abs(a) + np.abs(f)
    return float(np.mean(np.where(d == 0, 0.0, 2 * np.abs(a - f) / np.where(d == 0, 1, d)))) * 100


def seleccion(y):
    """Backtest de selección: hasta 4 orígenes de 52 semanas con al menos 104 semanas de ajuste cada uno."""
    n = len(y)
    origenes = [n - S - 13 * k for k in range(4) if n - S - 13 * k >= 2 * S]
    if not origenes:
        raise ValueError("serie demasiado corta para seleccionar")
    res = {m: {"err": [], "smape": [], "mae": []} for m in MODELOS}
    for o in origenes:
        tr, te = y[:o], y[o:o + S]
        for nombre, fn in MODELOS.items():
            try:
                f = fn(tr, S)
            except Exception:
                f = snaive(tr, S)
            res[nombre]["err"].append(te - f)
            res[nombre]["smape"].append([smape(te[a - 1:b], f[a - 1:b]) for a, b in TRAMOS] + [smape(te, f)])
            res[nombre]["mae"].append(float(np.mean(np.abs(te - f))))
    out = {}
    for nombre, r in res.items():
        sm = np.mean(np.array(r["smape"]), axis=0)
        out[nombre] = {"smape_por_tramo": {f"h{a}-{b}": round(float(v), 2) for (a, b), v in zip(TRAMOS, sm[:3])},
                       "smape_1_52": round(float(sm[3]), 2), "mae": round(float(np.mean(r["mae"])), 3),
                       "origenes": len(origenes), "errores": np.array(r["err"])}
    return out


def elegir(bt):
    a, b = bt["ets"], bt["ingenuo_estacional"]
    if abs(a["smape_1_52"] - b["smape_1_52"]) <= 0.05 * max(a["smape_1_52"], b["smape_1_52"], 1e-9):
        return "ets" if a["mae"] <= b["mae"] else "ingenuo_estacional"
    return "ets" if a["smape_1_52"] < b["smape_1_52"] else "ingenuo_estacional"


def bandas(errores, h_total):
    """Cuantiles empíricos de error por tramo; horizontes > 52 usan el último tramo."""
    q = {(a, b): np.quantile(errores[:, a - 1:b].ravel(), [0.025, 0.10, 0.90, 0.975]) for a, b in TRAMOS}
    return np.array([q[next(((a, b) for a, b in TRAMOS if a <= h <= b), TRAMOS[-1])] for h in range(1, h_total + 1)])


def sistema(ys, h_total, region_de):
    """Corre el sistema completo sobre {clave: serie}. Solo ve los datos que recibe (sin futuro)."""
    crudo = {}
    for k, y in ys.items():
        bt = seleccion(y)
        modelo = elegir(bt)
        try:
            f = MODELOS[modelo](y, h_total)
        except Exception:
            modelo, f = "ingenuo_estacional", snaive(y, h_total)
        b = bandas(bt[modelo]["errores"], h_total)
        crudo[k] = {"y": y, "modelo": modelo, "f": f,
                    "lo95": np.clip(f + b[:, 0], 0, None), "lo80": np.clip(f + b[:, 1], 0, None),
                    "hi80": np.clip(f + b[:, 2], 0, None), "hi95": np.clip(f + b[:, 3], 0, None),
                    "seleccion": {m: {kk: vv for kk, vv in r.items() if kk != "errores"} for m, r in bt.items()},
                    "casos_52": float(y[-S:].sum())}
    for k, c in crudo.items():  # respaldo regional
        if k[1] == "estado" and c["casos_52"] < 5:
            reg = crudo[(k[0], "region", region_de[k[2]], k[3])]
            hermanos = [kk for kk in crudo if kk[0] == k[0] and kk[1] == "estado" and kk[3] == k[3] and region_de[kk[2]] == region_de[k[2]]]
            tot = sum(crudo[kk]["y"][-2 * S:].sum() for kk in hermanos)
            prop = c["y"][-2 * S:].sum() / tot if tot else 0.0
            for campo in CAMPOS:
                c[campo] = reg[campo] * prop
            c["modelo"] = f"respaldo_regional ({prop:.4f} de la región)"
    for tipo in {k[0] for k in crudo}:  # coherencia de arriba abajo
        for sexo in {k[3] for k in crudo if k[0] == tipo}:
            nac = crudo[(tipo, "nacional", "mx", sexo)]
            for campo in CAMPOS:
                nac[campo + "_rec"] = nac[campo]
            regiones = [k for k in crudo if k[0] == tipo and k[1] == "region" and k[3] == sexo]
            suma_r = sum(crudo[k]["f"] for k in regiones)
            fac_r = np.divide(nac["f"], suma_r, out=np.ones_like(suma_r), where=suma_r > 0)
            for kr in regiones:
                rc = crudo[kr]
                for campo in CAMPOS:
                    rc[campo + "_rec"] = rc[campo] * fac_r
                estados = [k for k in crudo if k[0] == tipo and k[1] == "estado" and k[3] == sexo and region_de[k[2]] == kr[2]]
                suma_e = sum(crudo[k]["f"] for k in estados)
                fac_e = np.divide(rc["f_rec"], suma_e, out=np.ones_like(suma_e), where=suma_e > 0)
                for ke in estados:
                    for campo in CAMPOS:
                        crudo[ke][campo + "_rec"] = crudo[ke][campo] * fac_e
    return crudo


def evaluar(ys, region_de, h=H_PUBLICADO):
    """Evaluación anidada del sistema reconciliado hasta h pasos, con orígenes que no se usan para seleccionar."""
    n = len(next(iter(ys.values())))
    origenes = [o for o in (n - h - 13 * k for k in range(4)) if o - S >= 2 * S]
    filas, pronosticos = [], {}
    for o in origenes:
        c = sistema({k: y[:o] for k, y in ys.items()}, h, region_de)
        pronosticos[o] = {k: v["f_rec"] for k, v in c.items()}
        for k, y in ys.items():
            real, v = y[o:o + h], c[k]
            filas.append({"clave": k, "origen": o, "real": real, "f": v["f_rec"], "lo80": v["lo80_rec"], "hi80": v["hi80_rec"],
                          "lo95": v["lo95_rec"], "hi95": v["hi95_rec"]})
    resumen = {}
    for nivel in ("nacional", "region", "estado"):
        sel = [r for r in filas if r["clave"][1] == nivel]
        if not sel:
            continue
        resumen[nivel] = {}
        for a, b in TRAMOS_EVAL:
            sl = slice(a - 1, b)
            sm = [smape(r["real"][sl], r["f"][sl]) for r in sel]
            cob80 = np.mean(np.concatenate([(r["real"][sl] >= r["lo80"][sl]) & (r["real"][sl] <= r["hi80"][sl]) for r in sel]))
            cob95 = np.mean(np.concatenate([(r["real"][sl] >= r["lo95"][sl]) & (r["real"][sl] <= r["hi95"][sl]) for r in sel]))
            ancho80 = np.mean(np.concatenate([(r["hi80"][sl] - r["lo80"][sl]) / np.maximum(np.mean(r["real"][sl]), 1) for r in sel]))
            resumen[nivel][f"h{a}-{b}"] = {"smape": round(float(np.mean(sm)), 2), "cobertura_80": round(float(cob80), 3),
                                           "cobertura_95": round(float(cob95), 3), "ancho_80_relativo": round(float(ancho80), 3)}
    por_serie = {}
    for r in filas:
        d = por_serie.setdefault(r["clave"], {f"h{a}-{b}": [] for a, b in TRAMOS_EVAL})
        for a, b in TRAMOS_EVAL:
            d[f"h{a}-{b}"].append(smape(r["real"][a - 1:b], r["f"][a - 1:b]))
    por_serie = {k: {t: round(float(np.mean(v)), 2) for t, v in d.items()} for k, d in por_serie.items()}
    return {"origenes": origenes, "horizonte": h, "por_nivel": resumen, "por_serie": por_serie, "pronosticos": pronosticos}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hoy", default="2026-10-17", help="fecha de referencia (fija para reproducir)")
    ap.add_argument("--costo-mxn", type=float, default=None)
    ap.add_argument("--fuente-costo", default=None)
    a = ap.parse_args()
    if (a.costo_mxn is None) != (a.fuente_costo is None):
        raise SystemExit("el costo unitario requiere su fuente (--fuente-costo)")

    series = cargar()
    region_de = {r["cve_ent"]: r["region_sinave"] for r in csv.DictReader(open(os.path.join(RAIZ, "data", "catalogos", "entidades.csv"), encoding="utf-8"))}
    ultimo = max(d for v in series.values() for d, _ in v)
    lunes_ref = datetime.date.fromisoformat(a.hoy) - datetime.timedelta(days=datetime.date.fromisoformat(a.hoy).weekday())
    nowcast = (lunes_ref - datetime.date.fromisoformat(ultimo)).days // 7
    h_total = nowcast + S
    fechas = [(datetime.date.fromisoformat(ultimo) + datetime.timedelta(weeks=i)).isoformat() for i in range(1, h_total + 1)]

    ys, fechas_hist, faltantes = {}, {}, {}
    for k, v in series.items():
        v = [(d, y) for d, y in v if d >= INICIO_AJUSTE]
        ys[k], faltantes[k] = interpolar([y for _, y in v])
        fechas_hist[k] = [d for d, _ in v]

    crudo = sistema(ys, h_total, region_de)
    ev = evaluar(ys, region_de, h=h_total)

    ini = nowcast
    salida = {"version": "e5-pronostico-v2", "fecha_referencia": a.hoy, "ultima_observacion": ultimo, "semanas_nowcast": nowcast,
              "pasos_desde_ultima_observacion": h_total,
              "horizonte": {"desde": fechas[ini], "hasta": fechas[-1], "semanas": S}, "inicio_ajuste": INICIO_AJUSTE,
              "costo_unitario_mxn": a.costo_mxn, "fuente_costo": a.fuente_costo,
              "evaluacion_anidada": {"origenes": [fechas_hist[next(iter(ys))][o] for o in ev["origenes"]], "horizonte_pasos": ev["horizonte"],
                                     "por_nivel": ev["por_nivel"],
                                     "nota": "Sistema completo (selección, bandas, respaldo y reconciliación) corrido solo con datos previos a cada origen y comparado con las semanas reales siguientes. Pocos orígenes: es una evaluación orientativa."},
              "advertencias": ["Bandas 80/95 exploratorias: su cobertura fuera de muestra está en la evaluación anidada; no tienen cobertura nominal garantizada.",
                               "Bandas marginales por serie y semana. Los escenarios conservador y estrés suman límites semanales: no son un intervalo conjunto del total.",
                               "Casos notificados al SINAVE, no casos reales."],
              "series": []}
    resumen_modelos = {}
    for k, c in sorted(crudo.items()):
        r = lambda v: [int(round(max(x, 0))) for x in v]
        f52 = c["f_rec"][ini:]
        serie = {"tipo": k[0], "nivel": k[1], "id": k[2], "sexo": k[3], "modelo": c["modelo"], "semanas_interpoladas": faltantes[k],
                 "seleccion": c["seleccion"], "evaluacion_smape": ev["por_serie"][k],
                 "historia": {"fechas": fechas_hist[k][-2 * S:], "casos": r(c["y"][-2 * S:])},
                 "pronostico": {"fechas": fechas, "punto": r(c["f_rec"]), "lo80": r(c["lo80_rec"]), "hi80": r(c["hi80_rec"]),
                                "lo95": r(c["lo95_rec"]), "hi95": r(c["hi95_rec"])},
                 "total_52": {"punto": int(round(f52.sum())), "escenario_conservador_suma_hi80": int(round(c["hi80_rec"][ini:].sum())),
                              "escenario_estres_suma_hi95": int(round(c["hi95_rec"][ini:].sum()))}}
        if a.costo_mxn is not None:
            serie["presupuesto_52_mxn"] = {kk: round(v * a.costo_mxn, 2) for kk, v in serie["total_52"].items()}
        resumen_modelos[c["modelo"].split(" ")[0]] = resumen_modelos.get(c["modelo"].split(" ")[0], 0) + 1
        salida["series"].append(serie)
    salida["modelos_elegidos"] = resumen_modelos
    salida["nombres"] = {r["cve_ent"]: r["nombre_corto"] for r in csv.DictReader(open(os.path.join(RAIZ, "data", "catalogos", "entidades.csv"), encoding="utf-8"))}
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w") as fo:
        json.dump(salida, fo, ensure_ascii=False, separators=(",", ":"))
    for t in ("diabetes_t1", "diabetes_t2"):
        n_ = next(s for s in salida["series"] if s["tipo"] == t and s["nivel"] == "nacional" and s["sexo"] == "general")
        print(f"{t} nacional general · {n_['modelo']} · evaluación h1-63 {n_['evaluacion_smape']} · total 52 semanas {n_['total_52']}")
    print("modelos elegidos:", resumen_modelos, "· pasos", h_total, "· orígenes de evaluación", salida["evaluacion_anidada"]["origenes"])
    print(json.dumps(salida["evaluacion_anidada"]["por_nivel"], ensure_ascii=False))


if __name__ == "__main__":
    main()
