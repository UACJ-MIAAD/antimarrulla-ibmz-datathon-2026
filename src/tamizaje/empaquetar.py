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
    "docs/DOS_MAQUINAS.md", "docs/PLAN_CIERRE.md", "submission/USO_IA.md",
    "artefactos/modelo/modelo_logistico_v1.json", "artefactos/modelo/esquema_cdc21_v1.json",
    "artefactos/metricas/modelo_logistico_v1.json", "artefactos/metricas/ensanut_exploratorio_v1.json",
    "artefactos/pronostico/e5_pronostico_v1.json",
]
DOCUMENTAL_GLOB = ["submission/evidencias/README.md", "submission/evidencias/metricas/*", "submission/evidencias/local/*",
                   "submission/evidencias/linuxone/*", "submission/evidencias/labs/*",
                   "submission/evidencias/dos_maquinas/*"]
DOCUMENTAL_GLOB += ["submission/VIDEO_REGISTRO.json", "submission/evidencias/instancia/*"]
CODIGO_GLOB = ["src/**/*.py", "src/**/*.html", "src/datos/README.md", "tests/*.py", "tests/instance/*.py", "tests/instance/*.sh", "docker/*", "artefactos/**/*.json",
               "data/cdc_891/*", "data/sinave/tipo1/products.csv", "data/sinave/tipo2/products.csv", "data/catalogos/entidades.csv"]
CODIGO = ["Makefile", "requirements.txt", ".dockerignore", "LICENSE", "README.md", "docs/LINUXONE.md", "docs/PROYECTO.md",
          "docs/DOS_MAQUINAS.md", "docs/PLAN_CIERRE.md", "submission/USO_IA.md"]


def _expandir(globs):
    out = []
    for g in globs:
        out += [os.path.relpath(p, RAIZ) for p in glob.glob(os.path.join(RAIZ, g), recursive=True) if os.path.isfile(p)]
    return out


