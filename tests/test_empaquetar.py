"""F05: el paquete excluye lo privado y el modo final exige evidencias."""
from tamizaje import empaquetar


def test_excluye_privado():
    for ruta in ["data/raw/ensanut/x.csv", ".git/config", ".venv/bin/python", "submission/Los_Antimarrulla_Pitch.pptx",
                 "docs/AUDITORIA_2.md", "docs/PLAN_REAUDITORIA.md", "x/servicio.key", "dist/a.zip"]:
        assert empaquetar.EXCLUIR.search(ruta), ruta
    for ruta in ["src/tamizaje/protocolo.py", "submission/Los_Antimarrulla_Pitch_Tamizaje.pptx", "data/cdc_891/cdc_diabetes_891.csv"]:
        assert not empaquetar.EXCLUIR.search(ruta), ruta


def test_modo_final_lista_faltantes():
    falta = empaquetar.faltantes_finales({"limpio": False})
    assert any("procedencia" in f for f in falta)
    assert any("video" in f for f in falta)
