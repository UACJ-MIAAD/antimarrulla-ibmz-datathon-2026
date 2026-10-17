"""Arma el paquete de entrega en dist/ con un manifiesto de hashes y el commit.

Incluye el PDF, el flowchart, el guion, el texto para Hack2skill, las métricas y la evidencia disponible.
No sustituye el envío en Hack2skill ni la revisión de los 4.

Uso: python -m tamizaje.empaquetar
"""
import datetime, glob, hashlib, json, os, subprocess, zipfile
from .rutas import RAIZ

ARCHIVOS = [
    "submission/Los Antimarrulla_IBM Z Datathon 2026 Project.pdf", "submission/Los_Antimarrulla_Pitch_Tamizaje.pptx",
    "submission/PITCH.md", "submission/HACK2SKILL.md", "submission/flowchart/arquitectura.pdf", "submission/flowchart/arquitectura.png",
    "README.md", "docs/PROYECTO.md", "docs/LINUXONE.md", "docs/CHECKLIST_ENTREGA.md",
    "artefactos/modelo/modelo_logistico_v1.json", "artefactos/modelo/esquema_cdc21_v1.json", "artefactos/metricas/modelo_logistico_v1.json",
]
PATRONES = ["submission/evidencias/metricas/*", "submission/evidencias/local/*", "submission/evidencias/linuxone/*"]


def main():
    commit = subprocess.run(["git", "-C", RAIZ, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    sucio = bool(subprocess.run(["git", "-C", RAIZ, "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True).stdout.strip())
    archivos = list(ARCHIVOS) + sorted(os.path.relpath(p, RAIZ) for pat in PATRONES for p in glob.glob(os.path.join(RAIZ, pat)))
    faltan = [a for a in archivos if not os.path.exists(os.path.join(RAIZ, a))]
    if faltan:
        raise SystemExit(f"faltan archivos: {faltan}")
    ahora = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(os.path.join(RAIZ, "dist"), exist_ok=True)
    destino = os.path.join(RAIZ, "dist", f"Los_Antimarrulla_entrega_{ahora}.zip")
    manifiesto = {"commit": commit, "cambios_sin_commit": sucio, "fecha_utc": ahora, "archivos": {}}
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for a in archivos:
            p = os.path.join(RAIZ, a)
            manifiesto["archivos"][a] = hashlib.sha256(open(p, "rb").read()).hexdigest()
            z.write(p, a)
        pendientes = ["video de máx. 3 min (grabar, subir y probar el link)", "medición y capturas en LinuxONE (docs/LINUXONE.md)",
                      "evidencia de los 2 labs obligatorios", "revisión de los 4 integrantes", "envío del líder registrado en Hack2skill"]
        manifiesto["pendientes_externos"] = pendientes
        z.writestr("MANIFIESTO.json", json.dumps(manifiesto, ensure_ascii=False, indent=1))
    print(f"paquete: {os.path.relpath(destino, RAIZ)} · {len(archivos)} archivos · commit {commit[:10]}{' (con cambios sin commit)' if sucio else ''}")
    for p in pendientes:
        print("  pendiente:", p)


if __name__ == "__main__":
    main()
