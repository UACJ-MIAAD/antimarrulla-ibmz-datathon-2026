"Project paths relative to the repository root or SCREENING_ROOT inside a container."
import os

ROOT = os.environ.get("SCREENING_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
CDC_CSV = os.path.join(ROOT, "data", "cdc_891", "cdc_diabetes_891.csv")
ARTIFACTS = os.path.join(ROOT, "artifacts")
SPLITS = os.path.join(ARTIFACTS, "splits", "cdc891_splits_v1.json")
SCHEMA_JSON = os.path.join(ARTIFACTS, "model", "cdc19_schema_v1.json")
MODEL_JSON = os.path.join(ARTIFACTS, "model", "logistic_model_v1.json")
MODEL_METRICS = os.path.join(ARTIFACTS, "metrics", "logistic_model_v1.json")
MEASUREMENTS = os.environ.get("SCREENING_MEASUREMENTS", os.path.join(ROOT, "submission", "evidence", "metrics"))


def ensure_dirs():
    for d in (os.path.dirname(SPLITS), os.path.dirname(MODEL_JSON), os.path.dirname(MODEL_METRICS)):
        os.makedirs(d, exist_ok=True)
