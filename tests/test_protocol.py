"Required Paillier protocol correctness tests."
import copy, json, random
import pytest
from phe.paillier import PaillierPrivateKey
from screening import contract, schema, protocol
from screening.protocol import InvalidMessage


def record(x):
    return dict(zip(schema.FEATURE_NAMES, x))


def round_trip(h, s, x):
    sol, xv = h.prepare(record(x))
    z, _ = h.decrypt(s.evaluate(sol))
    return z, xv


def valid_sample(n, seed=7):
    rnd = random.Random(seed)
    return [[rnd.randint(what, hi) for _, what, hi in schema.VARIABLES] for _ in range(n)]


# a) Decrypted integer equals the exact integer reference.
def test_a_integer_identical(hospital, service, model):
    for x in valid_sample(40):
        z, xv = round_trip(hospital, service, x)
        assert z == contract.logit_integer(model["weights_integers"], model["intercept_integer"], xv)


# b) Floating-point error stays within the derived bound.
def test_b_error_within_of_bound(hospital, service, model):
    for x in valid_sample(40, seed=11):
        z, xv = round_trip(hospital, service, x)
        floating = sum(w * v for w, v in zip(model["weights_floating"], xv)) + model["intercept_floating"]
        assert abs(contract.logit_from_integer(z) - floating) <= contract.logit_error_bound(xv)
    assert contract.MAX_LOGIT_BOUND < 1.1e-7


# c) Negative/zero weights, extreme values and invalid inputs
def test_c_negative_zeros_and_extreme(model, keys):
    W = [0, -7, 3, -1_000_000_000_000, 5, 0, 1, -1, 2, 0, -3, 4, 0, 9, -2, 1, 0, -5, 6, -4, 8]
    m = copy.deepcopy(model); m["weights_integers"], m["intercept_integer"] = W, -123456789
    h = protocol.hospital(m, keys=keys)
    s = protocol.RiskService(protocol.QuantizedModel.from_json(m))
    for x in ([what for _, what, _ in schema.VARIABLES], [hi for _, _, hi in schema.VARIABLES]):
        z, xv = round_trip(h, s, x)
        assert z == contract.logit_integer(W, -123456789, xv)
    assert any(w < 0 for w in model["weights_integers"]), "the actual model contains negative coefficients"


def test_c_all_zeros(model, keys):
    m = copy.deepcopy(model); m["weights_integers"], m["intercept_integer"] = [0] * 21, 0
    h = protocol.hospital(m, keys=keys)
    s = protocol.RiskService(protocol.QuantizedModel.from_json(m))
    z, _ = round_trip(h, s, valid_sample(1)[0])
    assert z == 0


def test_c_overflow_rejected(model, keys):
    pub = keys[0]
    W = [0] * 21; W[3] = pub.max_int // 98  # BMI: 98 * W approaches max_int; adding the intercept overflows.
    with pytest.raises(contract.InvalidModel):
        contract.verify_overflow(W, 10 ** 6, pub.max_int)
    m = copy.deepcopy(model); m["weights_integers"], m["intercept_integer"] = W, 10 ** 6
    with pytest.raises(contract.InvalidModel):
        protocol.hospital(m, keys=keys)


@pytest.mark.parametrize("change", [{"BMI": 30.5}, {"BMI": float("nan")}, {"Age": 14}, {"HighBP": None}])
def test_c_input_invalid_does_not_self_encrypts(hospital, change):
    r = record(valid_sample(1)[0]); r.update(change)
    with pytest.raises(schema.InvalidInput):
        hospital.prepare(r)


def test_c_messages_tampered_rejected(hospital, service):
    sol, _ = hospital.prepare(record(valid_sample(1)[0]))
    cases = []
    for field, value in [("protocol", "other"), ("model", "other"), ("schema", "other"), ("exponent", -2), ("id", "x")]:
        c = copy.deepcopy(sol); c[field] = value; cases.append(c)
    c = copy.deepcopy(sol); c["ciphertexts"] = c["ciphertexts"][:20]; cases.append(c)
    c = copy.deepcopy(sol); c["ciphertexts"][0] = "0"; cases.append(c)
    c = copy.deepcopy(sol); c["ciphertexts"][0] = str(int(sol["key_public"]["n"]) ** 2); cases.append(c)
    c = copy.deepcopy(sol); c["key_public"] = {"n": str(2 ** 1023 + 1)}; cases.append(c)
    c = copy.deepcopy(sol); c["extra"] = 1; cases.append(c)
    for c in cases:
        with pytest.raises(InvalidMessage):
            service.evaluate(c)


