"""Build and verify documentation/code ZIPs under dist/ with SHA-256 manifests.
The public repository is the primary code deliverable; a code ZIP is an alternative.
Documentation includes the pitch PDF/PPTX, script, video instructions, diagram and evidence.
Exclude secrets, raw microdata, private audits, .git, environments, dist and the personal PowerPoint.
Default DRAFT mode lists missing evidence. --final rejects missing requirements or uncommitted code.
Run: python -m screening.package [--kind documentation|code|both] [--final]
"""
import argparse, datetime, glob, hashlib, json, os, re, zipfile
from . import provenance
from .paths import ROOT

EXCLUDE = re.compile(r"(^|/)(\.git|\.venv|__pycache__|dist|data/raw)(/|$)|\.(key|pem)$|AUDITORIA|PLAN_REAUDITORIA|AI_USE\.local|USO_IA\.local|submission/Los_Antimarrulla_Pitch\.pptx$")
DOCUMENTATION = ["data/README.md",
    "submission/Los Antimarrulla_IBM Z Datathon 2026 Project.pdf", "submission/Los_Antimarrulla_Screening_Pitch.pptx",
    "submission/PITCH.md", "submission/SLIDES.md", "submission/VIDEO.md", "submission/HACK2SKILL.md",
    "submission/flowchart/architecture.pdf", "submission/flowchart/architecture.png", "submission/flowchart/architecture.svg",
    "README.md", "LICENSE", "docs/PROJECT.md", "docs/DATA_MODEL.md", "docs/LINUXONE.md", "docs/ENSANUT_EXPERIMENT.md",
    "docs/FORECAST.md", "docs/SUBMISSION_CHECKLIST.md", "docs/REVIEW.md", "docs/TIMELINE.md",
    "docs/TWO_HOSTS.md", "docs/DELIVERY_PLAN.md", "submission/AI_USE.md",
    "artifacts/model/logistic_model_v1.json", "artifacts/model/cdc19_schema_v1.json",
    "artifacts/metrics/logistic_model_v1.json", "artifacts/metrics/ensanut_exploratory_v1.json", "artifacts/metrics/ablation_cdc19_v1.json",
    "artifacts/forecast/e5_forecast_v1.json",
]
DOCUMENTATION_GLOB = ["submission/evidence/README.md", "submission/evidence/local/*", "submission/evidence/metrics/*",
                   "submission/evidence/linuxone/*", "submission/evidence/labs/*",
                   "submission/evidence/two_hosts/*", "submission/evidence/runs/**/*"]
DOCUMENTATION_GLOB += ["submission/VIDEO_RECORD.json", "submission/evidence/instance/*", "docs/*.md", "docs/*.pptx"]
CODE_GLOB = ["tools/**/*.py", ".github/workflows/*.yml", "docs/*.md", "docs/*.pptx", "notebooks/README.md", "src/README.md", "src/**/*.py", "src/**/*.html", "src/data_prep/README.md", "tests/*.py", "tests/instance/*.py", "tests/instance/*.sh", "docker/*", "artifacts/**/*.json",
               "data/cdc_891/*", "data/sinave/tipo1/products.csv", "data/sinave/tipo2/products.csv", "data/catalogos/entidades.csv"]
CODE = ["data/README.md","Makefile", "requirements.txt", ".dockerignore", "LICENSE", "README.md", "docs/LINUXONE.md", "docs/PROJECT.md",
          "docs/TWO_HOSTS.md", "docs/DELIVERY_PLAN.md", "submission/AI_USE.md"]


def _expand(globs):
    out = []
    for g in globs:
        out += [os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, g), recursive=True) if os.path.isfile(p)]
    return out


