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
