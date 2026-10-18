"""Recorded evidence runs: execute the release checks, keep every log and publish them through Git.

  run    On the target host (LinuxONE VM): run the Docker checks and FINAL measurements, save logs,
         system identity and a manifest under submission/evidence/runs/<run_id>/, then commit them to
         a new branch evidence/<run_id> and push it. Failed runs are committed too, so the logs arrive.
  check  Validate recorded runs: complete steps, log hashes, measurement content and provenance,
         code hash at the recorded commit, smoke results and absence of secrets. Writes SUMMARY.md.
  index  Rebuild submission/evidence/runs/INDEX.md from all recorded runs.

Standard library only; run from the repository root with PYTHONPATH=src (the Makefile sets it).
"""
import argparse, datetime, getpass, hashlib, io, json, os, platform, re, subprocess, sys, tarfile, tempfile, time, urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from screening import package, provenance  # noqa: E402

RUNS = os.path.join("submission", "evidence", "runs")
METRICS = os.path.join("submission", "evidence", "metrics")
MODEL = os.path.join("artifacts", "model", "logistic_model_v1.json")
SCHEMA = "evidence-run-v1"
STEPS = [
    ("verify", "make verify-docker"),
    ("image_inspect", "make image-inspect"),
    ("demo", "make demo-docker"),
    ("measure_process", "make measure-docker FINAL=1"),
    ("measure_api", "make measure-api-docker FINAL=1"),
]
SYSTEM = [
    ("uname", "uname -a; echo; uname -m"),
    ("os_release", "cat /etc/os-release"),
    ("lscpu", "lscpu"),
    ("sysinfo", "grep -v -i -E '^(Sequence Code|Plant)' /proc/sysinfo"),  # IBM Z machine type/LPAR; serial omitted
    ("memory", "free -h || vm_stat"),
    ("docker", "docker version; echo; docker compose version"),
    ("openssl", "openssl version -a"),
    ("git", "git log -1 --format='%H %an %cI %s'; git status --short --branch"),
]
SECRET = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----|\b(ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{20,}|\bAKIA[0-9A-Z]{16}\b|\bxox[abp]-[A-Za-z0-9-]{10,}")
IPV4 = re.compile(r"(?<![\d.])(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})(?![\d.])")
SMOKE = re.compile(r"^(Synthetic [ABC])[^:]*: p=([0-9.]+) · exact z", re.M)


def _utc():
    return datetime.datetime.now(datetime.timezone.utc)


def _sha(path):
    return provenance.sha256(path)


def _private(octets):
    a, b = octets[0], octets[1]
    return a in (0, 10, 127) or (a == 172 and 16 <= b <= 31) or (a == 192 and b == 168) or (a == 169 and b == 254)


def redact(text):
    "Remove secrets and public IPv4 addresses; return (text, count)."
    n = 0

    def ip(m):
        nonlocal n
        octets = [int(g) for g in m.groups()]
        if any(o > 255 for o in octets) or _private(octets):
            return m.group(0)
        n += 1
        return "[public-ip]"

    text, k = SECRET.subn("[REDACTED-SECRET]", text)
    return IPV4.sub(ip, text), n + k


def _git(*a, check=False):
    r = subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(a)}: {r.stderr.strip()}")
    return r.stdout.strip() if r.returncode == 0 else None


