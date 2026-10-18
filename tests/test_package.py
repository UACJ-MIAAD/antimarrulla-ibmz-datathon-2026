"F05/R2: final mode validates substantive evidence, not file presence alone."
import json, os
import pytest
from screening import package, provenance

PROV = {"clean": True, "commit": "a" * 40, "code_sha256": "c" * 64}
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 12000


def test_excludes_private():
    for path in ["data/raw/ensanut/x.csv", ".git/config", ".venv/bin/python", "submission/Los_Antimarrulla_Pitch.pptx",
                 "docs/AUDITORIA_2.md", "docs/PLAN_REAUDITORIA.md", "x/service.key", "dist/a.zip"]:
        assert package.EXCLUDE.search(path), path
    for path in ["src/screening/protocol.py", "submission/Los_Antimarrulla_Screening_Pitch.pptx", "data/cdc_891/cdc_diabetes_891.csv"]:
        assert not package.EXCLUDE.search(path), path


def w(root, rel, contents):
    p = os.path.join(root, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb" if isinstance(contents, bytes) else "w") as f:
        f.write(contents if isinstance(contents, (bytes, str)) else json.dumps(contents))


def complete(root):
    w(root, "artifacts/model/logistic_model_v1.json", "{}")
    msha = provenance.sha256(os.path.join(root, "artifacts/model/logistic_model_v1.json"))
    base = {"environment_label": "s390x", "environment": {"is_linuxone_s390x": True},
            "provenance": {"clean": True, "commit": "a" * 40, "code_sha256": "c" * 64, "model_sha256": msha}}
    w(root, "submission/evidence/metrics/measurement_process_s390x_1.json", {**base, "mode": "process", "sample": {"n": 2000},
      "accuracy": {"identical_integers": 2000, "of": 2000, "all_within_bound": True}, "microbenchmark_in_process": {"x": 1}})
    w(root, "submission/evidence/metrics/measurement_api_s390x_1.json", {**base, "mode": "api", "sample": {"n": 200},
      "accuracy": {"identical_integers": 200, "of": 200}, "client_ms": {"n": 200},
      "hospital_remote": {"model_sha256": msha, "code_equal_to_client": True}})
    caps = {k: f"{k}.png" for k in ("dashboard_community_cloud", "uname_lscpu", "containers", "openssl")}
    for f in caps.values():
        w(root, f"submission/evidence/linuxone/{f}", PNG)
    w(root, "submission/evidence/linuxone/RECORD.json", {"owner": "Álvaro", "date": "2026-10-18", "screenshots": caps})
    for f in ("l1.png", "l2.png"):
        w(root, f"submission/evidence/labs/{f}", PNG)
    w(root, "submission/evidence/labs/RECORD.json", {
        "lab1": {"completed": True, "date": "2026-10-17", "owners": ["Carlos"], "screenshots": ["l1.png"]},
        "lab2": {"completed": True, "date": "2026-10-17", "owners": ["Yazmin"], "screenshots": ["l2.png"]}})
    url = "https://youtu.be/abcdefghijk"
    w(root, "submission/VIDEO_RECORD.json", {"url": url, "duration_s": 172.0, "audio": True, "voices_authorized": True,
      "access_public_verified": True, "verified_by": "Javier", "date": "2026-10-18"})
    w(root, "submission/HACK2SKILL.md", f"| Video | {url} |\n| AI use | [Declaration](AI_USE.md) |\n")
    w(root, "submission/AI_USE.md", "Assistant tools and tasks declared; the team documents human review.")
    w(root, "docs/REVIEW.md", """| Member | Date and time | Commands run | Comments |
|---|---|---|---|
| Carlos | 2026-10-18 02:00 | make verify | ok |
""")


def test_r2_complete_passes(tmp_path):
    complete(str(tmp_path))
    assert package.final_requirements(PROV, root=str(tmp_path)) == []


def test_r2_cases_of_auditor_rejected(tmp_path):
    r = str(tmp_path)
    w(r, "artifacts/model/logistic_model_v1.json", "{}")
    w(r, "submission/evidence/metrics/measurement_s390x.json", {"environment_label": "s390x"})
    w(r, "submission/evidence/linuxone/README.txt", "pending")
    w(r, "submission/evidence/labs/lab1.txt", "lab 1 is incomplete")
    w(r, "submission/HACK2SKILL.md", "| Video | https://example.com/draft |\n")
    w(r, "submission/VIDEO_RECORD.json", {"url": "https://example.com/draft", "duration_s": 170})
    missing = " ".join(package.final_requirements(PROV, root=r))
    for expected in ("measurement process", "measurement api", "dashboard_community_cloud", "lab1", "lab2", "final video", "review"):
        assert expected in missing, expected


@pytest.mark.parametrize("break_case", ["without_results", "lab2_false", "screenshot_txt", "video_length", "video_without_audio", "without_revision", "api_other_code"])
def test_r2_each_failure_self_detects(tmp_path, break_case):
    r = str(tmp_path); complete(r)
    if break_case == "without_results":
        p = os.path.join(r, "submission/evidence/metrics/measurement_process_s390x_1.json"); m = json.load(open(p)); m["accuracy"]["identical_integers"] = 1999; w(r, p[len(r) + 1:], m)
    elif break_case == "lab2_false":
        p = os.path.join(r, "submission/evidence/labs/RECORD.json"); m = json.load(open(p)); m["lab2"]["completed"] = False; w(r, p[len(r) + 1:], m)
    elif break_case == "screenshot_txt":
        w(r, "submission/evidence/linuxone/dashboard_community_cloud.png", "text, not an image" * 1000)
    elif break_case in ("video_length", "video_without_audio"):
        p = os.path.join(r, "submission/VIDEO_RECORD.json"); m = json.load(open(p))
        m.update({"duration_s": 181} if break_case == "video_length" else {"audio": False}); w(r, p[len(r) + 1:], m)
    elif break_case == "without_revision":
        w(r, "docs/REVIEW.md", "| Member | Date |\n|---|---|\n| _pending_ | |\n")
    elif break_case == "api_other_code":
        p = os.path.join(r, "submission/evidence/metrics/measurement_api_s390x_1.json"); m = json.load(open(p)); m["hospital_remote"]["code_equal_to_client"] = False; w(r, p[len(r) + 1:], m)
    assert package.final_requirements(PROV, root=r), break_case


def test_r2_provenance_unknown_rejected(tmp_path):
    complete(str(tmp_path))
    assert package.final_requirements({"clean": None, "commit": "a"}, root=str(tmp_path))


def test_without_declaration_ai_does_not_is_package_final(tmp_path):
    complete(str(tmp_path))
    os.unlink(tmp_path / "submission/AI_USE.md")
    assert any("AI-use declaration" in f for f in package.final_requirements(PROV, root=str(tmp_path)))


def test_partial_clone_check_does_not_close_independent_review(tmp_path):
    complete(str(tmp_path))
    w(str(tmp_path), "docs/REVIEW.md", "| Member | Date | Commands | Comments |\n|---|---|---|---|\n| Yazmin | 2026-10-17 | make verify | **Partial:** clone check only |\n")
    assert any("independent teammate review" in item for item in package.final_requirements(PROV, root=str(tmp_path)))


def test_local_ai_draft_does_not_satisfy_final_declaration(tmp_path):
    complete(str(tmp_path))
    w(str(tmp_path), "submission/AI_USE.md", "# Local AI-use declaration draft\nPublication remains pending the team decision.")
    assert any("AI-use declaration" in item for item in package.final_requirements(PROV, root=str(tmp_path)))


@pytest.mark.parametrize("mode", ["process", "api"])
def test_final_package_rejects_single_patient_measurement(tmp_path, mode):
    root = str(tmp_path); complete(root)
    path = f"submission/evidence/metrics/measurement_{mode}_s390x_1.json"
    measurement = json.load(open(os.path.join(root, path)))
    measurement["sample"]["n"] = 1
    measurement["accuracy"].update(identical_integers=1, of=1)
    if mode == "api": measurement["client_ms"]["n"] = 1
    w(root, path, measurement)
    assert any(f"measurement {mode}" in e for e in package.final_requirements(PROV, root=root))


def test_final_package_rejects_other_executable_code(tmp_path):
    root = str(tmp_path); complete(root)
    current = dict(PROV, code_sha256="d" * 64)
    assert sum(e.startswith("measurement ") for e in package.final_requirements(current, root=root)) == 2


@pytest.mark.parametrize("mode,n,valid", [("process", 20, False), ("process", 200, False), ("process", 2000, True), ("process", 16000, True), ("process", 1, False), ("api", 20, False), ("api", 200, True), ("api", 16000, True)])
def test_release_samples_respect_diagnostic_and_final_sizes(mode, n, valid):
    from screening.benchmark_profiles import release_size
    assert release_size(mode, n) is valid