def test_c_hospital_does_not_is_oracle(hospital, service):
    sol, _ = hospital.prepare(record(valid_sample(1)[0]))
    resp = service.evaluate(sol)
    false = dict(resp, id="f" * 32)
    with pytest.raises(InvalidMessage):
        hospital.decrypt(false)
    hospital.decrypt(resp)
    with pytest.raises(InvalidMessage):  # A response cannot be decrypted twice.
        hospital.decrypt(resp)


def test_c_result_rerandomized(hospital, service):
    x = valid_sample(1)[0]
    s1, _ = hospital.prepare(record(x)); s2, _ = hospital.prepare(record(x))
    r1, r2 = service.evaluate(s1), service.evaluate(s2)
    assert r1["result"] != r2["result"]
    assert hospital.decrypt(r1)[0] == hospital.decrypt(r2)[0]


# d) Predictions remain consistent after export and reload.
def test_d_export_and_reload(tmp_path, model, keys, service):
    p = tmp_path / "model.json"
    p.write_text(json.dumps(model))
    m2 = json.loads(p.read_text())
    h2 = protocol.hospital(m2, keys=keys)
    s2 = protocol.RiskService(protocol.QuantizedModel.from_json(m2))
    for x in valid_sample(5, seed=3):
        za, _ = round_trip(h2, s2, x)
        assert za == contract.logit_integer(model["weights_integers"], model["intercept_integer"], x)
        assert h2.interpret(za, x)["probability"] == pytest.approx(contract.sigmoid(za / contract.S_W), abs=0)


# e) The risk service has no private key.
def test_e_service_without_key_private(service):
    seen = set()

    def find(o, prof=0):
        if id(o) in seen or prof > 6:
            return
        seen.add(id(o))
        assert not isinstance(o, PaillierPrivateKey)
        for v in (vars(o).values() if hasattr(o, "__dict__") else (o.values() if isinstance(o, dict) else (o if isinstance(o, (list, tuple)) else []))):
            find(v, prof + 1)
    find(service)
    import inspect
    source = inspect.getsource(protocol.RiskService)
    assert "_priv" not in source and "PrivateKey" not in source and "decrypt" not in source


# F11: Accept only the exact request format generated by the hospital.
def test_f11_id_key_and_sizes(hospital, service):
    sol, _ = hospital.prepare(record(valid_sample(1)[0]))
    cases = []
    c = copy.deepcopy(sol); c["id"] = """Patient: Test Person
"""; cases.append(c)
    c = copy.deepcopy(sol); c["id"] = "TO" * 32; cases.append(c)
    c = copy.deepcopy(sol); c["key_public"] = {"n": str(2 ** 5000 + 1)}; cases.append(c)
    c = copy.deepcopy(sol); c["key_public"] = {"n": sol["key_public"]["n"], "g": "2"}; cases.append(c)
    c = copy.deepcopy(sol); c["key_public"] = {"n": int(sol["key_public"]["n"])}; cases.append(c)
    c = copy.deepcopy(sol); c["ciphertexts"][0] = "1" * 5000; cases.append(c)
    for c in cases:
        with pytest.raises(InvalidMessage):
            service.evaluate(c)
    assert protocol.VALID_ID.match(sol["id"])


def test_r3_id_with_break_of_line_final_rejected(hospital, service):
    sol, _ = hospital.prepare(record(valid_sample(1)[0]))
    c = copy.deepcopy(sol); c["id"] = sol["id"] + "\n"
    with pytest.raises(InvalidMessage):
        service.evaluate(c)
    assert protocol.VALID_ID.fullmatch("a" * 32 + "\n") is None
