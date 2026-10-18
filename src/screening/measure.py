"""Measurements with verifiable execution provenance.
Process mode compares floating point, fixed point and Paillier on one stratified CDC test sample;
measure encryption/evaluation/aecryption separately. A same-process HTTPS microbenchmark includes
mutual TLS, hospital logic and the vault; it is not a two-container deployment.
API mode calls the deployed hospital API and verifies model hash and exact expected integers
using deterministic synthetic inputs. Record code/model/split/image identity and environment.
--final requires a clean identifiable commit and, for API mode, matching remote code.
Run: python -m screening.measure [--budget-s 600] [--max 2000] [--https 100] [--final]
     python -m screening.measure --mode api --url http://127.0.0.1:8080 [--n 200] [--final]
"""
import argparse, datetime, json, math, os, platform, random, shutil, statistics, subprocess, tempfile, threading, time
import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score
from . import contract, data, schema, hospital, provenance, protocol, secrets_setup, service, synthetic
from .paths import MEASUREMENTS, MODEL_JSON, SPLITS, ROOT

SAMPLE_SEED = 2026


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, max(0, math.ceil(q / 100 * len(xs)) - 1))]


def summary(xs):
    return {"n": len(xs), "p50_ms": round(pct(xs, 50), 3), "p95_ms": round(pct(xs, 95), 3), "mean_ms": round(statistics.mean(xs), 3)}


def benchmark_plaintext(model, xs, repetitions=10):
    """Time sequential per-patient logits on the encrypted experiment's exact sample.
Exclude network, sigmoid and I/O. Use microseconds so plaintext timings do not round to zero.
Do not compare a vectorized batch with individual requests or label this as clinical latency.
"""
    if not xs or repetitions < 1:
        raise ValueError("a nonempty sample and at least one repetition are required")
    w, b = model["weights_floating"], model["intercept_floating"]
    W, B = model["weights_integers"], model["intercept_integer"]
    functions = {"floating": lambda x: sum(a * v for a, v in zip(w, x)) + b,
                 "fixed_point": lambda x: contract.logit_integer(W, B, x)}
    out = {"n_patients": len(xs), "repetitions": repetitions, "concurrency": 1,
           "scope": "sequential per-patient logit only; excludes encryption, network, sigmoid, decryption and vault",
           "sample_sha256": __import__("hashlib").sha256(json.dumps(xs).encode()).hexdigest()}
    for name, fn in functions.items():
        for x in xs[:5]:
            fn(x)
        timings = []
        for _ in range(repetitions):
            for x in xs:
                t0 = time.perf_counter_ns()
                fn(x)
                timings.append((time.perf_counter_ns() - t0) / 1000)
        out[name] = {"n_evaluations": len(timings), "p50_us": round(pct(timings, 50), 3),
                       "p95_us": round(pct(timings, 95), 3), "mean_us": round(statistics.mean(timings), 3)}
    return out


def cmd(*a):
    try:
        return subprocess.run(a, capture_output=True, text=True, timeout=20).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def environment():
    import cryptography, phe, sklearn
    from cryptography.hazmat.backends.openssl.backend import backend
    try:
        import gmpy2; g = gmpy2.version()
    except ImportError:
        g = None
    info = {
        "machine": platform.machine(), "system": platform.system(), "platform": platform.platform(),
        "processor": platform.processor(), "cpus": os.cpu_count(), "python": platform.python_version(),
        "container": os.path.exists("/.dockerenv"),
        "is_linuxone_s390x": platform.machine() == "s390x",
        "versions": {"phe": phe.__version__ if hasattr(phe, "__version__") else "1.5.0", "gmpy2": g, "cryptography": cryptography.__version__,
                      "numpy": np.__version__, "scikit_learn": sklearn.__version__},
        "openssl_cli": cmd("openssl", "version", "-a"), "openssl_of_cryptography": backend.openssl_version_text(),
        "uname": cmd("uname", "-a"),
    }
    if platform.system() == "Linux":
        info["lscpu"] = cmd("lscpu")
        info["cpacfinfo"] = cmd("cpacfinfo", "-a") if shutil.which("cpacfinfo") else "cpacfinfo is not installed"
        try:
            info["cpuinfo_features"] = [l for l in open("/proc/cpuinfo") if l.startswith(("features", "Features", "flags"))][:1]
        except OSError:
            pass
    elif platform.system() == "Darwin":
        info["cpu"] = cmd("sysctl", "-n", "machdep.cpu.brand_string")
        info["memory_bytes"] = cmd("sysctl", "-n", "hw.memsize")
    return info


