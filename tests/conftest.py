import json, os, sys
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

from screening import protocol  # noqa: E402
from screening.paths import MODEL_JSON  # noqa: E402
from phe import paillier  # noqa: E402


@pytest.fixture(scope="session")
def model():
    with open(MODEL_JSON) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def keys():
    return paillier.generate_paillier_keypair(n_length=protocol.KEY_BITS)


@pytest.fixture()
def hospital(model, keys):
    return protocol.hospital(model, keys=keys)


@pytest.fixture(scope="session")
def service(model):
    return protocol.RiskService(protocol.QuantizedModel.from_json(model))
