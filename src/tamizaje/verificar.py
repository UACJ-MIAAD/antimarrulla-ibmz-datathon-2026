"""Verifica los artefactos sin modificarlos: hashes, esquema, contrato y reproducibilidad del entrenamiento.

Uso: python -m tamizaje.verificar
"""
import json, sys
import numpy as np
from . import contrato, datos, entrenar, esquema
from .rutas import METRICAS_MODELO, MODELO_JSON, PARTICIONES


def main():
    errores = []
    ok = lambda cond, msg: print(("  ok  " if cond else "  FALLA ") + msg) or (cond or errores.append(msg))
    m = json.load(open(MODELO_JSON)); met = json.load(open(METRICAS_MODELO)); part = json.load(open(PARTICIONES))
    ok(met["modelo_sha256"] == datos.sha256(MODELO_JSON), "hash del modelo coincide con el de las métricas")
    ok(m["entrenamiento"]["particiones_sha256"] == datos.sha256(PARTICIONES), "hash de las particiones coincide con el del modelo")
    ok(part["fuente_sha256"] == datos.sha256(datos.CDC_CSV), "hash del CSV del CDC coincide con el de las particiones")
    ok(m["variables"] == esquema.NOMBRES and m["esquema"]["version"] == esquema.VERSION, "esquema y orden de variables")
    ok((m["pesos_enteros"], m["intercepto_entero"]) == tuple(contrato.cuantizar(m["pesos_flotantes"], m["intercepto_flotante"])), "pesos cuantizados = round(10^9 · pesos)")
    n2048_max_int = (1 << 2047) // 3
    ok(contrato.verificar_desbordamiento(m["pesos_enteros"], m["intercepto_entero"], n2048_max_int) < n2048_max_int, "cota de desbordamiento con llave de 2048 bits (incluye intercepto)")
    ids = set(); total = 0
    for k, v in part["ids"].items():
        ids |= set(v); total += len(v)
    ok(len(ids) == total == 253680, "particiones disjuntas que cubren las 253,680 filas")

    ids_, X, y = datos.cargar_cdc()
    Xtr, ytr, _ = datos.cargar_particion(part, "entrenamiento", ids_, X, y)
    _, _, w, b = entrenar.ajustar(Xtr, ytr)
    dif = float(np.max(np.abs(np.array(w) - np.array(m["pesos_flotantes"])))); dif_b = abs(b - m["intercepto_flotante"])
    Xte, yte, _ = datos.cargar_particion(part, "prueba", ids_, X, y)
    auc_nuevo = entrenar.roc_auc_score(yte, entrenar.prob(Xte, w, b))
    print(f"        diferencia máxima de pesos {dif:.2e} · intercepto {dif_b:.2e} · ROC-AUC re-entrenado {auc_nuevo:.6f}")
    ok(dif < 1e-3 and dif_b < 1e-3 and abs(auc_nuevo - json.load(open(METRICAS_MODELO))["prueba"]["roc_auc"]) < 1e-3,
       "re-entrenamiento reproduce el modelo exportado (tolerancia 1e-3: el optimizador lbfgs puede variar entre versiones y arquitecturas)")
    if errores:
        sys.exit(f"{len(errores)} verificaciones fallaron")
    print("verificación OK")


if __name__ == "__main__":
    main()
