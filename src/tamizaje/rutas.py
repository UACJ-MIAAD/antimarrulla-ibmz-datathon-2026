"""Rutas del proyecto (relativas a la raíz del repo o a TAMIZAJE_RAIZ dentro de un contenedor)."""
import os

RAIZ = os.environ.get("TAMIZAJE_RAIZ", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
CDC_CSV = os.path.join(RAIZ, "data", "cdc_891", "cdc_diabetes_891.csv")
ARTEFACTOS = os.path.join(RAIZ, "artefactos")
PARTICIONES = os.path.join(ARTEFACTOS, "particiones", "cdc891_particiones_v1.json")
ESQUEMA_JSON = os.path.join(ARTEFACTOS, "modelo", "esquema_cdc21_v1.json")
MODELO_JSON = os.path.join(ARTEFACTOS, "modelo", "modelo_logistico_v1.json")
METRICAS_MODELO = os.path.join(ARTEFACTOS, "metricas", "modelo_logistico_v1.json")
MEDICIONES = os.environ.get("TAMIZAJE_MEDICIONES", os.path.join(RAIZ, "submission", "evidencias", "metricas"))


def asegurar_dirs():
    for d in (os.path.dirname(PARTICIONES), os.path.dirname(MODELO_JSON), os.path.dirname(METRICAS_MODELO)):
        os.makedirs(d, exist_ok=True)
