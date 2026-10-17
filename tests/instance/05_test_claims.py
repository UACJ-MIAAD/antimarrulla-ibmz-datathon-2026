#!/usr/bin/env python3
"""05_test_claims.py - Tests every security claim on the slide, before writing the real service.
Run from the same folder as 03_test_stack.py (it reuses its certificate helper).

  A. Paillier properties at the raw ciphertext level (the three formulas on the slide)
  B. End-to-end: hospital encrypts -> JSON over the wire -> server scores with only the
     public key -> hospital decrypts + sigmoid == scikit-learn predict_proba
  C. Same patient priority order as the plaintext model
  D. What the server can and cannot see (no plaintext in payload, random ciphertexts, key size)
  E. Logs contain only id, ms and bytes
  F. Vault: AES-256-GCM at rest (unique nonces, tamper and record-swap detection)
  G. mTLS rejects: no client cert, cert from another CA, TLS 1.2
  H. Throughput for a batch of patients (time on this hardware)
"""
import importlib.util, io, json, logging, math, os, re, socket, ssl, sys, tempfile, threading, time
import numpy as np, phe
from sklearn.linear_model import LogisticRegression

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("stack", os.path.join(HERE, "03_test_stack.py"))
stack = importlib.util.module_from_spec(spec); spec.loader.exec_module(stack)

results = []
def test(name):
    def deco(fn):
        t0 = time.perf_counter()
        try:
            d = fn() or ""
            results.append((True, name, f"{d} ({time.perf_counter()-t0:.2f}s)"))
        except Exception as e:
            results.append((False, name, f"{type(e).__name__}: {e}"))
        return fn
    return deco

# Shared setup: a model like the real one, and the hospital's 2048-bit keypair
rng = np.random.default_rng(42)
N_FEAT = 6
X = rng.normal(size=(600, N_FEAT)); X[:, 0] = rng.uniform(70, 250, 600)   # e.g. glucose-like feature
y = ((X[:, 0] - 140) / 40 + X[:, 1:] @ rng.normal(size=N_FEAT - 1) > 0).astype(int)
model = LogisticRegression(max_iter=2000).fit(X, y)
W, B = model.coef_[0].astype(float), float(model.intercept_[0])
PUB, PRIV = phe.generate_paillier_keypair(n_length=2048)
sigmoid = lambda z: 1 / (1 + math.exp(-z))

# ---- Reference protocol (replace with your real hospital/server functions later) ----
def hospital_encrypt(patient_id, features):
    enc = [PUB.encrypt(float(v)) for v in features]
    return json.dumps({"id": patient_id, "n": str(PUB.n),
                       "x": [[str(e.ciphertext()), e.exponent] for e in enc]})

log = logging.getLogger("risk-service")
def server_score(payload_json, weights, bias):
    t0 = time.perf_counter()
    p = json.loads(payload_json)
    pub = phe.PaillierPublicKey(int(p["n"]))           # server only ever builds a PUBLIC key
    xs = [phe.EncryptedNumber(pub, int(c), int(e)) for c, e in p["x"]]
    score = sum(x * float(w) for x, w in zip(xs, weights)) + float(bias)
    out = json.dumps({"id": p["id"], "s": [str(score.ciphertext()), score.exponent]})
    log.info("id=%s ms=%.1f bytes=%d", p["id"], (time.perf_counter() - t0) * 1000, len(payload_json))
    return out

def hospital_decrypt(result_json):
    r = json.loads(result_json)
    return sigmoid(PRIV.decrypt(phe.EncryptedNumber(PUB, int(r["s"][0]), int(r["s"][1]))))

