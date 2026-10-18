"""Ciphertext-only risk service over HTTPS with TLS 1.3 and mandatory client certificates.

The service has no private key. Operational logs contain request IDs, timings and sizes, never bodies.
Optional SERVICE_EVIDENCE records exact request/response bytes plus hashes, client identity, TLS version
and an in-process Paillier private-key check for the two-host audit. Recorded payloads contain ciphertexts.
Audit with python -m screening.two_hosts audit.
Environment: SERVICE_PORT, SERVICE_CERT, SERVICE_KEY, SERVICE_CLIENT_CA, MODEL_JSON, SERVICE_EVIDENCE.
Run: python -m screening.service
"""
import datetime, gc, hashlib, json, logging, os, platform, ssl, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from phe.paillier import PaillierPrivateKey
from . import contract, provenance, protocol

MAX_BODY = 512 * 1024
log = logging.getLogger("service")


HANDSHAKE_TIMEOUT = 15  # seconds a client gets to finish the TLS handshake


class TLSThreadingServer(ThreadingHTTPServer):
    """Accepts plain TCP and does the TLS 1.3 handshake in each connection's own thread.

    Wrapping the listening socket instead would run every handshake inside accept(), on the single main thread:
    one slow or stalled client would then block all others (seen with --concurrency through an SSH tunnel)."""

    # socketserver's default listen backlog is 5: a burst of simultaneous hospitals overflowed it and
    # connections were reset (ECONNRESET/EINVAL on macOS, measured 21-30 of 40 clients failing).
    request_queue_size = 128

    def __init__(self, address, handler, ctx):
        self.ctx = ctx
        super().__init__(address, handler)

    def finish_request(self, request, client_address):
        request.settimeout(HANDSHAKE_TIMEOUT)
        try:
            tls = self.ctx.wrap_socket(request, server_side=True)
        except (ssl.SSLError, OSError) as e:
            log.info("handshake rejected client=%s reason=%s", client_address[0], type(e).__name__)
            return
        try:
            self.RequestHandlerClass(tls, client_address, self)
        finally:
            try:
                tls.close()
            except OSError:
                pass


def context_tls(cert, key, client_ca):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_3
    ctx.load_cert_chain(cert, key)
    ctx.load_verify_locations(client_ca)
    ctx.verify_mode = ssl.CERT_REQUIRED
    return ctx


def private_key_in_memory():
    "Return whether any live PaillierPrivateKey object exists in this process."
    return any(isinstance(o, PaillierPrivateKey) for o in gc.get_objects())


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def machine_id():
    "VM identity from SCREENING_HOST_ID or /etc/machine-id; this is an operator assertion."
    if os.environ.get("SCREENING_HOST_ID"):
        return os.environ["SCREENING_HOST_ID"].strip()[:12]
    try:
        return open("/etc/machine-id").read().strip()[:12] or None
    except OSError:
        pass
    if platform.system() == "Darwin":  # macOS has no /etc/machine-id: use the hardware UUID
        try:
            import subprocess
            out = subprocess.run(["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"], capture_output=True, text=True, timeout=5).stdout
            uuid = next((l.split('"')[3] for l in out.splitlines() if "IOPlatformUUID" in l), None)
            return uuid[:12] if uuid else None
        except (OSError, IndexError, subprocess.SubprocessError):
            return None
    return None


