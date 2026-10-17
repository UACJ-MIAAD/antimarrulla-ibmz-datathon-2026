"""Contrato numérico del protocolo (ver docs/PROYECTO.md · Protocolo numérico).

- Entradas: los 21 códigos enteros del esquema, sin escalar (S_x = 1).
- Pesos e intercepto: W_i = round(S_W · w'_i), B = round(S_W · b'), con S_W = 10^9.
- Exponente de Paillier: 0 en todo (solo se cifran y multiplican enteros).
- Toda la aritmética de referencia usa enteros de Python (exacta).
"""
import math
from . import esquema

S_W = 10 ** 9
EXPONENTE = 0


class ModeloInvalido(ValueError):
    """El modelo no cumple el contrato (tamaño, tipos o cota de desbordamiento)."""


def cuantizar(pesos, intercepto):
    if len(pesos) != len(esquema.NOMBRES):
        raise ModeloInvalido(f"se esperaban {len(esquema.NOMBRES)} pesos")
    for v in list(pesos) + [intercepto]:
        if not math.isfinite(v):
            raise ModeloInvalido("peso no finito")
    return [int(round(w * S_W)) for w in pesos], int(round(intercepto * S_W))


def logit_entero(W, B, x):
    """z = Σ W_i·x_i + B con enteros exactos."""
    return sum(int(w) * int(v) for w, v in zip(W, x)) + int(B)


def logit_de_entero(z):
    return z / S_W


def sigmoide(t):
    if t >= 0:
        return 1.0 / (1.0 + math.exp(-t))
    e = math.exp(t)
    return e / (1.0 + e)


def cota_error_logit(x):
    """Cota del error de cuantización frente al modelo en flotante para la entrada x:
    |Σ(W_i/S_W − w_i)·x_i + (B/S_W − b)| ≤ 0.5·(Σ|x_i| + 1)/S_W."""
    return 0.5 * (sum(abs(int(v)) for v in x) + 1) / S_W


COTA_MAXIMA_LOGIT = 0.5 * (sum(esquema.MAX_ABS) + 1) / S_W  # ≈ 1.03e-7 con los rangos del esquema


def verificar_desbordamiento(W, B, max_int):
    """Exige Σ M_i·|W_i| + |B| < max_int (M_i = máximo absoluto permitido de la variable i)."""
    if len(W) != len(esquema.MAX_ABS):
        raise ModeloInvalido("número de pesos distinto del esquema")
    if not all(isinstance(w, int) and not isinstance(w, bool) for w in list(W) + [B]):
        raise ModeloInvalido("los pesos cuantizados deben ser enteros")
    cota = sum(m * abs(w) for m, w in zip(esquema.MAX_ABS, W)) + abs(B)
    if cota >= max_int:
        raise ModeloInvalido(f"riesgo de desbordamiento: {cota} >= max_int")
    return cota