# ---- A ----
@test("A. Raw Paillier: Enc(a)·Enc(b)=Enc(a+b), Enc(a)^k=Enc(k·a), ∏Enc(xi)^wi=Enc(w·x)")
def _():
    n2 = PUB.nsquare
    a, b, k = 123, 456, 7
    ca, cb = PUB.raw_encrypt(a), PUB.raw_encrypt(b)
    assert PRIV.raw_decrypt(ca * cb % n2) == a + b
    assert PRIV.raw_decrypt(pow(ca, k, n2)) == k * a
    xs, ws = [5, 12, 3, 40], [2, 1, 4, 3]
    prod = 1
    for x, w in zip(xs, ws):
        prod = prod * pow(PUB.raw_encrypt(x), w, n2) % n2
    assert PRIV.raw_decrypt(prod) == sum(x * w for x, w in zip(xs, ws))
    return "all three formulas hold"

# ---- B ----
@test("B. End-to-end encrypted score + sigmoid == predict_proba (negatives and floats)")
def _():
    worst = 0.0
    for i in range(5):
        p = hospital_decrypt(server_score(hospital_encrypt(f"P{i}", X[i]), W, B))
        worst = max(worst, abs(p - model.predict_proba(X[i:i+1])[0, 1]))
    assert worst < 1e-9, worst
    return f"max difference {worst:.1e}"

# ---- C ----
@test("C. Patient priority order identical to plaintext model")
def _():
    idx = range(20)
    enc_p = [hospital_decrypt(server_score(hospital_encrypt(f"P{i}", X[i]), W, B)) for i in idx]
    plain_p = model.predict_proba(X[:20])[:, 1]
    assert list(np.argsort(enc_p)[::-1]) == list(np.argsort(plain_p)[::-1])
    return "same ranking for 20 patients"

# ---- D ----
@test("D. Server sees no plaintext; ciphertexts are random; key is 2048-bit")
def _():
    feats = [182.0, 35.5, 1.0, 64.0, 0.0, 27.3]
    payload = hospital_encrypt("P-001", feats)
    for v in ["182", "35.5", "64", "27.3"]:
        assert not re.search(rf"(?<!\d){re.escape(v)}(?!\d)", payload.replace(str(PUB.n), "")), f"{v} visible"
    assert PUB.encrypt(100).ciphertext() != PUB.encrypt(100).ciphertext(), "equal values give equal ciphertexts"
    assert PUB.n.bit_length() >= 2048
    other_pub, _ = phe.generate_paillier_keypair(n_length=2048)
    try:
        PUB.encrypt(1) + other_pub.encrypt(1); raise AssertionError("mixed keys accepted")
    except ValueError:
        pass
    return "no plaintext in payload, randomized encryption, mixed keys rejected"

# ---- E ----
@test("E. Service logs contain only id, ms and bytes")
def _():
    buf = io.StringIO(); h = logging.StreamHandler(buf)
    log.addHandler(h); log.setLevel(logging.INFO)
    try:
        for i in range(3):
            server_score(hospital_encrypt(f"P{i}", X[i]), W, B)
    finally:
        log.removeHandler(h)
    lines = buf.getvalue().strip().splitlines()
    assert len(lines) == 3
    for line in lines:
        assert re.fullmatch(r"id=P\d+ ms=\d+\.\d bytes=\d+", line), f"unexpected log line: {line}"
    return f"{len(lines)} log lines, format OK"

# ---- F ----
@test("F. Vault AES-256-GCM: unique nonces, tamper + record-swap detected, no plaintext on disk")
def _():
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.exceptions import InvalidTag
    aes = AESGCM(AESGCM.generate_key(bit_length=256))
    def seal(pid, rec):
        nonce = os.urandom(12)
        return nonce + aes.encrypt(nonce, json.dumps(rec).encode(), pid.encode())
    def open_(pid, blob):
        return json.loads(aes.decrypt(blob[:12], blob[12:], pid.encode()))
    blobs = {f"P{i}": seal(f"P{i}", {"glucose": 180 + i, "risk": 0.8}) for i in range(500)}
    assert len({b[:12] for b in blobs.values()}) == 500, "nonce reused"
    path = os.path.join(tempfile.mkdtemp(), "vault.bin")
    with open(path, "wb") as f:
        for b in blobs.values(): f.write(b)
    assert b"glucose" not in open(path, "rb").read()
    assert open_("P1", blobs["P1"])["glucose"] == 181
    for bad in [lambda: open_("P2", blobs["P1"]),                                  # record swapped
                lambda: open_("P1", blobs["P1"][:-1] + bytes([blobs["P1"][-1] ^ 1]))]:  # tampered
        try: bad(); raise AssertionError("not detected")
        except InvalidTag: pass
    return "500 records OK"