def stratified_sample(ids_test, y_test, n):
    rnd = random.Random(SAMPLE_SEED)
    pos = [i for i, v in zip(ids_test, y_test) if v == 1]
    neg = [i for i, v in zip(ids_test, y_test) if v == 0]
    n_pos = round(n * len(pos) / len(ids_test))
    return sorted(rnd.sample(pos, n_pos) + rnd.sample(neg, n - n_pos))


def metrics(y, p, threshold):
    pred = p >= threshold
    tp = int(np.sum(pred & (y == 1))); fn = int(np.sum(~pred & (y == 1))); tn = int(np.sum(~pred & (y == 0))); fp = int(np.sum(pred & (y == 0)))
    return {"roc_auc": round(float(roc_auc_score(y, p)), 6), "average_precision": round(float(average_precision_score(y, p)), 6),
            "sensitivity": round(tp / (tp + fn), 4), "specificity": round(tn / (tn + fp), 4),
            "matrix_confusion": {"tn": tn, "fp": fp, "fn": fn, "tp": tp}}


def _save(out, mode, label, now, md):
    os.makedirs(MEASUREMENTS, exist_ok=True)
    base = os.path.join(MEASUREMENTS, f"measurement_{mode}_{label}_{now.strftime('%Y%m%dT%H%M%SZ')}")
    with open(base + ".json", "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with open(base + ".md", "w") as f:
        f.write(md)
    print(md)
    print("saved to", base + ".json")


def _header(out, env, prov):
    adv = ("> ⚠️ " + out["warning"]) if out["warning"] else "> Executed on s390x; verify LinuxONE Community Cloud identity using VM/provider evidence."
    dirty = "**relevant uncommitted changes**: " + ", ".join(prov["changes_relevant"]) if prov["clean"] is False else ("clean" if prov["clean"] else "state not declared")
    return f"""{adv}

- Commit `{prov['commit']}` ({prov['source_commit']}, {dirty}) · code `{prov['code_sha256'][:16]}` ({prov['code_files']} files) · model `{prov['model_sha256'][:16]}` · splits `{prov['splits_sha256'][:16]}`{' · image `' + prov['image'] + '`' if prov['image'] else ''}
- Architecture: {env['machine']} · {env['platform']} · {env['cpus']} CPU · container: {env['container']}
- Python {env['python']} · phe {env["versions"]['phe']} · gmpy2 {env["versions"]['gmpy2']} · cryptography {env["versions"]['cryptography']} ({env['openssl_of_cryptography']}) · OpenSSL CLI: {(env['openssl_cli'] or 'n/a').splitlines()[0]}
- Comando: `{out['command']}` · concurrencia 1
"""


def api_mode(a, model, prov, env, now, label):
    import hashlib, urllib.request
    local = provenance.sha256(MODEL_JSON)
    with urllib.request.urlopen(a.url + "/api/state", timeout=30) as r:
        state = json.loads(r.read())
    if state.get("model_sha256") != local:
        raise SystemExit(f"hospital at {a.url} runs a different model ({state.get('model_sha256')}) from the local model ({local})")
    if a.final and state.get("code_sha256") != prov["code_sha256"]:
        raise SystemExit("final mode: deployed hospital code differs from the client")
    W, B = model["weights_integers"], model["intercept_integer"]

    def request(patient):
        body = json.dumps({"patient": patient}).encode()
        req = urllib.request.Request(a.url + "/api/evaluate", data=body, headers={"Content-Type": "application/json"})
        t0 = time.perf_counter()
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = json.loads(r.read())
        return resp, (time.perf_counter() - t0) * 1e3

    patients = [synthetic.random_patient(SAMPLE_SEED + k) for k in range(a.n + 3)]
    for p in patients[:3]:
        request(p)  # Warmup
    client, comp, exact = [], {}, 0
    t_ini = time.perf_counter()
    for p in patients[3:]:
        resp, ms = request(p)
        client.append(ms)
        expected = contract.logit_integer(W, B, [p[nm] for nm in schema.FEATURE_NAMES])
        exact += int(int(resp["hospital"]["z_integer"]) == expected)
        for k, v in resp["timings_ms"].items():
            comp.setdefault(k, []).append(v)
    wall = time.perf_counter() - t_ini
    out = {
        "mode": "api", "date_utc": now.isoformat().replace("+00:00", "Z"), "environment_label": label,
        "warning": None if env["is_linuxone_s390x"] else "LOCAL measurement. This is not LinuxONE performance.",
        "command": f"python -m screening.measure --mode api --url {a.url} --n {a.n}" + (" --final" if a.final else ""),
        "flow": "HTTP client → deployed hospital API → mutual TLS 1.3 → risk service → decryption → interpretation → AES-256-GCM vault with fsync (no browser)",
        "hospital_remote": {"url": a.url, "machine": state.get("machine"), "system": state.get("system"), "model_sha256": state.get("model_sha256"),
                            "code_sha256": state.get("code_sha256"), "code_equal_to_client": state.get("code_sha256") == prov["code_sha256"], "key_bits": state.get("key_bits")},
        "sample": {"kind": "deterministic synthetic inputs (screening.synthetic.random_patient)", "initial_seed": SAMPLE_SEED, "n": a.n, "warmup": 3,
                    "sha256": hashlib.sha256(json.dumps(patients[3:]).encode()).hexdigest()},
        "accuracy": {"identical_integers": exact, "of": a.n},
        "client_ms": summary(client), "hospital_components_ms": {k: summary(v) for k, v in comp.items()},
        "patients_per_minute": round(a.n / wall * 60, 1), "concurrency": 1, "provenance": prov, "environment": env,
    }
    c = out["hospital_components_ms"]
    md = f"# Hospital API measurement · {label} · {out['date_utc']}\n\n" + _header(out, env, prov) + f"""- Flow: {out['flow']}
- Remote hospital: {a.url} · architecture {state.get('machine')} ({state.get('system')}) · model `{local[:16]}` verified
- Remote code matches client: {state.get('code_sha256') == prov['code_sha256']}

Sample: {a.n} deterministic synthetic inputs (seed {SAMPLE_SEED}) · integers matching reference: {exact} of {a.n}

| Component | p50 (ms) | p95 (ms) | mean (ms) |
|---|---:|---:|---:|
| Client: complete request | {out['client_ms']['p50_ms']} | {out['client_ms']['p95_ms']} | {out['client_ms']['mean_ms']} |
""" + "".join(f"| Hospital: {k} | {v['p50_ms']} | {v['p95_ms']} | {v['mean_ms']} |\n" for k, v in c.items()) + f"""
Sequential throughput: {out["patients_per_minute"]} patients/min (n / wall time).
"""
    _save(out, "api", label, now, md)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["process", "api"], default="process")
    ap.add_argument("--url", default=None, help="hospital API URL (API mode)")
    ap.add_argument("--n", type=int, default=200, help="API-mode requests")
    ap.add_argument("--budget-s", type=float, default=600, help="maximum seconds for in-process measurement")
    ap.add_argument("--max", type=int, default=2000)
    ap.add_argument("--https", type=int, default=100, help="round trips for the same-process HTTPS microbenchmark")
    ap.add_argument("--final", action="store_true", help="reject relevant uncommitted changes")
    a = ap.parse_args()
    if a.n < 2 or a.max < 8 or a.https < 1 or a.budget_s <= 0:
        ap.error("--n must be >=2 and --max >=8; --https and --budget-s must be positive")

    prov = provenance.capture()
    if a.final:
        provenance.require_clean(prov)
    env = environment()
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    label = ("s390x" if env["is_linuxone_s390x"] else f"local-{env['system'].lower()}-{env['machine']}") + ("-container" if env["container"] else "")
    model = json.load(open(MODEL_JSON))
    if a.mode == "api":
        if not a.url:
            raise SystemExit("--mode api requires --url")
        return api_mode(a, model, prov, env, now, label)

    part = json.load(open(SPLITS))
    ids, X, y = data.load_cdc()
    Xte, yte, idte = data.load_split(part, "test", ids, X, y)
    row = {int(i): k for k, i in enumerate(idte)}
    h = protocol.hospital(model)
    s = protocol.RiskService(protocol.QuantizedModel.from_json(model))
    W, B, wf, bf, threshold = model["weights_integers"], model["intercept_integer"], model["weights_floating"], model["intercept_floating"], model["threshold"]["probability"]

    def one(x):
        reg = dict(zip(schema.FEATURE_NAMES, x))
        t0 = time.perf_counter(); sol, xv = h.prepare(reg); t1 = time.perf_counter()
        body = json.dumps(sol); sol2 = json.loads(body)
        t2 = time.perf_counter(); resp = s.evaluate(sol2); t3 = time.perf_counter()
        response_body = json.dumps(resp)
        t4 = time.perf_counter(); z, _ = h.decrypt(json.loads(response_body)); t5 = time.perf_counter()
        return z, (t1 - t0) * 1e3, (t3 - t2) * 1e3, (t5 - t4) * 1e3, len(body.encode()), len(response_body.encode())

    for x in Xte[:5].tolist():
        one(x)
    t = time.perf_counter()
    for x in Xte[5:25].tolist():
        one(x)
    by_patient = (time.perf_counter() - t) / 20
    n = min(int(min(a.max, max(100, a.budget_s / by_patient))), len(idte))
    print(f"pilot: {by_patient * 1e3:.1f} ms per patient → sample size {n}")

    sample = stratified_sample(idte.tolist(), yte.tolist(), n)
    ciphertexts, ev, des, b_in, b_out, zs, xs, ys = [], [], [], [], [], [], [], []
    t_ini = time.perf_counter()
    for i in sample:
        x = Xte[row[i]].tolist()
        z, a1, a2, a3, bi, bo = one(x)
        ciphertexts.append(a1); ev.append(a2); des.append(a3); b_in.append(bi); b_out.append(bo); zs.append(z); xs.append(x); ys.append(int(yte[row[i]]))
    t_total = time.perf_counter() - t_ini
    ys = np.array(ys)
    z_ref = [contract.logit_integer(W, B, x) for x in xs]
    exact = sum(int(to_ == b_) for to_, b_ in zip(zs, z_ref))
    lf = np.array([sum(w * v for w, v in zip(wf, x)) + bf for x in xs])
    lq = np.array([int(z) / contract.S_W for z in z_ref]); lc = np.array([int(z) / contract.S_W for z in zs])
    sig = lambda v: 1 / (1 + np.exp(-v))
    err = np.abs(lc - lf); bounds = np.array([contract.logit_error_bound(x) for x in xs])
    plaintext = benchmark_plaintext(model, xs)

    tmp = tempfile.mkdtemp(prefix="screening-measure-")
    secrets_setup.generate(tmp); c = os.path.join(tmp, "certs")
    srv, _ = service.create_server("127.0.0.1", 0, model, f"{c}/service.pem", f"{c}/service.key", f"{c}/ca.pem")
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    cli = hospital.ServiceClient(f"https://localhost:{srv.server_address[1]}", f"{c}/ca.pem", f"{c}/hospital.pem", f"{c}/hospital.key")
    from . import vault
    bov = vault.Vault(os.path.join(tmp, "vault.jsonl"), vault.load_key(os.path.join(tmp, "vault.key")))
    clin = hospital.Clinic(model, cli, bov)
    rec, comp = [], {}
    t_https = time.perf_counter()
    for i in sample[: a.https]:
        t0 = time.perf_counter(); r = clin.evaluate(dict(zip(schema.FEATURE_NAMES, Xte[row[i]].tolist())), "measurement"); rec.append((time.perf_counter() - t0) * 1e3)
        for k, v in r["timings_ms"].items():
            comp.setdefault(k, []).append(v)
    wall_https = time.perf_counter() - t_https
    srv.shutdown(); shutil.rmtree(tmp, ignore_errors=True)

    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    aes = AESGCM(AESGCM.generate_key(bit_length=256)); block = os.urandom(1 << 20)
    t0 = time.perf_counter()
    for _ in range(50):
        aes.encrypt(os.urandom(12), block, None)
    mb_s = 50 / (time.perf_counter() - t0)

    out = {
        "mode": "process", "date_utc": now.isoformat().replace("+00:00", "Z"), "environment_label": label,
        "warning": None if env["is_linuxone_s390x"] else "LOCAL measurement. This is not LinuxONE performance.",
        "command": "python -m screening.measure " + " ".join(f"--{k.replace('_', '-')} {v}" for k, v in vars(a).items() if k not in ("mode", "url", "n", "final")) + (" --final" if a.final else ""),
        "model": model["model"], "key_paillier_bits": h.pub.n.bit_length(), "concurrency": 1, "warmup": 5,
        "pilot": {"patients": 20, "ms_by_patient": round(by_patient * 1e3, 2), "budget_s": a.budget_s},
        "sample": {"source": "CDC test split", "seed": SAMPLE_SEED, "n": n, "positives": int(ys.sum()),
                    "prevalence": round(float(ys.mean()), 4), "ids_sha256": __import__("hashlib").sha256(json.dumps(sample).encode()).hexdigest()},
        "accuracy": {"identical_integers": exact, "of": n, "error_max_logit_vs_floating": float(err.max()),
                      "applicable_max_bound": float(bounds.max()), "all_within_bound": bool(np.all(err <= bounds)),
                      "error_max_probability": float(np.abs(sig(lc) - sig(lf)).max())},
        "metrics_same_sample": {"floating": metrics(ys, sig(lf), threshold), "fixed_point": metrics(ys, sig(lq), threshold), "ciphertext": metrics(ys, sig(lc), threshold)},
        "benchmark_plaintext": plaintext,
        "microbenchmark_in_process": {"encrypt_hospital": summary(ciphertexts), "evaluate_service": summary(ev), "decrypt_hospital": summary(des),
                                      "patients_per_minute_sequential": round(n / t_total * 60, 1), "note": "without network or vault"},
        "microbenchmark_https_same_process": {"complete_request": summary(rec), "components": {k: summary(v) for k, v in comp.items()},
                                               "patients_per_minute_sequential": round(len(rec) / wall_https * 60, 1),
                                               "note": "hospital logic and HTTPS service in the SAME process, mutual TLS 1.3 with a new connection per request, vault and fsync; excludes two-container deployment and browser"},
        "sizes_bytes": {"request_p50": int(pct(b_in, 50)), "response_p50": int(pct(b_out, 50))},
        "aes256gcm_microbenchmark_mb_s": round(mb_s, 1), "provenance": prov, "environment": env,
    }
    tp = out["microbenchmark_in_process"]; mh = out["microbenchmark_https_same_process"]; mc = out["metrics_same_sample"]["ciphertext"]
    md = f"# In-process measurement · {label} · {out['date_utc']}\n\n" + _header(out, env, prov) + f"""
| Sample (stratified CDC test split, seed {SAMPLE_SEED}) | Value |
|---|---|
| Patients | {n} ({out['sample']['positives']} positives, prevalence {out['sample']['prevalence']}) |
| Decrypted integers matching the reference | {exact} of {n} |
| Maximum floating-point logit error | {out["accuracy"]['error_max_logit_vs_floating']:.3e} (bound {out["accuracy"]["applicable_max_bound"]:.3e}) |
| ROC-AUC floating / fixed point / encrypted | {out['metrics_same_sample']['floating']['roc_auc']} / {out['metrics_same_sample']["fixed_point"]['roc_auc']} / {mc['roc_auc']} |
| Sensitivity · specificity (encrypted, threshold {threshold:.4f}) | {mc['sensitivity']} · {mc['specificity']} |

| Microbenchmark | p50 (ms) | p95 (ms) | mean (ms) |
|---|---:|---:|---:|
| In process · encrypt {len(schema.FEATURE_NAMES)} features | {tp['encrypt_hospital']['p50_ms']} | {tp['encrypt_hospital']['p95_ms']} | {tp['encrypt_hospital']['mean_ms']} |
| In process · evaluate ciphertexts | {tp['evaluate_service']['p50_ms']} | {tp['evaluate_service']['p95_ms']} | {tp['evaluate_service']['mean_ms']} |
| In process · decrypt | {tp['decrypt_hospital']['p50_ms']} | {tp['decrypt_hospital']['p95_ms']} | {tp['decrypt_hospital']['mean_ms']} |
| Same-process HTTPS + vault ({len(rec)} requests) | {mh["complete_request"]['p50_ms']} | {mh["complete_request"]['p95_ms']} | {mh["complete_request"]['mean_ms']} |

Sequential throughput: {tp["patients_per_minute_sequential"]} patients/min without network; {mh["patients_per_minute_sequential"]} with same-process HTTPS (n / wall time). Request {out['sizes_bytes']['request_p50']} bytes · response {out['sizes_bytes']['response_p50']} bytes · AES-256-GCM library microbenchmark {out['aes256gcm_microbenchmark_mb_s']} MB/s.

Plaintext reference on the same {n} patients ({plaintext['repetitions']} repetitions, logit only):
floating p50 {plaintext['floating']['p50_us']} µs, p95 {plaintext['floating']['p95_us']} µs;
fixed point p50 {plaintext["fixed_point"]['p50_us']} µs, p95 {plaintext["fixed_point"]['p95_us']} µs.
Compare with evaluate_service for encrypted logit cost; HTTPS also includes encryption, network and vault.
"""
    _save(out, "process", label, now, md)


if __name__ == "__main__":
    main()
