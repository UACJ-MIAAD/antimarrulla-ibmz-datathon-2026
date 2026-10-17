"F03: provenance identifies executed code without hiding relevant uncommitted changes."
import os, shutil, subprocess
import pytest
from screening import provenance

without_git = pytest.mark.skipif(shutil.which("git") is None, reason="the dev image has no Git metadata; container provenance is declared by Makefile")


def git(d, *a):
    subprocess.run(["git", "-C", str(d), *a], check=True, capture_output=True)


@pytest.fixture()
def repo(tmp_path):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "test@example.com"); git(tmp_path, "config", "user.name", "test")
    (tmp_path / "src" / "screening").mkdir(parents=True)
    (tmp_path / "src" / "screening" / "a.py").write_text("x = 1\n")
    (tmp_path / "Makefile").write_text("all:\n")
    git(tmp_path, "add", "-A"); git(tmp_path, "commit", "-q", "-m", "startup")
    return tmp_path


@without_git
def test_clean(repo):
    e = provenance.git_state(str(repo))
    assert e["relevant"] == [] and e["commit"]


@without_git
def test_source_new_does_not_tracked_count(repo):
    (repo / "src" / "screening" / "measure.py").write_text("y = 2\n")
    e = provenance.git_state(str(repo))
    assert any("src/screening/measure.py" in r for r in e["relevant"])


@without_git
def test_source_modified_count(repo):
    (repo / "src" / "screening" / "a.py").write_text("x = 3\n")
    e = provenance.git_state(str(repo))
    assert any("src/screening/a.py" in r for r in e["relevant"])


@without_git
def test_file_personal_unrelated_does_not_marks_dirty(repo):
    (repo / "submission").mkdir()
    (repo / "submission" / "Los_Antimarrulla_Pitch.pptx").write_bytes(b"personal")
    e = provenance.git_state(str(repo))
    assert e["relevant"] == [] and any("Los_Antimarrulla_Pitch.pptx" in a for a in e["unrelated"])


def test_hash_of_code_changes_with_the_code(tmp_path):
    (tmp_path / "m.py").write_text("a = 1\n")
    h1, n = provenance.hash_code(str(tmp_path))
    (tmp_path / "m.py").write_text("a = 2\n")
    h2, _ = provenance.hash_code(str(tmp_path))
    (tmp_path / "nuevo.py").write_text("b = 1\n")
    h3, n3 = provenance.hash_code(str(tmp_path))
    assert n == 1 and n3 == 2 and len({h1, h2, h3}) == 3


def test_mismatch_of_hashes():
    reg = provenance.capture()
    assert provenance.verify(reg) == []
    false = dict(reg, code_sha256="0" * 64, model_sha256="1" * 64)
    assert set(provenance.verify(false)) == {"code_sha256", "model_sha256"}


def test_mode_final_rejects_changes_relevant():
    with pytest.raises(provenance.DirtyProvenance):
        provenance.require_clean({"clean": False, "changes_relevant": ["?? src/screening/x.py"], "source_commit": "git", "commit": "abc"})
    provenance.require_clean({"clean": True, "changes_relevant": [], "source_commit": "git", "commit": "abc"})


def test_container_without_git_uses_what_declared(tmp_path, monkeypatch):
    monkeypatch.setenv("SCREENING_COMMIT", "abc123"); monkeypatch.setenv("SCREENING_RELEVANT_CHANGES", "1")
    e = provenance.git_state(str(tmp_path))
    assert e["commit"] == "abc123" and e["relevant"]


def test_r1_final_rejects_state_unknown_and_commit_missing():
    with pytest.raises(provenance.DirtyProvenance):
        provenance.require_clean({"clean": None, "source_commit": "environment", "commit": "declared", "changes_relevant": None})
    with pytest.raises(provenance.DirtyProvenance):
        provenance.require_clean({"clean": True, "source_commit": "git", "commit": None, "changes_relevant": []})


def test_r1_git_that_failure_returns_state_unknown(tmp_path):
    (tmp_path / ".git").mkdir()  # Broken .git directory: Git cannot report the working-tree state.
    e = provenance.git_state(str(tmp_path))
    assert e["relevant"] is None and e["commit"] is None
