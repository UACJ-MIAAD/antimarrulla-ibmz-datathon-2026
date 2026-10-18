"""Paillier screening protocol: the hospital encrypts/decrypts; the risk service sees ciphertexts only.

Versioned JSON request: protocol, schema, model, id, key_public {n}, exponent 0, ciphertexts (one decimal string per schema feature).
Versioned response: protocol, schema, model, id, exponent 0, result (decimal ciphertext string).
Validate versions, structure, key size and ciphertext group membership. The service cannot inspect encrypted inputs.
The English wire format uses screening-paillier-v2; deploy both endpoints together.
"""
import math, re, secrets
from phe import paillier
from phe.paillier import EncryptedNumber, PaillierPublicKey
from . import contract, schema

PROTOCOL = "screening-paillier-v2"
KEY_BITS = 2048
MIN_KEY_BITS = 2048
MAX_KEY_BITS = 4096
VALID_ID = re.compile(r"[0-9a-f]{32}")  # Use fullmatch: exactly the 32 hex digits produced by the hospital prepare method.


class InvalidMessage(ValueError):
    "The request or response violates the protocol."


class QuantizedModel:
    "Service model containing integer weights, an integer intercept and version identifiers."

    def __init__(self, name, schema_version, W, B):
        if schema_version != schema.VERSION:
            raise contract.InvalidModel(f"schema {schema_version} differs from {schema.VERSION}")
        if len(W) != len(schema.FEATURE_NAMES):
            raise contract.InvalidModel("weight count differs from the schema")
        self.name, self.schema, self.W, self.B = name, schema_version, [int(w) for w in W], int(B)

    @classmethod
    def from_json(cls, m):
        if m.get("exponent") != contract.EXPONENT or m.get("weight_scale") != contract.S_W:
            raise contract.InvalidModel("exponent or scale differs from the contract")
        if m.get("variables") != schema.FEATURE_NAMES:
            raise contract.InvalidModel("feature names or order differ from the schema")
        return cls(m["model"], m["schema"]["version"], m["weights_integers"], m["intercept_integer"])


# ---------------------------------------------------------------- Risk service: no private key

class RiskService:
    def __init__(self, model: QuantizedModel, bits_min=MIN_KEY_BITS):
        self.model, self.bits_min = model, bits_min

    def _validate(self, sol):
        if not isinstance(sol, dict):
            raise InvalidMessage("the request must be an object")
        expected = {"protocol", "schema", "model", "id", "key_public", "exponent", "ciphertexts"}
        if set(sol) != expected:
            raise InvalidMessage(f"expected fields {sorted(expected)}")
        if sol["protocol"] != PROTOCOL:
            raise InvalidMessage("unsupported protocol version")
        if sol["schema"] != self.model.schema or sol["model"] != self.model.name:
            raise InvalidMessage("incompatible schema or model")
        if sol["exponent"] != contract.EXPONENT:
            raise InvalidMessage("exponent must equal zero")
        if not isinstance(sol["id"], str) or not VALID_ID.fullmatch(sol["id"]):
            raise InvalidMessage("invalid id: expected exactly 32 hexadecimal characters")
        lp = sol["key_public"]
        if not isinstance(lp, dict) or set(lp) != {"n"} or not isinstance(lp["n"], str) or not lp["n"].isdigit() or len(lp["n"]) > 1300:
            raise InvalidMessage("invalid public key")
        n = int(lp["n"])
        if not self.bits_min <= n.bit_length() <= MAX_KEY_BITS or n % 2 == 0:
            raise InvalidMessage(f"public key outside {self.bits_min}–{MAX_KEY_BITS} bits or invalid")
        ciphertexts = sol["ciphertexts"]
        if not isinstance(ciphertexts, list) or len(ciphertexts) != len(schema.FEATURE_NAMES):
            raise InvalidMessage(f"expected {len(schema.FEATURE_NAMES)} ciphertexts")
        n2 = n * n
        max_digits = len(str(n2))
        values = []
        for c in ciphertexts:
            if not isinstance(c, str) or not c.isdigit() or len(c) > max_digits:
                raise InvalidMessage("ciphertext must be a decimal integer string")
            v = int(c)
            if not 0 < v < n2 or math.gcd(v, n) != 1:
                raise InvalidMessage("ciphertext is outside the public-key group")
            values.append(v)
        return PaillierPublicKey(n), values

    def evaluate(self, sol):
        pub, values = self._validate(sol)
        contract.verify_overflow(self.model.W, self.model.B, pub.max_int)
        acc = None
        for v, w in zip(values, self.model.W):
            if w == 0:
                continue
            t = EncryptedNumber(pub, v, contract.EXPONENT) * w
            acc = t if acc is None else acc + t
        acc = (acc + self.model.B) if acc is not None else pub.encrypt(self.model.B)
        acc.obfuscate()  # Rerandomize before transmission.
        assert acc.exponent == contract.EXPONENT
        return {"protocol": PROTOCOL, "schema": self.model.schema, "model": self.model.name,
                "id": sol["id"], "exponent": contract.EXPONENT, "result": str(acc.ciphertext(be_secure=False))}


