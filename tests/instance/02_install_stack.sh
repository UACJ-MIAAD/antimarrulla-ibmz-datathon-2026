#!/usr/bin/env bash
# 02_install_stack.sh - Installs the Python stack in a virtual environment.
# On s390x, heavy libraries (numpy, scikit-learn, gmpy2, cryptography) are taken
# from Ubuntu's own packages, which are prebuilt for s390x, so nothing has to compile.
# Only python-paillier (pure Python) comes from pip.
# Usage: ./02_install_stack.sh        (apt mode, recommended)
#        MODE=pip ./02_install_stack.sh   (try everything from pip; may compile slowly)
set -euo pipefail
MODE="${MODE:-apt}"
VENV="${VENV:-$HOME/venv-datathon}"

echo "== Installing system packages =="
sudo apt-get update -y
sudo apt-get install -y python3-venv python3-dev python3-pip build-essential pkg-config \
  libgmp-dev libmpfr-dev libmpc-dev libssl-dev libffi-dev openssl curl

if [[ "$MODE" == "apt" ]]; then
  sudo apt-get install -y python3-numpy python3-sklearn python3-gmpy2 python3-cryptography
  python3 -m venv --system-site-packages "$VENV"
  "$VENV/bin/pip" install --upgrade pip
  "$VENV/bin/pip" install phe
else
  sudo apt-get install -y gfortran libopenblas-dev cargo rustc
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install --upgrade pip wheel
  "$VENV/bin/pip" install numpy scikit-learn gmpy2 cryptography phe
fi

echo
echo "Installed versions:"
"$VENV/bin/python" - <<'PY'
import importlib
for m in ["numpy", "sklearn", "gmpy2", "cryptography", "phe"]:
    try:
        mod = importlib.import_module(m)
        v = getattr(mod, "__version__", None) or (mod.version() if hasattr(mod, "version") else "?")
        print(f"  {m:13s} {v}")
    except Exception as e:
        print(f"  {m:13s} MISSING ({e})")
PY
echo "Virtual environment ready: source $VENV/bin/activate"