def _shell(cmd, log_path, echo=True):
    "Run a shell command from the repository root, streaming output to the terminal and a log."
    t0 = time.monotonic()
    p = subprocess.Popen(cmd, shell=True, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
    buf = io.StringIO()
    for line in p.stdout:
        buf.write(line)
        if echo:
            sys.stdout.write(line); sys.stdout.flush()
    code = p.wait()
    text, n = redact(f"$ {cmd}\n{buf.getvalue()}\n[exit {code}]\n")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(text)
    return code, round(time.monotonic() - t0, 1), n


def _measurements():
    d = os.path.join(ROOT, METRICS)
    return {f for f in os.listdir(d) if f.startswith("measurement_")} if os.path.isdir(d) else set()


def run(args):
    g = provenance.git_state(ROOT)
    if g.get("relevant") != [] or not g.get("commit"):
        sys.exit("evidence run: commit or stash relevant changes first (src, tests, docker, Makefile, artifacts): "
                 + ", ".join(g.get("relevant") or ["unknown state"]))
    started = _utc()
    arch = platform.machine().lower()
    run_id = f"{arch}_{started:%Y%m%dT%H%M%SZ}"
    rel_dir = os.path.join(RUNS, run_id)
    out = os.path.join(ROOT, rel_dir)
    os.makedirs(os.path.join(out, "logs")); os.makedirs(os.path.join(out, "system"))
    print(f"== evidence run {run_id} at {g['commit'][:7]} → {rel_dir}")
    redactions, system, steps, before = 0, [], [], _measurements()
    for name, cmd in SYSTEM:
        p = os.path.join(out, "system", f"{name}.txt")
        _, _, n = _shell(cmd, p, echo=False); redactions += n
        system.append({"name": name, "file": f"system/{name}.txt", "sha256": _sha(p)})
    status = "passed"
    selected = [s for s in STEPS if not args.steps or s[0] in args.steps]
    for i, (name, cmd) in enumerate(selected, 1):
        print(f"\n== [{i}/{len(selected)}] {name}: {cmd}")
        p = os.path.join(out, "logs", f"{i:02d}_{name}.log")
        code, secs, n = _shell(cmd, p); redactions += n
        steps.append({"name": name, "command": cmd, "exit_code": code, "seconds": secs, "log": f"logs/{i:02d}_{name}.log", "sha256": _sha(p)})
        if code:
            status = "failed"
            print(f"!! {name} failed with exit {code}; logs are still recorded and pushed")
            break
    if args.steps:
        status = "partial" if status == "passed" else status
    ui = os.environ.get("UI_URL", f"http://127.0.0.1:{os.environ.get('SCREENING_UI_PORT', '8080')}")
    post = [("compose_ps", "docker compose -f docker/compose.yml ps"),
            ("compose_logs", "docker compose -f docker/compose.yml logs --no-color --timestamps --tail 300")]
    for name, cmd in post:
        p = os.path.join(out, "system", f"{name}.txt")
        _, _, n = _shell(cmd, p, echo=False); redactions += n
        system.append({"name": name, "file": f"system/{name}.txt", "sha256": _sha(p)})
    try:
        with urllib.request.urlopen(ui + "/api/state", timeout=10) as r:
            state = json.loads(r.read())
        p = os.path.join(out, "system", "api_state.json")
        with open(p, "w") as f:
            json.dump(state, f, indent=2)
        system.append({"name": "api_state", "file": "system/api_state.json", "sha256": _sha(p)})
    except (OSError, ValueError) as e:
        print(f"note: {ui}/api/state not reachable ({e})")
    new = sorted(_measurements() - before)
    manifest = {
        "schema": SCHEMA, "run_id": run_id, "status": status,
        "started_utc": f"{started:%Y-%m-%dT%H:%M:%SZ}", "ended_utc": f"{_utc():%Y-%m-%dT%H:%M:%SZ}",
        "operator": _git("config", "user.name") or getpass.getuser(), "commit": g["commit"],
        "arch": arch, "system": platform.system(), "ui_url": ui, "redactions": redactions,
        "steps": steps, "system_files": system,
        "measurements": [{"path": f"{METRICS}/{f}", "sha256": _sha(os.path.join(ROOT, METRICS, f))} for f in new],
    }
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False); f.write("\n")
    errors, warnings, summary = check(out, require_s390x=(arch == "s390x"))
    write_summary(out, manifest, errors, warnings, summary)
    print(f"\n== {status.upper()} · check: {len(errors)} errors, {len(warnings)} warnings · {rel_dir}/SUMMARY.md")
    for e in errors:
        print("  error:", e)
    if args.down:
        _shell("make demo-down", os.devnull, echo=False)
    if not args.no_push:
        publish(run_id, rel_dir, [m["path"] for m in manifest["measurements"]], status, len(errors))
    return 0 if status == "passed" and not errors else 1


