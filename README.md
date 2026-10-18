<p align="center">
  <img src="assets/logo.png" alt="Los Antimarrulla team logo" width="320">
</p>

# Los Antimarrulla · IBM Z Datathon 2026

**Privacy-preserving screening** evaluates a diabetes screening model on Paillier ciphertexts. The hospital keeps its private key; the risk service evaluates the model without decrypting patient inputs.

Public site: [project, pitch, data and delivery plan](https://antimarrulla-tamizaje.netlify.app). The English migration and audit corrections are merged through PRs 9, 11, 12 and 13 (runtime baseline `ef1e21d`). The public forecast dashboard is live. Independent teammate sign-off and final VM/video evidence remain open. See the [current plan audit](docs/PLAN_AUDIT_20261017.md).

The [system diagram atlas](https://antimarrulla-tamizaje.netlify.app/architecture) covers the complete flow, deployment, hospital, risk service, cryptographic protocol, encrypted vault, analytical data model, model training, forecasting and release evidence. [Diagram guide and storage dictionary](docs/SYSTEM_DIAGRAMS.md).

**Submission deadline:** October 18, 2026, **16:30 UTC / 12:30 EDT / 10:30 Ciudad Juárez / 18:30 SAST**. Internal target: 13:00 UTC / 09:00 EDT / 07:00 Ciudad Juárez. The portal opened October 16 at 23:45 UTC. Follow the [delivery plan](docs/DELIVERY_PLAN.md) and [submission checklist](docs/SUBMISSION_CHECKLIST.md).

## Team

UACJ · Master's program in Artificial Intelligence and Data Analytics (MIAAD), virtual Americas track.

| Role | Member | Contact |
|------|--------|---------|
| Captain and coordination | Javier Augusto Rebull Saucedo | al263483@alumnos.uacj.mx |
| LinuxONE and infrastructure | Álvaro Hernández Jarquín | al263150@alumnos.uacj.mx |
| ML and encrypted inference | Carlos Enrique Gonzalez Moran | al271771@alumnos.uacj.mx |
| Data and pitch | Yazmin Ivonne Flores Martinez | al261548@alumnos.uacj.mx |

## Run the project

Python 3.12, Docker and Make are required for the host route. Commands use the English `screening` package and the English wire format `screening-paillier-v2`. Deploy both hospital and service from the same commit. The prior Spanish API/commands are historical and are not compatibility aliases.

```bash
make verify
make demo
```

Open [the local hospital UI](http://127.0.0.1:8080). Choose a synthetic profile or enter the 21 source-coded features. The split screen shows ciphertexts at the service and the decrypted risk at the hospital. Stop the containers with `make demo-down`.

```bash
make measure             # Same CDC sample: floating point, fixed point and Paillier
make measure-api         # Actual deployed hospital API with synthetic inputs
make rehearse-two-hosts N=8
make package             # Documentation and code ZIPs, explicitly DRAFT
```

`make measure` times plaintext/fixed-point logits separately from encryption, encrypted evaluation and decryption. Its same-process HTTPS microbenchmark is distinct from `make measure-api`, which exercises the two-container hospital/service/vault deployment. Neither includes browser rendering. Keep operations and environments separate when comparing timings.

For LinuxONE s390x, Ubuntu 24.04 apt dependencies avoid native pip-wheel requirements:

```bash
make verify-docker
make demo-docker
make measure-docker FINAL=1
make measure-api-docker FINAL=1
```

Use [the LinuxONE runbook](docs/LINUXONE.md) and pin the same release commit for both endpoints and measurements. The app image excludes CDC data, tests, sklearn and private keys. Secrets live outside the repository in `~/.screening` by default. `SCREENING_SECRETS` selects another directory. Generate fresh local demo credentials; do not overwrite or reuse another deployment's vault with a different key.

## Where the frontend and records live

The interactive form and its API are served together by the **Hospital container**. Saved synthetic evaluations stay in its persistent AES-256-GCM vault volume; the risk service receives ciphertexts only. The public pitch, map, forecast and plan stay on **Netlify**. Access the VM hospital through an SSH tunnel; the Netlify site does not expose its API. See [deployment placement and owners](docs/DEPLOYMENT.md).

## Model, evidence and limitations

The 19-feature logistic model (`logistic-cdc19-v1`, schema [`cdc19-v1`](docs/SCHEMA_CDC19.md): Education and Income dropped, validation AUC change −0.0006) uses public CDC BRFSS 2015 data (UCI 891). The stratified 70/15/15 splits are shared by training and evaluation. Standardization is fitted on training only and folded into weights/intercept. A validation threshold targets sensitivity >=0.80; test data is reserved for reporting.

- Test split: 38,052 records; ROC-AUC 0.825, AP 0.414, sensitivity 0.807, specificity 0.689, PPV 0.296 and Brier 0.098.
- Fixed point uses unscaled integer inputs and weights/intercept rounded at scale 10^9. Decrypted integer equality and floating-point quantization error are separate checks.
- Local measurements of `logistic-cdc19-v1` at clean commit `be9b27e`: 2,000/2,000 exact integers, AUC 0.806525 identical in floating, fixed-point and encrypted evaluation, and maximum logit error 3.37×10^-8 (sample bound 7.35×10^-8). Requests carry 19 ciphertexts (24,301 bytes). The local Docker API matched 200/200 synthetic cases with remote code and model hashes verified, client p50 114.8 ms and p95 118.2 ms. These are Mac/arm64 plus Docker measurements; LinuxONE remains pending. See [process evidence](submission/evidence/metrics/measurement_process_local-darwin-arm64_20261018T030142Z.json) and [deployed API evidence](submission/evidence/metrics/measurement_api_local-darwin-arm64_20261018T030546Z.json). Earlier measurements and audits (including `5412abe` and Carlos's two-host audit) describe the 21-feature model and remain as history.
- The reduced ten-feature ENSANUT experiment is separate from the MVP: weighted AUC about 0.77, underestimated risk and sensitivity 0.46–0.49 at the CDC threshold. It does not establish clinical validity in Mexico.
- E5 is an optional 222-series forecast. Nested evaluation and actual band coverage are reported; nominal 80/95% coverage is not guaranteed. Budget scenarios require a sourced unit cost.

This is a technical screening demonstration, not a diagnosis or a forecast of an individual's future diabetes or mortality. The survey label concerns reported diagnosis. Clinical use requires independent population-specific evaluation.

**Team runs on October 17:**

| Run | Result | Evidence status |
|-----|-----------------|-----------------|
| Carlos · Mac hospital to a remote s390x risk service | Original audit **approved, 10/10 checks**: service container on Linux s390x (Ubuntu, OpenSSL 3.0.13), hospital on macOS arm64, separate hosts; 200/200 exact integers; per record p50 606.9 ms and p95 805.0 ms (encrypt ≈141 ms, network + service ≈456 ms p50, decrypt ≈9 ms); TLS 1.3 with client certificate; no private key or plaintext on the service side | Raw report committed ([audit](submission/evidence/two_hosts/auditoria_20261017T194931Z.md), [summary](docs/CARLOS_REMOTE_AUDIT.md)). It ran the pre-English release `037ee1b`; LinuxONE Community Cloud identity and a run on the final English release are still pending. It used the earlier 21-feature model; the 19-feature `cdc19-v1` release must be rerun |
| Álvaro · legacy UI on the server | Linux s390x, 2048-bit key, synthetic C at 66.3% (earlier 21-feature model; 63.3% with `cdc19-v1`) | Screenshot only; provider dashboard, `uname`/`lscpu`, containers and measurement files pending |

Prepared sizes: `make evidence-run PROFILE=16000` (choose `20`, `200`, `2000` or `16000`), or `make evidence-suite PY=python3` for all four sequentially. For the pitch use `make demo-test N=20 FINAL=1` against a prewarmed demo. Larger profiles compare labeled CDC records and use 200 synthetic API requests by default; `API_N=16000` requests a full 16,000-request API test. [Profile guide](docs/BENCHMARK_PROFILES.md).

Next run, on the approved demo VM with the agreed release: `make evidence-run`. It runs `verify-docker`, `image-inspect`, `demo-docker` and both FINAL measurements, keeps every log and the system identity, and pushes them to a branch `evidence/s390x_n<process>_api<requests>_<UTC>` that CI validates before merge ([how](docs/LINUXONE.md#2-recorded-run-recommended-one-command-logs-pushed-to-github); [runs](submission/evidence/runs/)). Use the wording "One synthetic record from the measured run" (not "real patient").

**Trust boundary:** the risk service receives ciphertexts and has no Paillier private key. The approved demo uses two containers on one host; its administrator is trusted and could access hospital memory. Use synthetic demo inputs. Publicly anonymized CDC rows are reserved for explicit benchmarks. AES-256-GCM protects vault records, not every log, disk or backup. CPACF is a platform capability; effective use by this application remains unmeasured. LinuxONE execution and provider screenshots remain pending until actual evidence is committed.

## Repository map

| Location | Contents |
|----------|----------|
| `src/screening/` | Schema, numerical contract, training, protocol, service, hospital, vault, measurement and UI |
| `src/data_prep/` | Reproducible preparation scripts with original source column names preserved |
| `artifacts/` | Shared splits, schema, model, metrics and forecast artifacts |
| `tests/` | Protocol, integration, provenance, forecasting, packaging and instance checks |
| `docker/` | Ubuntu app/dev images and two-container Compose deployment |
| `data/` | Public datasets, catalogs, documentation and source-coded derived tables |
| `docs/` | Design, rules, data contracts, runbooks and delivery plan |
| `site/` | Public pitch, state indicators, forecast dashboard and evidence-based story status |
| `submission/` | English pitch, PDF, flowchart, video instructions and submission text |
| `submission/evidence/` | New English release evidence |
| `submission/evidencias/` | Preserved historical measurement files and screenshots; never relabeled as current |

Original datasets, source fields, proper names, the required submission title and historical evidence retain their original spelling. All current authored code, comments, UI and release documents use English. See [the language migration record](docs/ENGLISH_MIGRATION.md) for path/API changes and validation.

## Project and event documents

**Closing and demo:** [demo runbook and closing timeline](docs/DEMO_RUNBOOK.md) — recording order, VM commands, fallback ladder and judge Q&A.


[Project design](docs/PROJECT.md) · [decision](docs/DECISION.md) · [data model](docs/DATA_MODEL.md) · [data sources](docs/DATA_SOURCES.md) · [event](docs/EVENT.md) · [rules](docs/RULES.md) · [judging criteria](docs/JUDGING_CRITERIA.md) · [themes](docs/THEMES.md) · [roles](docs/ROLES.md) · [independent review](docs/REVIEW.md) · [factual timeline](docs/TIMELINE.md).

## Contribution and review

Use an English branch/commit/PR description. Changes enter `main` through a PR reviewed by another team member. Preserve the actual build history; do not backdate commits or infer a coding-start waiver from the submission window. Yazmin's recorded clone check is partial verification, not a complete protocol review. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Open-source credits

| Resource | License recorded by the project | Use |
|----------|---------------------------------|-----|
| [NumPy](https://github.com/numpy/numpy), [pandas](https://github.com/pandas-dev/pandas), [scikit-learn](https://github.com/scikit-learn/scikit-learn), [matplotlib](https://github.com/matplotlib/matplotlib), [Jupyter](https://github.com/jupyter/notebook) | BSD / PSF | Data, modeling and analysis |
| [python-paillier / phe](https://github.com/data61/python-paillier) | GPLv3, with Apache 2.0 portions | Paillier inference |
| [gmpy2](https://github.com/aleaxit/gmpy) | LGPL-3.0-or-later | Large integer arithmetic |
| [cryptography](https://github.com/pyca/cryptography) | Apache 2.0 / BSD | Vault encryption and TLS certificates |
| [pytest](https://github.com/pytest-dev/pytest) | MIT | Tests |
| [Ubuntu](https://hub.docker.com/_/ubuntu) | Package-specific free licenses | Multi-architecture container base |
| [ucimlrepo](https://github.com/uci-ml-repo/ucimlrepo) | MIT | CDC acquisition |
| [dbfread](https://github.com/olemb/dbfread) | MIT | INEGI DBF reading |
| [statsmodels](https://github.com/statsmodels/statsmodels) | BSD | Optional ETS forecast |
| [TenSEAL](https://github.com/OpenMined/TenSEAL) / [OpenFHE](https://github.com/openfheorg/openfhe-development) | Apache 2.0 / BSD-2 | Optional CKKS, not implemented |
| [llama.cpp](https://github.com/ggerganov/llama.cpp) / IBM Granite | MIT / Apache 2.0 | Optional explanations, not integrated |

Own source code uses [MIT](LICENSE). `phe` retains its GPLv3 terms; distribution of combined works such as images must retain applicable licenses/notices and satisfy the dependency's requirements rather than be described as MIT-only. Every dataset retains its source terms and attribution. CDC/BRFSS is public-domain source material; source metadata and transformations are documented in [data/README.md](data/README.md). ENSANUT microdata is not redistributed. The team is still deciding where to publish its separate AI-use declaration; do not treat a local draft as completed disclosure.
