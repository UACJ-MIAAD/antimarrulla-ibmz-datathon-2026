"""Two-host integration: service in a separate process with evidence; hospital uses synthetic inputs
and an explicit labeled CDC sample. CI runs on one host, so strict separation must fail while
--allow-same-machine passes only as a rehearsal. Detect tampering, plaintext result leakage,
a shared host and a private key in the service process.
"""
import argparse, json, os, socket, subprocess, sys, threading, time
import pytest
from screening import two_hosts, hospital, protocol, secrets_setup, service
from screening.paths import MODEL_JSON, ROOT


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    d = tmp_path_factory.mktemp("two_hosts")
    secrets_setup.generate(str(d / "service"), export_hospital=str(d / "for_hospital"))
    c = d / "service" / "certs"
    assert not (c / "hospital.key").exists() and (d / "for_hospital" / "hospital.key").exists()
    port = _free_port()
    env = {**os.environ, "PYTHONPATH": os.path.join(ROOT, "src"), "SERVICE_HOST": "127.0.0.1", "SERVICE_PORT": str(port),
           "SERVICE_CERT": str(c / "service.pem"), "SERVICE_KEY": str(c / "service.key"), "SERVICE_CLIENT_CA": str(c / "ca.pem"),
           "MODEL_JSON": MODEL_JSON, "SERVICE_EVIDENCE": str(d / "evidence")}
    log = open(d / "service.log", "w")
    proc = subprocess.Popen([sys.executable, "-m", "screening.service"], env=env, stdout=log, stderr=subprocess.STDOUT)
    try:
        for _ in range(100):
            if (d / "evidence" / "service_startup.json").exists():
                try:
                    socket.create_connection(("127.0.0.1", port), timeout=0.2).close()
                    break
                except OSError:
                    pass
            time.sleep(0.1)
        two_hosts.run_hospital(argparse.Namespace(service=f"https://localhost:{port}", certs=str(d / "for_hospital"),
                                                        output=str(d / "hospital"), n=8, without_evidence=False))
        two_hosts.run_hospital(argparse.Namespace(service=f"https://localhost:{port}", certs=str(d / "for_hospital"),
                                                        output=str(d / "hospital_cdc"), n=8, data="cdc", without_evidence=False))
        two_hosts.run_hospital(argparse.Namespace(service=f"https://localhost:{port}", certs=str(d / "for_hospital"),
                                                        output=str(d / "hospital_parallel"), n=12, data="cdc", concurrency=3,
                                                        without_evidence=False))
    finally:
        proc.terminate(); proc.wait(10); log.close()
    return d


def _audit(d, output, *extra):
    a = argparse.Namespace(service=str(d / "evidence"), hospital=str(d / "hospital"), log_service=[str(d / "service.log")],
                           output=str(output), samples=1, allow_same_machine="same" in extra)
    rc = two_hosts.audit(a)
    reports = sorted(p for p in output.glob("audit_*.json") if p.name.count("_") == 1)
    return rc, json.loads(reports[-1].read_text())


def test_rehearsal_passes_and_strict_requires_two_hosts(run, tmp_path):
    rc, rep = _audit(run, tmp_path / "a", "same")
    assert rc == 0 and rep["passed"] and rep["verdict"].startswith("REHEARSAL")
    assert rep["hospital"]["accuracy"]["identical_integers"] == 8
    assert rep["hospital"]["sample"]["data"] == "synthetic"
    assert rep["hospital"]["metrics_same_sample"] is None
    rc, rep = _audit(run, tmp_path / "b")
    failures = [c["key"] for c in rep["checks"] if not c["ok"]]
    assert rc == 1 and failures == ["two_hosts"]


def test_names_different_of_same_host_does_not_prove_two_hosts(run, tmp_path):
    p = run / "hospital" / "hospital_summary.json"
    original = p.read_text()
    try:
        m = json.loads(original)
        m["machine"] = "another-container-on-the-same-host"
        p.write_text(json.dumps(m))
        rc, rep = _audit(run, tmp_path)
        assert rc == 1
        assert any(c["key"] == "two_hosts" and not c["ok"] for c in rep["checks"])
    finally:
        p.write_text(original)


def test_cdc_is_benchmark_explicit_with_labels(run):
    m = json.loads((run / "hospital_cdc" / "hospital_summary.json").read_text())
    assert m["sample"]["data"] == "cdc" and m["accuracy"]["identical_integers"] == 8
    assert m["metrics_same_sample"]["floating"]["roc_auc"] == m["metrics_same_sample"]["ciphertext"]["roc_auc"]


def test_detects_log_of_hospital_tampered(run, tmp_path):
    p = run / "hospital" / "hospital_log.jsonl"
    original = p.read_bytes()
    try:
        p.write_bytes(original + b"\n")
        rc, rep = _audit(run, tmp_path, "same")
        assert rc == 1 and any(c["key"] == "integrity" and not c["ok"] for c in rep["checks"])
    finally:
        p.write_bytes(original)


def test_detects_model_of_service_different(run, tmp_path):
    p = run / "evidence" / "service_startup.json"
    original = p.read_text()
    try:
        m = json.loads(original); m["model_sha256"] = "0" * 64
        p.write_text(json.dumps(m))
        rc, rep = _audit(run, tmp_path, "same")
        assert rc == 1 and any(c["key"] == "versions" and not c["ok"] for c in rep["checks"])
    finally:
        p.write_text(original)


