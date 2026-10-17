"""Protocolo Paillier del tamizaje: el hospital cifra y descifra; el servicio de riesgo solo opera sobre cifrados.

Mensajes versionados (JSON):
  solicitud  = {protocolo, esquema, modelo, id, llave_publica: {n}, exponente: 0, cifrados: [21 enteros como texto]}
  respuesta  = {protocolo, esquema, modelo, id, exponente: 0, resultado: entero como texto}

El servicio valida estructura y compatibilidad (versiones, tamaño de llave, rango de cada cifrado);
no puede inspeccionar los valores que van cifrados.
"""
import math, secrets
from phe import paillier
from phe.paillier import EncryptedNumber, PaillierPublicKey
from . import contrato, esquema

PROTOCOLO = "tamizaje-paillier-v1"
BITS_LLAVE = 2048
BITS_LLAVE_MIN = 2048


class MensajeInvalido(ValueError):
    """La solicitud o la respuesta no cumple el protocolo."""


class ModeloCuantizado:
    """Lo único que necesita el servicio de riesgo: pesos enteros, intercepto entero y versiones."""

    def __init__(self, nombre, version_esquema, W, B):
        if version_esquema != esquema.VERSION:
            raise contrato.ModeloInvalido(f"esquema {version_esquema} distinto de {esquema.VERSION}")
        if len(W) != len(esquema.NOMBRES):
            raise contrato.ModeloInvalido("número de pesos distinto del esquema")
        self.nombre, self.esquema, self.W, self.B = nombre, version_esquema, [int(w) for w in W], int(B)

    @classmethod
    def desde_json(cls, m):
        if m.get("exponente") != contrato.EXPONENTE or m.get("escala_pesos") != contrato.S_W:
            raise contrato.ModeloInvalido("exponente o escala distintos del contrato")
        if m.get("variables") != esquema.NOMBRES:
            raise contrato.ModeloInvalido("variables u orden distintos del esquema")
        return cls(m["modelo"], m["esquema"]["version"], m["pesos_enteros"], m["intercepto_entero"])


# ---------------------------------------------------------------- servicio de riesgo (sin llave privada)

class ServicioRiesgo:
    def __init__(self, modelo: ModeloCuantizado, bits_min=BITS_LLAVE_MIN):
        self.modelo, self.bits_min = modelo, bits_min

    def _validar(self, sol):
        if not isinstance(sol, dict):
            raise MensajeInvalido("la solicitud debe ser un objeto")
        esperado = {"protocolo", "esquema", "modelo", "id", "llave_publica", "exponente", "cifrados"}
        if set(sol) != esperado:
            raise MensajeInvalido(f"campos esperados {sorted(esperado)}")
        if sol["protocolo"] != PROTOCOLO:
            raise MensajeInvalido("versión de protocolo no soportada")
        if sol["esquema"] != self.modelo.esquema or sol["modelo"] != self.modelo.nombre:
            raise MensajeInvalido("esquema o modelo incompatibles")
        if sol["exponente"] != contrato.EXPONENTE:
            raise MensajeInvalido("exponente distinto de 0")
        if not isinstance(sol["id"], str) or not 8 <= len(sol["id"]) <= 64:
            raise MensajeInvalido("id inválido")
        try:
            n = int(sol["llave_publica"]["n"])
        except (KeyError, TypeError, ValueError):
            raise MensajeInvalido("llave pública inválida")
        if n.bit_length() < self.bits_min or n % 2 == 0:
            raise MensajeInvalido(f"llave pública menor a {self.bits_min} bits o inválida")
        cif = sol["cifrados"]
        if not isinstance(cif, list) or len(cif) != len(esquema.NOMBRES):
            raise MensajeInvalido(f"se esperaban {len(esquema.NOMBRES)} cifrados")
        n2 = n * n
        valores = []
        for c in cif:
            if not isinstance(c, str) or not c.isdigit():
                raise MensajeInvalido("cifrado no es un entero en texto")
            v = int(c)
            if not 0 < v < n2 or math.gcd(v, n) != 1:
                raise MensajeInvalido("cifrado fuera del grupo de la llave")
            valores.append(v)
        return PaillierPublicKey(n), valores

    def evaluar(self, sol):
        pub, valores = self._validar(sol)
        contrato.verificar_desbordamiento(self.modelo.W, self.modelo.B, pub.max_int)
        acc = None
        for v, w in zip(valores, self.modelo.W):
            if w == 0:
                continue
            t = EncryptedNumber(pub, v, contrato.EXPONENTE) * w
            acc = t if acc is None else acc + t
        acc = (acc + self.modelo.B) if acc is not None else pub.encrypt(self.modelo.B)
        acc.obfuscate()  # re-aleatoriza antes de transmitir
        assert acc.exponent == contrato.EXPONENTE
        return {"protocolo": PROTOCOLO, "esquema": self.modelo.esquema, "modelo": self.modelo.nombre,
                "id": sol["id"], "exponente": contrato.EXPONENTE, "resultado": str(acc.ciphertext(be_secure=False))}


