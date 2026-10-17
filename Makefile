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

imagen:                               ## imagen de la demo, etapa app (sin CDC, pruebas ni herramientas de entrenamiento)
	docker build -f docker/Dockerfile --target app -t tamizaje:demo .

demo: secretos imagen                 ## levanta hospital + servicio y corre la prueba de humo
	$(COMPOSE) up -d
	$(BIN)/python -m tamizaje.smoke http://127.0.0.1:8080
	@echo "UI: http://127.0.0.1:8080"

smoke: setup
	$(BIN)/python -m tamizaje.smoke http://127.0.0.1:8080

demo-down:
	$(COMPOSE) down

medir: setup                          ## exactitud + microbenchmarks en proceso, con procedencia → submission/evidencias/metricas/
	$(BIN)/python -m tamizaje.medir $(if $(FINAL),--final,)

medir-api: setup                      ## mide la API del hospital desplegado (make demo) de punta a punta
	$(BIN)/python -m tamizaje.medir --modo api --url http://127.0.0.1:8080 $(if $(FINAL),--final,)

package: verify                       ## paquetes documental y de código en dist/ (BORRADOR; FINAL=1 exige evidencias)
	$(BIN)/python -m tamizaje.empaquetar --tipo ambos $(if $(FINAL),--final,)

# ---- Linux / LinuxONE (s390x) sin ruedas de pip: todo dentro de las imágenes de Ubuntu 24.04
COMMIT := $(shell git rev-parse HEAD 2>/dev/null)
# Cambios relevantes, incluidos archivos nuevos sin versionar (un PPTX personal fuera de estas rutas no cuenta)
RELEVANTES := src tests docker Makefile requirements.txt artefactos/modelo artefactos/particiones .dockerignore
CAMBIOS := $(shell test -n "$$(git status --porcelain --untracked-files=all -- $(RELEVANTES) 2>/dev/null)" && echo 1 || echo 0)
PROC = -e TAMIZAJE_COMMIT=$(COMMIT) -e TAMIZAJE_CAMBIOS_RELEVANTES=$(CAMBIOS) -e TAMIZAJE_IMAGEN=$$(docker image inspect -f '{{.Id}}' tamizaje:dev)
DEV = docker run --rm $(PROC) tamizaje:dev

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

imagen-inspeccion: imagen             ## comprueba que la imagen de la demo no trae CDC, pruebas, sklearn ni llaves
	docker run --rm tamizaje:demo sh -c 'test ! -e /app/data && test ! -e /app/tests && ! python3 -c "import sklearn" 2>/dev/null && ! find / -xdev \( -name "*.key" -o -name "boveda.key" \) 2>/dev/null | grep -q . && test -f /app/artefactos/modelo/modelo_logistico_v1.json && test -f /app/tamizaje/ui/index.html && echo "imagen app OK: modelo y UI; sin CDC, pruebas, sklearn ni llaves"' 

medir-docker: imagen-dev              ## mediciones dentro de Linux → submission/evidencias/metricas/
	mkdir -p submission/evidencias/metricas && chmod 777 submission/evidencias/metricas
	docker run --rm $(PROC) -v $(CURDIR)/submission/evidencias/metricas:/app/submission/evidencias/metricas tamizaje:dev python3 -m tamizaje.medir $(if $(FINAL),--final,)

medir-api-docker: imagen-dev          ## mide la API del hospital de Compose desde un contenedor cliente (sin Python en el host)
	mkdir -p submission/evidencias/metricas && chmod 777 submission/evidencias/metricas
	docker run --rm --network host $(PROC) -v $(CURDIR)/submission/evidencias/metricas:/app/submission/evidencias/metricas tamizaje:dev python3 -m tamizaje.medir --modo api --url http://127.0.0.1:8080 $(if $(FINAL),--final,)

ensanut: setup                        ## extra: evaluación exploratoria con ENSANUT (microdatos locales)
	$(BIN)/python -m tamizaje.ensanut

pronostico: setup                     ## extra E5: pronóstico a 52 semanas (222 series) → artefactos/pronostico/ y el sitio
	$(BIN)/python -m tamizaje.pronostico
	cp artefactos/pronostico/e5_pronostico_v1.json site/assets/pronostico.json

video-borrador:                       ## borrador sin audio con los tiempos del guion → dist/video/ (requiere ffmpeg)
	PYTHONPATH=src $(BIN)/python -m tamizaje.video_borrador

# ---- Prueba de dos máquinas (docs/DOS_MAQUINAS.md): servicio de riesgo en una VM, hospital en otra, con auditoría
DM ?= $(HOME)/.tamizaje-dos-maquinas
N ?= 200
MAQUINA_ID = -e TAMIZAJE_MAQUINA_ID=$$(cut -c1-12 /etc/machine-id 2>/dev/null)
.PHONY: secretos-dos-maquinas servicio-remoto-docker hospital-remoto-docker auditar-dos-maquinas-docker ensayo-dos-maquinas

