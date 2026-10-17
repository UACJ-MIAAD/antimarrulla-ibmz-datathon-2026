#!/usr/bin/env python3
"""03_test_stack.py - Functional tests for the datathon stack.
Runs: scikit-learn model, gmpy2, Paillier homomorphic encryption (including
encrypted scoring with a scikit-learn model), AES-256-GCM, and TLS 1.3 with mutual TLS.
"""
import datetime, platform, socket, ssl, sys, tempfile, threading, time, os

results = []
def check(name):
    def deco(fn):
        def run():
            t0 = time.perf_counter()
            try:
                detail = fn() or ""
                results.append((True, name, f"{detail} ({time.perf_counter()-t0:.2f}s)"))
            except Exception as e:
                results.append((False, name, f"{type(e).__name__}: {e}"))
        return run
    return deco

@check("scikit-learn: train a classifier")
def t_sklearn():
    from sklearn.datasets import make_classification
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    X, y = make_classification(n_samples=2000, n_features=8, random_state=0)
    Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=0)
    acc = LogisticRegression(max_iter=500).fit(Xtr, ytr).score(Xte, yte)
    assert acc > 0.7, f"accuracy too low: {acc}"
    return f"accuracy={acc:.2f}"

@check("gmpy2: big-number arithmetic")
def t_gmpy2():
    import gmpy2
    p = gmpy2.next_prime(2**1024)
    assert gmpy2.powmod(3, p - 1, p) == 1  # Fermat's little theorem
    return f"gmpy2 {gmpy2.version()}"

@check("python-paillier: homomorphic add / multiply")
def t_paillier():
    import phe, phe.util
    if not getattr(phe.util, "HAVE_GMP", False):
        raise RuntimeError("phe is NOT using gmpy2 (will be very slow)")
    pub, priv = phe.generate_paillier_keypair(n_length=2048)
    a, b = pub.encrypt(120), pub.encrypt(35.5)
    assert priv.decrypt(a + b) == 155.5
    assert priv.decrypt(a * 3) == 360
    return "phe uses gmpy2"

@check("Paillier + scikit-learn: score encrypted patient data")
def t_encrypted_scoring():
    import phe, numpy as np
    from sklearn.linear_model import LogisticRegression
    rng = np.random.default_rng(0)
    X = rng.normal(size=(500, 6)); y = (X @ rng.normal(size=6) > 0).astype(int)
    model = LogisticRegression().fit(X, y)
    w, b = model.coef_[0], model.intercept_[0]
    pub, priv = phe.generate_paillier_keypair(n_length=2048)
    patient = X[0]
    enc_features = [pub.encrypt(float(v)) for v in patient]           # hospital side
    enc_score = sum(e * float(wi) for e, wi in zip(enc_features, w)) + float(b)  # LinuxONE side
    score = priv.decrypt(enc_score)                                     # hospital side
    expected = float(patient @ w + b)
    assert abs(score - expected) < 1e-6, (score, expected)
    t0 = time.perf_counter()
    for _ in range(20): pub.encrypt(1.23)
    per_enc = (time.perf_counter() - t0) / 20 * 1000
    return f"encrypted score matches plaintext; {per_enc:.1f} ms per encryption"

@check("cryptography: AES-256-GCM encrypt / tamper detection")
def t_aes():
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.exceptions import InvalidTag
    key = AESGCM.generate_key(bit_length=256); aes = AESGCM(key); nonce = os.urandom(12)
    data = b'{"patient_id":"P-001","glucose":182}'
    ct = aes.encrypt(nonce, data, b"hospital-A")
    assert aes.decrypt(nonce, ct, b"hospital-A") == data
    tampered = bytes([ct[0] ^ 1]) + ct[1:]
    try:
        aes.decrypt(nonce, tampered, b"hospital-A"); raise AssertionError("tampering not detected")
    except InvalidTag:
        pass
    return "round-trip OK, tampering detected"

def make_cert(name, issuer_cert=None, issuer_key=None, is_ca=False):
    from cryptography import x509
    from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec
    key = ec.generate_private_key(ec.SECP256R1())
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, name)])
    now = datetime.datetime.now(datetime.timezone.utc)
    builder = (x509.CertificateBuilder().subject_name(subject)
        .issuer_name(issuer_cert.subject if issuer_cert else subject)
        .public_key(key.public_key()).serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(now + datetime.timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=is_ca, path_length=None), critical=True))
    if not is_ca:
        builder = (builder.add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost")]), critical=False)
            .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH, ExtendedKeyUsageOID.CLIENT_AUTH]), critical=False))
    cert = builder.sign(issuer_key or key, hashes.SHA256())
    return cert, key

@check("TLS 1.3 + mutual TLS (mTLS) over a local socket")
def t_tls():
    from cryptography.hazmat.primitives import serialization
    tmp = tempfile.mkdtemp()
    ca, ca_key = make_cert("Datathon CA", is_ca=True)
    srv, srv_key = make_cert("linuxone-server", ca, ca_key)
    cli, cli_key = make_cert("hospital-client", ca, ca_key)
    def write(name, cert, key=None):
        cp = os.path.join(tmp, name + ".pem")
        with open(cp, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
            if key: f.write(key.private_bytes(serialization.Encoding.PEM,
                    serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        return cp
    ca_p, srv_p, cli_p = write("ca", ca), write("srv", srv, srv_key), write("cli", cli, cli_key)

    sctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); sctx.minimum_version = ssl.TLSVersion.TLSv1_3
    sctx.load_cert_chain(srv_p); sctx.load_verify_locations(ca_p); sctx.verify_mode = ssl.CERT_REQUIRED
    cctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT); cctx.minimum_version = ssl.TLSVersion.TLSv1_3
    cctx.load_cert_chain(cli_p); cctx.load_verify_locations(ca_p)

    lsock = socket.socket(); lsock.bind(("127.0.0.1", 0)); lsock.listen(1)
    port = lsock.getsockname()[1]; info = {}
    def server():
        conn, _ = lsock.accept()
        with sctx.wrap_socket(conn, server_side=True) as s:
            info["client_cn"] = dict(x[0] for x in s.getpeercert()["subject"])["commonName"]
            s.sendall(s.recv(1024).upper())
    th = threading.Thread(target=server, daemon=True); th.start()
    with socket.create_connection(("127.0.0.1", port)) as raw:
        with cctx.wrap_socket(raw, server_hostname="localhost") as s:
            s.sendall(b"encrypted report"); reply = s.recv(1024)
            version, cipher = s.version(), s.cipher()[0]
    th.join(5); lsock.close()
    assert version == "TLSv1.3", version
    assert reply == b"ENCRYPTED REPORT"
    assert info.get("client_cn") == "hospital-client"
    return f"{version}, {cipher}, client cert verified"

if __name__ == "__main__":
    print(f"== Stack tests on {platform.machine()} / Python {platform.python_version()} / {ssl.OPENSSL_VERSION} ==")
    for t in [t_sklearn, t_gmpy2, t_paillier, t_encrypted_scoring, t_aes, t_tls]:
        t()
    for ok, name, detail in results:
        print(f"  {'[OK]  ' if ok else '[FAIL]'} {name}: {detail}")
    failed = sum(not r[0] for r in results)
    print(f"\n{len(results)-failed}/{len(results)} tests passed")
    sys.exit(1 if failed else 0)
