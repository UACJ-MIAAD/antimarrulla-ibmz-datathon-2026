import math
import pytest
from tamizaje import esquema
from tamizaje.esquema import EntradaInvalida


def base():
    return {n: lo for n, lo, hi in esquema.VARIABLES}


def test_orden_y_tamano():
    assert len(esquema.NOMBRES) == 21
    assert esquema.NOMBRES[0] == "HighBP" and esquema.NOMBRES[-1] == "Income"
    assert sum(esquema.MAX_ABS) == 204


def test_acepta_minimos_y_maximos():
    assert esquema.validar(base()) == [lo for _, lo, _ in esquema.VARIABLES]
    assert esquema.validar({n: hi for n, _, hi in esquema.VARIABLES}) == [hi for _, _, hi in esquema.VARIABLES]


def test_acepta_flotante_entero():
    r = base(); r["BMI"] = 30.0
    assert esquema.validar(r)[3] == 30


@pytest.mark.parametrize("valor", [30.5, math.nan, math.inf, -math.inf, None, True, "30", [30]])
def test_rechaza_valores_invalidos(valor):
    r = base(); r["BMI"] = valor
    with pytest.raises(EntradaInvalida):
        esquema.validar(r)


@pytest.mark.parametrize("var,valor", [("BMI", 11), ("BMI", 99), ("HighBP", 2), ("HighBP", -1), ("Age", 0), ("Age", 14), ("GenHlth", 6), ("Income", 9)])
def test_rechaza_fuera_de_rango(var, valor):
    r = base(); r[var] = valor
    with pytest.raises(EntradaInvalida):
        esquema.validar(r)


def test_rechaza_faltante_y_sobrante():
    r = base(); del r["Income"]
    with pytest.raises(EntradaInvalida):
        esquema.validar(r)
    r = base(); r["ID"] = 1
    with pytest.raises(EntradaInvalida):
        esquema.validar(r)
    with pytest.raises(EntradaInvalida):
        esquema.validar([0] * 21)
