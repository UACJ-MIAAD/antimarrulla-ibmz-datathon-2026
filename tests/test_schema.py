import math
import pytest
from screening import schema
from screening.schema import InvalidInput


def base():
    return {n: what for n, what, hi in schema.VARIABLES}


def test_order_and_size():
    assert len(schema.FEATURE_NAMES) == 21
    assert schema.FEATURE_NAMES[0] == "HighBP" and schema.FEATURE_NAMES[-1] == "Income"
    assert sum(schema.MAX_ABS) == 204


def test_accepts_minimum_and_maximum():
    assert schema.validate(base()) == [what for _, what, _ in schema.VARIABLES]
    assert schema.validate({n: hi for n, _, hi in schema.VARIABLES}) == [hi for _, _, hi in schema.VARIABLES]


def test_accepts_floating_integer():
    r = base(); r["BMI"] = 30.0
    assert schema.validate(r)[3] == 30


@pytest.mark.parametrize("value", [30.5, math.nan, math.inf, -math.inf, None, True, "30", [30]])
def test_rejects_values_invalid(value):
    r = base(); r["BMI"] = value
    with pytest.raises(InvalidInput):
        schema.validate(r)


@pytest.mark.parametrize("var,value", [("BMI", 11), ("BMI", 99), ("HighBP", 2), ("HighBP", -1), ("Age", 0), ("Age", 14), ("GenHlth", 6), ("Income", 9)])
def test_rejects_outside_of_range(var, value):
    r = base(); r[var] = value
    with pytest.raises(InvalidInput):
        schema.validate(r)


def test_rejects_missing_and_extra():
    r = base(); del r["Income"]
    with pytest.raises(InvalidInput):
        schema.validate(r)
    r = base(); r["ID"] = 1
    with pytest.raises(InvalidInput):
        schema.validate(r)
    with pytest.raises(InvalidInput):
        schema.validate([0] * 21)
