#!/usr/bin/env bash
# 04_docker_check.sh - Preflight de Docker y bibliotecas en Ubuntu 24.04.
# Para las pruebas completas del proyecto: make verify-docker desde la raíz.
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v docker >/dev/null; then
  echo "Docker not found, installing docker.io..."
  sudo apt-get update -y && sudo apt-get install -y docker.io
fi
sudo systemctl enable --now docker 2>/dev/null || true
DOCKER="docker"; docker info >/dev/null 2>&1 || DOCKER="sudo docker"

echo "== Docker: $($DOCKER --version)"
echo "== Running hello-world"
$DOCKER run --rm hello-world | grep -q "Hello from Docker" && echo "  [OK] hello-world"

echo "== Checking container architecture"
CARCH=$($DOCKER run --rm ubuntu:24.04 uname -m)
echo "  container arch: $CARCH (host: $(uname -m))"

cat > Dockerfile.test <<'DOCKERFILE'
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-venv python3-numpy python3-sklearn python3-gmpy2 python3-cryptography openssl \
 && python3 -m venv --system-site-packages /venv && /venv/bin/pip install --no-cache-dir phe \
 && rm -rf /var/lib/apt/lists/*
COPY 03_test_stack.py /app/03_test_stack.py
CMD ["/venv/bin/python", "/app/03_test_stack.py"]
DOCKERFILE

echo "== Building test image (first build can take a few minutes)"
$DOCKER build -q -f Dockerfile.test -t datathon-stack-test . >/dev/null
echo "== Running stack tests inside the container"
$DOCKER run --rm datathon-stack-test
