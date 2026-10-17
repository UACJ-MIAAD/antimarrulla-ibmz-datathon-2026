import json, os, sys
import pytest

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(RAIZ, "src"))

from tamizaje import protocolo  # noqa: E402
from tamizaje.rutas import MODELO_JSON  # noqa: E402
from phe import paillier  # noqa: E402


@pytest.fixture(scope="session")
def modelo():
    with open(MODELO_JSON) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def llaves():
    return paillier.generate_paillier_keypair(n_length=protocolo.BITS_LLAVE)


@pytest.fixture()
def hospital(modelo, llaves):
    return protocolo.Hospital(modelo, llaves=llaves)


@pytest.fixture(scope="session")
def servicio(modelo):
    return protocolo.ServicioRiesgo(protocolo.ModeloCuantizado.desde_json(modelo))
