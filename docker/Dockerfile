# Imágenes para los dos contenedores de la demo (target app) y para pruebas/mediciones (target dev).
# Base Ubuntu 24.04: existe para s390x (LinuxONE), amd64 y arm64; las dependencias nativas vienen de apt,
# así que no hace falta compilar ruedas de pip en s390x. Solo phe (Python puro) se instala con pip.
FROM ubuntu:24.04 AS app
ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TAMIZAJE_RAIZ=/app
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-pip python3-cryptography python3-gmpy2 ca-certificates openssl \
 && pip3 install --no-cache-dir --break-system-packages phe==1.5.0 \
 && rm -rf /var/lib/apt/lists/* \
 && useradd --system --uid 10001 --home /app tamizaje \
 && mkdir -p /var/lib/tamizaje && chmod 1777 /var/lib/tamizaje
WORKDIR /app
COPY src/tamizaje /app/tamizaje
COPY artefactos/modelo /app/artefactos/modelo
USER tamizaje
ENV MODELO_JSON=/app/artefactos/modelo/modelo_logistico_v1.json

# Pruebas, verificación y mediciones dentro de Linux (incluido s390x) con numpy/scikit-learn de apt.
FROM app AS dev
USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3-numpy python3-sklearn python3-pytest util-linux \
 && (apt-get install -y --no-install-recommends s390-tools || true) \
 && rm -rf /var/lib/apt/lists/*
COPY tests /app/tests
COPY data/cdc_891 /app/data/cdc_891
COPY artefactos /app/artefactos
ENV PYTHONPATH=/app
USER tamizaje
