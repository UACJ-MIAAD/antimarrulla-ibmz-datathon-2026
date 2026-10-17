"""Servicio de riesgo: HTTPS (TLS 1.3, certificado de cliente obligatorio) y solo cifrados.

No tiene la llave privada. Registra únicamente id de solicitud, tiempos y tamaños; nunca el cuerpo.

Evidencia opcional (SERVICIO_EVIDENCIA=<directorio>, para la prueba de dos máquinas): guarda los bytes EXACTOS que
recibió y que devolvió cada solicitud aceptada, más una línea de auditoría con sus SHA-256, el certificado del cliente,
la versión de TLS y la comprobación de que no hay ninguna llave privada Paillier en la memoria del proceso. Lo que se
guarda es lo mismo que vio el servicio: solo cifrados. `python -m tamizaje.dos_maquinas auditar` lo verifica.

Variables de entorno: SERVICIO_PUERTO (8443), SERVICIO_CERT, SERVICIO_LLAVE, SERVICIO_CA_CLIENTES, MODELO_JSON, SERVICIO_EVIDENCIA.
Uso: python -m tamizaje.servicio
"""
import datetime, gc, hashlib, json, logging, os, platform, ssl, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from phe.paillier import PaillierPrivateKey
from . import contrato, procedencia, protocolo

MAX_CUERPO = 512 * 1024
log = logging.getLogger("servicio")


def contexto_tls(cert, llave, ca_clientes):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_3
    ctx.load_cert_chain(cert, llave)
    ctx.load_verify_locations(ca_clientes)
    ctx.verify_mode = ssl.CERT_REQUIRED
    return ctx


def llave_privada_en_memoria():
    """True si este proceso tiene algún objeto PaillierPrivateKey vivo (el servicio nunca debería)."""
    return any(isinstance(o, PaillierPrivateKey) for o in gc.get_objects())


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def id_maquina():
    """Identificador de la VM: TAMIZAJE_MAQUINA_ID (lo pasa el Makefile al contenedor) o /etc/machine-id."""
    if os.environ.get("TAMIZAJE_MAQUINA_ID"):
        return os.environ["TAMIZAJE_MAQUINA_ID"].strip()[:12]
    try:
        return open("/etc/machine-id").read().strip()[:12] or None
    except OSError:
        return None


class Evidencia:
    """Bytes exactos recibidos y enviados + una línea de auditoría por solicitud aceptada."""

    def __init__(self, directorio, modelo_json, modelo_sha256=None):
        self.dir = os.path.abspath(directorio)
        self.solicitudes = os.path.join(self.dir, "solicitudes")
        os.makedirs(self.solicitudes, exist_ok=True)
        self.bitacora = os.path.join(self.dir, "auditoria_servicio.jsonl")
        self._candado = threading.Lock()
        codigo, n = procedencia.hash_codigo()
        self.inicio = {
            "fecha_utc": _ahora(), "maquina": platform.node(), "maquina_id": id_maquina(), "arquitectura": platform.machine(),
            "plataforma": platform.platform(), "python": platform.python_version(), "openssl_python": ssl.OPENSSL_VERSION,
            "contenedor": os.path.exists("/.dockerenv"), "codigo_sha256": codigo, "codigo_archivos": n,
            "modelo": modelo_json["modelo"], "modelo_sha256": modelo_sha256, "llave_privada_en_memoria": llave_privada_en_memoria(),
        }
        with open(os.path.join(self.dir, "servicio_inicio.json"), "w") as f:
            json.dump(self.inicio, f, ensure_ascii=False, indent=1)

    def registrar(self, rid, crudo, enviado, ms, conexion, cliente_ip):
        cert = conexion.getpeercert() or {}
        cn = dict(x[0] for x in cert.get("subject", ())).get("commonName")
        entrada = {
            "id": rid, "fecha_utc": _ahora(), "maquina": platform.node(), "cliente_ip": cliente_ip, "cliente_cn": cn,
            "tls": conexion.version(), "cifrado_tls": (conexion.cipher() or [None])[0],
            "bytes_in": len(crudo), "bytes_out": len(enviado), "sha256_solicitud": _sha(crudo), "sha256_respuesta": _sha(enviado),
            "servicio_ms": round(ms, 3), "llave_privada_en_memoria": llave_privada_en_memoria(),
        }
        base = os.path.join(self.solicitudes, rid)  # rid ya validado: 32 hexadecimales
        with open(base + ".solicitud.json", "wb") as f:
            f.write(crudo)
        with open(base + ".respuesta.json", "wb") as f:
            f.write(enviado)
        with self._candado, open(self.bitacora, "a") as f:
            f.write(json.dumps(entrada) + "\n")
        return entrada


