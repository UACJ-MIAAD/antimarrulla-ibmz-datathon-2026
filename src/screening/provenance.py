"""Execution provenance: identify the code, model and data actually used.
Hash sorted executable .py/.html files, model, splits and CDC input. Track relevant changes
under src/, tests/, docker/, Makefile, requirements.txt, .dockerignore, artifacts/model and artifacts/splits.
Relevant untracked files count as changes; unrelated personal artifacts do not.
Containers receive SCREENING_COMMIT and SCREENING_IMAGE; hash the code inside the image.
"""
import hashlib, os, subprocess
from .paths import MODEL_JSON, SPLITS, CDC_CSV, ROOT

CODE = os.path.dirname(os.path.abspath(__file__))
RELEVANT = ("src/", "tests/", "docker/", "Makefile", "requirements.txt", ".dockerignore", "artifacts/model/", "artifacts/splits/")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def hash_code(directory=CODE):
    "Stable hash of sorted executable relative paths and contents (.py/.html)."
    h = hashlib.sha256()
    files = []
    for base, dirs, names in os.walk(directory):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        for n in sorted(names):
            if n.endswith((".py", ".html")):
                files.append(os.path.join(base, n))
    for p in sorted(files):
        rel = os.path.relpath(p, directory).replace(os.sep, "/")
        h.update(rel.encode() + b"\0" + open(p, "rb").read() + b"\0")
    return h.hexdigest(), len(files)


def _git(root, *a):
    try:
        r = subprocess.run(["git", "-C", root, *a], capture_output=True, text=True, timeout=30)
        return r.stdout if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def is_relevant(path):
    return path.startswith(RELEVANT) or path in RELEVANT


def git_state(root=ROOT):
    "Return commit and relevant/unrelated changes; containers use SCREENING_COMMIT."
    if not os.path.isdir(os.path.join(root, ".git")):
        declared = os.environ.get("SCREENING_RELEVANT_CHANGES")
        rel = None if declared is None else ([] if declared == "0" else ["the image build declared relevant uncommitted changes"])
        return {"source": "environment", "commit": os.environ.get("SCREENING_COMMIT"), "relevant": rel, "unrelated": None,
                "note": "container without .git: Makefile declares commit/state; the in-image source hash identifies executable code"}
    commit = (_git(root, "rev-parse", "HEAD") or "").strip() or None
    output = _git(root, "status", "--porcelain", "--untracked-files=all")
    if commit is None or output is None:  # A Git failure means unknown state, not a clean working tree.
        return {"source": "git", "commit": commit, "relevant": None, "unrelated": None, "note": "Git did not return a valid state; cleanliness is unknown"}
    relevant, unrelated = [], []
    for line in output.splitlines():
        state, path = line[:2], line[3:].strip().strip('"')
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        (relevant if is_relevant(path) else unrelated).append(f"{state.strip() or '?'} {path}")
    return {"source": "git", "commit": commit, "relevant": relevant, "unrelated": unrelated}


def capture(root=ROOT):
    code, n = hash_code()
    g = git_state(root)
    return {
        "commit": g["commit"], "source_commit": g["source"],
        "clean": (g["relevant"] == []) if g["relevant"] is not None else None,
        "changes_relevant": g["relevant"], "files_unrelated_to_experiment": g["unrelated"],
        "code_sha256": code, "code_files": n,
        "model_sha256": sha256(MODEL_JSON), "splits_sha256": sha256(SPLITS),
        "cdc_sha256": sha256(CDC_CSV) if os.path.exists(CDC_CSV) else None,
        "image": os.environ.get("SCREENING_IMAGE"),
        **({"note": g["note"]} if "note" in g else {}),
    }


def verify(record, root=ROOT):
    "Compare recorded provenance with current artifact/code hashes and return mismatched fields."
    current = capture(root)
    return [k for k in ("code_sha256", "model_sha256", "splits_sha256", "cdc_sha256")
            if record.get(k) and record.get(k) != current.get(k)]


class DirtyProvenance(RuntimeError):
    pass


def require_clean(reg):
    "Final mode requires an identifiable commit and proven cleanliness (clean is True)."
    if not reg.get("commit"):
        raise DirtyProvenance("final mode: no identifiable commit (Git failed or the container omitted SCREENING_COMMIT)")
    if reg.get("clean") is not True:
        detail = ", ".join(reg.get("changes_relevant") or []) or "working-tree state is unknown"
        raise DirtyProvenance("final mode: absence of relevant uncommitted changes is not established: " + detail)
