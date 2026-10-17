"""Two-host encrypted-flow test with synthetic inputs by default and service evidence audit.
Host A runs screening.service with SERVICE_EVIDENCE set and no hospital private key.
Host B runs screening.two_hosts hospital with --service https://HOST_A:8443,
--certs HOSPITAL_BUNDLE and --output DIR. --data cdc explicitly selects labeled public CDC inputs.
The hospital encrypts, sends over mutual TLS 1.3, decrypts and checks the exact reference.
Save hospital_log.jsonl and hospital_summary.json outside the repository; never save input vectors.
Audit both evidence directories with screening.two_hosts audit --service DIR_A --hospital DIR_B.
Verify wire-byte hashes, protocol-only ciphertext fields, randomization, absence of plaintext,
service-process private-key checks, TLS/client identity, distinct host IDs, matching code/model
and exact results. Hostnames alone do not prove separation; provider identity needs external evidence.
Compute AUC only for labeled CDC samples containing both classes. Same-host runs remain REHEARSAL.
"""
import argparse, datetime, glob, hashlib, json, os, platform, re, shutil, sys, time
from . import contract, schema, hospital, provenance, protocol, service, synthetic
from .paths import MODEL_JSON, SPLITS, ROOT

REPORT_OUTPUT = os.path.join(ROOT, "submission", "evidencias", "two_hosts")
REQUEST_FIELDS = {"protocol", "schema", "model", "id", "key_public", "exponent", "ciphertexts"}
RESPONSE_FIELDS = {"protocol", "schema", "model", "id", "exponent", "result", "service_ms"}
PLAINTEXT_VECTOR = re.compile(r"\[\s*(?:-?\d{1,3}\s*,\s*){20}-?\d{1,3}\s*\]")
WARMUP = 3


def _sample(n, source):
    "Synthetic inputs by default; labeled CDC data require an explicit benchmark selection."
    from . import measure
    if n < 2:
        raise ValueError("at least two records are required")
    if source == "synthetic":
        rows = []
        for k in range(n + WARMUP):
            patient = synthetic.random_patient(measure.SAMPLE_SEED + k)
            rows.append((k, [patient[v] for v in schema.FEATURE_NAMES], None))
        return rows, WARMUP
    from . import data
    part = json.load(open(SPLITS))
    ids, X, y = data.load_cdc()
    Xte, yte, idte = data.load_split(part, "test", ids, X, y)
    row = {int(i): k for k, i in enumerate(idte)}
    sample = measure.stratified_sample(idte.tolist(), yte.tolist(), min(n, len(idte)))
    selected = set(sample)
    cal = [int(i) for i in idte if int(i) not in selected][:WARMUP]
    return [(i, Xte[row[i]].tolist(), int(yte[row[i]])) for i in cal + sample], len(cal)


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _sha_file(p):
    with open(p, "rb") as f:
        return _sha(f.read())


def _now():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)