def test_detects_evidence_tampered(run, tmp_path):
    # Select a request from this run, not a random UUID from another benchmark.
    rid = json.loads((run / "hospital" / "hospital_log.jsonl").read_text().splitlines()[-1])["id"]
    sol = run / "evidence" / "requests" / (rid + ".request.json")
    original = sol.read_bytes()
    try:
        changed = original.replace(b'"exponent": 0', b'"exponent": 0, "HighBP": 1')
        assert changed != original
        sol.write_bytes(changed)
        rc, rep = _audit(run, tmp_path, "same")
        assert rc == 1 and {c["key"] for c in rep["checks"] if not c["ok"]} >= {"bytes", "structure"}
    finally:
        sol.write_bytes(original)


def test_detects_result_in_plaintext_in_the_service(run, tmp_path):
    z = json.loads((run / "hospital" / "hospital_log.jsonl").read_text().splitlines()[-1])["z_decrypted"]
    with open(run / "service.log", "a") as f:
        f.write(f"debug: z={z}\n")
    try:
        rc, rep = _audit(run, tmp_path, "same")
        assert rc == 1 and [c["key"] for c in rep["checks"] if not c["ok"]] == ["without_plaintext"]
    finally:
        lines = (run / "service.log").read_text().splitlines(keepends=True)
        (run / "service.log").write_text("".join(lines[:-1]))


def test_the_check_of_key_detects_to_hospital_in_the_same_process(tmp_path, model, keys):
    "A service sharing the hospital process exposes a private key in its process-level check."
    secrets_setup.generate(str(tmp_path))
    c = tmp_path / "certs"
    srv, _ = service.create_server("127.0.0.1", 0, model, str(c / "service.pem"), str(c / "service.key"), str(c / "ca.pem"),
                                     evidence=str(tmp_path / "ev"))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        h = protocol.hospital(model, keys=keys)  # A private key exists in THIS process.
        cli = hospital.ServiceClient(f"https://localhost:{srv.server_address[1]}", str(c / "ca.pem"), str(c / "hospital.pem"), str(c / "hospital.key"))
        assert cli.health()["evidence"] is True
        sol, _ = h.prepare({n: 0 if n not in ("BMI", "GenHlth", "Age") else 12 if n == "BMI" else 1 for n in model["variables"]})
        cli.evaluate(sol)
    finally:
        srv.shutdown()
    e = json.loads((tmp_path / "ev" / "service_audit.jsonl").read_text())
    assert e["private_key_in_memory"] is True and e["tls"] == "TLSv1.3" and e["client_cn"] == "hospital"


def test_certificate_with_ip_of_service(tmp_path):
    from cryptography import x509
    secrets_setup.generate(str(tmp_path), san_extra=["148.100.77.9", "vm-service"])
    cert = x509.load_pem_x509_certificate((tmp_path / "certs" / "service.pem").read_bytes())
    san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
    assert "vm-service" in san.get_values_for_type(x509.DNSName)
    assert "148.100.77.9" in [str(i) for i in san.get_values_for_type(x509.IPAddress)]


def test_evidence_storage_failure_does_not_acknowledge_success(tmp_path, model, keys, monkeypatch):
    "An audited response cannot succeed when its evidence cannot be saved."
    secrets_setup.generate(str(tmp_path))
    c = tmp_path / "certs"
    srv, _ = service.create_server("127.0.0.1", 0, model, str(c / "service.pem"), str(c / "service.key"), str(c / "ca.pem"),
                                   evidence=str(tmp_path / "evidence"))
    def unavailable(*args):
        raise OSError("simulated audit storage failure")
    monkeypatch.setattr(srv.evidence, "capture", unavailable)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        h = protocol.hospital(model, keys=keys)
        cli = hospital.ServiceClient(f"https://localhost:{srv.server_address[1]}", str(c / "ca.pem"), str(c / "hospital.pem"), str(c / "hospital.key"))
        patient = {n: 0 if n not in ("BMI", "GenHlth", "Age") else 12 if n == "BMI" else 1 for n in model["variables"]}
        request, _ = h.prepare(patient)
        with pytest.raises(protocol.InvalidMessage, match="HTTP 503"):
            cli.evaluate(request)
    finally:
        srv.shutdown()
        srv.server_close()


def test_concurrency_keeps_exact_results_and_audit(run, tmp_path):
    """With 3 worker processes every patient still decrypts exactly and the audit still passes."""
    res = json.loads((run / "hospital_parallel" / "hospital_summary.json").read_text())
    assert res["concurrency"] == 3 and res["accuracy"]["identical_integers"] == 12 and res["wall_time_s"] > 0
    lines = [json.loads(l) for l in (run / "hospital_parallel" / "hospital_log.jsonl").read_text().splitlines()]
    assert len({l["id"] for l in lines}) == len(lines) == 12 + res["warmup"]
    a = argparse.Namespace(service=str(run / "evidence"), hospital=str(run / "hospital_parallel"),
                           log_service=[str(run / "service.log")], output=str(tmp_path), samples=1, allow_same_machine=True)
    assert two_hosts.audit(a) == 0


def test_plaintext_vector_detector_follows_schema_size():
    """The audit must recognize a leaked plaintext input of the CURRENT schema size, and not a ciphertext list."""
    from screening import schema
    n = len(schema.FEATURE_NAMES)
    assert two_hosts.PLAINTEXT_VECTOR.search(json.dumps([1] * n))
    assert not two_hosts.PLAINTEXT_VECTOR.search(json.dumps([str(10 ** 600)] * n))
