"""Numerical contract (docs/PROJECT.md).
Inputs are the schema's unscaled integer CDC codes (19 in cdc19-v1) (input scale 1).
W_i=round(10^9*w_i), B=round(10^9*b). Paillier exponent is zero throughout.
Reference arithmetic uses exact Python integers.
"""
import math
from . import schema

S_W = 10 ** 9
EXPONENT = 0


class InvalidModel(ValueError):
    "Model violates the size, type or overflow contract."


def quantize(weights, intercept):
    if len(weights) != len(schema.FEATURE_NAMES):
        raise InvalidModel(f"expected {len(schema.FEATURE_NAMES)} pesos")
    for v in list(weights) + [intercept]:
        if not math.isfinite(v):
            raise InvalidModel("non-finite weight")
    return [int(round(w * S_W)) for w in weights], int(round(intercept * S_W))


def logit_integer(W, B, x):
    "Compute z = sum(W_i*x_i) + B using exact integers."
    return sum(int(w) * int(v) for w, v in zip(W, x)) + int(B)


def logit_from_integer(z):
    return z / S_W


def sigmoid(t):
    if t >= 0:
        return 1.0 / (1.0 + math.exp(-t))
    e = math.exp(t)
    return e / (1.0 + e)


def logit_error_bound(x):
    "Floating-point quantization error bound: abs(sum((W_i/S_W-w_i)*x_i)+(B/S_W-b)) <= 0.5*(sum(abs(x_i))+1)/S_W."
    return 0.5 * (sum(abs(int(v)) for v in x) + 1) / S_W


MAX_LOGIT_BOUND = 0.5 * (sum(schema.MAX_ABS) + 1) / S_W  # Approximately 1.03e-7 at the schema limits


def verify_overflow(W, B, max_int):
    "Require sum(M_i*abs(W_i))+abs(B) < max_int for allowed feature maxima M_i."
    if len(W) != len(schema.MAX_ABS):
        raise InvalidModel("weight count differs from the schema")
    if not all(isinstance(w, int) and not isinstance(w, bool) for w in list(W) + [B]):
        raise InvalidModel("quantized weights must be integers")
    bound = sum(m * abs(w) for m, w in zip(schema.MAX_ABS, W)) + abs(B)
    if bound >= max_int:
        raise InvalidModel(f"overflow risk: {bound} >= max_int")
    return bound
