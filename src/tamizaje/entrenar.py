"""Entrena la regresión logística sobre el CDC (UCI 891) y exporta el modelo del protocolo.

- Particiones: artefactos/particiones/cdc891_particiones_v1.json (se crean si no existen).
- Preprocesamiento (estandarización) ajustado solo con entrenamiento y plegado en pesos e intercepto,
  así el hospital manda los códigos enteros originales.
- Umbral fijado en validación (sensibilidad >= 0.80 con la mayor especificidad); prueba solo se usa para reportar.
- Exporta pesos flotantes y cuantizados (S_W = 10^9), esquema, umbral, versiones y hashes.

Uso: python -m tamizaje.entrenar
"""
import datetime, hashlib, json, math, platform, sys
import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, confusion_matrix, roc_auc_score, roc_curve
from sklearn.preprocessing import StandardScaler
from . import contrato, datos, esquema
from .rutas import METRICAS_MODELO, MODELO_JSON, PARTICIONES, asegurar_dirs

SENSIBILIDAD_OBJETIVO = 0.80
NOMBRE_MODELO = "logistico-cdc21-v1"


def ajustar(Xtr, ytr, class_weight=None):
    sc = StandardScaler().fit(Xtr.astype(float))
    lr = LogisticRegression(C=1.0, max_iter=5000, class_weight=class_weight)
    lr.fit(sc.transform(Xtr.astype(float)), ytr)
    coef = lr.coef_[0]
    w = coef / sc.scale_
    b = float(lr.intercept_[0] - np.sum(coef * sc.mean_ / sc.scale_))
    return sc, lr, w, b


def prob(X, w, b):
    z = X.astype(float) @ w + b
    return 1.0 / (1.0 + np.exp(-z))


def umbral_por_sensibilidad(y, p, objetivo=SENSIBILIDAD_OBJETIVO):
    fpr, tpr, thr = roc_curve(y, p)
    i = int(np.argmax(tpr >= objetivo))
    return float(thr[i])


def ece(y, p, bins=10):
    """Error de calibración esperado con 10 grupos de igual tamaño (cuantiles de p)."""
    orden = np.argsort(p)
    tabla, total = [], 0.0
    for g in np.array_split(orden, bins):
        mp, oy = float(p[g].mean()), float(y[g].mean())
        tabla.append({"n": int(len(g)), "p_media": round(mp, 4), "observado": round(oy, 4)})
        total += len(g) / len(p) * abs(mp - oy)
    return total, tabla


def metricas(y, p, umbral):
    pred = (p >= umbral).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    e, tabla = ece(y, p)
    return {
        "n": int(len(y)), "positivos": int(y.sum()), "prevalencia": round(float(y.mean()), 4),
        "roc_auc": round(float(roc_auc_score(y, p)), 4),
        "average_precision": round(float(average_precision_score(y, p)), 4),
        "sensibilidad": round(tp / (tp + fn), 4), "especificidad": round(tn / (tn + fp), 4),
        "vpp": round(tp / (tp + fp), 4) if tp + fp else None,
        "matriz_confusion": {"vn": int(tn), "fp": int(fp), "fn": int(fn), "vp": int(tp)},
        "brier": round(float(brier_score_loss(y, p)), 4), "p_media": round(float(p.mean()), 4),
        "ece_10_cuantiles": round(e, 4), "calibracion_por_decil": tabla,
    }