IMAGEN = (b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff")
HOSTS_NO_VALIDOS = ("example.com", "example.org", "localhost", "127.0.0.1")


def _json(ruta):
    try:
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _captura_valida(directorio, nombre):
    """Una captura real: archivo PNG o JPEG de al menos 10 KB dentro del directorio indicado."""
    if not isinstance(nombre, str) or not nombre or "/" in nombre:
        return False
    p = os.path.join(directorio, nombre)
    if not os.path.isfile(p) or os.path.getsize(p) < 10 * 1024:
        return False
    with open(p, "rb") as f:
        cabeza = f.read(8)
    return cabeza.startswith(IMAGEN)


def _medicion_valida(m, modo, modelo_sha):
    """Medición en LinuxONE con resultados completos y procedencia limpia."""
    if not isinstance(m, dict) or m.get("modo") != modo or not str(m.get("entorno_etiqueta", "")).startswith("s390x"):
        return False
    env, prov = m.get("entorno") or {}, m.get("procedencia") or {}
    if env.get("es_linuxone_s390x") is not True or prov.get("limpio") is not True or not prov.get("commit"):
        return False
    if not re.fullmatch(r"[0-9a-f]{64}", str(prov.get("codigo_sha256", ""))) or prov.get("modelo_sha256") != modelo_sha:
        return False
    ex, mu = m.get("exactitud") or {}, m.get("muestra") or {}
    n = mu.get("n")
    if not isinstance(n, int) or n <= 0 or ex.get("enteros_identicos") != n or ex.get("de") != n:
        return False
    if modo == "proceso":
        return ex.get("todos_dentro_de_cota") is True and bool(m.get("microbenchmark_en_proceso"))
    hr = m.get("hospital_remoto") or {}
    return (m.get("cliente_ms") or {}).get("n") == n and hr.get("modelo_sha256") == modelo_sha and hr.get("codigo_igual_al_cliente") is True


def _url_publica(u):
    if not isinstance(u, str) or not u.startswith("https://") or "borrador" in u.lower():
        return False
    host = u.split("/")[2].split(":")[0].lower()
    return bool(host) and not any(host == h or host.endswith("." + h) for h in HOSTS_NO_VALIDOS)


def faltantes_finales(prov, raiz=RAIZ):
    """Lista concreta de lo que impide el modo final. El programa valida registros explícitos y archivos;
    no certifica el contenido de una captura ni el dictamen del organizador."""
    falta = []
    if prov.get("limpio") is not True or not prov.get("commit"):
        falta.append("procedencia: commit identificable y sin cambios relevantes sin commit")
    modelo = os.path.join(raiz, "artefactos/modelo/modelo_logistico_v1.json")
    modelo_sha = procedencia.sha256(modelo) if os.path.exists(modelo) else None
    med = [_json(p) for p in glob.glob(os.path.join(raiz, "submission/evidencias/metricas/medicion_*.json"))]
    for modo, comando in (("proceso", "make medir-docker FINAL=1"), ("api", "make medir-api-docker FINAL=1")):
        if not any(_medicion_valida(m, modo, modelo_sha) for m in med):
            falta.append(f"medición {modo} en LinuxONE con resultados completos y procedencia limpia ({comando} en la VM)")
    d_l1 = os.path.join(raiz, "submission/evidencias/linuxone")
    reg = _json(os.path.join(d_l1, "REGISTRO.json")) or {}
    cap = reg.get("capturas") or {}
    for clave in ("dashboard_community_cloud", "uname_lscpu", "contenedores", "openssl"):
        if not _captura_valida(d_l1, cap.get(clave)):
            falta.append(f"captura de LinuxONE '{clave}' (PNG/JPEG real) declarada en submission/evidencias/linuxone/REGISTRO.json")
    if not reg.get("responsable") or not reg.get("fecha"):
        falta.append("responsable y fecha en submission/evidencias/linuxone/REGISTRO.json")
    d_lab = os.path.join(raiz, "submission/evidencias/labs")
    labs = _json(os.path.join(d_lab, "REGISTRO.json")) or {}
    for lab in ("lab1", "lab2"):
        l = labs.get(lab) or {}
        if l.get("completado") is not True or not l.get("fecha") or not l.get("responsables") or not l.get("capturas") \
                or not all(_captura_valida(d_lab, c) for c in l.get("capturas", [])):
            falta.append(f"{lab} completado, con fecha, responsables y capturas reales en submission/evidencias/labs/REGISTRO.json")
    v = _json(os.path.join(raiz, "submission/VIDEO_REGISTRO.json")) or {}
    dur = v.get("duracion_s")
    if not (_url_publica(v.get("url")) and isinstance(dur, (int, float)) and 0 < dur <= 180 and v.get("audio") is True
            and v.get("voces_autorizadas") is True and v.get("acceso_publico_verificado") is True and v.get("verificado_por") and v.get("fecha")):
        falta.append("video final: URL pública https, duración ≤ 180 s (ffprobe), audio, voces autorizadas y acceso verificado en submission/VIDEO_REGISTRO.json")
    else:
        h2s_p = os.path.join(raiz, "submission/HACK2SKILL.md")
        h2s = open(h2s_p, encoding="utf-8").read() if os.path.exists(h2s_p) else ""
        if v["url"] not in h2s:
            falta.append("el link del video de VIDEO_REGISTRO.json no aparece en submission/HACK2SKILL.md")
    rev_p = os.path.join(raiz, "docs/REVISION.md")
    filas = []
    if os.path.exists(rev_p):
        for l in open(rev_p, encoding="utf-8"):
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            if len(c) >= 3 and c[0] and c[0] not in ("Integrante", "_pendiente_") and not c[0].startswith("---") and c[1]:
                filas.append(c)
    if not filas:
        falta.append("revisión de otro integrante registrada (nombre y fecha) en docs/REVISION.md")
    ia_p = os.path.join(raiz, "submission/USO_IA.md")
    ia = open(ia_p, encoding="utf-8").read().strip() if os.path.exists(ia_p) else ""
    if not ia or "USO_IA.md" not in (open(os.path.join(raiz, "submission/HACK2SKILL.md"), encoding="utf-8").read()
                                   if os.path.exists(os.path.join(raiz, "submission/HACK2SKILL.md")) else ""):
        falta.append("declaración de uso de IA en submission/USO_IA.md enlazada desde HACK2SKILL.md")
    return falta


def armar(tipo, final, prov):
    if tipo == "documental":
        archivos = DOCUMENTAL + _expandir(DOCUMENTAL_GLOB)
    else:
        archivos = CODIGO + _expandir(CODIGO_GLOB)
    archivos = sorted({a for a in archivos if not EXCLUIR.search(a)})
    opcionales = {"submission/USO_IA.md"}  # borrador local, fuera de git hasta que el equipo decida dónde va
    archivos = [a for a in archivos if a not in opcionales or os.path.exists(os.path.join(RAIZ, a))]
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
