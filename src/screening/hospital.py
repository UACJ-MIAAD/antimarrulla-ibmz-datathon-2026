"""Hospital environment: owns the private key, encrypts, calls the service over mutual TLS,
decrypts, explains and stores each result in an AES-256-GCM vault.
Serve the split-screen UI using SYNTHETIC inputs only. Never log patient records.
Environment: HOSPITAL_HOST, HOSPITAL_PORT, MODEL_JSON, SERVICE_URL, TLS_CA,
TLS_CLIENT_CERT, TLS_CLIENT_KEY, VAULT_KEY, VAULT_FILE.
Run: python -m screening.hospital
"""
import hashlib, http.client, json, logging, os, platform, ssl, time, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from . import vault, schema, provenance, protocol, synthetic, contract, benchmark_profiles

log = logging.getLogger("hospital")
UI = os.path.join(os.path.dirname(__file__), "ui", "index.html")


class ServiceClient:
    def __init__(self, url, ca, cert, key, timeout=30):
        u = urllib.parse.urlparse(url)
        if u.scheme != "https":
            raise ValueError("the risk service requires https")
        self.host, self.port, self.timeout = u.hostname, u.port or 443, timeout
        self.ctx = ssl.create_default_context(cafile=ca)
        self.ctx.minimum_version = ssl.TLSVersion.TLSv1_3
        self.ctx.load_cert_chain(cert, key)

    def _request(self, method, path, body=None):
        c = http.client.HTTPSConnection(self.host, self.port, context=self.ctx, timeout=self.timeout)
        try:
            c.request(method, path, body=body, headers={"Content-Type": "application/json"} if body else {})
            r = c.getresponse()
            data = r.read()
            return r.status, data
        finally:
            c.close()

    def health(self):
        st, d = self._request("GET", "/health")
        return json.loads(d) if st == 200 else {"state": f"HTTP {st}"}

    def evaluate(self, sol):
        body = json.dumps(sol).encode()
        st, d = self._request("POST", "/v2/evaluate", body)
        if st != 200:
            raise protocol.InvalidMessage(f"service returned HTTP {st}: {json.loads(d).get('error')}")
        return json.loads(d), len(body), len(d)


def _short(c):
    h = format(int(c), "x")
    return {"hex": h[:40] + "…", "bits": int(c).bit_length()}


class Clinic:
    "Hospital logic separated from the HTTP server for integration testing."

    def __init__(self, model_json, client, bov, model_sha256=None):
        self.h, self.client, self.vault, self.model_sha256 = protocol.hospital(model_json), client, bov, model_sha256
        self.code_sha256 = provenance.hash_code()[0]  # Identity of the code actually deployed inside the image

    def evaluate(self, patient, label):
        t0 = time.perf_counter()
        sol, x = self.h.prepare(patient)
        t1 = time.perf_counter()
        resp, b_in, b_out = self.client.evaluate(sol)
        t2 = time.perf_counter()
        z, x = self.h.decrypt(resp)
        t3 = time.perf_counter()
        result = self.h.interpret(z, x)
        model = self.h.model_json
        result["integer_reference_match"] = z == contract.logit_integer(model["weights_integers"], model["intercept_integer"], x)
        t4 = time.perf_counter()
        self.vault.save(sol["id"], {"synthetic": True, "profile": label, "input": dict(zip(schema.FEATURE_NAMES, x)),
                                        "probability": result["probability"], "risk_high": result["risk_high"], "date": time.time()})
        t5 = time.perf_counter()
        log.info("evaluated id=%s encrypt_ms=%.1f service_ms=%.1f decrypt_ms=%.1f vault_ms=%.1f", sol["id"], (t1 - t0) * 1e3, (t2 - t1) * 1e3, (t3 - t2) * 1e3, (t5 - t4) * 1e3)
        return {
            "synthetic": True, "profile": label, "id": sol["id"],
            "model_sha256": self.model_sha256, "code_sha256": self.code_sha256,
            "hospital": {"input": dict(zip(schema.FEATURE_NAMES, x)), **result},
            "server": {
                "received": {"protocol": sol["protocol"], "model": sol["model"], "schema": sol["schema"], "id": sol["id"],
                            "key_public_bits": self.h.pub.n.bit_length(), "ciphertexts": [_short(c) for c in sol["ciphertexts"]],
                            "bytes": b_in},
                "returned": {"result": _short(resp["result"]), "bytes": b_out, "service_ms": resp.get("service_ms")},
            },
            "timings_ms": {"encrypt": round((t1 - t0) * 1e3, 1), "network_and_service": round((t2 - t1) * 1e3, 1),
                           "decrypt": round((t3 - t2) * 1e3, 1), "interpret": round((t4 - t3) * 1e3, 2),
                           "vault": round((t5 - t4) * 1e3, 1), "total_in_hospital": round((t5 - t0) * 1e3, 1)},
        }


