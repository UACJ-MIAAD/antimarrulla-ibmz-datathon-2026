"""Épica E5 (extra): pronóstico semanal de casos nuevos de diabetes T1 y T2 y planeación financiera.

Decisiones (ver docs/PRONOSTICO.md):
- 222 series SINAVE (111 por tipo: nacional, 4 regiones y 32 estados × general, hombres y mujeres).
- Ajuste solo con 2022 en adelante (COVID 2020–2021 fuera); semanas no observadas → interpolación lineal (se cuentan).
- Horizonte explícito: la última observación es la semana del 27 jul 2026; se pronostican las semanas que faltan hasta
  la semana de referencia (nowcast) y las 52 semanas siguientes.
- Modelos: ingenuo estacional (misma semana del año anterior) y ETS (Holt-Winters aditivo, tendencia amortiguada, s = 52).
  Selección por serie con backtest de origen móvil (4 orígenes, cada 13 semanas) y SMAPE en horizontes 1–52;
  si la diferencia es menor a 5%, desempata el MAE.
- Intervalos 80% y 95% empíricos: cuantiles de los errores del backtest del modelo elegido, por tramo de horizonte.
- Series con menos de 5 casos en 52 semanas: proporción histórica dentro de su región aplicada al pronóstico regional.
- Coherencia: proporcional de arriba abajo por tipo y sexo (nacional → regiones → estados). "General" no se fuerza
  a ser hombres + mujeres (la fuente trae diferencias marcadas como sex_delta_total_mismatch).
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
SALIDA = os.path.join(ARTEFACTOS, "pronostico", "e5_pronostico_v1.json")


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


def backtest(y):
    n = len(y); res = {m: {"err": [], "smape": [], "mae": []} for m in MODELOS}
    for k in range(4):
        o = n - S - 13 * k
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
                       "smape_1_52": round(float(sm[3]), 2), "mae": round(float(np.mean(r["mae"])), 3), "errores": np.array(r["err"])}
    return out


def elegir(bt):
    a, b = bt["ets"], bt["ingenuo_estacional"]
    if abs(a["smape_1_52"] - b["smape_1_52"]) <= 0.05 * max(a["smape_1_52"], b["smape_1_52"], 1e-9):
        return "ets" if a["mae"] <= b["mae"] else "ingenuo_estacional"
    return "ets" if a["smape_1_52"] < b["smape_1_52"] else "ingenuo_estacional"


def bandas(errores, h_total):
    """Cuantiles empíricos de error por tramo; horizontes > 52 usan el último tramo."""
    q = {}
    for a, b in TRAMOS:
        e = errores[:, a - 1:b].ravel()
        q[(a, b)] = np.quantile(e, [0.025, 0.10, 0.90, 0.975])
    out = []
    for h in range(1, h_total + 1):
        t = next(((a, b) for a, b in TRAMOS if a <= h <= b), TRAMOS[-1])
        out.append(q[t])
    return np.array(out)


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

    crudo = {}
    for k, v in series.items():
        v = [(d, y) for d, y in v if d >= INICIO_AJUSTE]
        y, faltantes = interpolar([y for _, y in v])
        bt = backtest(y)
        modelo = elegir(bt)
        f = MODELOS[modelo](y, h_total) if modelo == "ingenuo_estacional" else None
        if f is None:
            try:
                f = ets(y, h_total)
            except Exception:
                modelo, f = "ingenuo_estacional", snaive(y, h_total)
        b = bandas(bt[modelo]["errores"], h_total)
        crudo[k] = {"y": y, "fechas_hist": [d for d, _ in v], "faltantes": faltantes, "modelo": modelo, "f": f,
                    "lo95": np.clip(f + b[:, 0], 0, None), "lo80": np.clip(f + b[:, 1], 0, None),
                    "hi80": np.clip(f + b[:, 2], 0, None), "hi95": np.clip(f + b[:, 3], 0, None),
                    "backtest": {m: {kk: vv for kk, vv in r.items() if kk != "errores"} for m, r in bt.items()},
                    "casos_52": float(y[-S:].sum())}

    # Respaldo regional para series con pocos casos
    for k, c in crudo.items():
        if k[1] == "estado" and c["casos_52"] < 5:
            reg = crudo[(k[0], "region", region_de[k[2]], k[3])]
            hermanos = [kk for kk in crudo if kk[0] == k[0] and kk[1] == "estado" and kk[3] == k[3] and region_de[kk[2]] == region_de[k[2]]]
            tot = sum(crudo[kk]["y"][-2 * S:].sum() for kk in hermanos)
            prop = c["y"][-2 * S:].sum() / tot if tot else 0.0
            for campo in ("f", "lo95", "lo80", "hi80", "hi95"):
                c[campo] = reg[campo] * prop
            c["modelo"] = f"respaldo_regional ({prop:.4f} de la región)"

    # Coherencia proporcional de arriba abajo por tipo y sexo
    for tipo in {k[0] for k in crudo}:
        for sexo in ("general", "hombres", "mujeres"):
            nac = crudo[(tipo, "nacional", "mx", sexo)]
            regiones = [k for k in crudo if k[0] == tipo and k[1] == "region" and k[3] == sexo]
            suma_r = sum(crudo[k]["f"] for k in regiones)
            for kr in regiones:
                fac_r = np.divide(nac["f"], suma_r, out=np.ones_like(suma_r), where=suma_r > 0)
                rc = crudo[kr]
                for campo in ("f", "lo95", "lo80", "hi80", "hi95"):
                    rc[campo + "_rec"] = rc[campo] * fac_r
                estados = [k for k in crudo if k[0] == tipo and k[1] == "estado" and k[3] == sexo and region_de[k[2]] == kr[2]]
                suma_e = sum(crudo[k]["f"] for k in estados)
                fac_e = np.divide(rc["f_rec"], suma_e, out=np.ones_like(suma_e), where=suma_e > 0)
                for ke in estados:
                    for campo in ("f", "lo95", "lo80", "hi80", "hi95"):
                        crudo[ke][campo + "_rec"] = crudo[ke][campo] * fac_e
            for campo in ("f", "lo95", "lo80", "hi80", "hi95"):
                nac[campo + "_rec"] = nac[campo]

    ini = nowcast  # índice de la primera semana del horizonte de 52
    salida = {"version": "e5-pronostico-v1", "fecha_referencia": a.hoy, "ultima_observacion": ultimo, "semanas_nowcast": nowcast,
              "horizonte": {"desde": fechas[ini], "hasta": fechas[-1], "semanas": S}, "inicio_ajuste": INICIO_AJUSTE,
              "costo_unitario_mxn": a.costo_mxn, "fuente_costo": a.fuente_costo,
              "advertencias": ["Intervalos empíricos marginales por serie y semana (errores de backtest).",
                               "Los escenarios conservador y estrés suman límites semanales marginales: no son un intervalo conjunto del total.",
                               "Casos notificados al SINAVE, no casos reales."],
              "series": []}
    resumen_modelos = {}
    for k, c in sorted(crudo.items()):
        r = lambda v: [int(round(max(x, 0))) for x in v]
        f52 = c["f_rec"][ini:]
        serie = {"tipo": k[0], "nivel": k[1], "id": k[2], "sexo": k[3], "modelo": c["modelo"], "semanas_interpoladas": c["faltantes"],
                 "backtest": c["backtest"], "historia": {"fechas": c["fechas_hist"][-2 * S:], "casos": r(c["y"][-2 * S:])},
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
        n = next(s for s in salida["series"] if s["tipo"] == t and s["nivel"] == "nacional" and s["sexo"] == "general")
        print(f"{t} nacional general · modelo {n['modelo']} · SMAPE 1-52 {n['backtest'][n['modelo']]['smape_1_52'] if n['modelo'] in n['backtest'] else 'n/d'} · total 52 semanas {n['total_52']}")
    print("modelos elegidos:", resumen_modelos, "· horizonte", salida["horizonte"], "· nowcast", nowcast, "semanas")


if __name__ == "__main__":
    main()
