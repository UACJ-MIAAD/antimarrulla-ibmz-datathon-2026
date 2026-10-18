"""Recorded evidence runs: execute the release checks, keep every log and publish them through Git.

  run    On the target host (LinuxONE VM): run the Docker checks and FINAL measurements, save logs,
         system identity and a manifest under submission/evidence/runs/<run_id>/, then commit them to
         a new branch evidence/<run_id> and push it. Failed runs are committed too, so the logs arrive.
  check  Validate recorded runs: complete steps, log hashes, measurement content and provenance,
         code hash at the recorded commit, smoke results and absence of secrets. Writes SUMMARY.md.
  index  Rebuild submission/evidence/runs/INDEX.md from all recorded runs.

Standard library only; run from the repository root with PYTHONPATH=src (the Makefile sets it).
"""
import argparse, datetime, getpass, hashlib, io, ipaddress, json, math, os, platform, re, subprocess, sys, tarfile, tempfile, time, urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from screening import package, provenance, benchmark_profiles  # noqa: E402

RUNS = os.path.join("submission", "evidence", "runs")
METRICS = os.path.join("submission", "evidence", "metrics")
MODEL = os.path.join("artifacts", "model", "logistic_model_v1.json")
SCHEMA = "evidence-run-v1"

def steps_for(plan):
    return [
        ("verify", "make verify-docker"),
        ("image_inspect", "make image-inspect"),
        ("demo", "make demo-docker"),
        ("measure_process", f'make measure-docker FINAL=1 MEASURE_ARGS="--patients {plan["process_n"]} --https {plan["https_n"]}"'),
        ("measure_api", f'make measure-api-docker FINAL=1 API_ARGS="--n {plan["api_n"]}"'),
    ]


