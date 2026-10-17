"""Prueba de dos máquinas: servicio en OTRO proceso con evidencia, hospital con registros reales del CDC y auditoría.

En CI corre en una sola máquina, así que la auditoría estricta debe fallar en la comprobación de dos máquinas y el
ensayo (--permitir-misma-maquina) debe aprobar. Además se comprueba que la auditoría detecta evidencia alterada,
un resultado en claro del lado del servicio y una llave privada en el proceso del servicio.
"""
import argparse, json, os, socket, subprocess, sys, threading, time
import pytest
from tamizaje import dos_maquinas, hospital, protocolo, secretos, servicio
from tamizaje.rutas import MODELO_JSON, RAIZ


def _puerto_libre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def corrida(tmp_path_factory):
    d = tmp_path_factory.mktemp("dos_maquinas")
    secretos.generar(str(d / "servicio"), exportar_hospital=str(d / "para_hospital"))
    c = d / "servicio" / "certs"
    assert not (c / "hospital.key").exists() and (d / "para_hospital" / "hospital.key").exists()
    puerto = _puerto_libre()
    env = {**os.environ, "PYTHONPATH": os.path.join(RAIZ, "src"), "SERVICIO_HOST": "127.0.0.1", "SERVICIO_PUERTO": str(puerto),
           "SERVICIO_CERT": str(c / "servicio.pem"), "SERVICIO_LLAVE": str(c / "servicio.key"), "SERVICIO_CA_CLIENTES": str(c / "ca.pem"),
           "MODELO_JSON": MODELO_JSON, "SERVICIO_EVIDENCIA": str(d / "evidencia")}
    log = open(d / "servicio.log", "w")
    proc = subprocess.Popen([sys.executable, "-m", "tamizaje.servicio"], env=env, stdout=log, stderr=subprocess.STDOUT)
    try:
        for _ in range(100):
            if (d / "evidencia" / "servicio_inicio.json").exists():
                try:
                    socket.create_connection(("127.0.0.1", puerto), timeout=0.2).close()
                    break
                except OSError:
                    pass
            time.sleep(0.1)
        dos_maquinas.correr_hospital(argparse.Namespace(servicio=f"https://localhost:{puerto}", certs=str(d / "para_hospital"),
                                                        salida=str(d / "hospital"), n=8, sin_evidencia=False))
        dos_maquinas.correr_hospital(argparse.Namespace(servicio=f"https://localhost:{puerto}", certs=str(d / "para_hospital"),
                                                        salida=str(d / "hospital_cdc"), n=8, datos="cdc", sin_evidencia=False))
    finally:
        proc.terminate(); proc.wait(10); log.close()
    return d


def _auditar(d, salida, *extra):
    a = argparse.Namespace(servicio=str(d / "evidencia"), hospital=str(d / "hospital"), log_servicio=[str(d / "servicio.log")],
                           salida=str(salida), muestras=1, permitir_misma_maquina="misma" in extra)
    rc = dos_maquinas.auditar(a)
    reportes = sorted(p for p in salida.glob("auditoria_*.json") if p.name.count("_") == 1)
    return rc, json.loads(reportes[-1].read_text())


def test_ensayo_aprueba_y_estricta_exige_dos_maquinas(corrida, tmp_path):
    rc, rep = _auditar(corrida, tmp_path / "a", "misma")
    assert rc == 0 and rep["aprobada"] and rep["veredicto"].startswith("ENSAYO")
    assert rep["hospital"]["exactitud"]["enteros_identicos"] == 8
    assert rep["hospital"]["muestra"]["datos"] == "sintetico"
    assert rep["hospital"]["metricas_misma_muestra"] is None
    rc, rep = _auditar(corrida, tmp_path / "b")
    fallas = [c["clave"] for c in rep["comprobaciones"] if not c["ok"]]
    assert rc == 1 and fallas == ["dos_maquinas"]


def test_nombres_diferentes_del_mismo_host_no_acreditan_dos_maquinas(corrida, tmp_path):
    p = corrida / "hospital" / "resumen_hospital.json"
    original = p.read_text()
    try:
        m = json.loads(original)
        m["maquina"] = "otro-contenedor-en-el-mismo-host"
        p.write_text(json.dumps(m))
        rc, rep = _auditar(corrida, tmp_path)
        assert rc == 1
        assert any(c["clave"] == "dos_maquinas" and not c["ok"] for c in rep["comprobaciones"])
    finally:
        p.write_text(original)


