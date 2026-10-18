"Plaintext logit timing on the encrypted experiment sample."
import pytest
from screening import measure, synthetic, schema


def test_benchmark_plaintext_reports_timings_and_same_sample(model):
    xs = [[synthetic.random_patient(k)[n] for n in schema.FEATURE_NAMES] for k in range(4)]
    r = measure.benchmark_plaintext(model, xs, repetitions=3)
    assert r["n_patients"] == 4 and len(r["sample_sha256"]) == 64
    for name in ("floating", "fixed_point"):
        assert r[name]["n_evaluations"] == 12
        assert 0 < r[name]["p50_us"] <= r[name]["p95_us"]


def test_benchmark_rejects_sample_empty(model):
    with pytest.raises(ValueError):
        measure.benchmark_plaintext(model, [])


def test_api_final_rejects_code_remote_different(model, monkeypatch):
    import argparse, io, json, urllib.request
    from screening import provenance
    from screening.paths import MODEL_JSON
    state = {"model_sha256": provenance.sha256(MODEL_JSON), "code_sha256": "0" * 64}
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **kw: io.BytesIO(json.dumps(state).encode()))
    a = argparse.Namespace(url="http://127.0.0.1:8080", final=True)
    with pytest.raises(SystemExit, match="hospital code"):
        measure.api_mode(a, model, {"code_sha256": "1" * 64}, {}, None, "local")


@pytest.mark.parametrize("requested", [20, 200, 2000, 16000])
def test_explicit_samples_never_shrink_to_the_time_budget(requested):
    from screening.benchmark_profiles import sample_size
    assert sample_size(38052, 2000, 1, 10, requested) == requested


def test_explicit_sample_larger_than_test_split_is_rejected():
    from screening.benchmark_profiles import sample_size
    with pytest.raises(ValueError):
        sample_size(38052, 2000, 600, 0.1, 50000)


def test_legacy_adaptive_budget_still_works():
    from screening.benchmark_profiles import sample_size
    assert sample_size(38052, 2000, 600, 0.5) == 1200
