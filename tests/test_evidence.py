"Recorded evidence runs: a complete s390x run validates; tampering, failures, other hosts and secrets are rejected."
import hashlib, importlib.util, json, os
import pytest

TOOL = os.path.join(os.path.dirname(__file__), "..", "tools", "evidence.py")
if not os.path.exists(TOOL):  # The dev image copies tests but not tools/.
    pytest.skip("tools/evidence.py is not in this build context", allow_module_level=True)
spec = importlib.util.spec_from_file_location("evidence", TOOL)
ev = importlib.util.module_from_spec(spec); spec.loader.exec_module(ev)

COMMIT = "a" * 40
SMOKE = ("service OK · architecture s390x · key 2048 bits · model e32420ac99fd\n"
         "Synthetic A · low risk: p=0.015 · exact z · 120 ms inside the hospital\n"
         "Synthetic B · intermediate risk: p=0.152 · exact z · 120 ms inside the hospital\n"
         "Synthetic C · high risk: p=0.633 · exact z · 120 ms inside the hospital\nsmoke OK\n")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def put(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(data if isinstance(data, str) else json.dumps(data))
    return path


def make_run(root, arch="s390x"):
    model = put(os.path.join(root, ev.MODEL), "{}")
    msha = sha(model)
    base = {"environment_label": "s390x-linuxone", "environment": {"is_linuxone_s390x": True},
            "provenance": {"clean": True, "commit": COMMIT, "code_sha256": "c" * 64, "model_sha256": msha}}
    proc = {**base, "mode": "process", "sample": {"n": 2000}, "microbenchmark_in_process": {"encrypt_hospital": {"p50_ms": 300.0}},
            "accuracy": {"identical_integers": 2000, "of": 2000, "all_within_bound": True, "error_max_logit_vs_floating": 3e-8},
            "metrics_same_sample": {"ciphertext": {"roc_auc": 0.806525}}}
    api = {**base, "mode": "api", "sample": {"n": 200}, "accuracy": {"identical_integers": 200, "of": 200},
           "client_ms": {"n": 200, "p50_ms": 350.0, "p95_ms": 380.0},
           "hospital_remote": {"model_sha256": msha, "code_equal_to_client": True}}
    mp = put(os.path.join(root, ev.METRICS, "measurement_process_s390x_1.json"), proc)
    ma = put(os.path.join(root, ev.METRICS, "measurement_api_s390x_1.json"), api)
    run = os.path.join(root, ev.RUNS, f"{arch}_20261018T050000Z")
    texts = {"verify": "100 passed\nverification OK\n", "demo": SMOKE}
    steps = []
    for i, (name, cmd) in enumerate(ev.STEPS, 1):
        log = put(os.path.join(run, "logs", f"{i:02d}_{name}.log"), f"$ {cmd}\n{texts.get(name, 'ok')}\n[exit 0]\n")
        steps.append({"name": name, "command": cmd, "exit_code": 0, "seconds": 1.0, "log": f"logs/{i:02d}_{name}.log", "sha256": sha(log)})
    uname = put(os.path.join(run, "system", "uname.txt"), f"Linux vm 6.8.0 {arch}\n{arch}\n")
    man = {"schema": ev.SCHEMA, "run_id": os.path.basename(run), "status": "passed", "arch": arch, "commit": COMMIT,
           "operator": "Carlos", "started_utc": "2026-10-18T05:00:00Z", "ended_utc": "2026-10-18T05:20:00Z", "redactions": 0,
           "steps": steps, "system_files": [{"name": "uname", "file": "system/uname.txt", "sha256": sha(uname)}],
           "measurements": [{"path": os.path.relpath(p, root), "sha256": sha(p)} for p in (mp, ma)]}
    put(os.path.join(run, "manifest.json"), man)
    return run


def manifest(run):
    return json.load(open(os.path.join(run, "manifest.json")))


def test_complete_s390x_run_is_valid(tmp_path):
    run = make_run(str(tmp_path))
    errors, warnings, s = ev.check(run, root=str(tmp_path))
    assert errors == []
    assert s["smoke"]["Synthetic C"] == 0.633 and s["process"]["exact"] == 2000 and s["api"]["client_ms"]["p50_ms"] == 350.0
    assert any("not available" in w for w in warnings)  # fake commit: code hash not recomputed, reported
    text = ev.write_summary(run, manifest(run), errors, warnings, s)
    assert "**VALID**" in text and "63.3%" in text and "3e-08" in text


def test_edited_log_is_rejected(tmp_path):
    run = make_run(str(tmp_path))
    with open(os.path.join(run, "logs", "05_measure_api.log"), "a") as f:
        f.write("edited by hand\n")
    assert any("hash mismatch" in e for e in ev.check(run, root=str(tmp_path))[0])


def test_failed_step_is_rejected(tmp_path):
    run = make_run(str(tmp_path)); man = manifest(run)
    man["steps"][3]["exit_code"] = 2; man["status"] = "failed"
    put(os.path.join(run, "manifest.json"), man)
    errors = ev.check(run, root=str(tmp_path))[0]
    assert any("measure_process exited 2" in e for e in errors) and any("status" in e for e in errors)


def test_other_architecture_needs_explicit_rehearsal_flag(tmp_path):
    run = make_run(str(tmp_path), arch="arm64")
    assert any("not s390x" in e for e in ev.check(run, root=str(tmp_path))[0])
    assert ev.check(run, require_s390x=False, root=str(tmp_path))[0] == []


def test_inexact_measurement_is_rejected(tmp_path):
    run = make_run(str(tmp_path)); man = manifest(run)
    p = os.path.join(str(tmp_path), man["measurements"][1]["path"])
    m = json.load(open(p)); m["accuracy"]["identical_integers"] = 199; put(p, m)
    man["measurements"][1]["sha256"] = sha(p); put(os.path.join(run, "manifest.json"), man)
    assert any("fails the final measurement rules" in e for e in ev.check(run, root=str(tmp_path))[0])


def test_secret_in_run_is_rejected(tmp_path):
    run = make_run(str(tmp_path))
    put(os.path.join(run, "notes.txt"), "-----BEGIN RSA PRIVATE KEY-----\nabc\n")
    assert any("possible secret" in e for e in ev.check(run, root=str(tmp_path))[0])


def test_redaction_keeps_versions_and_private_addresses():
    text, n = ev.redact("ssh from 203.0.113.7 to 10.0.0.5 and 127.0.0.1; OpenSSL 3.0.13; token ghp_" + "x" * 30)
    assert "203.0.113.7" not in text and "10.0.0.5" in text and "127.0.0.1" in text and "3.0.13" in text
    assert "ghp_" not in text and n == 2