IMAGE = (b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff")
INVALID_HOSTS = ("example.com", "example.org", "localhost", "127.0.0.1")


def _json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _valid_screenshot(directory, name):
    "Require a real PNG/JPEG file of at least 10 KB inside the evidence directory."
    if not isinstance(name, str) or not name or "/" in name:
        return False
    p = os.path.join(directory, name)
    if not os.path.isfile(p) or os.path.getsize(p) < 10 * 1024:
        return False
    with open(p, "rb") as f:
        header = f.read(8)
    return header.startswith(IMAGE)


def _valid_measurement(m, mode, model_sha):
    "Validate a complete LinuxONE measurement with clean execution provenance."
    if not isinstance(m, dict) or m.get("mode") != mode or not str(m.get("environment_label", "")).startswith("s390x"):
        return False
    env, prov = m.get("environment") or {}, m.get("provenance") or {}
    if env.get("is_linuxone_s390x") is not True or prov.get("clean") is not True or not prov.get("commit"):
        return False
    if not re.fullmatch(r"[0-9a-f]{64}", str(prov.get("code_sha256", ""))) or prov.get("model_sha256") != model_sha:
        return False
    ex, mu = m.get("accuracy") or {}, m.get("sample") or {}
    n = mu.get("n")
    if type(n) is not int or n != (2000 if mode == "process" else 200) or ex.get("identical_integers") != n or ex.get("of") != n:
        return False
    if mode == "process":
        return ex.get("all_within_bound") is True and bool(m.get("microbenchmark_in_process"))
    hr = m.get("hospital_remote") or {}
    return (m.get("client_ms") or {}).get("n") == n and hr.get("model_sha256") == model_sha and hr.get("code_equal_to_client") is True


def _public_url(u):
    if not isinstance(u, str) or not u.startswith("https://") or "draft" in u.lower():
        return False
    host = u.split("/")[2].split(":")[0].lower()
    return bool(host) and not any(host == h or host.endswith("." + h) for h in INVALID_HOSTS)


def final_requirements(prov, root=ROOT):
    "List concrete release blockers from explicit records and files. This does not certify screenshot content or an organizer decision."
    missing = []
    if prov.get("clean") is not True or not prov.get("commit"):
        missing.append("provenance: identifiable commit and no relevant uncommitted changes")
    model = os.path.join(root, "artifacts/model/logistic_model_v1.json")
    model_sha = provenance.sha256(model) if os.path.exists(model) else None
    med = [_json(p) for p in glob.glob(os.path.join(root, "submission/evidence/metrics/measurement_*.json"))]
    for mode, command in (("process", "make measure-docker FINAL=1"), ("api", "make measure-api-docker FINAL=1")):
        if not any(_valid_measurement(m, mode, model_sha) and (m.get("provenance") or {}).get("code_sha256") == prov.get("code_sha256") for m in med):
            missing.append(f"measurement {mode} on LinuxONE with complete results and clean provenance ({command} on the VM)")
    d_l1 = os.path.join(root, "submission/evidence/linuxone")
    reg = _json(os.path.join(d_l1, "RECORD.json")) or {}
    cap = reg.get("screenshots") or {}
    for key in ("dashboard_community_cloud", "uname_lscpu", "containers", "openssl"):
        if not _valid_screenshot(d_l1, cap.get(key)):
            missing.append(f"LinuxONE screenshot '{key}' declared as a real PNG/JPEG in submission/evidence/linuxone/RECORD.json")
    if not reg.get("owner") or not reg.get("date"):
        missing.append("owner and date in submission/evidence/linuxone/RECORD.json")
    d_lab = os.path.join(root, "submission/evidence/labs")
    labs = _json(os.path.join(d_lab, "RECORD.json")) or {}
    for lab in ("lab1", "lab2"):
        l = labs.get(lab) or {}
        if l.get("completed") is not True or not l.get("date") or not l.get("owners") or not l.get("screenshots") \
                or not all(_valid_screenshot(d_lab, c) for c in l.get("screenshots", [])):
            missing.append(f"{lab} completed with date, owners and real screenshots in submission/evidence/labs/RECORD.json")
    v = _json(os.path.join(root, "submission/VIDEO_RECORD.json")) or {}
    dur = v.get("duration_s")
    if not (_public_url(v.get("url")) and isinstance(dur, (int, float)) and 0 < dur <= 180 and v.get("audio") is True
            and v.get("voices_authorized") is True and v.get("access_public_verified") is True and v.get("verified_by") and v.get("date")):
        missing.append("final video: public HTTPS URL, duration <=180 seconds (ffprobe), audio, authorized voices and verified access in submission/VIDEO_RECORD.json")
    else:
        h2s_p = os.path.join(root, "submission/HACK2SKILL.md")
        h2s = open(h2s_p, encoding="utf-8").read() if os.path.exists(h2s_p) else ""
        if v["url"] not in h2s:
            missing.append("the video URL from VIDEO_RECORD.json is absent from submission/HACK2SKILL.md")
    rev_p = os.path.join(root, "docs/REVIEW.md")
    rows = []
    if os.path.exists(rev_p):
        for l in open(rev_p, encoding="utf-8"):
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            if len(c) >= 3 and c[0] and c[0] not in ("Member", "_pending_") and not c[0].startswith("---") and c[1] and not any("partial" in x.lower() for x in c):
                rows.append(c)
    if not rows:
        missing.append("independent teammate review with name and date in docs/REVIEW.md")
    ai_p = os.path.join(root, "submission/AI_USE.md")
    ai = open(ai_p, encoding="utf-8").read().strip() if os.path.exists(ai_p) else ""
    if not ai or "local ai-use declaration draft" in ai.lower() or "publication remains pending" in ai.lower() or "AI_USE.md" not in (open(os.path.join(root, "submission/HACK2SKILL.md"), encoding="utf-8").read()
                                   if os.path.exists(os.path.join(root, "submission/HACK2SKILL.md")) else ""):
        missing.append("AI-use declaration in submission/AI_USE.md linked from HACK2SKILL.md")
    return missing


def build(kind, final, prov):
    if kind == "documentation":
        files = DOCUMENTATION + _expand(DOCUMENTATION_GLOB)
    else:
        files = CODE + _expand(CODE_GLOB)
    files = sorted({a for a in files if not EXCLUDE.search(a)})
    optional = {"submission/AI_USE.md"}  # Local draft, excluded from Git until the team decides where to publish it
    files = [a for a in files if a not in optional or (os.path.exists(os.path.join(ROOT, a))
             and "publication remains pending" not in open(os.path.join(ROOT, a), encoding="utf-8").read().lower())]
    missing = [a for a in files if not os.path.exists(os.path.join(ROOT, a))]
    if missing:
        raise SystemExit(f"missing files in package {kind}: {missing}")
    pending = final_requirements(prov)
    if final and pending:
        raise SystemExit("""final mode rejected. Missing:
  - """ + "\n  - ".join(pending))
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
    name = f"Los_Antimarrulla_{kind}_{'FINAL' if final else 'DRAFT'}_{now}.zip"
    destination = os.path.join(ROOT, "dist", name)
    manifest = {"kind": kind, "mode": "final" if final else "draft", "date_utc": now, "provenance": prov,
                  "official_code": "https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026",
                  "pending_for_final": pending, "files": {}}
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as z:
        for a in files:
            p = os.path.join(ROOT, a)
            manifest["files"][a] = provenance.sha256(p)
            z.write(p, a)
        z.writestr("MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=1))
    # Verify ZIP contents against both the manifest and current files.
    with zipfile.ZipFile(destination) as z:
        man = json.loads(z.read("MANIFEST.json"))
        for a, h in man["files"].items():
            assert hashlib.sha256(z.read(a)).hexdigest() == h == provenance.sha256(os.path.join(ROOT, a)), f"hash mismatch: {a}"
    zsha = provenance.sha256(destination)
    print(f"{kind}: dist/{name} · {len(files)} files · sha256 {zsha[:16]} · commit {str(prov['commit'])[:10]}{'' if prov['clean'] else " (relevant uncommitted changes)"}")
    for p in pending:
        print("  pending for final:", p)
    return destination, zsha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=["documentation", "code", "both"], default="both")
    ap.add_argument("--final", action="store_true")
    a = ap.parse_args()
    prov = provenance.capture()
    for t in (["documentation", "code"] if a.kind == "both" else [a.kind]):
        build(t, a.final, prov)


if __name__ == "__main__":
    main()
