"""Pruebas obligatorias del protocolo Paillier (fase 3)."""
import copy, json, random
import pytest
from phe.paillier import PaillierPrivateKey
from tamizaje import contrato, esquema, protocolo
from tamizaje.protocolo import MensajeInvalido


def registro(x):
    return dict(zip(esquema.NOMBRES, x))


def ida_y_vuelta(h, s, x):
    sol, xv = h.preparar(registro(x))
    z, _ = h.descifrar(s.evaluar(sol))
    return z, xv


def muestra_valida(n, semilla=7):
    rnd = random.Random(semilla)
    return [[rnd.randint(lo, hi) for _, lo, hi in esquema.VARIABLES] for _ in range(n)]


# a) el entero descifrado es idéntico a la referencia entera (error cero)
def test_a_entero_identico(hospital, servicio, modelo):
    for x in muestra_valida(40):
        z, xv = ida_y_vuelta(hospital, servicio, x)
        assert z == contrato.logit_entero(modelo["pesos_enteros"], modelo["intercepto_entero"], xv)


# b) error frente al modelo flotante dentro de la cota justificada
def test_b_error_dentro_de_cota(hospital, servicio, modelo):
    for x in muestra_valida(40, semilla=11):
        z, xv = ida_y_vuelta(hospital, servicio, x)
        flotante = sum(w * v for w, v in zip(modelo["pesos_flotantes"], xv)) + modelo["intercepto_flotante"]
        assert abs(contrato.logit_de_entero(z) - flotante) <= contrato.cota_error_logit(xv)
    assert contrato.COTA_MAXIMA_LOGIT < 1.1e-7


# c) coeficientes negativos, ceros, extremos y entradas inválidas
def test_c_negativos_ceros_y_extremos(modelo, llaves):
    W = [0, -7, 3, -1_000_000_000_000, 5, 0, 1, -1, 2, 0, -3, 4, 0, 9, -2, 1, 0, -5, 6, -4, 8]
    m = copy.deepcopy(modelo); m["pesos_enteros"], m["intercepto_entero"] = W, -123456789
    h = protocolo.Hospital(m, llaves=llaves)
    s = protocolo.ServicioRiesgo(protocolo.ModeloCuantizado.desde_json(m))
    for x in ([lo for _, lo, _ in esquema.VARIABLES], [hi for _, _, hi in esquema.VARIABLES]):
        z, xv = ida_y_vuelta(h, s, x)
        assert z == contrato.logit_entero(W, -123456789, xv)
    assert any(w < 0 for w in modelo["pesos_enteros"]), "el modelo real tiene coeficientes negativos"


def test_c_todos_ceros(modelo, llaves):
    m = copy.deepcopy(modelo); m["pesos_enteros"], m["intercepto_entero"] = [0] * 21, 0
    h = protocolo.Hospital(m, llaves=llaves)
    s = protocolo.ServicioRiesgo(protocolo.ModeloCuantizado.desde_json(m))
    z, _ = ida_y_vuelta(h, s, muestra_valida(1)[0])
    assert z == 0


def test_c_desbordamiento_rechazado(modelo, llaves):
    pub = llaves[0]
    W = [0] * 21; W[3] = pub.max_int // 98  # BMI: 98·W ≈ max_int, más el intercepto se pasa
    with pytest.raises(contrato.ModeloInvalido):
        contrato.verificar_desbordamiento(W, 10 ** 6, pub.max_int)
    m = copy.deepcopy(modelo); m["pesos_enteros"], m["intercepto_entero"] = W, 10 ** 6
    with pytest.raises(contrato.ModeloInvalido):
        protocolo.Hospital(m, llaves=llaves)


@pytest.mark.parametrize("cambio", [{"BMI": 30.5}, {"BMI": float("nan")}, {"Age": 14}, {"HighBP": None}])
def test_c_entrada_invalida_no_se_cifra(hospital, cambio):
    r = registro(muestra_valida(1)[0]); r.update(cambio)
    with pytest.raises(esquema.EntradaInvalida):
        hospital.preparar(r)


