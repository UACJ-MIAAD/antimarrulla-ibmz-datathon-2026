"Integration: hospital UI/API → mutual TLS 1.3 → actual risk service → decryption → vault."
import json, logging, os, ssl, threading, urllib.request
import pytest
from screening import vault, hospital, protocol, secrets_setup, service, synthetic, provenance
from screening.paths import ROOT, MODEL_JSON


@pytest.fixture(scope="module")
def environment(tmp_path_factory, model):
    d = tmp_path_factory.mktemp("secrets_setup")
    secrets_setup.generate(str(d))
    c = os.path.join(d, "certs")
    srv, svc = service.create_server("127.0.0.1", 0, model, f"{c}/service.pem", f"{c}/service.key", f"{c}/ca.pem", model_sha256=provenance.sha256(MODEL_JSON))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"https://localhost:{srv.server_address[1]}"
    cli = hospital.ServiceClient(url, f"{c}/ca.pem", f"{c}/hospital.pem", f"{c}/hospital.key")
    bov = vault.Vault(str(d / "vault.jsonl"), vault.load_key(str(d / "vault.key")))
    clin = hospital.Clinic(model, cli, bov, provenance.sha256(MODEL_JSON))
    hsrv = hospital.create_server("127.0.0.1", 0, clin)
    threading.Thread(target=hsrv.serve_forever, daemon=True).start()
    yield {"dir": d, "certs": c, "url": url, "clinic": clin, "svc": svc, "hosp": f"http://127.0.0.1:{hsrv.server_address[1]}", "vault": bov}
    srv.shutdown(); hsrv.shutdown()


