"""The recorded ablation evidence is consistent with the current schema and supports removing Education and Income."""
import json, os
from screening import ablation, data, schema
from screening.paths import SPLITS


def test_recorded_ablation_matches_schema_and_splits():
    out = json.load(open(ablation.OUTPUT))
    assert out["splits_sha256"] == data.sha256(SPLITS)
    r = out["results"]
    assert r["without_both_19"]["features"] == len(schema.FEATURE_NAMES) == 19 and r["all_21"]["features"] == 21
    assert abs(r["without_both_19"]["delta_roc_auc_vs_21"]) < 0.005  # removal costs less than 0.005 AUC