# ---- G ----
def handshake(client_ctx, rogue=False):
    """Returns True if the client could exchange data with the mTLS server."""
    sctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); sctx.minimum_version = ssl.TLSVersion.TLSv1_3
    sctx.load_cert_chain(PATHS["srv"]); sctx.load_verify_locations(PATHS["ca"]); sctx.verify_mode = ssl.CERT_REQUIRED
    ls = socket.socket(); ls.bind(("127.0.0.1", 0)); ls.listen(1); port = ls.getsockname()[1]
    def srv():
        try:
            c, _ = ls.accept(); c.settimeout(5)
            with sctx.wrap_socket(c, server_side=True) as s: s.sendall(s.recv(64))
        except Exception:
            pass
    t = threading.Thread(target=srv, daemon=True); t.start()
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=5) as raw:
            with client_ctx.wrap_socket(raw, server_hostname="localhost") as s:
                s.sendall(b"ping"); return s.recv(64) == b"ping"
    except Exception:
        return False
    finally:
        t.join(5); ls.close()

def write_pem(cert, key=None):
    from cryptography.hazmat.primitives import serialization as se
    fd, p = tempfile.mkstemp(suffix=".pem")
    with os.fdopen(fd, "wb") as f:
        f.write(cert.public_bytes(se.Encoding.PEM))
        if key: f.write(key.private_bytes(se.Encoding.PEM, se.PrivateFormat.PKCS8, se.NoEncryption()))
    return p

CA, CA_KEY = stack.make_cert("Datathon CA", is_ca=True)
ROGUE, ROGUE_KEY = stack.make_cert("Rogue CA", is_ca=True)
PATHS = {"ca": write_pem(CA), "srv": write_pem(*stack.make_cert("linuxone", CA, CA_KEY)),
         "cli": write_pem(*stack.make_cert("hospital", CA, CA_KEY)),
         "rogue_cli": write_pem(*stack.make_cert("attacker", ROGUE, ROGUE_KEY))}

def client(cert=None, max_v=None):
    c = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT); c.load_verify_locations(PATHS["ca"])
    if cert: c.load_cert_chain(PATHS[cert])
    if max_v: c.maximum_version = max_v
    return c

@test("G. mTLS: valid client accepted; no cert, foreign CA and TLS 1.2 rejected")
def _():
    assert handshake(client("cli")), "valid hospital client was rejected"
    assert not handshake(client()), "client without certificate accepted"
    assert not handshake(client("rogue_cli")), "certificate from another CA accepted"
    assert not handshake(client("cli", ssl.TLSVersion.TLSv1_2)), "TLS 1.2 accepted"
    return "1 accepted, 3 rejected"

# ---- H ----
@test("H. Throughput: 25 patients end-to-end")
def _():
    t0 = time.perf_counter()
    for i in range(25):
        hospital_decrypt(server_score(hospital_encrypt(f"P{i}", X[i]), W, B))
    per = (time.perf_counter() - t0) / 25 * 1000
    return f"{per:.0f} ms per patient ({N_FEAT} features)"

print(f"== Claim tests ==")
for ok, name, d in results:
    print(f"  {'[OK]  ' if ok else '[FAIL]'} {name}: {d}")
failed = sum(not r[0] for r in results)
print(f"\n{len(results)-failed}/{len(results)} tests passed")
sys.exit(1 if failed else 0)
