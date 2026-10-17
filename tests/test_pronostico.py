"""Extra E5: coherencia del artefacto de pronóstico y funciones base."""
import json, os
import numpy as np
import pytest
from tamizaje import pronostico
from tamizaje.rutas import RAIZ

RUTA = os.path.join(RAIZ, "artefactos", "pronostico", "e5_pronostico_v1.json")


@pytest.fixture(scope="module")
def p():
    if not os.path.exists(RUTA):
        pytest.skip("sin artefacto de pronóstico (make pronostico)")
    return json.load(open(RUTA))


def test_ingenuo_estacional_repite_la_ultima_temporada():
    y = np.arange(104, dtype=float)
    assert list(pronostico.snaive(y, 54)[:3]) == [52.0, 53.0, 54.0] and pronostico.snaive(y, 54)[52] == 52.0


def test_smape():
    assert pronostico.smape(np.array([10.0, 0.0]), np.array([10.0, 0.0])) == 0
    assert pronostico.smape(np.array([10.0]), np.array([0.0])) == 200


def test_222_series_y_horizonte(p):
    assert len(p["series"]) == 222
    assert p["horizonte"]["semanas"] == 52 and p["ultima_observacion"] == "2026-07-27"
    for s in p["series"]:
        assert len(s["pronostico"]["punto"]) == p["semanas_nowcast"] + 52
        assert all(v >= 0 for v in s["pronostico"]["punto"])
        assert all(lo <= pt <= hi for lo, pt, hi in zip(s["pronostico"]["lo95"], s["pronostico"]["punto"], s["pronostico"]["hi95"]))


def test_estados_suman_al_nacional(p):
    for tipo in ("diabetes_t1", "diabetes_t2"):
        for sexo in ("general", "hombres", "mujeres"):
            nac = next(s for s in p["series"] if s["tipo"] == tipo and s["nivel"] == "nacional" and s["sexo"] == sexo)
            est = [s for s in p["series"] if s["tipo"] == tipo and s["nivel"] == "estado" and s["sexo"] == sexo]
            assert len(est) == 32
            suma = sum(s["total_52"]["punto"] for s in est)
            assert abs(suma - nac["total_52"]["punto"]) <= 0.005 * nac["total_52"]["punto"] + 32  # redondeo por serie


def test_sin_costo_no_hay_presupuesto(p):
    if p["costo_unitario_mxn"] is None:
        assert all("presupuesto_52_mxn" not in s for s in p["series"])


# ---- F06: el sistema evaluado es el publicado, hasta h63, sin futuro y reconciliado
REG = {"01": "centro", "02": "centro"}


def _jerarquia(n=240, semilla=0, futuro_raro_desde=None):
    rnd = np.random.default_rng(semilla)
    t = np.arange(n)
    base = lambda nivel: nivel * (1 + 0.3 * np.sin(2 * np.pi * t / 52)) + rnd.normal(0, nivel * 0.05, n)
    e1, e2 = np.clip(base(40), 0, None), np.clip(base(60), 0, None)
    ys = {("x", "estado", "01", "general"): e1, ("x", "estado", "02", "general"): e2,
          ("x", "region", "centro", "general"): e1 + e2, ("x", "nacional", "mx", "general"): e1 + e2}
    if futuro_raro_desde is not None:
        ys = {k: np.concatenate([v[:futuro_raro_desde], np.full(n - futuro_raro_desde, 1e6)]) for k, v in ys.items()}
    return ys


def test_f06_evaluacion_hasta_63_pasos_con_tramos():
    ev = pronostico.evaluar(_jerarquia(), REG, h=63)
    assert ev["horizonte"] == 63 and ev["origenes"]
    for nivel in ("nacional", "region", "estado"):
        assert {"h1-13", "h14-26", "h27-52", "h53-63", "h12-63"} <= set(ev["por_nivel"][nivel])
        assert 0 <= ev["por_nivel"][nivel]["h12-63"]["cobertura_80"] <= 1


def test_f06_sin_futuro_en_el_entrenamiento():
    normal = _jerarquia()
    o = max(pronostico.evaluar(normal, REG, h=63)["origenes"])
    raro = _jerarquia(futuro_raro_desde=o)
    a = pronostico.evaluar(normal, REG, h=63)["pronosticos"][o]
    b = pronostico.evaluar(raro, REG, h=63)["pronosticos"][o]
    for k in a:
        assert np.allclose(a[k], b[k])


def test_f06_pronostico_evaluado_esta_reconciliado():
    ev = pronostico.evaluar(_jerarquia(), REG, h=63)
    for o, f in ev["pronosticos"].items():
        assert np.allclose(f[("x", "estado", "01", "general")] + f[("x", "estado", "02", "general")], f[("x", "nacional", "mx", "general")])


def test_f06_publicado_trae_evaluacion_y_63_pasos(p):
    assert p["pasos_desde_ultima_observacion"] == 63 == p["evaluacion_anidada"]["horizonte_pasos"]
    for s in p["series"]:
        assert "h53-63" in s["evaluacion_smape"] and "seleccion" in s and "backtest" not in s
    assert any("exploratorias" in a for a in p["advertencias"])