# ---------------------------------------------------------------- Hospital: owns the private key

class hospital:
    def __init__(self, model_json, bits=KEY_BITS, keys=None):
        self.model_json = model_json
        self.quantized = QuantizedModel.from_json(model_json)
        self.pub, self._priv = keys if keys else paillier.generate_paillier_keypair(n_length=bits)
        contract.verify_overflow(self.quantized.W, self.quantized.B, self.pub.max_int)
        self._pending = {}

    def prepare(self, record):
        "Validate the schema record, encrypt every integer and build the request."
        x = schema.validate(record)
        ciphertexts = []
        for v in x:
            e = self.pub.encrypt(v)
            assert e.exponent == contract.EXPONENT
            ciphertexts.append(str(e.ciphertext(be_secure=True)))
        rid = secrets.token_hex(16)
        self._pending[rid] = x
        sol = {"protocol": PROTOCOL, "schema": self.quantized.schema, "model": self.quantized.name, "id": rid,
               "key_public": {"n": str(self.pub.n)}, "exponent": contract.EXPONENT, "ciphertexts": ciphertexts}
        return sol, x

    def decrypt(self, resp):
        "Decrypt each outstanding hospital request at most once; reject unsolicited responses."
        if not isinstance(resp, dict) or resp.get("protocol") != PROTOCOL:
            raise InvalidMessage("response uses a different protocol")
        rid = resp.get("id")
        if rid not in self._pending:
            raise InvalidMessage("response has no pending request")
        if resp.get("model") != self.quantized.name or resp.get("schema") != self.quantized.schema or resp.get("exponent") != contract.EXPONENT:
            raise InvalidMessage("response is incompatible with the request")
        x = self._pending.pop(rid)
        try:
            c = int(resp["result"])
        except (KeyError, TypeError, ValueError):
            raise InvalidMessage("invalid result")
        if not 0 < c < self.pub.nsquare:
            raise InvalidMessage("result is outside the public-key group")
        z = self._priv.decrypt_encoded(EncryptedNumber(self.pub, c, contract.EXPONENT)).decode()
        return int(z), x

    def interpret(self, z, x):
        m = self.model_json
        logit = contract.logit_from_integer(z)
        p = contract.sigmoid(logit)
        threshold = m["threshold"]["probability"]
        contribution = [(n, w * (v - mu)) for n, w, v, mu in zip(schema.FEATURE_NAMES, m["weights_floating"], x, m["means_training"])]
        contribution.sort(key=lambda t: -abs(t[1]))
        return {"z_integer": str(z), "logit": logit, "probability": p, "threshold": threshold,
                "risk_high": p >= threshold, "factors": [{"variable": n, "contribution_logit": round(c, 3)} for n, c in contribution[:5]]}