def _jsonl(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


# ------------------------------------------------------------------ Host B: hospital

def run_hospital(a):
    import numpy as np
    from . import data, measure

    with open(MODEL_JSON, "rb") as f:
        raw_model = f.read()
    model = json.loads(raw_model)
    certs = os.path.abspath(a.certs)
    cli = hospital.ServiceClient(a.service, os.path.join(certs, "ca.pem"), os.path.join(certs, "hospital.pem"),
                                   os.path.join(certs, "hospital.key"), timeout=60)
    health = cli.health()
    print("service:", health)
    if health.get("model") != model["model"] or health.get("model_sha256") != _sha(raw_model):
        raise SystemExit(f"the service runs a different model ({health.get('model')}) from this hospital ({model['model']})")
    if health.get("code_sha256") != provenance.hash_code()[0]:
        raise SystemExit("service code differs: use the same commit at both endpoints")
    if not health.get("evidence") and not a.without_evidence:
        raise SystemExit("the service is not saving evidence: start it with SERVICE_EVIDENCE=DIR "
                         "(or use --without-evidence for measurement without an audit)")

    source = getattr(a, "data", "synthetic")
    sample, n_cal = _sample(a.n, source)
    n = len(sample) - n_cal

    h = protocol.hospital(model)
    W, B, wf, bf = model["weights_integers"], model["intercept_integer"], model["weights_floating"], model["intercept_floating"]
    threshold = model["threshold"]["probability"]
    os.makedirs(a.output, exist_ok=True)
    path_bit = os.path.join(a.output, "hospital_log.jsonl")
    if os.path.exists(path_bit):
        os.replace(path_bit, path_bit + "." + _now().strftime("%Y%m%dT%H%M%SZ") + ".previous")

    rows, values_in_plaintext = [], set()
    with open(path_bit, "w") as bit:
        for k, (record_id, x, y) in enumerate(sample):
            is_cal = k < n_cal
            t0 = time.perf_counter()
            sol, xv = h.prepare(dict(zip(schema.FEATURE_NAMES, x)))
            body = json.dumps(sol).encode()
            t1 = time.perf_counter()
            st, d = cli._request("POST", "/v2/evaluate", body)
            t2 = time.perf_counter()
            if st != 200:
                raise SystemExit(f"service returned HTTP {st}: {d[:200]!r}")
            z, _ = h.decrypt(json.loads(d))
            t3 = time.perf_counter()
            z_ref = contract.logit_integer(W, B, xv)
            logit_f = sum(w * v for w, v in zip(wf, xv)) + bf
            e = {"id": sol["id"], "record_id": record_id, "data": source, "warmup": is_cal, "y": y,
                 "sha256_request": _sha(body), "sha256_response": _sha(d), "bytes_in": len(body), "bytes_out": len(d),
                 "ms_encrypt": round((t1 - t0) * 1e3, 3), "ms_network_and_service": round((t2 - t1) * 1e3, 3),
                 "ms_decrypt": round((t3 - t2) * 1e3, 3), "ms_total": round((t3 - t0) * 1e3, 3),
                 "z_decrypted": str(z), "z_expected": str(z_ref), "identical": z == z_ref,
                 "probability_ciphertext": contract.sigmoid(contract.logit_from_integer(z)), "probability_floating": contract.sigmoid(logit_f)}
            bit.write(json.dumps(e) + "\n")
            if not is_cal:
                rows.append(e)
                values_in_plaintext.update((i, v) for i, v in enumerate(xv))
            if not is_cal and (len(rows) % 25 == 0 or len(rows) == n):
                print(f"  {len(rows)}/{n} · last {e['ms_total']:.0f} ms · exact integers {sum(f['identical'] for f in rows)}/{len(rows)}")

    ys = np.array([f["y"] for f in rows]) if source == "cdc" else None
    pc = np.array([f["probability_ciphertext"] for f in rows]); pf = np.array([f["probability_floating"] for f in rows])
    env = measure.environment()
    summary = {
        "date_utc": _now().isoformat().replace("+00:00", "Z"), "machine": platform.node(), "machine_id": service.machine_id(),
        "architecture": platform.machine(),
        "service_url": a.service, "service_health": health, "model": model["model"], "model_sha256": _sha(raw_model),
        "key_paillier_bits": h.pub.n.bit_length(), "concurrency": 1, "warmup": n_cal,
        "sample": {"source": "deterministic synthetic inputs" if source == "synthetic" else "publicly anonymized CDC test split",
                    "data": source, "seed": measure.SAMPLE_SEED, "n": n,
                    "positives": int(ys.sum()) if ys is not None else None,
                    "prevalence": round(float(ys.mean()), 4) if ys is not None else None,
                    "ids_sha256": _sha(json.dumps(sample).encode())},
        "accuracy": {"identical_integers": sum(f["identical"] for f in rows), "of": n,
                      "error_max_probability_vs_floating": float(np.abs(pc - pf).max())},
        "metrics_same_sample": ({"floating": measure.metrics(ys, pf, threshold), "ciphertext": measure.metrics(ys, pc, threshold)}
                                   if ys is not None and len(set(ys)) == 2 else None),
        "note_metrics": "No AUC/sensitivity for synthetic inputs without observed clinical labels.",
        "timings_ms": {k: measure.summary([f[k] for f in rows]) for k in ("ms_total", "ms_encrypt", "ms_network_and_service", "ms_decrypt")},
        "sizes_bytes": {"request_p50": int(measure.pct([f["bytes_in"] for f in rows], 50)), "response_p50": int(measure.pct([f["bytes_out"] for f in rows], 50))},
        "values_in_plaintext_different": len(values_in_plaintext), "values_in_plaintext_total": n * len(schema.FEATURE_NAMES),
        "log_sha256": _sha_file(path_bit), "provenance": provenance.capture(), "environment": env,
        "command": " ".join(["python -m screening.two_hosts"] + sys.argv[1:]),
    }
    with open(os.path.join(a.output, "hospital_summary.json"), "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    t = summary["timings_ms"]["ms_total"]
    print(f"\n{n} records ({source}) · exact integers {summary["accuracy"]["identical_integers"]}/{n} · "
          f"p50 {t['p50_ms']} ms · p95 {t['p95_ms']} ms")
    print(f"hospital log: {path_bit}\nnext: copy directory {os.path.abspath(a.output)} to the service host and run the audit")


# ------------------------------------------------------------------ Evidence audit

def audit(a):
    hosp = _jsonl(os.path.join(a.hospital, "hospital_log.jsonl"))
    result_h = json.load(open(os.path.join(a.hospital, "hospital_summary.json")))
    serv = _jsonl(os.path.join(a.service, "service_audit.jsonl"))
    ini_s = json.load(open(os.path.join(a.service, "service_startup.json")))
    dir_sol = os.path.join(a.service, "requests")
    by_sha = {e["sha256_request"]: e for e in serv}
    ours = [by_sha.get(h["sha256_request"]) for h in hosp]
    checks = []

    def check(key, title, ok, detail):
        checks.append({"key": key, "title": title, "ok": bool(ok), "detail": detail})

    measurements = [h for h in hosp if not h.get("warmup")]
    ex = result_h["accuracy"]
    check("integrity", "Intact hospital log and consistent counts",
          bool(measurements) and _sha_file(os.path.join(a.hospital, "hospital_log.jsonl")) == result_h.get("log_sha256")
          and len(measurements) == result_h["sample"]["n"] == ex["of"]
          and sum(int(h["z_decrypted"]) == int(h["z_expected"]) for h in measurements) == ex["identical_integers"],
          "Log SHA-256, sample counts and reference integers match the summary")
    sh = result_h.get("service_health") or {}
    code = result_h.get("provenance", {}).get("code_sha256")
    model = result_h.get("model_sha256")
    check("versions", "Matching code and model at hospital, service health and service evidence",
          bool(code and model) and code == ini_s.get("code_sha256") == sh.get("code_sha256")
          and model == ini_s.get("model_sha256") == sh.get("model_sha256"),
          "Model names do not substitute for hashes")

    # 1. Matching hashes and intact files at both ends
    missing = sum(1 for s in ours if s is None)
    resp_different = sum(1 for h, s in zip(hosp, ours) if s and (s["sha256_response"] != h["sha256_response"] or s["id"] != h["id"]))
    tampered = 0
    for s in filter(None, ours):
        base = os.path.join(dir_sol, s["id"])
        try:
            tampered += (_sha_file(base + ".request.json") != s["sha256_request"]) + (_sha_file(base + ".response.json") != s["sha256_response"])
        except OSError:
            tampered += 2
    check("bytes", "Service evidence matches exactly what the hospital sent and received", missing == 0 and resp_different == 0 and tampered == 0,
          f"{len(hosp)} hospital requests · missing from service log: {missing} · different response: {resp_different} · "
          f"tampered or missing evidence files: {tampered}")

    # 2. Wire structure contains ciphertexts only
    bad, bits_min, key_bits, keys, all_ciphertexts = [], None, set(), set(), []
    for s in filter(None, ours):
        try:
            sol = json.load(open(os.path.join(dir_sol, s["id"] + ".request.json")))
            resp = json.load(open(os.path.join(dir_sol, s["id"] + ".response.json")))
            n_ = int(sol["key_public"]["n"]); n2 = n_ * n_
            ok = (set(sol) == REQUEST_FIELDS and set(sol["key_public"]) == {"n"} and sol["exponent"] == 0
                  and len(sol["ciphertexts"]) == len(schema.FEATURE_NAMES) and set(resp) <= RESPONSE_FIELDS and resp["exponent"] == 0)
            vals = [int(c) for c in sol["ciphertexts"]] + [int(resp["result"])]
            ok = ok and all(0 < v < n2 for v in vals)
            all_ciphertexts.extend(vals[:-1]); keys.add(n_); key_bits.add(n_.bit_length())
            m = min(v.bit_length() for v in vals)
            bits_min = m if bits_min is None else min(bits_min, m)
            if not ok:
                bad.append(s["id"])
        except (OSError, ValueError, KeyError, TypeError):
            bad.append(s["id"])
    check("structure", "Each request contains only protocol fields, 21 ciphertexts and no plaintext inputs",
          not bad and bits_min is not None and bits_min > 3000,
          f"allowed fields {sorted(REQUEST_FIELDS)} · public key: {sorted(key_bits)} bits · shortest ciphertext: {bits_min} bits · "
          f"nonconforming requests: {len(bad)}")

    # 3. Ciphertext randomization
    different = len(set(all_ciphertexts))
    vc_d, vc_t = result_h.get("values_in_plaintext_different"), result_h.get("values_in_plaintext_total")
    check("randomization", "Randomized encryption produces distinct ciphertexts for repeated plaintext values", all_ciphertexts and different == len(all_ciphertexts),
          f"{len(all_ciphertexts)} ciphertexts, {different} distinct · plaintext contained only {vc_d} distinct (feature, value) pairs among {vc_t} values")

    # 4. No plaintext result in service evidence
    patterns, small = set(), 0
    for h in hosp:
        z = int(h["z_decrypted"])
        if abs(z) >= 10 ** 6:
            patterns.add(str(abs(z)))
        else:
            small += 1
        patterns.add(repr(h["probability_ciphertext"])); patterns.add(repr(contract.logit_from_integer(z)))
    files = [os.path.join(a.service, "service_audit.jsonl"), os.path.join(a.service, "service_startup.json")]
    files += sorted(glob.glob(os.path.join(dir_sol, "*.json"))) + [p for p in a.log_service or [] if os.path.exists(p)]
    findings, vectors = [], []
    rx = re.compile(r"(?<![\d.])(?:" + "|".join(re.escape(p) for p in sorted(patterns, key=len, reverse=True)) + r")(?![\d])") if patterns else None
    for p in files:
        text = open(p, errors="replace").read()
        if rx:
            findings += [(os.path.basename(p), m.group(0)) for m in rx.finditer(text)][:3]
        vectors += [os.path.basename(p) for _ in PLAINTEXT_VECTOR.finditer(text)][:1]
    check("without_plaintext", "No decrypted result or plaintext input vector appears in service evidence", not findings and not vectors,
          f"{len(patterns)} searched values (hospital integer logits, logits and probabilities; {small} integers shorter than seven digits excluded) "
          f"in {len(files)} files · findings: {findings[:5] or 0} · 21-integer vectors: {len(vectors)}")

    # 5. Private-key isolation
    with_key = sum(1 for s in filter(None, ours) if s["private_key_in_memory"] is not False)
    check("without_key", "The service process had no live Paillier private key",
          ini_s.get("private_key_in_memory") is False and with_key == 0 and result_h["service_health"].get("key_private") is False,
          f"at startup: {ini_s.get('private_key_in_memory')} · requests with a key in memory: {with_key} · /health: private_key={result_h['service_health'].get('key_private')}")

    # 6. Transport channel
    tls = sorted({s["tls"] for s in filter(None, ours)}); cns = sorted({str(s["client_cn"]) for s in filter(None, ours)})
    check("channel", "TLS 1.3 with the hospital client certificate", tls == ["TLSv1.3"] and cns == ["hospital"],
          f"versions {tls} · client certificate {cns} · TLS cipher {sorted({str(s['ciphertext_tls']) for s in filter(None, ours)})}")

    # 7. Distinct hosts
    ips = sorted({s["client_ip"] for s in filter(None, ours)})
    loop = all(ip.startswith("127.") or ip == "::1" for ip in ips)
    ids_m = (result_h.get("machine_id"), ini_s.get("machine_id"))
    # Different hostnames can also belong to containers on the same host.
    different = bool(all(ids_m) and ids_m[0] != ids_m[1])
    detail = (f"hospital `{result_h['machine']}` id `{ids_m[0]}` ({result_h['architecture']}) · service `{ini_s['machine']}` id `{ids_m[1]}` ({ini_s['architecture']}) · "
               f"client IP seen by service: {', '.join(ips)}" + (" (loopback: SSH tunnel or same host)" if loop else ""))
    if not a.allow_same_machine:
        check("two_hosts", "Hospital and service ran on distinct hosts", different, detail)
    else:
        detail = "Single-host REHEARSAL (--allow-same-machine): " + detail

    # 8. Numerical correctness and metrics
    ex = result_h["accuracy"]
    metrics = result_h.get("metrics_same_sample")
    auc_equal = not metrics or abs(metrics["floating"]["roc_auc"] - metrics["ciphertext"]["roc_auc"]) < 1e-4
    check("accuracy", "Hospital decryption matches the exact plaintext reference and applicable metrics",
          ex["of"] > 0 and ex["identical_integers"] == ex["of"]
          and all(h["identical"] and int(h["z_decrypted"]) == int(h["z_expected"]) for h in hosp) and auc_equal,
          f"exact integers {ex["identical_integers"]}/{ex['of']} (+{result_h['warmup']} warmup) · "
          + (f"ROC-AUC floating point {metrics['floating']['roc_auc']} / encrypted {metrics['ciphertext']['roc_auc']} · "
             if metrics else "no AUC: sample has no clinical labels · ") +
          f"maximum probability error {ex['error_max_probability_vs_floating']:.2e}")

    ok = all(c["ok"] for c in checks)
    verdict = ("PASSED: service processed ciphertexts only" if ok and "two_hosts" in {c["key"] for c in checks}
                 else "REHEARSAL PASSED (same host; repeat on two real hosts)" if ok else "FAILED")
    s390 = [n for n, arch in (("hospital", result_h["architecture"]), ("service", ini_s["architecture"])) if arch == "s390x"]
    now = _now()
    t = result_h["timings_ms"]
    out = {"date_utc": now.isoformat().replace("+00:00", "Z"), "verdict": verdict, "passed": ok, "checks": checks,
           "hospital": {k: result_h[k] for k in ("machine", "architecture", "service_url", "model", "model_sha256", "key_paillier_bits", "sample", "accuracy",
                                              "metrics_same_sample", "timings_ms", "sizes_bytes", "provenance", "log_sha256")},
           "service": {**ini_s, "recorded_requests": len(serv), "log_sha256": _sha_file(os.path.join(a.service, "service_audit.jsonl"))},
           "linuxone_s390x": s390, "command": " ".join(["python -m screening.two_hosts"] + sys.argv[1:])}
    if "two_hosts" not in {c["key"] for c in checks}:
        out["note"] = detail

    adv = (f"> s390x architecture: {', '.join(s390)}. LinuxONE identity still requires Community Cloud evidence."
           if s390 else "> Neither architecture is s390x: this does not establish LinuxONE execution.")
    md = f"""# Two-host audit · {out['date_utc']}

**{verdict}**

{adv}

- Hospital (owns private key): `{result_h['machine']}` · {result_h['architecture']} · commit `{result_h['provenance']['commit']}` · code `{result_h['provenance']['code_sha256'][:16]}`
- Risk service (no private key): `{ini_s['machine']}` · {ini_s['architecture']} · {ini_s['platform']} · code `{ini_s['code_sha256'][:16]}` · container: {ini_s['container']}
- Matching code at both ends: {result_h['provenance']['code_sha256'] == ini_s['code_sha256']} · model `{result_h['model_sha256'][:16]}` (service `{(ini_s.get('model_sha256') or 'n/a')[:16]}`)
- Sample: {result_h['sample']['n']} records · {result_h['sample']['source']} (seed {result_h['sample']['seed']}) · Paillier key: {result_h['key_paillier_bits']} bits
- Flow: hospital encrypts → network/mutual TLS 1.3 → service evaluates Enc(w·x+B) → hospital decrypts · concurrency 1
""" + (f"- ⚠️ {out['note']}\n" if "note" in out else "") + f"""
| # | Check | Result | Detail |
|---|---|---|---|
""" + "".join(f"| {i} | {c['title']} | {'✅' if c['ok'] else '❌'} | {c['detail']} |\n" for i, c in enumerate(checks, 1)) + f"""
| Per-patient time observed by hospital | p50 (ms) | p95 (ms) | mean (ms) |
|---|---:|---:|---:|
""" + "".join(f"| {k.replace('ms_', '').replace('_', ' ')} | {v['p50_ms']} | {v['p95_ms']} | {v['mean_ms']} |\n" for k, v in t.items()) + f"""
Request {result_h['sizes_bytes']['request_p50']} bytes · response {result_h['sizes_bytes']['response_p50']} bytes (p50).
Logs: hospital `{result_h['log_sha256'][:16]}` · service `{out['service']['log_sha256'][:16]}` (SHA-256). Complete exact wire evidence remains outside the repository; a service-side sample follows.
"""
    os.makedirs(a.output, exist_ok=True)
    base = os.path.join(a.output, f"audit_{now.strftime('%Y%m%dT%H%M%SZ')}")
    for s in list(filter(None, ours))[WARMUP:WARMUP + a.samples]:
        for suf in (".request.json", ".response.json"):
            shutil.copy(os.path.join(dir_sol, s["id"] + suf), base + "_" + s["id"][:8] + suf)
        md += f"\n- Sample `{s['id'][:8]}`: `{os.path.basename(base)}_{s['id'][:8]}.request.json` and `.response.json`"
    with open(base + ".json", "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with open(base + ".md", "w") as f:
        f.write(md + "\n")
    print(md)
    print("report:", base + ".md")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("hospital", help="host B: encrypt synthetic inputs, or explicit CDC sample, and call the remote service")
    h.add_argument("--service", required=True, help="https://SERVICE_HOST:8443")
    h.add_argument("--certs", required=True, help="directory containing ca.pem, hospital.pem and hospital.key")
    h.add_argument("--output", required=True, help="directory for hospital_log.jsonl and hospital_summary.json outside the repository")
    h.add_argument("--n", type=int, default=200, help="number of records, at least two")
    h.add_argument("--data", choices=["synthetic", "cdc"], default="synthetic",
                   help="synthetic demo inputs; public CDC only for a labeled benchmark")
    h.add_argument("--without-evidence", action="store_true", help="allow a service without SERVICE_EVIDENCE; disables auditable evidence")
    u = sub.add_parser("audit", help="check that the service never received plaintext inputs/results")
    u.add_argument("--service", required=True, help="SERVICE_EVIDENCE directory from host A")
    u.add_argument("--hospital", required=True, help="--output directory from host B")
    u.add_argument("--log-service", action="append", help="additional service console log to inspect (repeatable)")
    u.add_argument("--output", default=REPORT_OUTPUT)
    u.add_argument("--samples", type=int, default=1, help="request/response examples to include in the report")
    u.add_argument("--allow-same-machine", action="store_true", help="local rehearsal: waive host separation without accrediting two hosts")
    a = ap.parse_args()
    if a.cmd == "hospital":
        run_hospital(a)
    else:
        sys.exit(audit(a))


if __name__ == "__main__":
    main()