secretos-dos-maquinas: imagen         ## VM del servicio: certificados con su IP + paquete para el hospital (SERVICIO_IP=...)
	@test -n "$(SERVICIO_IP)" || (echo "uso: make secretos-dos-maquinas SERVICIO_IP=<IP pública de esta VM>"; exit 1)
	@mkdir -p $(DM) && chmod 700 $(DM)
	docker run --rm --user $(TAMIZAJE_UID):$(TAMIZAJE_GID) -v $(DM):/dm tamizaje:demo python3 -m tamizaje.secretos /dm/servicio --servicio-san $(SERVICIO_IP) --exportar-hospital /dm/para_hospital
	@echo "Copia $(DM)/para_hospital a la VM del hospital (misma ruta) y bórralo de aquí: rm -r $(DM)/para_hospital"

servicio-remoto-docker: imagen        ## VM del servicio: escucha en :8443 sin llave privada y guarda evidencia (Ctrl+C para parar)
	@test -f $(DM)/servicio/certs/servicio.pem || (echo "primero: make secretos-dos-maquinas SERVICIO_IP=..."; exit 1)
	@mkdir -p $(DM)/evidencia_servicio
	docker run --rm --name tamizaje-servicio-remoto --hostname $$(hostname) $(MAQUINA_ID) --user $(TAMIZAJE_UID):$(TAMIZAJE_GID) -p 8443:8443 \
	  -v $(DM)/servicio/certs:/run/tamizaje:ro -v $(DM)/evidencia_servicio:/evidencia \
	  -e SERVICIO_CERT=/run/tamizaje/servicio.pem -e SERVICIO_LLAVE=/run/tamizaje/servicio.key -e SERVICIO_CA_CLIENTES=/run/tamizaje/ca.pem \
	  -e SERVICIO_EVIDENCIA=/evidencia tamizaje:demo python3 -m tamizaje.servicio 2>&1 | tee -a $(DM)/servicio.log

hospital-remoto-docker: imagen-dev    ## VM del hospital: N registros reales del CDC cifrados al servicio remoto (SERVICIO_URL=...)
	@test -n "$(SERVICIO_URL)" || (echo "uso: make hospital-remoto-docker SERVICIO_URL=https://<IP del servicio>:8443 [N=200]"; exit 1)
	@test -f $(DM)/para_hospital/hospital.key || (echo "falta $(DM)/para_hospital: cópialo desde la VM del servicio"; exit 1)
	@mkdir -p $(DM)/bitacora_hospital
	docker run --rm --network host $(PROC) $(MAQUINA_ID) --user $(TAMIZAJE_UID):$(TAMIZAJE_GID) \
	  -v $(DM)/para_hospital:/run/tamizaje:ro -v $(DM)/bitacora_hospital:/bitacora \
	  tamizaje:dev python3 -m tamizaje.dos_maquinas hospital --servicio $(SERVICIO_URL) --certs /run/tamizaje --salida /bitacora --n $(N)

auditar-dos-maquinas-docker: imagen-dev  ## VM del servicio, con la bitácora del hospital copiada: reporte → submission/evidencias/dos_maquinas/
	@test -f $(DM)/bitacora_hospital/resumen_hospital.json || (echo "copia la carpeta bitacora_hospital de la VM del hospital a $(DM)/"; exit 1)
	mkdir -p submission/evidencias/dos_maquinas && chmod 777 submission/evidencias/dos_maquinas
	docker run --rm $(PROC) -v $(DM):/dm:ro -v $(CURDIR)/submission/evidencias/dos_maquinas:/app/submission/evidencias/dos_maquinas \
	  tamizaje:dev python3 -m tamizaje.dos_maquinas auditar --servicio /dm/evidencia_servicio --hospital /dm/bitacora_hospital --log-servicio /dm/servicio.log

ensayo-dos-maquinas: setup            ## ensayo en UNA máquina (Mac o VM) con el venv: no es evidencia, solo prueba el flujo
	@E=/tmp/tamizaje-ensayo; rm -rf $$E; $(BIN)/python -m tamizaje.secretos $$E/servicio --exportar-hospital $$E/para_hospital >/dev/null; \
	C=$$E/servicio/certs; SERVICIO_HOST=127.0.0.1 SERVICIO_PUERTO=9443 SERVICIO_CERT=$$C/servicio.pem SERVICIO_LLAVE=$$C/servicio.key \
	SERVICIO_CA_CLIENTES=$$C/ca.pem MODELO_JSON=artefactos/modelo/modelo_logistico_v1.json SERVICIO_EVIDENCIA=$$E/evidencia_servicio \
	$(BIN)/python -m tamizaje.servicio > $$E/servicio.log 2>&1 & PID=$$!; sleep 3; \
	$(BIN)/python -m tamizaje.dos_maquinas hospital --servicio https://localhost:9443 --certs $$E/para_hospital --salida $$E/bitacora_hospital --n $(if $(filter 200,$(N)),20,$(N)); RC=$$?; \
	kill $$PID; test $$RC -eq 0 && $(BIN)/python -m tamizaje.dos_maquinas auditar --servicio $$E/evidencia_servicio --hospital $$E/bitacora_hospital \
	  --log-servicio $$E/servicio.log --salida $$E/reporte --permitir-misma-maquina