def publish(run_id, rel_dir, measurement_paths, status, n_errors):
    "Commit the run on evidence/<run_id> and push it; fall back to a Git bundle."
    branch = f"evidence/{run_id}"
    back = _git("rev-parse", "--abbrev-ref", "HEAD")
    try:
        _git("switch", "-c", branch, check=True)
        _git("add", "--", rel_dir, *measurement_paths, check=True)
        _git("commit", "-q", "-m", f"evidence: {run_id} {status} ({n_errors} check errors)", check=True)
    except RuntimeError as e:
        print("!! could not commit the run:", e); return
    pushed = subprocess.run(["git", "-C", ROOT, "push", "-u", "origin", branch]).returncode == 0
    if pushed:
        print(f"== pushed {branch}; CI validates it. Open a PR or tell the captain the branch name.")
    else:
        bundle = os.path.join(ROOT, "dist", f"{run_id}.bundle")
        os.makedirs(os.path.dirname(bundle), exist_ok=True)
        _git("bundle", "create", bundle, branch, check=False)
        print(f"!! push failed. Send this file instead: {bundle}\n   (receiver: git fetch {os.path.basename(bundle)} {branch}:{branch})")
    if back and back != "HEAD":
        _git("switch", back)


def _valid(m, mode, model_sha, require_s390x):
    if require_s390x:
        return package._valid_measurement(m, mode, model_sha)
    m = json.loads(json.dumps(m))
    m["environment_label"] = "s390x"
    m.setdefault("environment", {})["is_linuxone_s390x"] = True
    return package._valid_measurement(m, mode, model_sha)


def _code_hash_at(commit):
    "Hash src/screening as recorded at a commit, using the same rule as provenance.hash_code."
    raw = subprocess.run(["git", "-C", ROOT, "archive", "--format=tar", commit, "src/screening"], capture_output=True)
    if raw.returncode:
        return None
    with tempfile.TemporaryDirectory() as d:
        with tarfile.open(fileobj=io.BytesIO(raw.stdout)) as t:
            t.extractall(d, filter="data") if hasattr(tarfile, "data_filter") else t.extractall(d)
        return provenance.hash_code(os.path.join(d, "src", "screening"))[0]