# ---------------------------------------------------------------- hospital (tiene la llave privada)

class Hospital:
    def __init__(self, modelo_json, bits=BITS_LLAVE, llaves=None):
        self.modelo_json = modelo_json
        self.cuantizado = ModeloCuantizado.desde_json(modelo_json)
        self.pub, self._priv = llaves if llaves else paillier.generate_paillier_keypair(n_length=bits)
        contrato.verificar_desbordamiento(self.cuantizado.W, self.cuantizado.B, self.pub.max_int)
        self._pendientes = {}

    def preparar(self, registro):
        """Valida el registro (dict de 21 variables), cifra cada entero y arma la solicitud."""
        x = esquema.validar(registro)
        cif = []
        for v in x:
            e = self.pub.encrypt(v)
            assert e.exponent == contrato.EXPONENTE
            cif.append(str(e.ciphertext(be_secure=True)))
        rid = secrets.token_hex(16)
        self._pendientes[rid] = x
        sol = {"protocolo": PROTOCOLO, "esquema": self.cuantizado.esquema, "modelo": self.cuantizado.nombre, "id": rid,
               "llave_publica": {"n": str(self.pub.n)}, "exponente": contrato.EXPONENTE, "cifrados": cif}
        return sol, x

    def descifrar(self, resp):
        """Descifra solo respuestas a solicitudes propias pendientes (una vez cada una): evita ser un oráculo."""
        if not isinstance(resp, dict) or resp.get("protocolo") != PROTOCOLO:
            raise MensajeInvalido("respuesta de otro protocolo")
        rid = resp.get("id")
        if rid not in self._pendientes:
            raise MensajeInvalido("respuesta sin solicitud pendiente")
        if resp.get("modelo") != self.cuantizado.nombre or resp.get("esquema") != self.cuantizado.esquema or resp.get("exponente") != contrato.EXPONENTE:
            raise MensajeInvalido("respuesta incompatible con la solicitud")
        x = self._pendientes.pop(rid)
        try:
            c = int(resp["resultado"])
        except (KeyError, TypeError, ValueError):
            raise MensajeInvalido("resultado inválido")
        if not 0 < c < self.pub.nsquare:
            raise MensajeInvalido("resultado fuera del grupo de la llave")
        z = self._priv.decrypt_encoded(EncryptedNumber(self.pub, c, contrato.EXPONENTE)).decode()
        return int(z), x

    def interpretar(self, z, x):
        m = self.modelo_json
        logit = contrato.logit_de_entero(z)
        p = contrato.sigmoide(logit)
        umbral = m["umbral"]["probabilidad"]
        contrib = [(n, w * (v - mu)) for n, w, v, mu in zip(esquema.NOMBRES, m["pesos_flotantes"], x, m["medias_entrenamiento"])]
        contrib.sort(key=lambda t: -abs(t[1]))
        return {"z_entero": str(z), "logit": logit, "probabilidad": p, "umbral": umbral,
                "riesgo_alto": p >= umbral, "factores": [{"variable": n, "aporte_logit": round(c, 3)} for n, c in contrib[:5]]}