def _ahora():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def crear_servidor(host, puerto, modelo_json, cert, llave, ca_clientes, evidencia=None, modelo_sha256=None):
    servicio = protocolo.ServicioRiesgo(protocolo.ModeloCuantizado.desde_json(modelo_json))
    ev = Evidencia(evidencia, modelo_json, modelo_sha256) if evidencia else None

    class Manejador(BaseHTTPRequestHandler):
        server_version = "tamizaje-servicio"
        sys_version = ""
        timeout = 15  # segundos para leer la solicitud completa

        def log_message(self, fmt, *args):  # sin rutas de consulta ni cuerpos
            pass

        def _responder(self, codigo, obj):
            cuerpo = json.dumps(obj).encode()
            self.send_response(codigo)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)
            self._enviado = cuerpo
            return len(cuerpo)

        def do_GET(self):
            if self.path != "/salud":
                return self._responder(404, {"error": "no existe"})
            self._responder(200, {"estado": "ok", "protocolo": protocolo.PROTOCOLO, "modelo": servicio.modelo.nombre,
                                  "esquema": servicio.modelo.esquema, "llave_privada": False,
                                  "evidencia": ev is not None})

        def do_POST(self):
            if self.path != "/v1/evaluar":
                return self._responder(404, {"error": "no existe"})
            try:
                largo = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                largo = -1
            if not 0 < largo <= MAX_CUERPO:
                return self._responder(413, {"error": "cuerpo vacío o demasiado grande"})
            if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
                return self._responder(415, {"error": "se espera application/json"})
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
            if ev is not None:
                try:
                    e = ev.registrar(sol["id"], crudo, self._enviado, ms, self.connection, self.client_address[0])
                    log.info("evidencia id=%s cliente=%s cn=%s %s llave_privada_en_memoria=%s sha256_solicitud=%s…",
                             e["id"], e["cliente_ip"], e["cliente_cn"], e["tls"], e["llave_privada_en_memoria"], e["sha256_solicitud"][:16])
                except OSError:
                    log.exception("no se pudo guardar la evidencia")

    srv = ThreadingHTTPServer((host, puerto), Manejador)
    srv.socket = contexto_tls(cert, llave, ca_clientes).wrap_socket(srv.socket, server_side=True)
    srv.evidencia = ev
    return srv, servicio


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s servicio %(message)s")
    with open(os.environ["MODELO_JSON"], "rb") as f:
        crudo = f.read()
    modelo = json.loads(crudo)
    srv, servicio = crear_servidor(os.environ.get("SERVICIO_HOST", "0.0.0.0"), int(os.environ.get("SERVICIO_PUERTO", "8443")), modelo,
                                   os.environ["SERVICIO_CERT"], os.environ["SERVICIO_LLAVE"], os.environ["SERVICIO_CA_CLIENTES"],
                                   evidencia=os.environ.get("SERVICIO_EVIDENCIA") or None, modelo_sha256=_sha(crudo))
    log.info("escuchando TLS 1.3 en el puerto %d · modelo=%s · esquema=%s · sin llave privada · evidencia=%s", srv.server_address[1],
             servicio.modelo.nombre, servicio.modelo.esquema, srv.evidencia.dir if srv.evidencia else "no")
    srv.serve_forever()


if __name__ == "__main__":
    main()