def main():
    asegurar_dirs()
    part = datos.guardar_particiones()
    ids, X, y = datos.cargar_cdc()
    Xtr, ytr, _ = datos.cargar_particion(part, "entrenamiento", ids, X, y)
    Xva, yva, _ = datos.cargar_particion(part, "validacion", ids, X, y)
    Xte, yte, _ = datos.cargar_particion(part, "prueba", ids, X, y)

    sc, lr, w, b = ajustar(Xtr, ytr)
    # El plegado debe reproducir la predicción de sklearn sobre los datos estandarizados.
    p_sk = lr.predict_proba(sc.transform(Xte.astype(float)))[:, 1]
    assert np.allclose(p_sk, prob(Xte, w, b), atol=1e-12), "el plegado de la estandarización no coincide"

    p_va, p_te = prob(Xva, w, b), prob(Xte, w, b)
    umbral = umbral_por_sensibilidad(yva, p_va)
    W, B = contrato.cuantizar(w.tolist(), b)

    # Flotante vs. punto fijo en todo prueba (aritmética entera exacta).
    z_int = np.array([contrato.logit_entero(W, B, x) for x in Xte.tolist()], dtype=object)
    logit_q = np.array([int(z) / contrato.S_W for z in z_int], dtype=float)
    logit_f = Xte.astype(float) @ w + b
    err = np.abs(logit_q - logit_f)
    cotas = np.array([contrato.cota_error_logit(x) for x in Xte.tolist()])
    p_q = 1.0 / (1.0 + np.exp(-logit_q))

    # Efecto de class_weight="balanced" sobre la calibración (no se usa en el modelo exportado).
    _, _, wb, bb = ajustar(Xtr, ytr, class_weight="balanced")
    p_te_bal = prob(Xte, wb, bb)
    umbral_bal = umbral_por_sensibilidad(yva, prob(Xva, wb, bb))

    # Duplicados: filas idénticas (sin ID) y sensibilidad entrenando sin duplicados.
    filas = np.hstack([X, y[:, None]])
    _, cuenta = np.unique(filas, axis=0, return_counts=True)
    dup_total = int((cuenta - 1).sum())
    tr_set = {tuple(r) for r in np.hstack([Xtr, ytr[:, None]]).tolist()}
    te_en_tr = int(sum(tuple(r) in tr_set for r in np.hstack([Xte, yte[:, None]]).tolist()))
    Xtr_u, idx = np.unique(np.hstack([Xtr, ytr[:, None]]), axis=0, return_index=True)
    _, _, wd, bd = ajustar(Xtr[np.sort(idx)], ytr[np.sort(idx)])
    p_te_dedup = prob(Xte, wd, bd)

    ahora = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    modelo = {
        "modelo": NOMBRE_MODELO, "esquema": esquema.como_dict(), "variables": esquema.NOMBRES,
        "pesos_flotantes": [float(v) for v in w], "intercepto_flotante": b,
        "escala_pesos": contrato.S_W, "pesos_enteros": W, "intercepto_entero": B, "exponente": contrato.EXPONENTE,
        "umbral": {"probabilidad": umbral, "logit": math.log(umbral / (1 - umbral)),
                   "criterio": f"sensibilidad >= {SENSIBILIDAD_OBJETIVO} en validación con la mayor especificidad"},
        "medias_entrenamiento": [float(v) for v in sc.mean_],
        "entrenamiento": {
            "datos": "CDC Diabetes Health Indicators (UCI 891)", "datos_sha256": part["fuente_sha256"],
            "particiones": "artefactos/particiones/cdc891_particiones_v1.json", "particiones_sha256": datos.sha256(PARTICIONES),
            "semilla": datos.SEMILLA, "algoritmo": "LogisticRegression(lbfgs, C=1.0, max_iter=5000, class_weight=None) sobre variables estandarizadas; estandarización plegada en pesos e intercepto",
            "python": platform.python_version(), "numpy": np.__version__, "scikit_learn": sklearn.__version__,
            "plataforma": f"{platform.system()} {platform.machine()}", "fecha_utc": ahora,
        },
    }
    with open(MODELO_JSON, "w") as f:
        json.dump(modelo, f, ensure_ascii=False, indent=1)
    modelo_sha = datos.sha256(MODELO_JSON)

    met = {
        "modelo": NOMBRE_MODELO, "modelo_sha256": modelo_sha, "fecha_utc": ahora, "entorno": modelo["entrenamiento"]["plataforma"],
        "definiciones": {
            "average_precision": "sklearn.metrics.average_precision_score: suma de precisiones ponderada por el incremento de recall (no es el área trapezoidal bajo la curva PR)",
            "umbral": modelo["umbral"]["criterio"], "ece": "error de calibración esperado, 10 grupos de igual tamaño",
        },
        "umbral_probabilidad": round(umbral, 6),
        "validacion": metricas(yva, p_va, umbral), "prueba": metricas(yte, p_te, umbral),
        "cuantizacion_en_prueba": {
            "n": int(len(yte)), "escala_pesos": contrato.S_W,
            "error_max_logit": float(err.max()), "error_medio_logit": float(err.mean()),
            "cota_max_aplicable": float(cotas.max()), "todas_dentro_de_cota": bool(np.all(err <= cotas)),
            "error_max_probabilidad": float(np.abs(p_q - p_te).max()),
            "roc_auc_flotante": round(float(roc_auc_score(yte, p_te)), 6), "roc_auc_punto_fijo": round(float(roc_auc_score(yte, p_q)), 6),
            "decisiones_distintas_en_umbral": int(np.sum((p_q >= umbral) != (p_te >= umbral))),
        },
        "class_weight_balanced": {
            "nota": "Con class_weight='balanced' las probabilidades se inflan hacia la clase positiva; el ranking casi no cambia. Por eso el modelo exportado no lo usa y el umbral se fija en validación.",
            "prueba": metricas(yte, p_te_bal, umbral_bal), "umbral_validacion": round(umbral_bal, 6),
        },
        "duplicados": {
            "filas_repetidas_sin_id_en_todo_el_cdc": dup_total,
            "filas_de_prueba_con_copia_identica_en_entrenamiento": te_en_tr,
            "nota": "Pueden ser respuestas idénticas de personas distintas (variables categóricas), no necesariamente personas duplicadas.",
            "sensibilidad_entrenando_sin_duplicados": {"filas_entrenamiento": int(len(idx)), "prueba": metricas(yte, p_te_dedup, umbral_por_sensibilidad(yva, prob(Xva, wd, bd)))},
        },
        "xgboost": "pendiente: subordinado a terminar y verificar la logística (no se entrenó)",
    }
    with open(METRICAS_MODELO, "w") as f:
        json.dump(met, f, ensure_ascii=False, indent=1)
    t = met["prueba"]
    print(f"modelo {modelo_sha[:12]} · prueba: ROC-AUC {t['roc_auc']} · AP {t['average_precision']} · sens {t['sensibilidad']} · esp {t['especificidad']} · Brier {t['brier']} · umbral {umbral:.4f}")
    print("cuantización:", met["cuantizacion_en_prueba"])


if __name__ == "__main__":
    main()
