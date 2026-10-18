# Project command interface. See README.md for setup and deployment.
.DEFAULT_GOAL := all
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
PY ?= python3.12
VENV := .venv
BIN := $(VENV)/bin
export PYTHONPATH := src
export SCREENING_SECRETS ?= $(HOME)/.screening
export SCREENING_UID := $(shell id -u)
export SCREENING_GID := $(shell id -g)
export SCREENING_UI_PORT ?= 8080
UI_URL ?= http://127.0.0.1:$(SCREENING_UI_PORT)
COMPOSE ?= docker compose -f docker/compose.yml
MEASUREMENT_DIR ?= submission/evidence/metrics

.PHONY: all setup model test verify secrets image demo demo-down smoke measure measure-api package instance-claims
all: setup verify demo                ## Install, verify and start the demo.
setup: $(VENV)/.installed             ## Install pinned Python dependencies.
$(VENV)/.installed: requirements.txt
	$(PY) -m venv $(VENV)
	$(BIN)/pip install -q --upgrade pip
	$(BIN)/pip install -q -r requirements.txt
	touch $@
model: setup                         ## Create missing splits and retrain the exported model.
	$(BIN)/python -m screening.data
	$(BIN)/python -m screening.train
test: setup                          ## Protocol, service, provenance and integration tests.
	$(BIN)/python -m pytest -q tests
verify: test                         ## Verify artifacts and reproduce the model without modifying it.
	$(BIN)/python -m screening.verify
instance-claims: setup               ## Run actual 21-feature project tests and save provenance.
	$(BIN)/python tests/instance/05_test_claims.py
secrets: setup                       ## Create TLS credentials and the vault key outside the repo.
	@test -f $(SCREENING_SECRETS)/certs/service.pem -a -f $(SCREENING_SECRETS)/vault.key || $(BIN)/python -m screening.secrets_setup $(SCREENING_SECRETS)
image:                               ## Build the app image without CDC, tests or training tools.
	docker build -f docker/Dockerfile --target app -t screening:demo .
demo: secrets image                  ## Start hospital/service containers and run the smoke test.
	$(COMPOSE) up -d
	$(BIN)/python -m screening.smoke $(UI_URL)
	@echo "UI: $(UI_URL)"
smoke: setup
	$(BIN)/python -m screening.smoke $(UI_URL)
demo-down:
	$(COMPOSE) down
measure: setup                       ## Same-sample numerical comparison and process microbenchmarks.
	$(BIN)/python -m screening.measure $(MEASURE_ARGS) $(if $(FINAL),--final,)
measure-api: setup                   ## Measure the deployed hospital API end to end.
	$(BIN)/python -m screening.measure --mode api --url $(UI_URL) $(API_ARGS) $(if $(FINAL),--final,)
package: verify                      ## Build DRAFT ZIPs; FINAL=1 requires final evidence.
	$(BIN)/python -m screening.package --kind both $(if $(FINAL),--final,)

ablation: setup                       ## 21 vs 19 features evidence (validation split) → artifacts/metrics/ablation_cdc19_v1.json
	$(BIN)/python -m screening.ablation

# Ubuntu apt packages support amd64, arm64 and LinuxONE s390x without native pip wheels.
COMMIT := $(shell git rev-parse HEAD 2>/dev/null)
RELEVANT := src tests docker Makefile requirements.txt artifacts/model artifacts/splits .dockerignore
CHANGES := $(shell test -n "$$(git status --porcelain --untracked-files=all -- $(RELEVANT) 2>/dev/null)" && echo 1 || echo 0)
PROC = -e SCREENING_COMMIT=$(COMMIT) -e SCREENING_RELEVANT_CHANGES=$(CHANGES) -e SCREENING_IMAGE=$$(docker image inspect -f '{{.Id}}' screening:dev)
DEV = docker run --rm $(PROC) screening:dev
.PHONY: image-dev secrets-docker verify-docker demo-docker image-inspect measure-docker measure-api-docker
image-dev:
	docker build -f docker/Dockerfile --target dev -t screening:dev .
secrets-docker: image                ## Generate credentials using the image, without a host venv.
	@mkdir -p $(SCREENING_SECRETS)
	@test -f $(SCREENING_SECRETS)/certs/service.pem -a -f $(SCREENING_SECRETS)/vault.key || docker run --rm --user $(SCREENING_UID):$(SCREENING_GID) -v $(SCREENING_SECRETS):/secrets screening:demo python3 -m screening.secrets_setup /secrets
