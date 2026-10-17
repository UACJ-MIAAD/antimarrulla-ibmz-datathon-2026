"""Integración: UI/API del hospital → TLS 1.3 mutuo → servicio de riesgo real → descifrado → bóveda."""
import json, logging, os, ssl, threading, urllib.request
import pytest
from tamizaje import boveda, hospital, protocolo, secretos, servicio, sinteticos
from tamizaje.rutas import RAIZ


@pytest.fixture(scope="module")
def entorno(tmp_path_factory, modelo):
    d = tmp_path_factory.mktemp("secretos")
    secretos.generar(str(d))
    c = os.path.join(d, "certs")
    srv, svc = servicio.crear_servidor("127.0.0.1", 0, modelo, f"{c}/servicio.pem", f"{c}/servicio.key", f"{c}/ca.pem")
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"https://localhost:{srv.server_address[1]}"
    cli = hospital.ClienteServicio(url, f"{c}/ca.pem", f"{c}/hospital.pem", f"{c}/hospital.key")
    bov = boveda.Boveda(str(d / "boveda.jsonl"), boveda.cargar_llave(str(d / "boveda.key")))
    clin = hospital.Clinica(modelo, cli, bov)
    hsrv = hospital.crear_servidor("127.0.0.1", 0, clin)
    threading.Thread(target=hsrv.serve_forever, daemon=True).start()
    yield {"dir": d, "certs": c, "url": url, "clinica": clin, "svc": svc, "hosp": f"http://127.0.0.1:{hsrv.server_address[1]}", "boveda": bov}
    srv.shutdown(); hsrv.shutdown()


def post(url, obj):
    req = urllib.request.Request(url, data=json.dumps(obj).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def test_recorrido_completo_por_la_ui(entorno, modelo, caplog):
    caplog.set_level(logging.INFO)
    perfil = "Sintético C · riesgo alto"
    r = post(entorno["hosp"] + "/api/evaluar", {"perfil": perfil})
    x = [sinteticos.PERFILES[perfil][n] for n in modelo["variables"]]
    from tamizaje import contrato
    assert int(r["hospital"]["z_entero"]) == contrato.logit_entero(modelo["pesos_enteros"], modelo["intercepto_entero"], x)
    assert r["sintetico"] is True and len(r["servidor"]["recibio"]["cifrados"]) == 21
    assert r["servidor"]["recibio"]["llave_publica_bits"] >= 2048
    # e) los logs no contienen entradas ni resultados en claro
    texto = "\n".join(rec.getMessage() for rec in caplog.records)
    assert r["hospital"]["z_entero"] not in texto
    assert "BMI" not in texto and json.dumps(sinteticos.PERFILES[perfil]) not in texto
    assert str(round(r["hospital"]["probabilidad"], 4)) not in texto


def test_entrada_invalida_por_la_ui(entorno):
    p = dict(sinteticos.PERFILES["Sintético A · riesgo bajo"], BMI=30.5)
    with pytest.raises(urllib.error.HTTPError) as e:
        post(entorno["hosp"] + "/api/evaluar", {"paciente": p})
    assert e.value.code == 400


def test_estado_reporta_servicio_sin_llave(entorno):
    with urllib.request.urlopen(entorno["hosp"] + "/api/estado", timeout=30) as r:
        e = json.loads(r.read())
    assert e["servicio"]["estado"] == "ok" and e["servicio"]["llave_privada"] is False


def test_tls_rechaza_ca_desconocida(entorno, tmp_path):
    otro = tmp_path / "otro"; secretos.generar(str(otro))
    oc = otro / "certs"
    cli = hospital.ClienteServicio(entorno["url"], str(oc / "ca.pem"), str(oc / "hospital.pem"), str(oc / "hospital.key"))
    with pytest.raises(ssl.SSLError):
        cli.salud()


def test_tls_exige_certificado_de_cliente(entorno):
    ctx = ssl.create_default_context(cafile=f"{entorno['certs']}/ca.pem")
    with pytest.raises((ssl.SSLError, ConnectionResetError, urllib.error.URLError)):
        urllib.request.urlopen(entorno["url"] + "/salud", context=ctx, timeout=10).read()


def test_boveda_cifra_y_detecta_alteraciones(entorno):
    bov = entorno["boveda"]
    bov.guardar("prueba-0001", {"sintetico": True, "x": 1})
    registros = bov.leer()
    assert ("prueba-0001", {"sintetico": True, "x": 1}) in registros
    crudo = open(bov.archivo).read()
    assert '"x": 1' not in crudo
    lineas = crudo.splitlines()
    nonces = [json.loads(l)["nonce"] for l in lineas]
    assert len(nonces) == len(set(nonces))
    alterada = json.loads(lineas[-1]); alterada["id"] = "prueba-0002"
    with open(bov.archivo, "a") as f:
        f.write(json.dumps(alterada) + "\n")
    with pytest.raises(Exception):
        bov.leer()


def test_llave_de_boveda_fuera_del_repo(tmp_path):
    dentro = os.path.join(RAIZ, "artefactos", "llave_prohibida.key")
    with pytest.raises(boveda.BovedaError):
        boveda.cargar_llave(dentro)


def _crudo(url, cuerpo, tipo="application/json", largo=None):
    req = urllib.request.Request(url, data=cuerpo, method="POST")
    if tipo:
        req.add_header("Content-Type", tipo)
    if largo is not None:
        req.add_header("Content-Length", largo)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code


def test_f11_api_del_hospital_rechaza_tipos_y_tamanos(entorno):
    u = entorno["hosp"] + "/api/evaluar"
    assert _crudo(u, b'{"aleatorio": true}', tipo="text/plain") == 415
    assert _crudo(u, b"[1, 2]") == 400
    assert _crudo(u, b"x" * (70 * 1024)) == 413


def test_f11_tiempos_separados_e_incluyen_boveda(entorno):
    r = post(entorno["hosp"] + "/api/evaluar", {"perfil": "Sintético A · riesgo bajo"})
    t = r["tiempos_ms"]
    assert {"cifrar", "red_y_servicio", "descifrar", "interpretar", "boveda", "total_en_hospital"} <= set(t)
    assert t["total_en_hospital"] >= t["cifrar"] + t["red_y_servicio"] + t["descifrar"] - 1