def check(run_dir, require_s390x=True, root=ROOT):
    "Return (errors, warnings, summary) for one recorded run."
    errors, warnings, s = [], [], {}
    mpath = os.path.join(run_dir, "manifest.json")
    try:
        man = json.load(open(mpath, encoding="utf-8"))
    except (OSError, ValueError):
        return [f"{mpath}: missing or invalid manifest"], [], s
    if man.get("schema") != SCHEMA:
        errors.append(f"manifest schema is {man.get('schema')!r}, expected {SCHEMA}")
    s.update({k: man.get(k) for k in ("run_id", "status", "arch", "commit", "operator", "started_utc", "ended_utc")})
    if man.get("status") != "passed":
        errors.append(f"run status is {man.get('status')!r}")
    if require_s390x and man.get("arch") != "s390x":
        errors.append(f"architecture is {man.get('arch')!r}, not s390x")
    done = {st.get("name"): st for st in man.get("steps", [])}
    for name, _ in STEPS:
        st = done.get(name)
        if not st:
            errors.append(f"step {name} was not run")
        elif st.get("exit_code") != 0:
            errors.append(f"step {name} exited {st.get('exit_code')} (see {st.get('log')})")
    for item in man.get("steps", []) + man.get("system_files", []):
        f = os.path.join(run_dir, item.get("log") or item.get("file") or "")
        if not os.path.isfile(f):
            errors.append(f"missing file {os.path.relpath(f, run_dir)}")
        elif _sha(f) != item.get("sha256"):
            errors.append(f"{os.path.relpath(f, run_dir)} was modified after the run (hash mismatch)")
    for base, _, names in os.walk(run_dir):
        for n in names:
            try:
                text = open(os.path.join(base, n), encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if SECRET.search(text):
                errors.append(f"possible secret in {os.path.relpath(os.path.join(base, n), run_dir)}")
    model_path = os.path.join(root, MODEL)
    model_sha = _sha(model_path) if os.path.exists(model_path) else None
    found = {}
    for item in man.get("measurements", []):
        p = os.path.join(root, item.get("path", ""))
        if not os.path.isfile(p):
            errors.append(f"measurement {item.get('path')} is missing"); continue
        if _sha(p) != item.get("sha256"):
            errors.append(f"measurement {item.get('path')} hash mismatch"); continue
        if p.endswith(".json"):
            m = json.load(open(p, encoding="utf-8"))
            found[m.get("mode")] = (item["path"], m)
    codes = set()
    for mode in ("process", "api"):
        if mode not in found:
            errors.append(f"no {mode} measurement recorded by this run"); continue
        path, m = found[mode]
        if not _valid(m, mode, model_sha, require_s390x):
            errors.append(f"{path} fails the final measurement rules (s390x, clean commit, model {str(model_sha)[:12]}, all integers exact)")
        prov = m.get("provenance") or {}
        codes.add(prov.get("code_sha256"))
        if prov.get("commit") != man.get("commit"):
            errors.append(f"{path} commit {str(prov.get('commit'))[:7]} differs from the run commit {str(man.get('commit'))[:7]}")
    if len(codes) > 1:
        errors.append("process and api measurements report different code hashes")
    if codes and man.get("commit"):
        at = _code_hash_at(man["commit"])
        if at is None:
            warnings.append(f"commit {man['commit'][:7]} is not available here; code hash not recomputed (fetch it)")
        elif at not in codes:
            errors.append(f"measured code hash differs from src/screening at {man['commit'][:7]}")
        else:
            s["code_sha256"] = at
    logs = {st.get("name"): os.path.join(run_dir, st.get("log", "")) for st in man.get("steps", [])}

    def read(name):
        try:
            return open(logs[name], encoding="utf-8").read()
        except (KeyError, OSError):
            return ""
    if done.get("verify") and "verification OK" not in read("verify"):
        errors.append("verify log lacks 'verification OK'")
    demo = read("demo")
    s["smoke"] = {k: float(v) for k, v in SMOKE.findall(demo)}
    if done.get("demo") and ("smoke OK" not in demo or len(s["smoke"]) != 3):
        errors.append("demo log lacks the three exact synthetic results and 'smoke OK'")
    s["model_sha256"] = model_sha
    if "process" in found:
        m = found["process"][1]
        auc = (m.get("metrics_same_sample") or {})
        s["process"] = {"file": found["process"][0], "n": (m.get("sample") or {}).get("n"),
                        "exact": (m.get("accuracy") or {}).get("identical_integers"),
                        "max_logit_error": (m.get("accuracy") or {}).get("error_max_logit_vs_floating"),
                        "auc": (auc.get("ciphertext") or {}).get("roc_auc"), "micro": m.get("microbenchmark_in_process"), "env": m.get("environment", {})}
    if "api" in found:
        m = found["api"][1]
        s["api"] = {"file": found["api"][0], "n": (m.get("sample") or {}).get("n"),
                    "exact": (m.get("accuracy") or {}).get("identical_integers"),
                    "client_ms": m.get("client_ms"), "components": m.get("hospital_components_ms"),
                    "patients_per_minute": m.get("patients_per_minute")}
    if man.get("redactions"):
        warnings.append(f"{man['redactions']} values were redacted from logs (public IPs or secrets)")
    return errors, warnings, s


def _fmt(d, k):
    v = (d or {}).get(k)
    return "—" if v is None else v


def write_summary(run_dir, man, errors, warnings, s):
    verdict = "VALID" if not errors else "NOT VALID"
    lines = [f"# Evidence run {man.get('run_id')}", "",
             f"**{verdict}** · status `{man.get('status')}` · arch `{man.get('arch')}` · commit `{str(man.get('commit'))[:7]}` · "
             f"operator {man.get('operator')} · {man.get('started_utc')} → {man.get('ended_utc')}", "",
             f"Model `{str(s.get('model_sha256'))[:12]}` · code `{str(s.get('code_sha256'))[:12]}`", "",
             "| Step | Exit | Seconds | Log |", "|---|---:|---:|---|"]
    for st in man.get("steps", []):
        lines.append(f"| {st['name']} | {st['exit_code']} | {st['seconds']} | [{st['log']}]({st['log']}) |")
    if s.get("smoke"):
        lines += ["", "Smoke: " + " · ".join(f"{k} {v:.1%}" for k, v in s["smoke"].items())]
    p, a = s.get("process"), s.get("api")
    if p:
        micro = p.get("micro") or {}
        enc = next((v for k, v in micro.items() if "encrypt" in k), {})
        lines += ["", f"Process: {p['exact']}/{p['n']} exact · encrypted ROC-AUC {p['auc']} · max logit error {p['max_logit_error']} · "
                      f"encrypt p50 {_fmt(enc, 'p50_ms')} ms · `{p['file']}`"]
    if a:
        c = a.get("client_ms") or {}
        lines += [f"API: {a['exact']}/{a['n']} exact · client p50 {_fmt(c, 'p50_ms')} ms · p95 {_fmt(c, 'p95_ms')} ms · "
                  f"{a.get('patients_per_minute')} patients/min · `{a['file']}`"]
    if errors:
        lines += ["", "## Errors", *[f"- {e}" for e in errors]]
    if warnings:
        lines += ["", "## Warnings", *[f"- {w}" for w in warnings]]
    with open(os.path.join(run_dir, "SUMMARY.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return "\n".join(lines)


def _run_dirs(paths):
    if paths:
        return [os.path.abspath(p) for p in paths]
    base = os.path.join(ROOT, RUNS)
    return sorted(os.path.join(base, d) for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))) if os.path.isdir(base) else []


def cmd_check(args):
    dirs, bad, out = _run_dirs(args.runs), 0, []
    if not dirs:
        print("no recorded evidence runs"); return 0
    for d in dirs:
        man = json.load(open(os.path.join(d, "manifest.json"))) if os.path.exists(os.path.join(d, "manifest.json")) else {}
        errors, warnings, s = check(d, require_s390x=not args.allow_non_s390x)
        text = write_summary(d, man, errors, warnings, s) if man else f"# {d}\n\nmissing manifest"
        out.append(text)
        print(text, "\n")
        bad += bool(errors)
    if args.github_summary and os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write("\n\n".join(out) + "\n")
    return 1 if bad else 0


def cmd_index(_):
    rows = ["# Recorded evidence runs", "", "Generated by `make evidence-index`. VALID requires s390x and every final check.", "",
            "| Run | Verdict | Commit | Smoke C | Process exact | API p50 / p95 (ms) |", "|---|---|---|---:|---:|---:|"]
    for d in _run_dirs(None):
        if not os.path.exists(os.path.join(d, "manifest.json")):
            continue
        errors, _, s = check(d)
        c = (s.get("api") or {}).get("client_ms") or {}
        p = s.get("process") or {}
        rows.append(f"| [{os.path.basename(d)}]({os.path.basename(d)}/SUMMARY.md) | {'VALID' if not errors else 'not valid'} | "
                    f"`{str(s.get('commit'))[:7]}` | {(s.get('smoke') or {}).get('Synthetic C', '—')} | "
                    f"{_fmt(p, 'exact')}/{_fmt(p, 'n')} | {_fmt(c, 'p50_ms')} / {_fmt(c, 'p95_ms')} |")
    os.makedirs(os.path.join(ROOT, RUNS), exist_ok=True)
    with open(os.path.join(ROOT, RUNS, "INDEX.md"), "w") as f:
        f.write("\n".join(rows) + "\n")
    print("\n".join(rows))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="record a run on this host")
    r.add_argument("--no-push", action="store_true", help="keep the run local (no branch, commit or push)")
    r.add_argument("--down", action="store_true", help="stop the demo containers at the end")
    r.add_argument("--steps", nargs="*", choices=[s[0] for s in STEPS], help="subset of steps (marks the run partial)")
    c = sub.add_parser("check", help="validate recorded runs")
    c.add_argument("runs", nargs="*")
    c.add_argument("--allow-non-s390x", action="store_true", help="for local rehearsals only")
    c.add_argument("--github-summary", action="store_true")
    sub.add_parser("index", help="rebuild INDEX.md")
    a = ap.parse_args(argv)
    return {"run": run, "check": cmd_check, "index": cmd_index}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
