#!/usr/bin/env python3
"""Pruebas del proyecto real (21 variables), no un protocolo de referencia aparte.

Ejecutar desde cualquier carpeta con el Python del entorno del proyecto.
Guarda salida de pytest y procedencia; s390x por sí solo no identifica al proveedor.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))
from tamizaje import procedencia


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--salida", type=Path, default=RAIZ / "submission/evidencias/instancia")
    args = ap.parse_args()
    pruebas = ["tests/test_protocolo.py", "tests/test_integracion.py", "tests/test_medicion.py"]
    comando = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *pruebas]
    env = {**os.environ, "PYTHONPATH": str(RAIZ / "src")}
    run = subprocess.run(comando, cwd=RAIZ, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(run.stdout, end="")
    ahora = datetime.datetime.now(datetime.timezone.utc)
    args.salida.mkdir(parents=True, exist_ok=True)
    base = args.salida / ("claims_proyecto_" + ahora.strftime("%Y%m%dT%H%M%S%fZ"))
    log = base.with_suffix(".log")
    log.write_text(run.stdout, encoding="utf-8")
    registro = {"fecha_utc": ahora.isoformat(), "tipo": "pruebas_del_proyecto_cdc21",
                "arquitectura": platform.machine(), "python": platform.python_version(),
                "linuxone": "no_verificado: contrastar con dashboard de Community Cloud",
                "pruebas": pruebas, "pytest_exit_code": run.returncode,
                "procedencia": procedencia.registrar(), "log": log.name,
                "log_sha256": procedencia.sha256(log)}
    base.with_suffix(".json").write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Evidencia del proyecto:", base.with_suffix(".json"))
    return run.returncode


if __name__ == "__main__":
    sys.exit(main())