STEPS = steps_for(benchmark_profiles.profile())
SYSTEM = [
    ("uname", "uname -a && uname -m"),
    ("os_release", "cat /etc/os-release"),
    ("lscpu", "lscpu"),
    ("sysinfo", "grep -v -i -E '^(Sequence Code|Plant)' /proc/sysinfo"),  # IBM Z machine type/LPAR; serial omitted
    ("memory", "free -h || vm_stat"),
    ("docker", "docker version && docker compose version"),
    ("openssl", "openssl version -a"),
    ("git", "git log -1 --format='%H %an %cI %s'; git status --short --branch"),
]
SECRET = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----|\b(?:ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{20,}|\b(?:AKIA|ASIA)[0-9A-Z]{16}\b|\bxox[abp]-[A-Za-z0-9-]{10,}")
PEM = re.compile(r"-----BEGIN ([A-Z0-9 ]*PRIVATE KEY)-----.*?(?:-----END \1-----|\Z)", re.S)
CREDENTIAL = re.compile(r"(?im)(?:authorization[\"\x27]?\s*[:=]\s*[\"\x27]?(?:bearer|basic)\s+[^\s\"']+|(?:[a-z_]*(?:token|password|secret|api_key|access_key)[a-z_]*)[\"\x27]?\s*[:=]\s*[\"']?[^\s,;\"']{8,}|https?://[^/\s:@]+:[^/\s@]+@)")
IPV4 = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
IPV6 = re.compile(r"(?<![\w:])(?:[0-9a-fA-F]{0,4}:){2,}[0-9a-fA-F:.]*(?:%[\w.-]+)?")
SMOKE = re.compile(r"^(Synthetic [ABC])[^:]*: p=([0-9.]+) · exact z", re.M)


def redact(text):
    "Remove complete private keys, common credentials and public IPv4/IPv6 addresses."
    text, count = PEM.subn("[REDACTED-PRIVATE-KEY]", text)
    for pattern in (SECRET, CREDENTIAL):
        text, n = pattern.subn("[REDACTED-SECRET]", text)
        count += n

    def ip(match):
        nonlocal count
        try:
            addr = ipaddress.ip_address(match.group(0).split("%")[0])
        except ValueError:
            return match.group(0)
        # Keep local routes and version numbers such as 3.0.13; hide other addresses.
        local = ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8", "169.254.0.0/16", "0.0.0.0/8", "::1/128", "fc00::/7", "fe80::/10")
        if any(addr in ipaddress.ip_network(net) for net in local):
            return match.group(0)
        count += 1
        return "[public-ip]"

    for pattern in (IPV6, IPV4):
        text = pattern.sub(ip, text)
    return text, count


def safe_path(base, relative):
    "Only regular files inside the declared directory; reject symlink components."
    if not isinstance(relative, str) or not relative or os.path.isabs(relative) or ".." in relative.split("/"):
        raise ValueError("unsafe evidence path")
    current = os.path.abspath(base)
    for part in relative.split("/"):
        current = os.path.join(current, part)
        if os.path.islink(current):
            raise ValueError("symlink in evidence path")
    return current


def _utc():
    return datetime.datetime.now(datetime.timezone.utc)


def _sha(path):
    return provenance.sha256(path)


def _git(*a, check=False):
    r = subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(redact(f"git {' '.join(a)}: {r.stderr.strip()}")[0])
    return r.stdout.strip() if r.returncode == 0 else None


def _shell(cmd, log_path, echo=True):
    "Capture output, then redact the complete text before displaying or saving it."
    t0 = time.monotonic()
    p = subprocess.Popen(cmd, shell=True, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
    buf = io.StringIO()
    for line in p.stdout:
        buf.write(line)
    code = p.wait()
    text, n = redact(f"$ {cmd}\n{buf.getvalue()}\n[exit {code}]\n")
    if echo:
        sys.stdout.write(text); sys.stdout.flush()
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(text)
    return code, round(time.monotonic() - t0, 1), n


def _measurements():
    d = os.path.join(ROOT, METRICS)
    return {f for f in os.listdir(d) if f.startswith("measurement_")} if os.path.isdir(d) else set()


def run(args):
    if _git("diff", "--cached", "--name-only"):
        sys.exit("evidence run: the staging area must be empty; preserve your staged work first")
    if _git("status", "--porcelain", "--", "tools/evidence.py", ".github/workflows/evidence.yml"):
        sys.exit("evidence run: commit the runner and workflow changes first")
    if not args.no_push and _git("symbolic-ref", "--quiet", "--short", "HEAD") is None:
        sys.exit("evidence run: switch to a named release branch before publishing")
    g = provenance.git_state(ROOT)
    if g.get("relevant") != [] or not g.get("commit"):
        sys.exit("evidence run: commit or stash relevant changes first (src, tests, docker, Makefile, artifacts): "
                 + ", ".join(g.get("relevant") or ["unknown state"]))
    plan = benchmark_profiles.profile(getattr(args, "profile", benchmark_profiles.DEFAULT), getattr(args, "api_n", None))
    started = _utc()
    arch = platform.machine().lower()
    run_id = f"{arch}_n{plan['process_n']}_api{plan['api_n']}_{started:%Y%m%dT%H%M%SZ}"
    rel_dir = os.path.join(RUNS, run_id)
    out = os.path.join(ROOT, rel_dir)
    os.makedirs(os.path.join(out, "logs")); os.makedirs(os.path.join(out, "system"))
    print(f"== evidence run {run_id} at {g['commit'][:7]} → {rel_dir}")
    redactions, system, steps, before = 0, [], [], _measurements()
    for name, cmd in SYSTEM:
        p = os.path.join(out, "system", f"{name}.txt")
        code, _, n = _shell(cmd, p, echo=False); redactions += n
        system.append({"name": name, "file": f"system/{name}.txt", "sha256": _sha(p), "exit_code": code})
    status = "passed"
    selected = [s for s in steps_for(plan) if not args.steps or s[0] in args.steps]
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
        code, _, n = _shell(cmd, p, echo=False); redactions += n
        system.append({"name": name, "file": f"system/{name}.txt", "sha256": _sha(p), "exit_code": code})
    try:
        with urllib.request.urlopen(ui + "/api/state", timeout=10) as r:
            state = json.loads(r.read())
        p = os.path.join(out, "system", "api_state.json")
        with open(p, "w") as f:
            encoded, n = redact(json.dumps(state, indent=2)); redactions += n
            f.write(encoded)
        system.append({"name": "api_state", "file": "system/api_state.json", "sha256": _sha(p)})
    except (OSError, ValueError) as e:
        print(redact(f"note: {ui}/api/state not reachable ({e})")[0])
    new = sorted(_measurements() - before)
    manifest = {
        "schema": SCHEMA, "run_id": run_id, "status": status, "profile": plan,
        "started_utc": f"{started:%Y-%m-%dT%H:%M:%SZ}", "ended_utc": f"{_utc():%Y-%m-%dT%H:%M:%SZ}",
        "operator": _git("config", "user.name") or getpass.getuser(), "commit": g["commit"],
        "arch": arch, "system": platform.system(), "ui_url": ui, "redactions": redactions,
        "steps": steps, "system_files": system,
        "measurements": [{"path": f"{METRICS}/{f}", "sha256": _sha(os.path.join(ROOT, METRICS, f))} for f in new],
    }
    # Measurement JSON/Markdown are included in the branch too: sanitize before hashing.
    for item in manifest["measurements"]:
        path = os.path.join(ROOT, item["path"])
        raw = open(path, encoding="utf-8").read()
        cleaned, n = redact(raw); redactions += n
        with open(path, "w", encoding="utf-8") as f:
            f.write(cleaned)
        item["sha256"] = _sha(path)
    manifest["redactions"] = redactions
    with open(os.path.join(out, "manifest.json"), "w") as f:
        f.write(redact(json.dumps(manifest, indent=2))[0] + "\n")
    errors, warnings, summary = check(out, require_s390x=(arch == "s390x"))
    write_summary(out, manifest, errors, warnings, summary)
    print(f"\n== {status.upper()} · check: {len(errors)} errors, {len(warnings)} warnings · {rel_dir}/SUMMARY.md")
    for e in errors:
        print("  error:", e)
    if args.down:
        _shell("make demo-down", os.devnull, echo=False)
    delivered = True
    if not args.no_push:
        delivered = publish(run_id, rel_dir, [m["path"] for m in manifest["measurements"]], status, len(errors))
    return 0 if status == "passed" and not errors and delivered else 1


def publish(run_id, rel_dir, measurement_paths, status, n_errors):
    "Commit the run on evidence/<run_id> and push it; fall back to a Git bundle."
    branch = f"evidence/{run_id}"
    back = _git("rev-parse", "--abbrev-ref", "HEAD")
    if _git("diff", "--cached", "--name-only"):
        print("!! publication refused: staging area is no longer empty")
        return False
    # Never let an unrecognized file/symlink enter the publication commit.
    paths = [os.path.join(rel_dir, os.path.relpath(os.path.join(base, n), os.path.join(ROOT, rel_dir)))
             for base, _, names in os.walk(os.path.join(ROOT, rel_dir)) for n in names] + measurement_paths
    try:
        for path in paths:
            file = safe_path(ROOT, path)
            raw = open(file, encoding="utf-8").read()
            if redact(raw)[1]:
                raise ValueError(f"unredacted sensitive content in {path}")
        _git("switch", "-c", branch, check=True)
        _git("add", "--", *paths, check=True)
        _git("commit", "-q", "-m", f"evidence: {run_id} {status} ({n_errors} check errors)", check=True)
        result = subprocess.run(["git", "-C", ROOT, "push", "-u", "origin", branch], capture_output=True, text=True)
        print(redact(result.stdout + result.stderr)[0])
        pushed = result.returncode == 0
        if pushed:
            print(f"== pushed {branch}; CI validates it. Open a PR or tell the captain the branch name.")
            return True
        bundle = os.path.join(ROOT, "dist", f"{run_id}.bundle")
        os.makedirs(os.path.dirname(bundle), exist_ok=True)
        _git("bundle", "create", bundle, branch, check=True)
        print(f"!! push failed. Verified bundle saved: {bundle}")
        return False  # Delivery remains incomplete even when a backup exists.
    except (RuntimeError, ValueError, OSError) as e:
        print("!! could not publish the run:", e)
        return False
    finally:
        if back and back != "HEAD":
            _git("switch", back)


def _valid(m, mode, model_sha, require_s390x):
    # Reuse release identity/exactness checks for diagnostic counts, without promoting
    # a diagnostic measurement into release evidence. Its original count is checked below.
    m = json.loads(json.dumps(m))
    n = (m.get("sample") or {}).get("n")
    if type(n) is not int or n <= 0 or (m.get("accuracy") or {}).get("identical_integers") != n or (m.get("accuracy") or {}).get("of") != n:
        return False
    if mode == "api" and (m.get("client_ms") or {}).get("n") != n:
        return False
    if not require_s390x:
        m["environment_label"] = "s390x"
        m.setdefault("environment", {})["is_linuxone_s390x"] = True
    normalized = 2000 if mode == "process" else 200
    m["sample"]["n"] = normalized
    m["accuracy"].update(identical_integers=normalized, of=normalized)
    if mode == "api": m["client_ms"]["n"] = normalized
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
    "Fail closed on malformed/untrusted evidence without crashing the entire batch."
    try:
        return _check(run_dir, require_s390x, root)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError) as e:
        return [f"malformed evidence: {type(e).__name__}: {e}"], [], {}


def _check(run_dir, require_s390x=True, root=ROOT):
    "Return (errors, warnings, summary) for one recorded run."
    errors, warnings, s = [], [], {}
    mpath = os.path.join(run_dir, "manifest.json")
    try:
        man = json.load(open(mpath, encoding="utf-8"))
    except (OSError, ValueError):
        return [f"{mpath}: missing or invalid manifest"], [], s
    started = datetime.datetime.fromisoformat(man["started_utc"].replace("Z", "+00:00"))
    ended = datetime.datetime.fromisoformat(man["ended_utc"].replace("Z", "+00:00"))
    if started.tzinfo is None or ended.tzinfo is None or ended < started:
        errors.append("run timestamps must be ordered and timezone-aware")
    if not re.fullmatch(r"[0-9a-f]{40}", str(man.get("commit", ""))):
        errors.append("manifest must identify a full Git commit")
    if man.get("schema") != SCHEMA:
        errors.append(f"manifest schema is {man.get('schema')!r}, expected {SCHEMA}")
    s.update({k: man.get(k) for k in ("run_id", "status", "arch", "commit", "operator", "started_utc", "ended_utc")})
    if man.get("status") != "passed":
        errors.append(f"run status is {man.get('status')!r}")
    if require_s390x and man.get("arch") != "s390x":
        errors.append(f"architecture is {man.get('arch')!r}, not s390x")
    declared = man.get("profile") or benchmark_profiles.profile()
    plan = benchmark_profiles.profile(declared["name"], declared["api_n"])
    if declared != plan:
        errors.append("profile declaration is inconsistent")
    s["profile"] = plan
    expected_steps = steps_for(plan)
    done = {st.get("name"): st for st in man.get("steps", [])}
    if [st.get("name") for st in man.get("steps", [])] != [name for name, _ in expected_steps]:
        errors.append("steps must occur exactly once in the required order")
    for name, command in expected_steps:
        st = done.get(name)
        if not st:
            errors.append(f"step {name} was not run")
        elif st.get("exit_code") != 0:
            errors.append(f"step {name} exited {st.get('exit_code')} (see {st.get('log')})")
        elif st.get("command") != command:
            errors.append(f"step {name} does not use the required command")
    for item in man.get("steps", []) + man.get("system_files", []):
        f = safe_path(run_dir, item.get("log") or item.get("file") or "")
        if not os.path.isfile(f):
            errors.append(f"missing file {os.path.relpath(f, run_dir)}")
        elif _sha(f) != item.get("sha256"):
            errors.append(f"{os.path.relpath(f, run_dir)} was modified after the run (hash mismatch)")
    for base, _, names in os.walk(run_dir):
        for n in names:
            try:
                f = safe_path(run_dir, os.path.relpath(os.path.join(base, n), run_dir))
                text = open(f, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if redact(text)[1]:
                errors.append(f"possible secret or public address in {os.path.relpath(os.path.join(base, n), run_dir)}")
    model_path = os.path.join(root, MODEL)
    model_sha = _sha(model_path) if os.path.exists(model_path) else None
    found = {}
    for item in man.get("measurements", []):
        relative = item.get("path", "")
        if not relative.startswith(METRICS + "/measurement_"):
            errors.append("measurement path must be inside the metrics directory"); continue
        p = safe_path(root, relative)
        if not os.path.isfile(p):
            errors.append(f"measurement {item.get('path')} is missing"); continue
        if _sha(p) != item.get("sha256"):
            errors.append(f"measurement {item.get('path')} hash mismatch"); continue
        if redact(open(p, encoding="utf-8").read())[1]:
            errors.append(f"possible secret or public address in {relative}")
        if p.endswith(".json"):
            m = json.load(open(p, encoding="utf-8"))
            if m.get("mode") in found:
                errors.append(f"duplicate {m.get('mode')} measurement")
            found[m.get("mode")] = (item["path"], m)
    codes = set()
    for mode in ("process", "api"):
        if mode not in found:
            errors.append(f"no {mode} measurement recorded by this run"); continue
        path, m = found[mode]
        if not _valid(m, mode, model_sha, require_s390x):
            errors.append(f"{path} fails the final measurement rules (s390x, clean commit, model {str(model_sha)[:12]}, all integers exact)")
        measured = datetime.datetime.fromisoformat(m["date_utc"].replace("Z", "+00:00"))
        if measured.tzinfo is None or not started <= measured <= ended:
            errors.append(f"{mode} measurement timestamp is outside this run")
        expected_n = plan["process_n" if mode == "process" else "api_n"]
        if (m.get("sample") or {}).get("n") != expected_n:
            errors.append(f"{mode} requires exactly {expected_n} patients")
        env = m.get("environment") or {}
        if env.get("machine") != man.get("arch") or (require_s390x and env.get("system") != "Linux"):
            errors.append(f"{mode} environment differs from manifest/required Linux architecture")
        if mode == "process":
            acc = m.get("accuracy") or {}
            error, bound = acc.get("error_max_logit_vs_floating"), acc.get("applicable_max_bound")
            from screening.contract import MAX_LOGIT_BOUND
            if not all(isinstance(v, (float, int)) and math.isfinite(v) for v in (error, bound)) or not 0 <= error <= bound <= MAX_LOGIT_BOUND + 1e-14:
                errors.append("process quantization error/bound is invalid")
            aucs = [(m.get("metrics_same_sample", {}).get(k) or {}).get("roc_auc") for k in ("floating", "fixed_point", "ciphertext")]
            if not all(isinstance(v, (int, float)) and math.isfinite(v) and 0 <= v <= 1 for v in aucs) or len(set(aucs)) != 1:
                errors.append("floating/fixed-point/encrypted ROC-AUC must agree on the same sample")
        else:
            timing = m.get("client_ms") or {}
            p50, p95 = timing.get("p50_ms"), timing.get("p95_ms")
            if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in (p50, p95)) or not 0 < p50 <= p95:
                errors.append("API timings are invalid")
            hr = m.get("hospital_remote") or {}
            if hr.get("code_sha256") != (m.get("provenance") or {}).get("code_sha256") or hr.get("machine") != man.get("arch"):
                errors.append("remote hospital code/architecture differs from measured client")
        prov = m.get("provenance") or {}
        codes.add(prov.get("code_sha256"))
        if prov.get("commit") != man.get("commit"):
            errors.append(f"{path} commit {str(prov.get('commit'))[:7]} differs from the run commit {str(man.get('commit'))[:7]}")
    if len(codes) > 1:
        errors.append("process and api measurements report different code hashes")
    if codes and man.get("commit"):
        at = _code_hash_at(man["commit"])
        if at is None:
            errors.append(f"commit {man['commit'][:7]} is not available here; code hash not recomputed (fetch it)")
        elif at not in codes:
            errors.append(f"measured code hash differs from src/screening at {man['commit'][:7]}")
        else:
            s["code_sha256"] = at
    recorded_model = subprocess.run(["git", "-C", ROOT, "show", f"{man.get('commit')}:{MODEL}"], capture_output=True)
    if recorded_model.returncode or hashlib.sha256(recorded_model.stdout).hexdigest() != model_sha:
        errors.append("model differs from the recorded commit or commit model is unavailable")
    systems = {item["name"]: item for item in man.get("system_files", [])}
    required = ["uname", "docker", "openssl", "compose_ps", "compose_logs", "api_state"]
    if require_s390x:
        required += ["lscpu", "sysinfo", "os_release"]
    for name in required:
        item = systems.get(name)
        if not item:
            errors.append(f"missing system evidence: {name}")
        elif name != "api_state" and item.get("exit_code") != 0:
            errors.append(f"system evidence command failed: {name}")
    if "uname" in systems:
        uname = open(safe_path(run_dir, systems["uname"]["file"])).read()
        if man.get("arch") not in uname:
            errors.append("uname does not corroborate manifest architecture")
    if "api_state" in systems:
        state = json.load(open(safe_path(run_dir, systems["api_state"]["file"])))
        health = state.get("service") or {}
        if (state.get("machine") != man.get("arch") or state.get("model_sha256") != model_sha
            or state.get("code_sha256") not in codes or health.get("state") != "ok"
            or health.get("key_private") is not False or health.get("model_sha256") != model_sha
            or health.get("code_sha256") not in codes):
            errors.append("API state does not corroborate host, code, model and service key isolation")
    logs = {st.get("name"): safe_path(run_dir, st.get("log", "")) for st in man.get("steps", [])}

    def read(name):
        try:
            return open(logs[name], encoding="utf-8").read()
        except (KeyError, OSError):
            return ""
    for name, command in expected_steps:
        log = read(name)
        if not log.startswith(f"$ {command}\n") or not log.rstrip().endswith("[exit 0]"):
            errors.append(f"{name} log command/exit does not corroborate manifest")
    if done.get("image_inspect") and "app image OK:" not in read("image_inspect"):
        errors.append("image inspection log lacks its success marker")
    if done.get("verify") and "verification OK" not in read("verify"):
        errors.append("verify log lacks 'verification OK'")
    demo = read("demo")
    s["smoke"] = {k: float(v) for k, v in SMOKE.findall(demo)}
    if done.get("demo") and ("smoke OK" not in demo or len(s["smoke"]) != 3):
        errors.append("demo log lacks the three exact synthetic results and 'smoke OK'")
    from screening import contract, synthetic
    model = json.load(open(model_path))
    expected = {}
    for profile, patient in synthetic.PROFILES.items():
        z = contract.logit_integer(model["weights_integers"], model["intercept_integer"], [patient[k] for k in model["variables"]])
        expected[profile.split(" ·")[0]] = round(contract.sigmoid(z / model["weight_scale"]), 3)
    if s["smoke"] != expected:
        errors.append("synthetic A/B/C probabilities differ from the recorded model")
    if f"model {str(model_sha)[:12]}" not in demo or f"architecture {man.get('arch')}" not in demo:
        errors.append("smoke host/model identity differs from manifest")
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
    plan = s.get("profile") or benchmark_profiles.profile()
    verdict = "NOT VALID" if errors else ("VALID" if man.get("arch") == "s390x" else "VALID REHEARSAL (not s390x; not LinuxONE evidence)")
    if not errors and not plan["release_eligible"]:
        verdict += " DIAGNOSTIC ONLY (insufficient release sample)"
    lines = [f"# Evidence run {man.get('run_id')}", "",
             f"**{verdict}** · status `{man.get('status')}` · arch `{man.get('arch')}` · commit `{str(man.get('commit'))[:7]}` · "
             f"operator {man.get('operator')} · {man.get('started_utc')} → {man.get('ended_utc')}", "",
             f"Model `{str(s.get('model_sha256'))[:12]}` · code `{str(s.get('code_sha256'))[:12]}`", "",
             "| Step | Exit | Seconds | Log |", "|---|---:|---:|---|"]
    for st in man.get("steps", []):
        lines.append(f"| {st['name']} | {st['exit_code']} | {st['seconds']} | [{st['log']}]({st['log']}) |")
    lines += ["", f"Declared profile: process {plan['process_n']} labeled CDC records; API {plan['api_n']} synthetic requests; release-sized sample: {plan['release_eligible']}. Counts and scopes are separate."]
    if s.get("smoke"):
        lines += ["", "Smoke: " + " · ".join(f"{k} {v:.1%}" for k, v in s["smoke"].items())]
    p, a = s.get("process"), s.get("api")
    if p:
        micro = p.get("micro") or {}
        enc = next((v for k, v in micro.items() if "encrypt" in k), {})
        lines += ["", f"Process: {p['exact']}/{p['n']} exact · encrypted ROC-AUC {p['auc']} · max logit error {p['max_logit_error'] if p['max_logit_error'] is None else format(p['max_logit_error'], '.3g')} · "
                      f"encrypt p50 {_fmt(enc, 'p50_ms')} ms · `{p['file']}`"]
    if a:
        c = a.get("client_ms") or {}
        lines += [f"API: {a['exact']}/{a['n']} exact · client p50 {_fmt(c, 'p50_ms')} ms · p95 {_fmt(c, 'p95_ms')} ms · "
                  f"{a.get('patients_per_minute')} patients/min · `{a['file']}`"]
    if errors:
        lines += ["", "## Errors", *[f"- {e}" for e in errors]]
    if warnings:
        lines += ["", "## Warnings", *[f"- {w}" for w in warnings]]
    lines += ["", "Hashes check internal consistency; they are not signed execution attestation. Provider identity and independent teammate review remain separate release gates."]
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
        print("no recorded evidence runs"); return 1 if args.require_runs else 0
    for d in dirs:
        man = package._json(os.path.join(d, "manifest.json")) or {}
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
    rows = ["# Recorded evidence runs", "", "Generated by `make evidence-index`. VALID requires s390x and every configured check; small profiles are diagnostic only.", "",
            "| Run | Verdict | Commit | Smoke C | Process exact | API p50 / p95 (ms) |", "|---|---|---|---:|---:|---:|"]
    for d in _run_dirs(None):
        if not os.path.exists(os.path.join(d, "manifest.json")):
            continue
        errors, _, s = check(d)
        c = (s.get("api") or {}).get("client_ms") or {}
        p = s.get("process") or {}
        rows.append(f"| [{os.path.basename(d)}]({os.path.basename(d)}/SUMMARY.md) | {('VALID' if s.get('profile', {}).get('release_eligible') else 'diagnostic only') if not errors else 'not valid'} | "
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
    r.add_argument("--profile", choices=list(map(str, benchmark_profiles.SIZES)), default=benchmark_profiles.DEFAULT)
    r.add_argument("--api-n", type=int, choices=benchmark_profiles.SIZES, help="override synthetic API sample (default: up to 200)")
    r.add_argument("--no-push", action="store_true", help="keep the run local (no branch, commit or push)")
    r.add_argument("--down", action="store_true", help="stop the demo containers at the end")
    r.add_argument("--steps", nargs="*", choices=[s[0] for s in STEPS], help="subset of steps (marks the run partial)")
    c = sub.add_parser("check", help="validate recorded runs")
    c.add_argument("runs", nargs="*")
    c.add_argument("--allow-non-s390x", action="store_true", help="for local rehearsals only")
    c.add_argument("--github-summary", action="store_true")
    c.add_argument("--require-runs", action="store_true", help="fail if there is no evidence run")
    sub.add_parser("index", help="rebuild INDEX.md")
    a = ap.parse_args(argv)
    return {"run": run, "check": cmd_check, "index": cmd_index}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
