"""Entorno del hospital: tiene la llave privada, cifra, llama al servicio por TLS mutuo, descifra y explica.

Sirve la UI de pantalla dividida (solo pacientes SINTÉTICOS) y guarda cada resultado en la bóveda AES-256-GCM.
No registra datos de pacientes en los logs.

Variables de entorno: HOSPITAL_HOST (127.0.0.1), HOSPITAL_PUERTO (8080), MODELO_JSON, SERVICIO_URL (https://servicio:8443),
TLS_CA, TLS_CERT_CLIENTE, TLS_LLAVE_CLIENTE, BOVEDA_LLAVE, BOVEDA_ARCHIVO.
Uso: python -m tamizaje.hospital
"""
import http.client, json, logging, os, platform, ssl, time, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from . import boveda, esquema, protocolo, sinteticos

log = logging.getLogger("hospital")
UI = os.path.join(os.path.dirname(__file__), "ui", "index.html")


class ClienteServicio:
    def __init__(self, url, ca, cert, llave, timeout=30):
        u = urllib.parse.urlparse(url)
        if u.scheme != "https":
            raise ValueError("el servicio solo se llama por https")
        self.host, self.puerto, self.timeout = u.hostname, u.port or 443, timeout
        self.ctx = ssl.create_default_context(cafile=ca)
        self.ctx.minimum_version = ssl.TLSVersion.TLSv1_3
        self.ctx.load_cert_chain(cert, llave)

    def _pedir(self, metodo, ruta, cuerpo=None):
        c = http.client.HTTPSConnection(self.host, self.puerto, context=self.ctx, timeout=self.timeout)
        try:
            c.request(metodo, ruta, body=cuerpo, headers={"Content-Type": "application/json"} if cuerpo else {})
            r = c.getresponse()
            datos = r.read()
            return r.status, datos
        finally:
            c.close()

    def salud(self):
        st, d = self._pedir("GET", "/salud")
        return json.loads(d) if st == 200 else {"estado": f"HTTP {st}"}

    def evaluar(self, sol):
        cuerpo = json.dumps(sol).encode()
        st, d = self._pedir("POST", "/v1/evaluar", cuerpo)
        if st != 200:
            raise protocolo.MensajeInvalido(f"el servicio respondió HTTP {st}: {json.loads(d).get('error')}")
        return json.loads(d), len(cuerpo), len(d)


def _corto(c):
    h = format(int(c), "x")
    return {"hex": h[:40] + "…", "bits": int(c).bit_length()}


class Clinica:
    """Lógica del hospital, separada del servidor HTTP para poder probarla."""

    def __init__(self, modelo_json, cliente, bov):
        self.h, self.cliente, self.boveda = protocolo.Hospital(modelo_json), cliente, bov

    def evaluar(self, paciente, etiqueta):
        t0 = time.perf_counter()
        sol, x = self.h.preparar(paciente)
        t1 = time.perf_counter()
        resp, b_in, b_out = self.cliente.evaluar(sol)
        t2 = time.perf_counter()
        z, x = self.h.descifrar(resp)
        t3 = time.perf_counter()
        res = self.h.interpretar(z, x)
        self.boveda.guardar(sol["id"], {"sintetico": True, "perfil": etiqueta, "entrada": dict(zip(esquema.NOMBRES, x)),
                                        "probabilidad": res["probabilidad"], "riesgo_alto": res["riesgo_alto"], "fecha": time.time()})
        log.info("evaluada id=%s cifrar_ms=%.1f servicio_ms=%.1f descifrar_ms=%.1f", sol["id"], (t1 - t0) * 1e3, (t2 - t1) * 1e3, (t3 - t2) * 1e3)
        return {
            "sintetico": True, "perfil": etiqueta, "id": sol["id"],
            "hospital": {"entrada": dict(zip(esquema.NOMBRES, x)), **res},
            "servidor": {
                "recibio": {"protocolo": sol["protocolo"], "modelo": sol["modelo"], "esquema": sol["esquema"], "id": sol["id"],
                            "llave_publica_bits": self.h.pub.n.bit_length(), "cifrados": [_corto(c) for c in sol["cifrados"]],
                            "bytes": b_in},
                "devolvio": {"resultado": _corto(resp["resultado"]), "bytes": b_out, "servicio_ms": resp.get("servicio_ms")},
            },
            "tiempos_ms": {"cifrar": round((t1 - t0) * 1e3, 1), "red_y_servicio": round((t2 - t1) * 1e3, 1),
                           "descifrar": round((t3 - t2) * 1e3, 1), "total": round((t3 - t0) * 1e3, 1)},
        }