def post(url, obj):
    req = urllib.request.Request(url, data=json.dumps(obj).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def test_flow_complete_by_the_ui(environment, model, caplog):
    caplog.set_level(logging.INFO)
    profile = "Synthetic C · high risk"
    r = post(environment["hosp"] + "/api/evaluate", {"profile": profile})
    x = [synthetic.PROFILES[profile][n] for n in model["variables"]]
    from screening import contract
    assert int(r["hospital"]["z_integer"]) == contract.logit_integer(model["weights_integers"], model["intercept_integer"], x)
    assert r["synthetic"] is True and len(r["server"]["received"]["ciphertexts"]) == len(model["variables"])
    assert r["server"]["received"]["key_public_bits"] >= 2048
    # e) Logs contain neither plaintext inputs nor plaintext results.
    text = "\n".join(rec.getMessage() for rec in caplog.records)
    assert r["hospital"]["z_integer"] not in text
    assert "BMI" not in text and json.dumps(synthetic.PROFILES[profile]) not in text
    assert str(round(r["hospital"]["probability"], 4)) not in text


def test_input_invalid_by_the_ui(environment):
    p = dict(synthetic.PROFILES["Synthetic A · low risk"], BMI=30.5)
    with pytest.raises(urllib.error.HTTPError) as e:
        post(environment["hosp"] + "/api/evaluate", {"patient": p})
    assert e.value.code == 400


def test_state_reports_service_without_key(environment):
    with urllib.request.urlopen(environment["hosp"] + "/api/state", timeout=30) as r:
        e = json.loads(r.read())
    assert e["service"]["state"] == "ok" and e["service"]["key_private"] is False


def test_tls_rejects_ca_unknown(environment, tmp_path):
    other = tmp_path / "other"; secrets_setup.generate(str(other))
    oc = other / "certs"
    cli = hospital.ServiceClient(environment["url"], str(oc / "ca.pem"), str(oc / "hospital.pem"), str(oc / "hospital.key"))
    with pytest.raises(ssl.SSLError):
        cli.health()


def test_tls_requires_certificate_of_client(environment):
    ctx = ssl.create_default_context(cafile=f"{environment['certs']}/ca.pem")
    with pytest.raises((ssl.SSLError, ConnectionResetError, urllib.error.URLError)):
        urllib.request.urlopen(environment["url"] + "/health", context=ctx, timeout=10).read()


def test_vault_encrypts_and_detects_tampering(environment):
    bov = environment["vault"]
    bov.save("test-0001", {"synthetic": True, "x": 1})
    records = bov.read()
    assert ("test-0001", {"synthetic": True, "x": 1}) in records
    raw = open(bov.file).read()
    assert '"x": 1' not in raw
    lines = raw.splitlines()
    nonces = [json.loads(l)["nonce"] for l in lines]
    assert len(nonces) == len(set(nonces))
    tampered = json.loads(lines[-1]); tampered["id"] = "test-0002"
    with open(bov.file, "a") as f:
        f.write(json.dumps(tampered) + "\n")
    with pytest.raises(Exception):
        bov.read()


def test_key_of_vault_outside_of_repo(tmp_path):
    within = os.path.join(ROOT, "artifacts", "forbidden_key.key")
    with pytest.raises(vault.VaultError):
        vault.load_key(within)


def _raw(url, body, kind="application/json", length=None):
    req = urllib.request.Request(url, data=body, method="POST")
    if kind:
        req.add_header("Content-Type", kind)
    if length is not None:
        req.add_header("Content-Length", length)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code


def test_f11_api_of_hospital_rejects_kinds_and_sizes(environment):
    u = environment["hosp"] + "/api/evaluate"
    assert _raw(u, b'{"random_patient": true}', kind="text/plain") == 415
    assert _raw(u, b"[1, 2]") == 400
    # The server rejects an oversized declared length before reading the body.
    # Send only one byte to avoid an OS-dependent reset while the client is still writing.
    assert _raw(u, b"x", length=70 * 1024) == 413


def test_f11_timings_separate_and_include_vault(environment):
    r = post(environment["hosp"] + "/api/evaluate", {"profile": "Synthetic A · low risk"})
    t = r["timings_ms"]
    assert {"encrypt", "network_and_service", "decrypt", "interpret", "vault", "total_in_hospital"} <= set(t)
    assert t["total_in_hospital"] >= t["encrypt"] + t["network_and_service"] + t["decrypt"] - 1


def test_frontend_config_exposes_all_scopes_and_source_identity(environment):
    with urllib.request.urlopen(environment["hosp"] + "/api/test-config") as response:
        config = json.loads(response.read())
    assert config["api_sizes"] == [20, 200, 2000, 16000]
    assert [(p["process_n"],p["api_n"]) for p in config["profiles"]] == [(20,20),(200,200),(2000,200),(16000,200)]
    assert config["warmup"] == 3 and config["seed"] == 2026
    assert config["code_sha256"] == provenance.hash_code()[0]
    assert config["model_sha256"] == provenance.sha256(MODEL_JSON)


def test_seeded_browser_input_is_reproducible_and_exact(environment):
    seed = 2030
    first = post(environment["hosp"] + "/api/evaluate", {"synthetic_seed":seed})
    second = post(environment["hosp"] + "/api/evaluate", {"synthetic_seed":seed})
    assert first["hospital"]["input"] == second["hospital"]["input"] == synthetic.random_patient(seed)
    assert first["hospital"]["integer_reference_match"] is True
    assert first["hospital"]["z_integer"] == second["hospital"]["z_integer"]
    assert first["id"] != second["id"]
    assert first["code_sha256"] == provenance.hash_code()[0]
    assert first["model_sha256"] == provenance.sha256(MODEL_JSON)
    assert first["server"]["received"]["ciphertexts"] != second["server"]["received"]["ciphertexts"]


@pytest.mark.parametrize("seed", [True,"2026",-1,2**32,1.5])
def test_invalid_browser_seed_is_rejected(environment, seed):
    with pytest.raises(urllib.error.HTTPError) as error:
        post(environment["hosp"] + "/api/evaluate", {"synthetic_seed":seed})
    assert error.value.code == 400
