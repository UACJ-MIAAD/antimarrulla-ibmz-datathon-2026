"""F03: la procedencia identifica el código ejecutado y no esconde cambios relevantes."""
import os, shutil, subprocess
import pytest
from tamizaje import procedencia

sin_git = pytest.mark.skipif(shutil.which("git") is None, reason="la imagen dev no trae git; dentro del contenedor la procedencia viene del Makefile")


def git(d, *a):
    subprocess.run(["git", "-C", str(d), *a], check=True, capture_output=True)


@pytest.fixture()
def repo(tmp_path):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "prueba@example.com"); git(tmp_path, "config", "user.name", "prueba")
    (tmp_path / "src" / "tamizaje").mkdir(parents=True)
    (tmp_path / "src" / "tamizaje" / "a.py").write_text("x = 1\n")
    (tmp_path / "Makefile").write_text("all:\n")
    git(tmp_path, "add", "-A"); git(tmp_path, "commit", "-q", "-m", "inicio")
    return tmp_path


@sin_git
def test_limpio(repo):
    e = procedencia.estado_git(str(repo))
    assert e["relevantes"] == [] and e["commit"]


@sin_git
def test_fuente_nueva_no_versionada_cuenta(repo):
    (repo / "src" / "tamizaje" / "medir.py").write_text("y = 2\n")
    e = procedencia.estado_git(str(repo))
    assert any("src/tamizaje/medir.py" in r for r in e["relevantes"])


@sin_git
def test_fuente_modificada_cuenta(repo):
    (repo / "src" / "tamizaje" / "a.py").write_text("x = 3\n")
    e = procedencia.estado_git(str(repo))
    assert any("src/tamizaje/a.py" in r for r in e["relevantes"])


@sin_git
def test_archivo_personal_ajeno_no_ensucia(repo):
    (repo / "submission").mkdir()
    (repo / "submission" / "Los_Antimarrulla_Pitch.pptx").write_bytes(b"personal")
    e = procedencia.estado_git(str(repo))
    assert e["relevantes"] == [] and any("Los_Antimarrulla_Pitch.pptx" in a for a in e["ajenos"])


def test_hash_de_codigo_cambia_con_el_codigo(tmp_path):
    (tmp_path / "m.py").write_text("a = 1\n")
    h1, n = procedencia.hash_codigo(str(tmp_path))
    (tmp_path / "m.py").write_text("a = 2\n")
    h2, _ = procedencia.hash_codigo(str(tmp_path))
    (tmp_path / "nuevo.py").write_text("b = 1\n")
    h3, n3 = procedencia.hash_codigo(str(tmp_path))
    assert n == 1 and n3 == 2 and len({h1, h2, h3}) == 3


def test_discrepancia_de_hashes():
    reg = procedencia.registrar()
    assert procedencia.verificar(reg) == []
    falso = dict(reg, codigo_sha256="0" * 64, modelo_sha256="1" * 64)
    assert set(procedencia.verificar(falso)) == {"codigo_sha256", "modelo_sha256"}


def test_modo_final_rechaza_cambios_relevantes():
    with pytest.raises(procedencia.ProcedenciaSucia):
        procedencia.exigir_limpio({"limpio": False, "cambios_relevantes": ["?? src/tamizaje/x.py"], "fuente_commit": "git", "commit": "abc"})
    procedencia.exigir_limpio({"limpio": True, "cambios_relevantes": [], "fuente_commit": "git", "commit": "abc"})


def test_contenedor_sin_git_usa_lo_declarado(tmp_path, monkeypatch):
    monkeypatch.setenv("TAMIZAJE_COMMIT", "abc123"); monkeypatch.setenv("TAMIZAJE_CAMBIOS_RELEVANTES", "1")
    e = procedencia.estado_git(str(tmp_path))
    assert e["commit"] == "abc123" and e["relevantes"]


def test_r1_final_rechaza_estado_desconocido_y_commit_ausente():
    with pytest.raises(procedencia.ProcedenciaSucia):
        procedencia.exigir_limpio({"limpio": None, "fuente_commit": "entorno", "commit": "declarado", "cambios_relevantes": None})
    with pytest.raises(procedencia.ProcedenciaSucia):
        procedencia.exigir_limpio({"limpio": True, "fuente_commit": "git", "commit": None, "cambios_relevantes": []})


def test_r1_git_que_falla_da_estado_desconocido(tmp_path):
    (tmp_path / ".git").mkdir()  # carpeta .git rota: git no responde
    e = procedencia.estado_git(str(tmp_path))
    assert e["relevantes"] is None and e["commit"] is None
