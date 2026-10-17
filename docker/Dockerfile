# Ubuntu 24.04 app/dev images for amd64, arm64 and LinuxONE s390x.
# Native dependencies use apt; phe is pure Python. The app excludes training data/tools.
FROM ubuntu:24.04 AS app
ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 SCREENING_ROOT=/app
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-pip python3-cryptography python3-gmpy2 ca-certificates openssl \
 && pip3 install --no-cache-dir --break-system-packages phe==1.5.0 \
 && rm -rf /var/lib/apt/lists/* \
 && useradd --system --uid 10001 --home /app screening \
 && mkdir -p /var/lib/screening && chmod 1777 /var/lib/screening
WORKDIR /app
COPY src/screening /app/screening
COPY artifacts/model /app/artifacts/model
USER screening
ENV MODEL_JSON=/app/artifacts/model/logistic_model_v1.json

FROM app AS dev
USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3-numpy python3-sklearn python3-pytest util-linux \
 && (apt-get install -y --no-install-recommends s390-tools || true) \
 && rm -rf /var/lib/apt/lists/*
COPY tests /app/tests
COPY data/cdc_891 /app/data/cdc_891
COPY artifacts /app/artifacts
ENV PYTHONPATH=/app
USER screening