verify-docker: image-dev             ## Run tests and model verification inside Ubuntu.
	$(DEV) sh -c "python3 -m pytest -q -p no:cacheprovider tests && python3 -m screening.verify"
demo-docker: secrets-docker image    ## Run the demo and container smoke test without host Python.
	$(COMPOSE) up -d
	docker run --rm --network host screening:demo python3 -m screening.smoke $(UI_URL)
image-inspect: image                 ## Verify the app image excludes data, tests, sklearn and keys.
	docker run --rm screening:demo sh -c 'test ! -e /app/data && test ! -e /app/tests && ! python3 -c "import sklearn" 2>/dev/null && ! find / -xdev \( -name "*.key" -o -name "vault.key" \) 2>/dev/null | grep -q . && test -f /app/artifacts/model/logistic_model_v1.json && test -f /app/screening/ui/index.html && echo "app image OK: model/UI present; no CDC, tests, sklearn or keys"'
measure-docker: image-dev            ## Write process measurements with container provenance.
	mkdir -p $(MEASUREMENT_DIR)
	docker run --rm --user $(SCREENING_UID):$(SCREENING_GID) $(PROC) -v $(CURDIR)/$(MEASUREMENT_DIR):/app/submission/evidence/metrics screening:dev python3 -m screening.measure $(MEASURE_ARGS) $(if $(FINAL),--final,)
measure-api-docker: image-dev        ## Measure the Compose hospital API from a client container.
	mkdir -p $(MEASUREMENT_DIR)
	docker run --rm --user $(SCREENING_UID):$(SCREENING_GID) --network host $(PROC) -v $(CURDIR)/$(MEASUREMENT_DIR):/app/submission/evidence/metrics screening:dev python3 -m screening.measure --mode api --url $(UI_URL) $(API_ARGS) $(if $(FINAL),--final,)

PROFILE ?= 2000
.PHONY: evidence-run evidence-check evidence-index demo-test test-profiles
evidence-run:                        ## On the VM: run checks + FINAL measurements, keep logs, push branch evidence/<run>.
	$(PY) tools/evidence.py run --profile $(PROFILE) $(if $(API_N),--api-n $(API_N),) $(if $(NO_PUSH),--no-push,) $(if $(DOWN),--down,)
evidence-check:                      ## Validate recorded runs (RUN=dir for one; LOCAL=1 accepts non-s390x rehearsals).
	$(PY) tools/evidence.py check $(RUN) $(if $(LOCAL),--allow-non-s390x,)
evidence-index:                      ## Rebuild submission/evidence/runs/INDEX.md.
	$(PY) tools/evidence.py index

.PHONY: ensanut forecast video-draft
ensanut: setup                       ## Optional reduced ENSANUT experiment with local microdata.
	$(BIN)/python -m screening.ensanut
forecast: setup                      ## Optional 52-week forecasts, evaluation and dashboard data.
	$(BIN)/python -m screening.forecast
	cp artifacts/forecast/e5_forecast_v1.json site/assets/forecast.json
video-draft:                         ## Build the silent 170-second editing draft; requires ffmpeg.
	PYTHONPATH=src $(BIN)/python -m screening.video_draft

# Optional two-host test: service on host A; hospital on host B.
DM ?= $(HOME)/.screening-two-hosts
N ?= 200
CONCURRENCY ?= 1
DATA ?= synthetic
HOST_ID = -e SCREENING_HOST_ID=$$(cut -c1-12 /etc/machine-id 2>/dev/null || true)
.PHONY: secrets-two-hosts service-remote-docker hospital-remote-docker audit-two-hosts-docker rehearse-two-hosts
secrets-two-hosts: image              ## SERVICE_IP must match the service certificate SAN.
	@test -n "$(SERVICE_IP)" || (echo "usage: make secrets-two-hosts SERVICE_IP=<service VM IP>"; exit 1)
	@mkdir -p $(DM) && chmod 700 $(DM)
	docker run --rm --user $(SCREENING_UID):$(SCREENING_GID) -v $(DM):/dm screening:demo python3 -m screening.secrets_setup /dm/service --service-san $(SERVICE_IP) --export-hospital /dm/for_hospital
	@echo "Transfer $(DM)/for_hospital securely to the hospital VM, then remove the transfer copy."