def create_server(host, port, clinic):
    class Handler(BaseHTTPRequestHandler):
        server_version = "screening-hospital"
        sys_version = ""
        timeout = 15

        def log_message(self, fmt, *args):
            pass

        def _json(self, code, obj):
            body = json.dumps(obj, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = urllib.parse.urlsplit(self.path).path
            if path in ("/", "/index.html"):
                body = open(UI, "rb").read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                return self.wfile.write(body)
            if path == "/api/synthetic":
                return self._json(200, {"profiles": synthetic.PROFILES, "schema": schema.as_dict()})
            if path == "/api/test-config":
                return self._json(200, {"api_sizes": list(benchmark_profiles.SIZES), "warmup": 3, "seed": 2026,
                    "profiles": [benchmark_profiles.profile(n) for n in benchmark_profiles.SIZES],
                    "model_sha256": clinic.model_sha256, "code_sha256": clinic.code_sha256})
            if path == "/api/state":
                try:
                    health = clinic.client.health()
                except OSError as e:
                    health = {"state": f"disconnected ({type(e).__name__})"}
                return self._json(200, {"service": health, "model": clinic.h.quantized.name, "model_sha256": clinic.model_sha256, "code_sha256": clinic.code_sha256, "schema": schema.VERSION,
                                        "key_bits": clinic.h.pub.n.bit_length(), "machine": platform.machine(),
                                        "system": platform.system(), "threshold": clinic.h.model_json["threshold"]})
            self._json(404, {"error": "not found"})

        def do_POST(self):
            if urllib.parse.urlsplit(self.path).path != "/api/evaluate":
                return self._json(404, {"error": "not found"})
            try:
                length = int(self.headers.get("Content-Length", ""))
            except ValueError:
                return self._json(411, {"error": "a valid Content-Length is required"})
            if not 0 < length <= 64 * 1024:
                return self._json(413, {"error": "empty or oversized body"})
            if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
                return self._json(415, {"error": "expected application/json"})
            try:
                request = json.loads(self.rfile.read(length))
                if not isinstance(request, dict):
                    raise ValueError("expected a JSON object")
                if "profile" in request:
                    label = request["profile"]
                    patient = synthetic.PROFILES[label]
                elif "synthetic_seed" in request:
                    seed = request["synthetic_seed"]
                    if type(seed) is not int or not 0 <= seed < 2 ** 32:
                        raise ValueError("synthetic_seed must be an integer from 0 to 4294967295")
                    label, patient = "Seeded synthetic input", synthetic.random_patient(seed)
                elif request.get("random_patient"):
                    label, patient = "Random synthetic input", synthetic.random_patient()
                else:
                    label, patient = "Custom synthetic input", request["patient"]
                return self._json(200, clinic.evaluate(patient, label))
            except (KeyError, ValueError, schema.InvalidInput) as e:
                return self._json(400, {"error": str(e)})
            except (protocol.InvalidMessage, OSError) as e:
                return self._json(502, {"error": f"risk service: {e}"})

    return ThreadingHTTPServer((host, port), Handler)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s hospital %(message)s")
    with open(os.environ["MODEL_JSON"], "rb") as f:
        raw = f.read()
    model = json.loads(raw)
    client = ServiceClient(os.environ.get("SERVICE_URL", "https://service:8443"), os.environ["TLS_CA"],
                              os.environ["TLS_CLIENT_CERT"], os.environ["TLS_CLIENT_KEY"])
    bov = vault.Vault(os.environ.get("VAULT_FILE", "/var/lib/screening/vault.jsonl"), vault.load_key(os.environ["VAULT_KEY"]))
    clinic = Clinic(model, client, bov, hashlib.sha256(raw).hexdigest())
    srv = create_server(os.environ.get("HOSPITAL_HOST", "127.0.0.1"), int(os.environ.get("HOSPITAL_PORT", "8080")), clinic)
    log.info("UI at http://%s:%s · %d-bit Paillier key generated in hospital memory", *srv.server_address[:2], clinic.h.pub.n.bit_length())
    srv.serve_forever()


if __name__ == "__main__":
    main()