def test_cdc_es_benchmark_explicito_con_etiquetas(corrida):
    m = json.loads((corrida / "hospital_cdc" / "resumen_hospital.json").read_text())
    assert m["muestra"]["datos"] == "cdc" and m["exactitud"]["enteros_identicos"] == 8
    assert m["metricas_misma_muestra"]["flotante"]["roc_auc"] == m["metricas_misma_muestra"]["cifrado"]["roc_auc"]


def test_detecta_bitacora_del_hospital_alterada(corrida, tmp_path):
    p = corrida / "hospital" / "bitacora_hospital.jsonl"
    original = p.read_bytes()
    try:
        p.write_bytes(original + b"\n")
        rc, rep = _auditar(corrida, tmp_path, "misma")
        assert rc == 1 and any(c["clave"] == "integridad" and not c["ok"] for c in rep["comprobaciones"])
    finally:
        p.write_bytes(original)


def test_detecta_modelo_del_servicio_distinto(corrida, tmp_path):
    p = corrida / "evidencia" / "servicio_inicio.json"
    original = p.read_text()
    try:
        m = json.loads(original); m["modelo_sha256"] = "0" * 64
        p.write_text(json.dumps(m))
        rc, rep = _auditar(corrida, tmp_path, "misma")
        assert rc == 1 and any(c["clave"] == "versiones" and not c["ok"] for c in rep["comprobaciones"])
    finally:
        p.write_text(original)


def test_detecta_evidencia_alterada(corrida, tmp_path):
    # Seleccionar una petición de esta corrida, no un UUID aleatorio de otro benchmark.
    rid = json.loads((corrida / "hospital" / "bitacora_hospital.jsonl").read_text().splitlines()[-1])["id"]
    sol = corrida / "evidencia" / "solicitudes" / (rid + ".solicitud.json")
    original = sol.read_bytes()
    try:
        sol.write_bytes(original.replace(b'"exponente": 0', b'"exponente": 0, "HighBP": 1'))
        rc, rep = _auditar(corrida, tmp_path, "misma")
        assert rc == 1 and {c["clave"] for c in rep["comprobaciones"] if not c["ok"]} >= {"bytes", "estructura"}
    finally:
        sol.write_bytes(original)


def test_detecta_resultado_en_claro_en_el_servicio(corrida, tmp_path):
    z = json.loads((corrida / "hospital" / "bitacora_hospital.jsonl").read_text().splitlines()[-1])["z_descifrado"]
    with open(corrida / "servicio.log", "a") as f:
        f.write(f"depuración: z={z}\n")
    try:
        rc, rep = _auditar(corrida, tmp_path, "misma")
        assert rc == 1 and [c["clave"] for c in rep["comprobaciones"] if not c["ok"]] == ["sin_claro"]
    finally:
        lineas = (corrida / "servicio.log").read_text().splitlines(keepends=True)
        (corrida / "servicio.log").write_text("".join(lineas[:-1]))


def test_la_comprobacion_de_llave_detecta_un_hospital_en_el_mismo_proceso(tmp_path, modelo, llaves):
    """Si el servicio corriera junto al hospital, su evidencia lo delataría."""
    secretos.generar(str(tmp_path))
    c = tmp_path / "certs"
    srv, _ = servicio.crear_servidor("127.0.0.1", 0, modelo, str(c / "servicio.pem"), str(c / "servicio.key"), str(c / "ca.pem"),
                                     evidencia=str(tmp_path / "ev"))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        h = protocolo.Hospital(modelo, llaves=llaves)  # llave privada en ESTE proceso
        cli = hospital.ClienteServicio(f"https://localhost:{srv.server_address[1]}", str(c / "ca.pem"), str(c / "hospital.pem"), str(c / "hospital.key"))
        assert cli.salud()["evidencia"] is True
        sol, _ = h.preparar({n: 0 if n not in ("BMI", "GenHlth", "Age", "Education", "Income") else 12 if n == "BMI" else 1 for n in modelo["variables"]})
        cli.evaluar(sol)
    finally:
        srv.shutdown()
    e = json.loads((tmp_path / "ev" / "auditoria_servicio.jsonl").read_text())
    assert e["llave_privada_en_memoria"] is True and e["tls"] == "TLSv1.3" and e["cliente_cn"] == "hospital"


def test_certificado_con_ip_del_servicio(tmp_path):
    from cryptography import x509
    secretos.generar(str(tmp_path), san_extra=["148.100.77.9", "vm-servicio"])
    cert = x509.load_pem_x509_certificate((tmp_path / "certs" / "servicio.pem").read_bytes())
    san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
    assert "vm-servicio" in san.get_values_for_type(x509.DNSName)
    assert "148.100.77.9" in [str(i) for i in san.get_values_for_type(x509.IPAddress)]