service-remote-docker: image          ## Listen on :8443 with ciphertext evidence; stop with Ctrl+C.
	@test -f $(DM)/service/certs/service.pem || (echo "first run: make secrets-two-hosts SERVICE_IP=..."; exit 1)
	@mkdir -p $(DM)/service_evidence
	docker run --rm --name screening-service-remote --hostname $$(hostname) $(HOST_ID) --user $(SCREENING_UID):$(SCREENING_GID) -p 8443:8443 \
	  -v $(DM)/service/certs:/run/screening:ro -v $(DM)/service_evidence:/evidence \
	  -e SERVICE_CERT=/run/screening/service.pem -e SERVICE_KEY=/run/screening/service.key -e SERVICE_CLIENT_CA=/run/screening/ca.pem \
	  -e SERVICE_EVIDENCE=/evidence screening:demo python3 -m screening.service 2>&1 | tee -a $(DM)/service.log
hospital-remote-docker: image-dev     ## Synthetic by default; DATA=cdc explicitly selects labeled public data.
	@test -n "$(SERVICE_URL)" || (echo "usage: make hospital-remote-docker SERVICE_URL=https://<service IP>:8443 [N=200]"; exit 1)
	@test -f $(DM)/for_hospital/hospital.key || (echo "missing hospital credential bundle: $(DM)/for_hospital"; exit 1)
	@mkdir -p $(DM)/hospital_log
	docker run --rm --network host $(PROC) $(HOST_ID) --user $(SCREENING_UID):$(SCREENING_GID) \
	  -v $(DM)/for_hospital:/run/screening:ro -v $(DM)/hospital_log:/hospital_log \
	  screening:dev python3 -m screening.two_hosts hospital --service $(SERVICE_URL) --certs /run/screening --output /hospital_log --n $(N) --data $(DATA) --concurrency $(CONCURRENCY)
audit-two-hosts-docker: image-dev     ## Copy host B's log to host A before auditing both evidence directories.
	@test -f $(DM)/hospital_log/hospital_summary.json || (echo "copy the hospital_log directory from host B to $(DM)/"; exit 1)
	mkdir -p submission/evidence/two_hosts && chmod 777 submission/evidence/two_hosts
	docker run --rm $(PROC) -v $(DM):/dm:ro -v $(CURDIR)/submission/evidence/two_hosts:/app/submission/evidence/two_hosts \
	  screening:dev python3 -m screening.two_hosts audit --service /dm/service_evidence --hospital /dm/hospital_log --log-service /dm/service.log
rehearse-two-hosts: setup             ## Single-host synthetic rehearsal; never accredits two real VMs.
	@set -eu; E=$$(mktemp -d /tmp/screening-rehearsal.XXXXXX); $(BIN)/python -m screening.secrets_setup $$E/service --export-hospital $$E/for_hospital >/dev/null; \
	P=$$($(BIN)/python -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1]); s.close()'); \
	C=$$E/service/certs; SERVICE_HOST=127.0.0.1 SERVICE_PORT=$$P SERVICE_CERT=$$C/service.pem SERVICE_KEY=$$C/service.key \
	SERVICE_CLIENT_CA=$$C/ca.pem MODEL_JSON=artifacts/model/logistic_model_v1.json SERVICE_EVIDENCE=$$E/service_evidence \
	$(BIN)/python -m screening.service > $$E/service.log 2>&1 & PID=$$!; trap 'kill "$$PID" 2>/dev/null || true' EXIT; sleep 3; \
	$(BIN)/python -m screening.two_hosts hospital --service https://localhost:$$P --certs $$E/for_hospital --output $$E/hospital_log --n $(if $(filter 200,$(N)),20,$(N)) --data $(DATA); \
	kill $$PID; wait $$PID 2>/dev/null || true; $(BIN)/python -m screening.two_hosts audit --service $$E/service_evidence --hospital $$E/hospital_log \
	  --log-service $$E/service.log --output $$E/report --allow-same-machine

# Fast live demonstration against the already-running Hospital; no model retraining.
demo-test:                           ## Synthetic end-to-end requests; N=20 for the pitch, N=200 for a short test.
	$(MAKE) measure-api-docker API_ARGS="--n $(N)" $(if $(FINAL),FINAL=$(FINAL),)
test-profiles:                       ## Print configured sizes without executing measurements.
	@$(PY) -c 'from screening.benchmark_profiles import profile, SIZES; [print(profile(n)) for n in SIZES]'

.PHONY: evidence-suite
evidence-suite:                      ## Run 20, 200, 2,000 and 16,000 profiles sequentially; stop on any failure.
	@for size in 20 200 2000 16000; do $(MAKE) evidence-run PROFILE=$$size || exit $$?; done
