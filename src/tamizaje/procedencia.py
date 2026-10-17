"""Procedencia de una ejecución: qué código, modelo y datos corrieron de verdad.

- Hash del código ejecutado (todos los .py y la UI de src/tamizaje, en orden), del modelo, las particiones y el CSV del CDC.
- Estado de git separando lo RELEVANTE para el experimento (src/, tests/, docker/, Makefile, requirements.txt,
  artefactos/modelo, artefactos/particiones) de archivos AJENOS (por ejemplo, un PPTX personal sin versionar).
  Los archivos relevantes sin versionar o modificados cuentan como cambios: no se esconden.
- En contenedor no hay .git: el commit llega por TAMIZAJE_COMMIT y la imagen por TAMIZAJE_IMAGEN; el hash del código
  se calcula sobre el código que hay dentro de la imagen.
"""
import hashlib, os, subprocess
from .rutas import MODELO_JSON, PARTICIONES, CDC_CSV, RAIZ

CODIGO = os.path.dirname(os.path.abspath(__file__))
RELEVANTES = ("src/", "tests/", "docker/", "Makefile", "requirements.txt", ".dockerignore", "artefactos/modelo/", "artefactos/particiones/")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def hash_codigo(directorio=CODIGO):
    """Hash estable del código ejecutable: ruta relativa + contenido de cada .py/.html, ordenados."""
    h = hashlib.sha256()
    archivos = []
    for base, dirs, nombres in os.walk(directorio):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        for n in sorted(nombres):
            if n.endswith((".py", ".html")):
                archivos.append(os.path.join(base, n))
    for p in sorted(archivos):
        rel = os.path.relpath(p, directorio).replace(os.sep, "/")
        h.update(rel.encode() + b"\0" + open(p, "rb").read() + b"\0")
    return h.hexdigest(), len(archivos)


def _git(raiz, *a):
    try:
        r = subprocess.run(["git", "-C", raiz, *a], capture_output=True, text=True, timeout=30)
        return r.stdout if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def es_relevante(ruta):
    return ruta.startswith(RELEVANTES) or ruta in RELEVANTES


def estado_git(raiz=RAIZ):
    """Regresa commit y cambios, separando relevantes de ajenos. Sin .git, usa TAMIZAJE_COMMIT."""
    if not os.path.isdir(os.path.join(raiz, ".git")):
        declarado = os.environ.get("TAMIZAJE_CAMBIOS_RELEVANTES")
        rel = None if declarado is None else ([] if declarado == "0" else ["declarado por el Makefile al construir la imagen: hay cambios relevantes sin commit"])
        return {"fuente": "entorno", "commit": os.environ.get("TAMIZAJE_COMMIT"), "relevantes": rel, "ajenos": None,
                "nota": "sin .git (contenedor): commit y estado los declara el Makefile; el código se identifica por su hash dentro de la imagen"}
    commit = (_git(raiz, "rev-parse", "HEAD") or "").strip() or None
    salida = _git(raiz, "status", "--porcelain", "--untracked-files=all")
    if commit is None or salida is None:  # git falló: el estado es desconocido, no limpio
        return {"fuente": "git", "commit": commit, "relevantes": None, "ajenos": None, "nota": "git no respondió: estado desconocido"}
    relevantes, ajenos = [], []
    for linea in salida.splitlines():
        estado, ruta = linea[:2], linea[3:].strip().strip('"')
        if " -> " in ruta:
            ruta = ruta.split(" -> ", 1)[1]
        (relevantes if es_relevante(ruta) else ajenos).append(f"{estado.strip() or '?'} {ruta}")
    return {"fuente": "git", "commit": commit, "relevantes": relevantes, "ajenos": ajenos}


def registrar(raiz=RAIZ):
    codigo, n = hash_codigo()
    g = estado_git(raiz)
    return {
        "commit": g["commit"], "fuente_commit": g["fuente"],
        "limpio": (g["relevantes"] == []) if g["relevantes"] is not None else None,
        "cambios_relevantes": g["relevantes"], "archivos_ajenos_al_experimento": g["ajenos"],
        "codigo_sha256": codigo, "codigo_archivos": n,
        "modelo_sha256": sha256(MODELO_JSON), "particiones_sha256": sha256(PARTICIONES),
        "cdc_sha256": sha256(CDC_CSV) if os.path.exists(CDC_CSV) else None,
        "imagen": os.environ.get("TAMIZAJE_IMAGEN"),
        **({"nota": g["nota"]} if "nota" in g else {}),
    }


def verificar(registro, raiz=RAIZ):
    """Compara un registro con el estado actual; regresa la lista de discrepancias (vacía si coincide)."""
    actual = registrar(raiz)
    return [k for k in ("codigo_sha256", "modelo_sha256", "particiones_sha256", "cdc_sha256")
            if registro.get(k) and registro.get(k) != actual.get(k)]


class ProcedenciaSucia(RuntimeError):
    pass


def exigir_limpio(reg):
    """Modo final: exige commit presente y limpieza DEMOSTRADA (limpio is True). Desconocido o sucio se rechaza."""
    if not reg.get("commit"):
        raise ProcedenciaSucia("modo final: no hay commit identificable (git falló o el contenedor no declara TAMIZAJE_COMMIT)")
    if reg.get("limpio") is not True:
        detalle = ", ".join(reg.get("cambios_relevantes") or []) or "estado de cambios desconocido"
        raise ProcedenciaSucia("modo final: no está demostrado que no haya cambios relevantes sin commit: " + detalle)
