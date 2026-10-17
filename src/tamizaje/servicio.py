"""Servicio de riesgo: HTTPS (TLS 1.3, certificado de cliente obligatorio) y solo cifrados.

No tiene la llave privada. Registra únicamente id de solicitud, tiempos y tamaños; nunca el cuerpo.

Variables de entorno: SERVICIO_PUERTO (8443), SERVICIO_CERT, SERVICIO_LLAVE, SERVICIO_CA_CLIENTES, MODELO_JSON.
Uso: python -m tamizaje.servicio
"""
import json, logging, os, ssl, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from . import contrato, protocolo

MAX_CUERPO = 512 * 1024
log = logging.getLogger("servicio")


def contexto_tls(cert, llave, ca_clientes):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_3
    ctx.load_cert_chain(cert, llave)
    ctx.load_verify_locations(ca_clientes)
    ctx.verify_mode = ssl.CERT_REQUIRED
    return ctx


def crear_servidor(host, puerto, modelo_json, cert, llave, ca_clientes):
    servicio = protocolo.ServicioRiesgo(protocolo.ModeloCuantizado.desde_json(modelo_json))

    class Manejador(BaseHTTPRequestHandler):
        server_version = "tamizaje-servicio"
        sys_version = ""

        def log_message(self, fmt, *args):  # sin rutas de consulta ni cuerpos
            pass

        def _responder(self, codigo, obj):
            cuerpo = json.dumps(obj).encode()
            self.send_response(codigo)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)
            return len(cuerpo)

        def do_GET(self):
            if self.path != "/salud":
                return self._responder(404, {"error": "no existe"})
            self._responder(200, {"estado": "ok", "protocolo": protocolo.PROTOCOLO, "modelo": servicio.modelo.nombre,
                                  "esquema": servicio.modelo.esquema, "llave_privada": False})

        def do_POST(self):
            if self.path != "/v1/evaluar":
                return self._responder(404, {"error": "no existe"})
            try:
                largo = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                largo = -1
            if not 0 < largo <= MAX_CUERPO:
                return self._responder(413, {"error": "cuerpo vacío o demasiado grande"})
            crudo = self.rfile.read(largo)
            t0 = time.perf_counter()
            try:
                sol = json.loads(crudo)
                resp = servicio.evaluar(sol)
            except (ValueError, protocolo.MensajeInvalido, contrato.ModeloInvalido) as e:
                log.info("rechazada bytes=%d motivo=%s", largo, type(e).__name__)
                return self._responder(400, {"error": str(e) if isinstance(e, (protocolo.MensajeInvalido, contrato.ModeloInvalido)) else "JSON inválido"})
            except Exception:
                log.exception("error interno")
                return self._responder(500, {"error": "error interno"})
            ms = (time.perf_counter() - t0) * 1000
            resp["servicio_ms"] = round(ms, 3)
            enviados = self._responder(200, resp)
            log.info("evaluada id=%s ms=%.1f bytes_in=%d bytes_out=%d", sol["id"], ms, largo, enviados)

    srv = ThreadingHTTPServer((host, puerto), Manejador)
    srv.socket = contexto_tls(cert, llave, ca_clientes).wrap_socket(srv.socket, server_side=True)
    return srv, servicio


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s servicio %(message)s")
    with open(os.environ["MODELO_JSON"]) as f:
        modelo = json.load(f)
    srv, servicio = crear_servidor(os.environ.get("SERVICIO_HOST", "0.0.0.0"), int(os.environ.get("SERVICIO_PUERTO", "8443")), modelo,
                                   os.environ["SERVICIO_CERT"], os.environ["SERVICIO_LLAVE"], os.environ["SERVICIO_CA_CLIENTES"])
    log.info("escuchando TLS 1.3 · modelo=%s · esquema=%s · sin llave privada", servicio.modelo.nombre, servicio.modelo.esquema)
    srv.serve_forever()


if __name__ == "__main__":
    main()
