"""Esquema versionado de las 21 variables del CDC (UCI 891) que acepta el protocolo.

El hospital manda los códigos enteros tal cual (sin escalar). Cualquier vector que no cumpla
exactamente este esquema se rechaza completo.
"""
import math

VERSION = "cdc21-v1"

# (nombre, mínimo, máximo) en el orden fijo del protocolo. Rangos del libro de códigos del CDC (BRFSS 2015).
VARIABLES = [
    ("HighBP", 0, 1), ("HighChol", 0, 1), ("CholCheck", 0, 1), ("BMI", 12, 98), ("Smoker", 0, 1),
    ("Stroke", 0, 1), ("HeartDiseaseorAttack", 0, 1), ("PhysActivity", 0, 1), ("Fruits", 0, 1),
    ("Veggies", 0, 1), ("HvyAlcoholConsump", 0, 1), ("AnyHealthcare", 0, 1), ("NoDocbcCost", 0, 1),
    ("GenHlth", 1, 5), ("MentHlth", 0, 30), ("PhysHlth", 0, 30), ("DiffWalk", 0, 1), ("Sex", 0, 1),
    ("Age", 1, 13), ("Education", 1, 6), ("Income", 1, 8),
]
NOMBRES = [v[0] for v in VARIABLES]
RANGOS = {n: (lo, hi) for n, lo, hi in VARIABLES}
MAX_ABS = [max(abs(lo), abs(hi)) for _, lo, hi in VARIABLES]
OBJETIVO = "Diabetes_binary"


class EntradaInvalida(ValueError):
    """El vector del paciente no cumple el esquema."""


def a_entero(nombre, valor):
    """Convierte un valor a entero solo si ya es un entero exacto y finito; si no, lo rechaza."""
    if isinstance(valor, bool) or valor is None:
        raise EntradaInvalida(f"{nombre}: valor ausente o booleano")
    if isinstance(valor, int):
        v = valor
    elif isinstance(valor, float):
        if not math.isfinite(valor):
            raise EntradaInvalida(f"{nombre}: valor no finito")
        if not valor.is_integer():
            raise EntradaInvalida(f"{nombre}: valor fraccionario ({valor})")
        v = int(valor)
    else:
        raise EntradaInvalida(f"{nombre}: tipo no permitido ({type(valor).__name__})")
    lo, hi = RANGOS[nombre]
    if not lo <= v <= hi:
        raise EntradaInvalida(f"{nombre}: {v} fuera de rango [{lo}, {hi}]")
    return v


def validar(registro):
    """Recibe un dict {variable: valor} y regresa la lista de 21 enteros en el orden del protocolo."""
    if not isinstance(registro, dict):
        raise EntradaInvalida("se esperaba un objeto con las 21 variables")
    faltan = [n for n in NOMBRES if n not in registro]
    sobran = sorted(set(registro) - set(NOMBRES))
    if faltan or sobran:
        raise EntradaInvalida(f"variables faltantes {faltan} o no permitidas {sobran}")
    return [a_entero(n, registro[n]) for n in NOMBRES]


def como_dict():
    return {"version": VERSION, "objetivo": OBJETIVO,
            "variables": [{"nombre": n, "min": lo, "max": hi, "tipo": "entero"} for n, lo, hi in VARIABLES]}
