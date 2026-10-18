"Recorded evidence runs: a complete s390x run validates; tampering, failures, other hosts and secrets are rejected."
import hashlib, importlib.util, json, os, shutil, subprocess
import pytest

TOOL = os.path.join(os.path.dirname(__file__), "..", "tools", "evidence.py")
if not os.path.exists(TOOL):  # The dev image copies tests but not tools/.
    pytest.skip("tools/evidence.py is not in this build context", allow_module_level=True)
spec = importlib.util.spec_from_file_location("evidence", TOOL)
ev = importlib.util.module_from_spec(spec); spec.loader.exec_module(ev)

COMMIT = ev._git("rev-parse", "HEAD")
CODE = ev._code_hash_at(COMMIT)
MODEL = json.load(open(os.path.join(ev.ROOT, ev.MODEL)))
MODEL_SHA = ev._sha(os.path.join(ev.ROOT, ev.MODEL))
SMOKE = (f"service OK · architecture s390x · key 2048 bits · model {MODEL_SHA[:12]}\n"
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


def make_run(root, arch="s390x", profile="2000", api_n=None):
    plan = ev.benchmark_profiles.profile(profile, api_n)
    model = put(os.path.join(root, ev.MODEL), open(os.path.join(ev.ROOT, ev.MODEL)).read())
    msha = sha(model)
    base = {"date_utc": "2026-10-18T05:10:00Z", "environment_label": "s390x-linuxone", "environment": {"is_linuxone_s390x": arch == "s390x", "machine": arch, "system": "Linux"},
            "provenance": {"clean": True, "commit": COMMIT, "code_sha256": CODE, "model_sha256": msha}}
    proc = {**base, "mode": "process", "sample": {"n": plan["process_n"]}, "microbenchmark_in_process": {"encrypt_hospital": {"p50_ms": 300.0}},
            "accuracy": {"identical_integers": plan["process_n"], "of": plan["process_n"], "all_within_bound": True, "error_max_logit_vs_floating": 3e-8, "applicable_max_bound": 9e-8},
            "metrics_same_sample": {k: {"roc_auc": 0.806525} for k in ("floating", "fixed_point", "ciphertext")}}
    api = {**base, "mode": "api", "sample": {"n": plan["api_n"]}, "accuracy": {"identical_integers": plan["api_n"], "of": plan["api_n"]},
           "client_ms": {"n": plan["api_n"], "p50_ms": 350.0, "p95_ms": 380.0},
           "hospital_remote": {"model_sha256": msha, "code_equal_to_client": True, "code_sha256": CODE, "machine": arch}}
    mp = put(os.path.join(root, ev.METRICS, "measurement_process_s390x_1.json"), proc)
    ma = put(os.path.join(root, ev.METRICS, "measurement_api_s390x_1.json"), api)
    run = os.path.join(root, ev.RUNS, f"{arch}_20261018T050000Z")
    texts = {"verify": "100 passed\nverification OK\n", "demo": SMOKE.replace("architecture s390x", f"architecture {arch}"), "image_inspect": "app image OK: model/UI present"}
    steps = []
    for i, (name, cmd) in enumerate(ev.steps_for(plan), 1):
        log = put(os.path.join(run, "logs", f"{i:02d}_{name}.log"), f"$ {cmd}\n{texts.get(name, 'ok')}\n[exit 0]\n")
        steps.append({"name": name, "command": cmd, "exit_code": 0, "seconds": 1.0, "log": f"logs/{i:02d}_{name}.log", "sha256": sha(log)})
    uname = put(os.path.join(run, "system", "uname.txt"), f"Linux vm 6.8.0 {arch}\n{arch}\n")
    system_files = [{"name": "uname", "file": "system/uname.txt", "sha256": sha(uname), "exit_code": 0}]
    for name in ("docker", "openssl", "compose_ps", "compose_logs", "lscpu", "sysinfo", "os_release"):
        file = put(os.path.join(run, "system", name + ".txt"), "recorded fixture")
        system_files.append({"name": name, "file": f"system/{name}.txt", "sha256": sha(file), "exit_code": 0})
    state = {"machine": arch, "model_sha256": msha, "code_sha256": CODE,
             "service": {"state": "ok", "key_private": False, "model_sha256": msha, "code_sha256": CODE}}
    state_file = put(os.path.join(run, "system", "api_state.json"), state)
    system_files.append({"name": "api_state", "file": "system/api_state.json", "sha256": sha(state_file)})
    man = {"schema": ev.SCHEMA, "profile": plan, "run_id": os.path.basename(run), "status": "passed", "arch": arch, "commit": COMMIT,
           "operator": "Carlos", "started_utc": "2026-10-18T05:00:00Z", "ended_utc": "2026-10-18T05:20:00Z", "redactions": 0,
           "steps": steps, "system_files": system_files,
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
    assert s["code_sha256"] == CODE
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


def change_measurement(root, run, mode, edit):
    man = manifest(run)
    for item in man["measurements"]:
        path = os.path.join(root, item["path"])
        data = json.load(open(path))
        if data["mode"] == mode:
            edit(data); put(path, data); item["sha256"] = sha(path)
    put(os.path.join(run, "manifest.json"), man)


@pytest.mark.parametrize("mode", ["process", "api"])
def test_single_patient_cannot_pass_final_gate(tmp_path, mode):
    root = str(tmp_path); run = make_run(root)
    def change(d):
        d["sample"]["n"] = 1; d["accuracy"].update(identical_integers=1, of=1)
        if mode == "api": d["client_ms"]["n"] = 1
    change_measurement(root, run, mode, change)
    assert any("requires exactly" in e for e in ev.check(run, root=root)[0])


def test_unavailable_commit_fails_closed(tmp_path, monkeypatch):
    run = make_run(str(tmp_path)); monkeypatch.setattr(ev, "_code_hash_at", lambda _: None)
    assert any("not available" in e for e in ev.check(run, root=str(tmp_path))[0])


def test_smoke_values_are_recomputed_even_if_hash_is_updated(tmp_path):
    run = make_run(str(tmp_path)); man = manifest(run); st = man["steps"][2]
    p = os.path.join(run, st["log"]); put(p, open(p).read().replace("0.633", "0.999"))
    st["sha256"] = sha(p); put(os.path.join(run, "manifest.json"), man)
    assert any("probabilities differ" in e for e in ev.check(run, root=str(tmp_path))[0])


@pytest.mark.parametrize("name", ["uname", "lscpu", "sysinfo", "docker", "openssl", "compose_ps", "api_state"])
def test_missing_identity_is_rejected(tmp_path, name):
    run = make_run(str(tmp_path)); man = manifest(run)
    man["system_files"] = [i for i in man["system_files"] if i["name"] != name]
    put(os.path.join(run, "manifest.json"), man)
    assert any("missing system evidence" in e for e in ev.check(run, root=str(tmp_path))[0])


@pytest.mark.parametrize("mutation", ["auc", "nan", "wrong_arch", "remote_code"])
def test_inconsistent_metrics_fail(tmp_path, mutation):
    root = str(tmp_path); run = make_run(root)
    def change(d):
        if mutation == "auc": d["metrics_same_sample"]["ciphertext"]["roc_auc"] = 0.5
        elif mutation == "nan": d["accuracy"]["error_max_logit_vs_floating"] = float("nan")
        elif mutation == "wrong_arch": d["environment"]["machine"] = "x86_64"
        else: d["hospital_remote"]["code_sha256"] = "f" * 64
    change_measurement(root, run, "api" if mutation == "remote_code" else "process", change)
    assert ev.check(run, root=root)[0]


@pytest.mark.parametrize("relative", ["../../outside.log", "/tmp/outside.log", "logs/link.log"])
def test_unsafe_log_paths_are_rejected(tmp_path, relative):
    run = make_run(str(tmp_path)); man = manifest(run)
    if relative.endswith("link.log"):
        os.symlink(os.path.join(run, "logs", "01_verify.log"), os.path.join(run, relative))
    man["steps"][0]["log"] = relative; put(os.path.join(run, "manifest.json"), man)
    assert any("unsafe evidence path" in e or "symlink" in e for e in ev.check(run, root=str(tmp_path))[0])


def test_private_key_body_and_unterminated_key_are_removed():
    for end in ("-----END PRIVATE KEY-----", ""):
        value, count = ev.redact("-----BEGIN PRIVATE KEY-----\ndummy-private-body\n" + end)
        assert "dummy-private-body" not in value and count


@pytest.mark.parametrize("value", ["https://[2001:4860:4860::8888]/", "Authorization: Bearer dummy-access-token", '"token": "dummy-access-token"', '"Authorization": "Bearer dummy-access-token"', "password=not-a-real-password", "https://user:dummy-password@example.org/"])
def test_additional_sensitive_values_are_redacted(value):
    cleaned, count = ev.redact(value)
    assert cleaned != value and count


def test_shell_redacts_before_terminal_and_file(tmp_path, capsys):
    log = str(tmp_path / "output.log")
    ev._shell("printf '%s\\n' '-----BEGIN PRIVATE KEY-----' 'dummy-private-body' '-----END PRIVATE KEY-----'", log)
    assert "dummy-private-body" not in capsys.readouterr().out
    assert "dummy-private-body" not in open(log).read()


def test_measurement_secrets_are_scanned(tmp_path):
    root = str(tmp_path); run = make_run(root)
    change_measurement(root, run, "api", lambda d: d.update(note="Authorization: Bearer dummy-access-token"))
    assert any("possible secret" in e for e in ev.check(run, root=root)[0])


def test_no_runs_fails_when_required(tmp_path, monkeypatch):
    import argparse
    monkeypatch.setattr(ev, "ROOT", str(tmp_path))
    assert ev.cmd_check(argparse.Namespace(runs=[], require_runs=True, allow_non_s390x=False, github_summary=False)) == 1


def test_publish_preserves_unrelated_staged_work(tmp_path, monkeypatch):
    monkeypatch.setattr(ev, "_git", lambda *a, **kw: "main" if a[0] == "rev-parse" else "unrelated.txt")
    assert ev.publish("test", "unused", [], "passed", 0) is False


@pytest.mark.parametrize("push_works", [True, False])
def test_publication_and_bundle_with_fake_remote(tmp_path, monkeypatch, push_works):
    repo = tmp_path / "repo"; remote = tmp_path / "remote.git"; repo.mkdir()
    def git(*args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    git("init", "-b", "main"); git("config", "user.name", "Test Operator"); git("config", "user.email", "test@example.org")
    git("config", "commit.gpgsign", "false"); put(str(repo / "tracked.txt"), "fixture")
    git("add", "tracked.txt"); git("commit", "-m", "fixture")
    git("remote", "add", "origin", str(remote) if push_works else str(tmp_path / "absent.git"))
    rel = os.path.join(ev.RUNS, "fixture"); put(str(repo / rel / "SUMMARY.md"), "synthetic fixture")
    put(str(repo / "personal.pptx"), "must remain untracked")
    monkeypatch.setattr(ev, "ROOT", str(repo))
    assert ev.publish("fixture", rel, [], "failed", 1) is push_works
    assert git("branch", "--show-current") == "main"
    assert git("ls-tree", "--name-only", "-r", "evidence/fixture") == rel + "/SUMMARY.md\ntracked.txt"
    if not push_works:
        bundle = str(repo / "dist" / "fixture.bundle")
        assert os.path.isfile(bundle)
        git("bundle", "verify", bundle)


def test_replayed_measurement_from_before_the_run_is_rejected(tmp_path):
    root = str(tmp_path); run = make_run(root)
    change_measurement(root, run, "process", lambda d: d.update(date_utc="2026-10-17T05:00:00Z"))
    assert any("outside this run" in e for e in ev.check(run, root=root)[0])


def test_failure_run_keeps_logs_and_reports_publication_failure(tmp_path, monkeypatch):
    import argparse
    root = str(tmp_path)
    monkeypatch.setattr(ev, "ROOT", root)
    monkeypatch.setattr(ev.provenance, "git_state", lambda _: {"relevant": [], "commit": COMMIT})
    monkeypatch.setattr(ev, "_git", lambda *a, **kw: "main" if a[0] == "symbolic-ref" else ("Test Operator" if a[0] == "config" else ""))
    def shell(command, log, echo=True):
        put(log, "$ " + command + "\nfixture failure\n[exit 2]\n")
        return 2, 0.1, 0
    monkeypatch.setattr(ev, "_shell", shell)
    monkeypatch.setattr(ev.urllib.request, "urlopen", lambda *a, **kw: (_ for _ in ()).throw(OSError("fixture offline")))
    deliveries = []
    monkeypatch.setattr(ev, "publish", lambda *a: deliveries.append(a) or False)
    assert ev.run(argparse.Namespace(no_push=False, steps=None, down=False)) == 1
    assert len(deliveries) == 1 and deliveries[0][3] == "failed"
    run = ev._run_dirs(None)[0]
    assert manifest(run)["status"] == "failed"
    assert os.path.isfile(os.path.join(run, "logs", "01_verify.log"))
    assert "NOT VALID" in open(os.path.join(run, "SUMMARY.md")).read()


@pytest.mark.parametrize("profile", ["20", "200", "2000", "16000"])
def test_declared_profile_validates_exact_requested_sample(tmp_path, profile):
    root = str(tmp_path); run = make_run(root, profile=profile)
    errors, warnings, summary = ev.check(run, root=root)
    assert errors == []
    assert summary["process"]["n"] == int(profile)
    text = ev.write_summary(run, manifest(run), errors, warnings, summary)
    assert ("DIAGNOSTIC ONLY" in text) == (int(profile) < 2000)


def test_large_api_override_is_recorded_and_checked(tmp_path):
    root = str(tmp_path); run = make_run(root, profile="16000", api_n=16000)
    assert ev.check(run, root=root)[0] == []
    assert manifest(run)["profile"]["api_n"] == 16000
    change_measurement(root, run, "api", lambda d: d["sample"].update(n=200))
    assert any("requires exactly 16000" in e for e in ev.check(run, root=root)[0])


def test_diagnostic_cannot_declare_itself_release_sized(tmp_path):
    root = str(tmp_path); run = make_run(root, profile="20"); man = manifest(run)
    man["profile"]["release_eligible"] = True; put(os.path.join(run, "manifest.json"), man)
    assert any("profile declaration" in e for e in ev.check(run, root=root)[0])


def test_live_output_is_streamed_and_redacted(tmp_path, capsys):
    cmd = ("printf 'pilot: estimated 90 min\\nfrom 203.0.113.9\\n"
           "-----BEGIN RSA PRIVATE KEY-----\\nSECRETBODY\\n-----END RSA PRIVATE KEY-----\\ndone\\n'")
    code, _, n = ev._shell(cmd, str(tmp_path / "x.log"))
    shown = capsys.readouterr().out
    assert code == 0 and n >= 2 and "pilot: estimated 90 min" in shown and "done" in shown
    assert "203.0.113.9" not in shown and "SECRETBODY" not in shown and "[REDACTED-PRIVATE-KEY]" in shown
    saved = open(tmp_path / "x.log").read()
    assert "SECRETBODY" not in saved and "203.0.113.9" not in saved and saved.rstrip().endswith("[exit 0]")