def crear_servidor(host, puerto, clinica):
    class Manejador(BaseHTTPRequestHandler):
        server_version = "tamizaje-hospital"
        sys_version = ""

        def log_message(self, fmt, *args):
            pass

        def _json(self, codigo, obj):
            cuerpo = json.dumps(obj, ensure_ascii=False).encode()
            self.send_response(codigo)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(cuerpo)

        def do_GET(self):
            ruta = urllib.parse.urlsplit(self.path).path
            if ruta in ("/", "/index.html"):
                cuerpo = open(UI, "rb").read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(cuerpo)))
                self.end_headers()
                return self.wfile.write(cuerpo)
            if ruta == "/api/sinteticos":
                return self._json(200, {"perfiles": sinteticos.PERFILES, "esquema": esquema.como_dict()})
            if ruta == "/api/estado":
                try:
                    salud = clinica.cliente.salud()
                except OSError as e:
                    salud = {"estado": f"sin conexión ({type(e).__name__})"}
                return self._json(200, {"servicio": salud, "modelo": clinica.h.cuantizado.nombre, "esquema": esquema.VERSION,
                                        "llave_bits": clinica.h.pub.n.bit_length(), "maquina": platform.machine(),
                                        "sistema": platform.system(), "umbral": clinica.h.modelo_json["umbral"]})
            self._json(404, {"error": "no existe"})

        def do_POST(self):
            if urllib.parse.urlsplit(self.path).path != "/api/evaluar":
                return self._json(404, {"error": "no existe"})
            try:
                largo = int(self.headers.get("Content-Length", "0"))
                pedido = json.loads(self.rfile.read(min(largo, 64 * 1024)))
                if "perfil" in pedido:
                    etiqueta = pedido["perfil"]
                    paciente = sinteticos.PERFILES[etiqueta]
                elif pedido.get("aleatorio"):
                    etiqueta, paciente = "Sintético aleatorio", sinteticos.aleatorio()
                else:
                    etiqueta, paciente = "Sintético capturado", pedido["paciente"]
                return self._json(200, clinica.evaluar(paciente, etiqueta))
            except (KeyError, ValueError, esquema.EntradaInvalida) as e:
                return self._json(400, {"error": str(e)})
            except (protocolo.MensajeInvalido, OSError) as e:
                return self._json(502, {"error": f"servicio de riesgo: {e}"})

    return ThreadingHTTPServer((host, puerto), Manejador)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s hospital %(message)s")
    with open(os.environ["MODELO_JSON"]) as f:
        modelo = json.load(f)
    cliente = ClienteServicio(os.environ.get("SERVICIO_URL", "https://servicio:8443"), os.environ["TLS_CA"],
                              os.environ["TLS_CERT_CLIENTE"], os.environ["TLS_LLAVE_CLIENTE"])
    bov = boveda.Boveda(os.environ.get("BOVEDA_ARCHIVO", "/var/lib/tamizaje/boveda.jsonl"), boveda.cargar_llave(os.environ["BOVEDA_LLAVE"]))
    clinica = Clinica(modelo, cliente, bov)
    srv = crear_servidor(os.environ.get("HOSPITAL_HOST", "127.0.0.1"), int(os.environ.get("HOSPITAL_PUERTO", "8080")), clinica)
    log.info("UI en http://%s:%s · llave Paillier de %d bits generada en memoria", *srv.server_address[:2], clinica.h.pub.n.bit_length())
    srv.serve_forever()


if __name__ == "__main__":
    main()
