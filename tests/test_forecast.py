"Optional E5: forecast artifact coherence and forecasting primitives."
import json, os
import numpy as np
import pytest
from screening import forecast
from screening.paths import ROOT

PATH = os.path.join(ROOT, "artifacts", "forecast", "e5_forecast_v1.json")


@pytest.fixture(scope="module")
def p():
    if not os.path.exists(PATH):
        pytest.skip("forecast artifact missing (make forecast)")
    return json.load(open(PATH))


def test_naive_seasonal_repeats_the_last_season():
    y = np.arange(104, dtype=float)
    assert list(forecast.snaive(y, 54)[:3]) == [52.0, 53.0, 54.0] and forecast.snaive(y, 54)[52] == 52.0


def test_smape():
    assert forecast.smape(np.array([10.0, 0.0]), np.array([10.0, 0.0])) == 0
    assert forecast.smape(np.array([10.0]), np.array([0.0])) == 200


def test_222_series_and_horizon(p):
    assert len(p["series"]) == 222
    assert p["horizon"]["weeks"] == 52 and p["last_observation"] == "2026-07-27"
    for s in p["series"]:
        assert len(s["forecast"]["point"]) == p["weeks_nowcast"] + 52
        assert all(v >= 0 for v in s["forecast"]["point"])
        assert all(low <= pt <= high for low, pt, high in zip(s["forecast"]["lo95"], s["forecast"]["point"], s["forecast"]["hi95"]))


def test_states_sum_to_national(p):
    for kind in ("diabetes_t1", "diabetes_t2"):
        for sex in ("all", "men", "women"):
            national = next(s for s in p["series"] if s["kind"] == kind and s["level"] == "national" and s["sex"] == sex)
            est = [s for s in p["series"] if s["kind"] == kind and s["level"] == "state" and s["sex"] == sex]
            assert len(est) == 32
            total = sum(s["total_52"]["point"] for s in est)
            assert abs(total - national["total_52"]["point"]) <= 0.005 * national["total_52"]["point"] + 32  # Per-series rounding


def test_without_cost_does_not_has_budget(p):
    if p["unit_cost_mxn"] is None:
        assert all("budget_52_mxn" not in s for s in p["series"])


# F06: evaluate the published reconciled system through h63 without future leakage.
REG = {"01": "centro", "02": "centro"}


def _hierarchy(n=240, seed=0, unusual_future_from=None):
    rnd = np.random.default_rng(seed)
    t = np.arange(n)
    base = lambda level: level * (1 + 0.3 * np.sin(2 * np.pi * t / 52)) + rnd.normal(0, level * 0.05, n)
    e1, e2 = np.clip(base(40), 0, None), np.clip(base(60), 0, None)
    ys = {("x", "state", "01", "all"): e1, ("x", "state", "02", "all"): e2,
          ("x", "region", "centro", "all"): e1 + e2, ("x", "national", "mx", "all"): e1 + e2}
    if unusual_future_from is not None:
        ys = {k: np.concatenate([v[:unusual_future_from], np.full(n - unusual_future_from, 1e6)]) for k, v in ys.items()}
    return ys


def test_f06_evaluation_through_63_steps_with_segments():
    ev = forecast.evaluate(_hierarchy(), REG, h=63)
    assert ev["horizon"] == 63 and ev["origins"]
    for level in ("national", "region", "state"):
        assert {"h1-13", "h14-26", "h27-52", "h53-63", "h12-63"} <= set(ev["by_level"][level])
        assert 0 <= ev["by_level"][level]["h12-63"]["coverage_80"] <= 1


def test_f06_without_future_in_the_training():
    normal = _hierarchy()
    o = max(forecast.evaluate(normal, REG, h=63)["origins"])
    unusual = _hierarchy(unusual_future_from=o)
    a = forecast.evaluate(normal, REG, h=63)["forecasts"][o]
    b = forecast.evaluate(unusual, REG, h=63)["forecasts"][o]
    for k in a:
        assert np.allclose(a[k], b[k])


def test_f06_forecast_evaluated_is_reconciled():
    ev = forecast.evaluate(_hierarchy(), REG, h=63)
    for o, f in ev["forecasts"].items():
        assert np.allclose(f[("x", "state", "01", "all")] + f[("x", "state", "02", "all")], f[("x", "national", "mx", "all")])


def test_f06_published_includes_evaluation_and_63_steps(p):
    assert p["steps_since_last_observation"] == 63 == p["nested_evaluation"]["horizon_steps"]
    for s in p["series"]:
        assert "h53-63" in s["evaluation_smape"] and "selection" in s and "backtest" not in s
    assert any("exploratory" in a for a in p["warnings"])


def test_rejects_missing_observations_before_any_global_interpolation():
    # A missing value immediately before a holdout can otherwise use that holdout.
    with pytest.raises(ValueError, match="fold-local imputation"):
        forecast.prepare_observations([1.0, np.nan, 1000.0])
    with pytest.raises(ValueError, match="finite"):
        forecast.prepare_observations([1.0, np.inf])
    values, count = forecast.prepare_observations([1.0, 2.0, 3.0])
    assert list(values) == [1.0, 2.0, 3.0] and count == 0


@pytest.mark.parametrize("cost,source", [("0", "reference"), ("-1", "reference"),
                                         ("nan", "reference"), ("inf", "reference"),
                                         ("100", "   ")])
def test_rejects_invalid_budget_assumptions_before_loading_data(monkeypatch, cost, source):
    monkeypatch.setattr("sys.argv", ["forecast", "--cost-mxn", cost, "--source-cost", source])
    with pytest.raises(SystemExit, match="positive and finite"):
        forecast.main()
