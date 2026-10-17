"""Referencia de tiempo en claro sobre la misma muestra del experimento cifrado."""
import pytest
from tamizaje import medir, sinteticos, esquema


def test_benchmark_claro_reporta_tiempos_y_misma_muestra(modelo):
    xs = [[sinteticos.aleatorio(k)[n] for n in esquema.NOMBRES] for k in range(4)]
    r = medir.benchmark_claro(modelo, xs, repeticiones=3)
    assert r["n_pacientes"] == 4 and len(r["muestra_sha256"]) == 64
    for nombre in ("flotante", "punto_fijo"):
        assert r[nombre]["n_evaluaciones"] == 12
        assert 0 < r[nombre]["p50_us"] <= r[nombre]["p95_us"]


def test_benchmark_rechaza_muestra_vacia(modelo):
    with pytest.raises(ValueError):
        medir.benchmark_claro(modelo, [])


def test_api_final_rechaza_codigo_remoto_distinto(modelo, monkeypatch):
    import argparse, io, json, urllib.request
    from tamizaje import procedencia
    from tamizaje.rutas import MODELO_JSON
    estado = {"modelo_sha256": procedencia.sha256(MODELO_JSON), "codigo_sha256": "0" * 64}
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **kw: io.BytesIO(json.dumps(estado).encode()))
    a = argparse.Namespace(url="http://127.0.0.1:8080", final=True)
    with pytest.raises(SystemExit, match="código del hospital"):
        medir.modo_api(a, modelo, {"codigo_sha256": "1" * 64}, {}, None, "local")