class Evidence:
    "Record exact wire bytes and an audit entry for each accepted request."

    def __init__(self, directory, model_json, model_sha256=None):
        self.dir = os.path.abspath(directory)
        self.requests = os.path.join(self.dir, "requests")
        os.makedirs(self.requests, exist_ok=True)
        self.log = os.path.join(self.dir, "service_audit.jsonl")
        self._lock = threading.Lock()
        code, n = provenance.hash_code()
        self.startup = {
            "date_utc": _now(), "machine": platform.node(), "machine_id": machine_id(), "architecture": platform.machine(),
            "platform": platform.platform(), "python": platform.python_version(), "openssl_python": ssl.OPENSSL_VERSION,
            "container": os.path.exists("/.dockerenv"), "code_sha256": code, "code_files": n,
            "model": model_json["model"], "model_sha256": model_sha256, "private_key_in_memory": private_key_in_memory(),
        }
        with open(os.path.join(self.dir, "service_startup.json"), "w") as f:
            json.dump(self.startup, f, ensure_ascii=False, indent=1)

    def capture(self, rid, raw, sent, ms, connection, client_ip):
        cert = connection.getpeercert() or {}
        cn = dict(x[0] for x in cert.get("subject", ())).get("commonName")
        input = {
            "id": rid, "date_utc": _now(), "machine": platform.node(), "client_ip": client_ip, "client_cn": cn,
            "tls": connection.version(), "ciphertext_tls": (connection.cipher() or [None])[0],
            "bytes_in": len(raw), "bytes_out": len(sent), "sha256_request": _sha(raw), "sha256_response": _sha(sent),
            "service_ms": round(ms, 3), "private_key_in_memory": private_key_in_memory(),
        }
        base = os.path.join(self.requests, rid)  # rid was validated as exactly 32 hexadecimal characters.
        with open(base + ".request.json", "wb") as f:
            f.write(raw)
        with open(base + ".response.json", "wb") as f:
            f.write(sent)
        with self._lock, open(self.log, "a") as f:
            f.write(json.dumps(input) + "\n")
        return input


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def create_server(host, port, model_json, cert, key, client_ca, evidence=None, model_sha256=None):
    service = protocol.RiskService(protocol.QuantizedModel.from_json(model_json))
    ev = Evidence(evidence, model_json, model_sha256) if evidence else None
    code_sha256 = provenance.hash_code()[0]

    class Handler(BaseHTTPRequestHandler):
        server_version = "screening-service"
        sys_version = ""
        timeout = 15  # Seconds allowed to read the complete request

        def log_message(self, fmt, *args):  # Omit request paths and bodies.
            pass

        def _respond(self, code, obj, body=None):
            body = json.dumps(obj).encode() if body is None else body
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            self._sent = body
            return len(body)

        def do_GET(self):
            if self.path != "/health":
                return self._respond(404, {"error": "not found"})
            self._respond(200, {"state": "ok", "protocol": protocol.PROTOCOL, "model": service.model.name,
                                  "schema": service.model.schema, "key_private": False,
                                  "model_sha256": model_sha256, "code_sha256": code_sha256,
                                  "evidence": ev is not None})

        def do_POST(self):
            if self.path != "/v2/evaluate":
                return self._respond(404, {"error": "not found"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                length = -1
            if not 0 < length <= MAX_BODY:
                return self._respond(413, {"error": "empty or oversized body"})
            if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
                return self._respond(415, {"error": "expected application/json"})
            raw = self.rfile.read(length)
            t0 = time.perf_counter()
            try:
                sol = json.loads(raw)
                resp = service.evaluate(sol)
            except (ValueError, protocol.InvalidMessage, contract.InvalidModel) as e:
                log.info("rejected bytes=%d reason=%s", length, type(e).__name__)
                return self._respond(400, {"error": str(e) if isinstance(e, (protocol.InvalidMessage, contract.InvalidModel)) else "invalid JSON"})
            except Exception:
                log.exception("internal error")
                return self._respond(500, {"error": "internal error"})
            ms = (time.perf_counter() - t0) * 1000
            resp["service_ms"] = round(ms, 3)
            sent_body = json.dumps(resp).encode()
            if ev is not None:
                try:
                    e = ev.capture(sol["id"], raw, sent_body, ms, self.connection, self.client_address[0])
                except OSError:
                    log.exception("could not save evidence")
                    return self._respond(503, {"error": "evidence capture failed"})
            # Success acknowledges completed evidence capture when audit mode is enabled.
            sent = self._respond(200, resp, body=sent_body)
            log.info("evaluated id=%s ms=%.1f bytes_in=%d bytes_out=%d", sol["id"], ms, length, sent)
            if ev is not None:
                log.info("evidence id=%s client=%s cn=%s %s private_key_in_memory=%s request_sha256=%s…",
                         e["id"], e["client_ip"], e["client_cn"], e["tls"], e["private_key_in_memory"], e["sha256_request"][:16])

    srv = TLSThreadingServer((host, port), Handler, context_tls(cert, key, client_ca))
    srv.evidence = ev
    return srv, service


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s service %(message)s")
    with open(os.environ["MODEL_JSON"], "rb") as f:
        raw = f.read()
    model = json.loads(raw)
    srv, service = create_server(os.environ.get("SERVICE_HOST", "0.0.0.0"), int(os.environ.get("SERVICE_PORT", "8443")), model,
                                   os.environ["SERVICE_CERT"], os.environ["SERVICE_KEY"], os.environ["SERVICE_CLIENT_CA"],
                                   evidence=os.environ.get("SERVICE_EVIDENCE") or None, model_sha256=_sha(raw))
    log.info("listening with TLS 1.3 on port %d · model=%s · schema=%s · no private key · evidence=%s", srv.server_address[1],
             service.model.name, service.model.schema, srv.evidence.dir if srv.evidence else "does_not")
    srv.serve_forever()


if __name__ == "__main__":
    main()
