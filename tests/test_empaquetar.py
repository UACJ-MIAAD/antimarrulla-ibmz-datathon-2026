"""F05/R2: el modo final valida contenido y requisitos, no solo presencia."""
import json, os
import pytest
from tamizaje import empaquetar, procedencia

PROV = {"limpio": True, "commit": "a" * 40, "codigo_sha256": "c" * 64}
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 12000


def test_excluye_privado():
    for ruta in ["data/raw/ensanut/x.csv", ".git/config", ".venv/bin/python", "submission/Los_Antimarrulla_Pitch.pptx",
                 "docs/AUDITORIA_2.md", "docs/PLAN_REAUDITORIA.md", "x/servicio.key", "dist/a.zip"]:
        assert empaquetar.EXCLUIR.search(ruta), ruta
    for ruta in ["src/tamizaje/protocolo.py", "submission/Los_Antimarrulla_Pitch_Tamizaje.pptx", "data/cdc_891/cdc_diabetes_891.csv"]:
        assert not empaquetar.EXCLUIR.search(ruta), ruta


def w(raiz, rel, contenido):
    p = os.path.join(raiz, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb" if isinstance(contenido, bytes) else "w") as f:
        f.write(contenido if isinstance(contenido, (bytes, str)) else json.dumps(contenido))


def completo(raiz):
    w(raiz, "artefactos/modelo/modelo_logistico_v1.json", "{}")
    msha = procedencia.sha256(os.path.join(raiz, "artefactos/modelo/modelo_logistico_v1.json"))
    base = {"entorno_etiqueta": "s390x", "entorno": {"es_linuxone_s390x": True},
            "procedencia": {"limpio": True, "commit": "a" * 40, "codigo_sha256": "c" * 64, "modelo_sha256": msha}}
    w(raiz, "submission/evidencias/metricas/medicion_proceso_s390x_1.json", {**base, "modo": "proceso", "muestra": {"n": 2000},
      "exactitud": {"enteros_identicos": 2000, "de": 2000, "todos_dentro_de_cota": True}, "microbenchmark_en_proceso": {"x": 1}})
    w(raiz, "submission/evidencias/metricas/medicion_api_s390x_1.json", {**base, "modo": "api", "muestra": {"n": 200},
      "exactitud": {"enteros_identicos": 200, "de": 200}, "cliente_ms": {"n": 200},
      "hospital_remoto": {"modelo_sha256": msha, "codigo_igual_al_cliente": True}})
    caps = {k: f"{k}.png" for k in ("dashboard_community_cloud", "uname_lscpu", "contenedores", "openssl")}
    for f in caps.values():
        w(raiz, f"submission/evidencias/linuxone/{f}", PNG)
    w(raiz, "submission/evidencias/linuxone/REGISTRO.json", {"responsable": "Álvaro", "fecha": "2026-10-18", "capturas": caps})
    for f in ("l1.png", "l2.png"):
        w(raiz, f"submission/evidencias/labs/{f}", PNG)
    w(raiz, "submission/evidencias/labs/REGISTRO.json", {
        "lab1": {"completado": True, "fecha": "2026-10-17", "responsables": ["Carlos"], "capturas": ["l1.png"]},
        "lab2": {"completado": True, "fecha": "2026-10-17", "responsables": ["Yazmin"], "capturas": ["l2.png"]}})
    url = "https://youtu.be/abcdefghijk"
    w(raiz, "submission/VIDEO_REGISTRO.json", {"url": url, "duracion_s": 172.0, "audio": True, "voces_autorizadas": True,
      "acceso_publico_verificado": True, "verificado_por": "Javier", "fecha": "2026-10-18"})
    w(raiz, "submission/HACK2SKILL.md", f"| Video | {url} |\n| Uso de IA | [Declaración](USO_IA.md) |\n")
    w(raiz, "submission/USO_IA.md", "Uso declarado de asistentes y tareas; revisión humana documentada por el equipo.")
    w(raiz, "docs/REVISION.md", "| Integrante | Fecha y hora | Qué corrió | Comentarios |\n|---|---|---|---|\n| Carlos | 2026-10-18 02:00 | make verify | ok |\n")


def test_r2_completo_pasa(tmp_path):
    completo(str(tmp_path))
    assert empaquetar.faltantes_finales(PROV, raiz=str(tmp_path)) == []


def test_r2_casos_del_auditor_rechazados(tmp_path):
    r = str(tmp_path)
    w(r, "artefactos/modelo/modelo_logistico_v1.json", "{}")
    w(r, "submission/evidencias/metricas/medicion_s390x.json", {"entorno_etiqueta": "s390x"})
    w(r, "submission/evidencias/linuxone/README.txt", "pendiente")
    w(r, "submission/evidencias/labs/lab1.txt", "lab 1 sin completar")
    w(r, "submission/HACK2SKILL.md", "| Video | https://example.com/borrador |\n")
    w(r, "submission/VIDEO_REGISTRO.json", {"url": "https://example.com/borrador", "duracion_s": 170})
    falta = " ".join(empaquetar.faltantes_finales(PROV, raiz=r))
    for esperado in ("medición proceso", "medición api", "dashboard_community_cloud", "lab1", "lab2", "video final", "revisión"):
        assert esperado in falta, esperado


@pytest.mark.parametrize("romper", ["sin_resultados", "lab2_falso", "captura_txt", "video_largo", "video_sin_audio", "sin_revision", "api_otro_codigo"])
def test_r2_cada_falla_se_detecta(tmp_path, romper):
    r = str(tmp_path); completo(r)
    if romper == "sin_resultados":
        p = os.path.join(r, "submission/evidencias/metricas/medicion_proceso_s390x_1.json"); m = json.load(open(p)); m["exactitud"]["enteros_identicos"] = 1999; w(r, p[len(r) + 1:], m)
    elif romper == "lab2_falso":
        p = os.path.join(r, "submission/evidencias/labs/REGISTRO.json"); m = json.load(open(p)); m["lab2"]["completado"] = False; w(r, p[len(r) + 1:], m)
    elif romper == "captura_txt":
        w(r, "submission/evidencias/linuxone/dashboard_community_cloud.png", "texto, no imagen" * 1000)
    elif romper in ("video_largo", "video_sin_audio"):
        p = os.path.join(r, "submission/VIDEO_REGISTRO.json"); m = json.load(open(p))
        m.update({"duracion_s": 181} if romper == "video_largo" else {"audio": False}); w(r, p[len(r) + 1:], m)
    elif romper == "sin_revision":
        w(r, "docs/REVISION.md", "| Integrante | Fecha |\n|---|---|\n| _pendiente_ | |\n")
    elif romper == "api_otro_codigo":
        p = os.path.join(r, "submission/evidencias/metricas/medicion_api_s390x_1.json"); m = json.load(open(p)); m["hospital_remoto"]["codigo_igual_al_cliente"] = False; w(r, p[len(r) + 1:], m)
    assert empaquetar.faltantes_finales(PROV, raiz=r), romper


def test_r2_procedencia_desconocida_rechazada(tmp_path):
    completo(str(tmp_path))
    assert empaquetar.faltantes_finales({"limpio": None, "commit": "a"}, raiz=str(tmp_path))


def test_sin_declaracion_ia_no_es_paquete_final(tmp_path):
    completo(str(tmp_path))
    os.unlink(tmp_path / "submission/USO_IA.md")
    assert any("uso de IA" in f for f in empaquetar.faltantes_finales(PROV, raiz=str(tmp_path)))
