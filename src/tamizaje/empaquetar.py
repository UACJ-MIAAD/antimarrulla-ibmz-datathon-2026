"""Arma los paquetes de entrega en dist/, con manifiesto de hashes, y los verifica al terminar.

Dos tipos (el código entregable oficial es el repo público de GitHub):
- documental: PDF, deck, guion, video (estado y storyboard), flowchart, texto para Hack2skill, docs y evidencias.
- codigo: alternativa al link del repo (la guía acepta un zip): fuente, pruebas, Makefile, Docker, requirements,
  licencia, artefactos y los datos públicos que necesitan `make verify` y `make pronostico`.
Nunca incluye secretos, data/raw, auditorías locales, .git, .venv, dist ni el PPTX personal.

Modo borrador (por defecto): el nombre del archivo dice BORRADOR y el manifiesto lista lo que falta.
Modo final (--final): falla con la lista concreta si falta evidencia obligatoria o hay cambios relevantes sin commit.

Uso: python -m tamizaje.empaquetar [--tipo documental|codigo|ambos] [--final]
"""
import argparse, datetime, glob, hashlib, json, os, re, zipfile
from . import procedencia
from .rutas import RAIZ

EXCLUIR = re.compile(r"(^|/)(\.git|\.venv|__pycache__|dist|data/raw)(/|$)|\.(key|pem)$|AUDITORIA|PLAN_REAUDITORIA|submission/Los_Antimarrulla_Pitch\.pptx$")
DOCUMENTAL = [
    "submission/Los Antimarrulla_IBM Z Datathon 2026 Project.pdf", "submission/Los_Antimarrulla_Pitch_Tamizaje.pptx",
    "submission/PITCH.md", "submission/SLIDES.md", "submission/VIDEO.md", "submission/HACK2SKILL.md",
    "submission/flowchart/arquitectura.pdf", "submission/flowchart/arquitectura.png", "submission/flowchart/arquitectura.svg",
    "README.md", "LICENSE", "docs/PROYECTO.md", "docs/MODELO_DATOS.md", "docs/LINUXONE.md", "docs/ENSANUT_EXPERIMENTO.md",
    "docs/PRONOSTICO.md", "docs/CHECKLIST_ENTREGA.md", "docs/REVISION.md", "docs/CRONOLOGIA.md",
    "artefactos/modelo/modelo_logistico_v1.json", "artefactos/modelo/esquema_cdc21_v1.json",
    "artefactos/metricas/modelo_logistico_v1.json", "artefactos/metricas/ensanut_exploratorio_v1.json",
    "artefactos/pronostico/e5_pronostico_v1.json",
]
DOCUMENTAL_GLOB = ["submission/evidencias/README.md", "submission/evidencias/metricas/*", "submission/evidencias/local/*",
                   "submission/evidencias/linuxone/*", "submission/evidencias/labs/*"]
CODIGO_GLOB = ["src/**/*.py", "src/**/*.html", "src/datos/README.md", "tests/*.py", "docker/*", "artefactos/**/*.json",
               "data/cdc_891/*", "data/sinave/tipo1/products.csv", "data/sinave/tipo2/products.csv", "data/catalogos/entidades.csv"]
CODIGO = ["Makefile", "requirements.txt", ".dockerignore", "LICENSE", "README.md", "docs/LINUXONE.md", "docs/PROYECTO.md"]


def _expandir(globs):
    out = []
    for g in globs:
        out += [os.path.relpath(p, RAIZ) for p in glob.glob(os.path.join(RAIZ, g), recursive=True) if os.path.isfile(p)]
    return out


def faltantes_finales(prov):
    falta = []
    if prov["limpio"] is not True:
        falta.append("procedencia limpia: hay cambios relevantes sin commit")
    med = [json.load(open(p)) for p in glob.glob(os.path.join(RAIZ, "submission/evidencias/metricas/medicion_*.json"))]
    if not any(m.get("entorno_etiqueta", "").startswith("s390x") for m in med):
        falta.append("medición en LinuxONE (s390x): make medir-docker y make medir-api-docker en la VM")
    if not _expandir(["submission/evidencias/linuxone/*"]):
        falta.append("capturas de LinuxONE en submission/evidencias/linuxone/ (docs/LINUXONE.md §4)")
    if not _expandir(["submission/evidencias/labs/*"]):
        falta.append("evidencia de los 2 labs obligatorios en submission/evidencias/labs/")
    h2s = open(os.path.join(RAIZ, "submission/HACK2SKILL.md"), encoding="utf-8").read()
    fila = next((l for l in h2s.splitlines() if l.startswith("| Video")), "")
    if "Pendiente" in fila or "http" not in fila:
        falta.append("link público del video final (≤ 3 min) en submission/HACK2SKILL.md")
    return falta


def armar(tipo, final, prov):
    if tipo == "documental":
        archivos = DOCUMENTAL + _expandir(DOCUMENTAL_GLOB)
    else:
        archivos = CODIGO + _expandir(CODIGO_GLOB)
    archivos = sorted({a for a in archivos if not EXCLUIR.search(a)})
    faltan = [a for a in archivos if not os.path.exists(os.path.join(RAIZ, a))]
    if faltan:
        raise SystemExit(f"faltan archivos del paquete {tipo}: {faltan}")
    pendientes = faltantes_finales(prov)
    if final and pendientes:
        raise SystemExit("modo final rechazado. Falta:\n  - " + "\n  - ".join(pendientes))
    ahora = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(os.path.join(RAIZ, "dist"), exist_ok=True)
    nombre = f"Los_Antimarrulla_{tipo}_{'FINAL' if final else 'BORRADOR'}_{ahora}.zip"
    destino = os.path.join(RAIZ, "dist", nombre)
    manifiesto = {"tipo": tipo, "modo": "final" if final else "borrador", "fecha_utc": ahora, "procedencia": prov,
                  "codigo_oficial": "https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026",
                  "pendientes_para_final": pendientes, "archivos": {}}
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for a in archivos:
            p = os.path.join(RAIZ, a)
            manifiesto["archivos"][a] = procedencia.sha256(p)
            z.write(p, a)
        z.writestr("MANIFIESTO.json", json.dumps(manifiesto, ensure_ascii=False, indent=1))
    # Verificación: lo que quedó dentro coincide con el manifiesto y con los archivos vigentes
    with zipfile.ZipFile(destino) as z:
        man = json.loads(z.read("MANIFIESTO.json"))
        for a, h in man["archivos"].items():
            assert hashlib.sha256(z.read(a)).hexdigest() == h == procedencia.sha256(os.path.join(RAIZ, a)), f"hash distinto: {a}"
    zsha = procedencia.sha256(destino)
    print(f"{tipo}: dist/{nombre} · {len(archivos)} archivos · sha256 {zsha[:16]} · commit {str(prov['commit'])[:10]}{'' if prov['limpio'] else ' (con cambios relevantes sin commit)'}")
    for p in pendientes:
        print("  pendiente para final:", p)
    return destino, zsha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tipo", choices=["documental", "codigo", "ambos"], default="ambos")
    ap.add_argument("--final", action="store_true")
    a = ap.parse_args()
    prov = procedencia.registrar()
    for t in (["documental", "codigo"] if a.tipo == "ambos" else [a.tipo]):
        armar(t, a.final, prov)


if __name__ == "__main__":
    main()
