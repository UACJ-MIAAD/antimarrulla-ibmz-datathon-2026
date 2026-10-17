# Interfaz única del proyecto. Ver README · "Cómo correrlo".
PY ?= python3.12
VENV := .venv
BIN := $(VENV)/bin
export PYTHONPATH := src
export TAMIZAJE_SECRETOS ?= $(HOME)/.tamizaje
export TAMIZAJE_UID := $(shell id -u)
export TAMIZAJE_GID := $(shell id -g)
COMPOSE := docker compose -f docker/compose.yml

.PHONY: all setup modelo test verify secretos imagen demo demo-down smoke medir package

all: setup verify demo                ## instala, verifica y levanta la demo

setup: $(VENV)/.instalado             ## crea .venv con las versiones fijadas
$(VENV)/.instalado: requirements.txt
	$(PY) -m venv $(VENV)
	$(BIN)/pip install -q --upgrade pip
	$(BIN)/pip install -q -r requirements.txt
	touch $@

modelo: setup                         ## regenera particiones (si faltan) y re-entrena el modelo exportado
	$(BIN)/python -m tamizaje.datos
	$(BIN)/python -m tamizaje.entrenar

test: setup                           ## pruebas del protocolo, servicio e integración
	$(BIN)/python -m pytest -q tests

verify: test                          ## pruebas + verificación de artefactos (no modifica nada)
	$(BIN)/python -m tamizaje.verificar

secretos: setup                       ## certificados TLS y llave de la bóveda, fuera del repo
	@test -f $(TAMIZAJE_SECRETOS)/certs/servicio.pem -a -f $(TAMIZAJE_SECRETOS)/boveda.key || $(BIN)/python -m tamizaje.secretos $(TAMIZAJE_SECRETOS)

imagen:                               ## construye la imagen (Ubuntu 24.04: amd64, arm64 y s390x)
	docker build -f docker/Dockerfile -t tamizaje:demo .

demo: secretos imagen                 ## levanta hospital + servicio y corre la prueba de humo
	$(COMPOSE) up -d
	$(BIN)/python -m tamizaje.smoke http://127.0.0.1:8080
	@echo "UI: http://127.0.0.1:8080"

smoke: setup
	$(BIN)/python -m tamizaje.smoke http://127.0.0.1:8080

demo-down:
	$(COMPOSE) down

medir: setup                          ## mediciones con evidencia del entorno → submission/evidencias/metricas/
	$(BIN)/python -m tamizaje.medir

package: verify                       ## paquete de entrega en dist/
	$(BIN)/python -m tamizaje.empaquetar

# ---- Linux / LinuxONE (s390x) sin ruedas de pip: todo dentro de las imágenes de Ubuntu 24.04
COMMIT := $(shell git rev-parse HEAD 2>/dev/null)
CAMBIOS := $(shell test -n "$$(git status --porcelain --untracked-files=no 2>/dev/null)" && echo 1 || echo 0)
DEV := docker run --rm -e TAMIZAJE_COMMIT=$(COMMIT) -e TAMIZAJE_CAMBIOS=$(CAMBIOS) tamizaje:dev

imagen-dev:
	docker build -f docker/Dockerfile --target dev -t tamizaje:dev .

secretos-docker: imagen               ## genera los secretos con la imagen (sin venv en el host)
	@mkdir -p $(TAMIZAJE_SECRETOS)
	@test -f $(TAMIZAJE_SECRETOS)/certs/servicio.pem -a -f $(TAMIZAJE_SECRETOS)/boveda.key || docker run --rm --user $(TAMIZAJE_UID):$(TAMIZAJE_GID) -v $(TAMIZAJE_SECRETOS):/secretos tamizaje:demo python3 -m tamizaje.secretos /secretos

verify-docker: imagen-dev             ## pruebas + verificación dentro de Linux
	$(DEV) sh -c "python3 -m pytest -q -p no:cacheprovider tests && python3 -m tamizaje.verificar"

demo-docker: secretos-docker imagen   ## demo sin venv en el host
	$(COMPOSE) up -d
	docker run --rm --network host tamizaje:demo python3 -m tamizaje.smoke http://127.0.0.1:8080

medir-docker: imagen-dev              ## mediciones dentro de Linux → submission/evidencias/metricas/
	mkdir -p submission/evidencias/metricas && chmod 777 submission/evidencias/metricas
	docker run --rm -e TAMIZAJE_COMMIT=$(COMMIT) -e TAMIZAJE_CAMBIOS=$(CAMBIOS) -v $(CURDIR)/submission/evidencias/metricas:/app/submission/evidencias/metricas tamizaje:dev python3 -m tamizaje.medir

ensanut: setup                        ## extra: evaluación exploratoria con ENSANUT (microdatos locales)
	$(BIN)/python -m tamizaje.ensanut

pronostico: setup                     ## extra E5: pronóstico a 52 semanas (222 series) → artefactos/pronostico/ y el sitio
	$(BIN)/python -m tamizaje.pronostico
	cp artefactos/pronostico/e5_pronostico_v1.json site/assets/pronostico.json

video-borrador:                       ## borrador sin audio con los tiempos del guion → dist/video/ (requiere ffmpeg)
	PYTHONPATH=src $(BIN)/python -m tamizaje.video_borrador
