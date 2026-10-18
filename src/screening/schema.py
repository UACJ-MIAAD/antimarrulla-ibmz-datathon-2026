"""Versioned 19-feature CDC UCI 891 schema (Education and Income removed: no measurable AUC contribution).
The hospital sends original unscaled integer codes. Reject the whole record if any feature,
type, range or name violates this schema.
"""
import math

VERSION = "cdc19-v1"

# (name, minimum, maximum) in protocol order, using CDC BRFSS 2015 codebook ranges.
VARIABLES = [
    ("HighBP", 0, 1), ("HighChol", 0, 1), ("CholCheck", 0, 1), ("BMI", 12, 98), ("Smoker", 0, 1),
    ("Stroke", 0, 1), ("HeartDiseaseorAttack", 0, 1), ("PhysActivity", 0, 1), ("Fruits", 0, 1),
    ("Veggies", 0, 1), ("HvyAlcoholConsump", 0, 1), ("AnyHealthcare", 0, 1), ("NoDocbcCost", 0, 1),
    ("GenHlth", 1, 5), ("MentHlth", 0, 30), ("PhysHlth", 0, 30), ("DiffWalk", 0, 1), ("Sex", 0, 1),
    ("Age", 1, 13),
]
# Columns present in the CDC file but outside the protocol; only used by exploratory analyses (ENSANUT).
AUXILIARY_RANGES = {"Education": (1, 6), "Income": (1, 8)}
FEATURE_NAMES = [v[0] for v in VARIABLES]
RANGES = {n: (low, high) for n, low, high in VARIABLES}
MAX_ABS = [max(abs(low), abs(high)) for _, low, high in VARIABLES]
TARGET = "Diabetes_binary"


class InvalidInput(ValueError):
    "Patient input violates the feature schema."


def to_integer(name, value):
    "Accept only exact finite integer values within the feature range."
    if isinstance(value, bool) or value is None:
        raise InvalidInput(f"{name}: missing or boolean value")
    if isinstance(value, int):
        v = value
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise InvalidInput(f"{name}: non-finite value")
        if not value.is_integer():
            raise InvalidInput(f"{name}: fractional value ({value})")
        v = int(value)
    else:
        raise InvalidInput(f"{name}: unsupported type ({type(value).__name__})")
    low, high = RANGES[name] if name in RANGES else AUXILIARY_RANGES[name]
    if not low <= v <= high:
        raise InvalidInput(f"{name}: {v} outside range [{low}, {high}]")
    return v


def validate(record):
    "Return 19 integers in protocol order from a feature-name/value dictionary."
    if not isinstance(record, dict):
        raise InvalidInput(f"expected an object containing all {len(FEATURE_NAMES)} features")
    missing = [n for n in FEATURE_NAMES if n not in record]
    extra = sorted(set(record) - set(FEATURE_NAMES))
    if missing or extra:
        raise InvalidInput(f"missing variables {missing} or unexpected variables {extra}")
    return [to_integer(n, record[n]) for n in FEATURE_NAMES]


def as_dict():
    return {"version": VERSION, "target": TARGET,
            "variables": [{"name": n, "min": low, "max": high, "kind": "integer"} for n, low, high in VARIABLES]}