def test_c_mensajes_alterados_rechazados(hospital, servicio):
    sol, _ = hospital.preparar(registro(muestra_valida(1)[0]))
    casos = []
    for campo, valor in [("protocolo", "otro"), ("modelo", "otro"), ("esquema", "otro"), ("exponente", -2), ("id", "x")]:
        c = copy.deepcopy(sol); c[campo] = valor; casos.append(c)
    c = copy.deepcopy(sol); c["cifrados"] = c["cifrados"][:20]; casos.append(c)
    c = copy.deepcopy(sol); c["cifrados"][0] = "0"; casos.append(c)
    c = copy.deepcopy(sol); c["cifrados"][0] = str(int(sol["llave_publica"]["n"]) ** 2); casos.append(c)
    c = copy.deepcopy(sol); c["llave_publica"] = {"n": str(2 ** 1023 + 1)}; casos.append(c)
    c = copy.deepcopy(sol); c["extra"] = 1; casos.append(c)
    for c in casos:
        with pytest.raises(MensajeInvalido):
            servicio.evaluar(c)


def test_c_hospital_no_es_oraculo(hospital, servicio):
    sol, _ = hospital.preparar(registro(muestra_valida(1)[0]))
    resp = servicio.evaluar(sol)
    falsa = dict(resp, id="f" * 32)
    with pytest.raises(MensajeInvalido):
        hospital.descifrar(falsa)
    hospital.descifrar(resp)
    with pytest.raises(MensajeInvalido):  # no se descifra dos veces
        hospital.descifrar(resp)


def test_c_resultado_realeatorizado(hospital, servicio):
    x = muestra_valida(1)[0]
    s1, _ = hospital.preparar(registro(x)); s2, _ = hospital.preparar(registro(x))
    r1, r2 = servicio.evaluar(s1), servicio.evaluar(s2)
    assert r1["resultado"] != r2["resultado"]
    assert hospital.descifrar(r1)[0] == hospital.descifrar(r2)[0]


# d) predicción coherente después de exportar y recargar el modelo
def test_d_exportar_y_recargar(tmp_path, modelo, llaves, servicio):
    p = tmp_path / "modelo.json"
    p.write_text(json.dumps(modelo))
    m2 = json.loads(p.read_text())
    h2 = protocolo.Hospital(m2, llaves=llaves)
    s2 = protocolo.ServicioRiesgo(protocolo.ModeloCuantizado.desde_json(m2))
    for x in muestra_valida(5, semilla=3):
        za, _ = ida_y_vuelta(h2, s2, x)
        assert za == contrato.logit_entero(modelo["pesos_enteros"], modelo["intercepto_entero"], x)
        assert h2.interpretar(za, x)["probabilidad"] == pytest.approx(contrato.sigmoide(za / contrato.S_W), abs=0)


# e) el servicio de riesgo no tiene llave privada
def test_e_servicio_sin_llave_privada(servicio):
    vistos = set()

    def buscar(o, prof=0):
        if id(o) in vistos or prof > 6:
            return
        vistos.add(id(o))
        assert not isinstance(o, PaillierPrivateKey)
        for v in (vars(o).values() if hasattr(o, "__dict__") else (o.values() if isinstance(o, dict) else (o if isinstance(o, (list, tuple)) else []))):
            buscar(v, prof + 1)
    buscar(servicio)
    import inspect
    fuente = inspect.getsource(protocolo.ServicioRiesgo)
    assert "_priv" not in fuente and "PrivateKey" not in fuente and "decrypt" not in fuente


# F11: el servicio solo acepta el formato que genera el hospital
def test_f11_id_llave_y_tamanos(hospital, servicio):
    sol, _ = hospital.preparar(registro(muestra_valida(1)[0]))
    casos = []
    c = copy.deepcopy(sol); c["id"] = "Paciente: Juan Pérez\n"; casos.append(c)
    c = copy.deepcopy(sol); c["id"] = "A" * 32; casos.append(c)
    c = copy.deepcopy(sol); c["llave_publica"] = {"n": str(2 ** 5000 + 1)}; casos.append(c)
    c = copy.deepcopy(sol); c["llave_publica"] = {"n": sol["llave_publica"]["n"], "g": "2"}; casos.append(c)
    c = copy.deepcopy(sol); c["llave_publica"] = {"n": int(sol["llave_publica"]["n"])}; casos.append(c)
    c = copy.deepcopy(sol); c["cifrados"][0] = "1" * 5000; casos.append(c)
    for c in casos:
        with pytest.raises(MensajeInvalido):
            servicio.evaluar(c)
    assert protocolo.ID_VALIDO.match(sol["id"])
