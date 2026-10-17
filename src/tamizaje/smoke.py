"""Prueba de humo contra la demo levantada: estado del servicio y un recorrido real por perfil sintético.

Comprueba que el entero descifrado coincide exactamente con la referencia entera del modelo.
Uso: python -m tamizaje.smoke [http://127.0.0.1:8080]
"""
import json, sys, time, urllib.request
from . import contrato, sinteticos
from .rutas import MODELO_JSON


def pedir(url, cuerpo=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(url, data=datos, headers={"Content-Type": "application/json"} if datos else {})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def main(base="http://127.0.0.1:8080"):
    modelo = json.load(open(MODELO_JSON))
    for _ in range(30):
        try:
            estado = pedir(base + "/api/estado")
            if estado["servicio"].get("estado") == "ok":
                break
        except OSError:
            pass
        time.sleep(1)
    else:
        sys.exit("la demo no respondió en 30 s")
    assert estado["servicio"]["llave_privada"] is False
    print(f"servicio ok · máquina {estado['maquina']} · llave {estado['llave_bits']} bits")
    for perfil, p in sinteticos.PERFILES.items():
        r = pedir(base + "/api/evaluar", {"perfil": perfil})
        x = [p[n] for n in modelo["variables"]]
        ref = contrato.logit_entero(modelo["pesos_enteros"], modelo["intercepto_entero"], x)
        assert int(r["hospital"]["z_entero"]) == ref, "el entero descifrado no coincide"
        print(f"{perfil}: p={r['hospital']['probabilidad']:.3f} · z exacto · {r['tiempos_ms']['total']} ms")
    print("smoke OK")


if __name__ == "__main__":
    main(*sys.argv[1:])
