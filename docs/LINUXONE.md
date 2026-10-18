# LinuxONE runbook (s390x)

A supplied legacy Spanish UI screenshot now reports Linux `s390x`, service `ok` and synthetic profile C at 66.3%; see [Álvaro’s partial evidence](../submission/evidence/linuxone/alvaro_20261017_legacy_ui_reported.md). **Provider identity and final English v2 execution remain unverified**. Local Mac/Ubuntu containers and GitHub x86_64 CI do not replace them. Owner: Álvaro, with Carlos for measurements. Use the translated release commit throughout. The optional [two-host test](TWO_HOSTS.md) is separate from the approved one-VM/two-container MVP.

## 0. Prerequisites

- [ ] Both required labs completed, with actual dates and screenshots in `submission/evidence/labs/`
- [ ] SSH access for the operator; no private keys, tokens or passwords in Git, screenshots or chat
- [ ] Registered leader and submission access confirmed
- [ ] Same translated commit for hospital, service, measurements and recording

The labs-before-coding chronology remains disclosed in [TIMELINE.md](TIMELINE.md). Do not infer an organizer waiver.

## 1. Prepare the VM

```bash
sudo apt-get update
sudo apt-get install -y git make python3 docker.io docker-compose-v2
sudo usermod -aG docker "$USER"
# Log out and back in before using the Docker group.
git clone https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026.git
cd antimarrulla-ibmz-datathon-2026
git switch -c demo/final-evidence RELEASE_COMMIT
```

Ubuntu 24.04 `python3-*` apt packages support s390x; only pure-Python `phe` is installed through pip in the image. No native pip wheels are required on the host.

## 2. Recorded run (recommended): one command, logs pushed to GitHub

Use an existing SSH credential or, if GitHub CLI is installed, `gh auth login` with browser/device authentication and `gh auth setup-git`. Do not use the plaintext `credential.helper store`. Check `git config user.name` and `git config user.email` before running. Switch to the approved named branch first, then pull with `--ff-only`; `git pull && git checkout main` can pull into the wrong branch. Pin the reviewed commit agreed by the team. See the [preflight audit](EVIDENCE_PREFLIGHT_AUDIT.md) before the first final run.

```bash
git config user.name "Your Name"   # identifies the operator in the run manifest
make evidence-run                   # verify-docker, image-inspect, demo-docker, measure(-api)-docker FINAL=1
```

The five steps run sequentially. For safe multiline secret redaction, each step's output is displayed **after that step ends**; a quiet terminal during a measurement does not mean it has stopped. Select `PROFILE=20`, `200`, `2000` (default) or `16000`; the exact CDC sample is never reduced by the pilot budget. The API uses up to 200 synthetic requests by default, or the explicit `API_N` override. The strict checker requires exactly the declared counts; 20/200 process runs are diagnostic only. See [prepared benchmark profiles](BENCHMARK_PROFILES.md) for the four-run suite and short live-demo command.

Files go to `submission/evidence/runs/s390x_n<process>_api<requests>_<UTC>/`: step logs, host/system identity, Compose state/logs, `/api/state`, `manifest.json` and `SUMMARY.md`. Common credentials, complete PEM private-key blocks and public IPv4/IPv6 addresses are redacted from logs and newly generated measurement files before publication. Pattern scanning cannot establish the absence of every possible secret; inspect the files before sharing screenshots or making claims.

The runner requires committed runtime/tests/runner/workflow changes and an empty staging area. It commits only the run's regular files and new measurements on `evidence/s390x_n<process>_api<requests>_<UTC>`; failed runs can also be published for diagnosis and remain invalid. A failed push returns an error and attempts a Git bundle in `dist/`; it never reports a successful upload. The original branch is restored. `make evidence-run NO_PUSH=1` records locally only.

GitHub's `evidence` workflow checks recorded branches with `--require-runs`, so an empty evidence branch cannot pass. It verifies required step order/commands and exit markers, file hashes, required system records, consistency of host/model/code across measurements and API state, exact sample sizes/results, finite numerical bounds and matching ROC-AUCs, plus A/B/C recomputed from the model. A missing recorded Git commit is an error. `make evidence-check RUN=submission/evidence/runs/RUN_ID` repeats validation locally; `LOCAL=1` explicitly permits a rehearsal environment.

**Scope:** unkeyed hashes establish internal consistency, not signed execution attestation; an operator can rewrite a log and its manifest together. The CI does not rerun measurements on s390x, prove provider identity, or replace teammate review. The first actual s390x run, Community Cloud screenshots, labs, approved AI declaration and narrated video remain open. Preserve failed runs on diagnostic branches; include only approved valid runs in a release PR, because strict checks reject any included failed/rehearsal run. After independent review and merge, update README/deck/site from that run's summary, keeping environment and commit labels.

## 2b. Verify, start and measure manually

`03_test_stack.py` is library preflight. `05_test_claims.py` runs the actual project tests and saves provenance under `submission/evidence/instance/`; `make instance-claims` uses a configured host environment. Without host Python setup, use `make verify-docker`.

```bash
make verify-docker
make image-inspect
make demo-docker
make measure-docker FINAL=1
make measure-api-docker FINAL=1
docker image inspect -f '{{.Id}}' screening:demo screening:dev
```

Keep output JSON/MD and screenshots. `FINAL=1` requires an identifiable clean code commit. The API measurement also requires matching remote code/model. Records include hashes for executed code, model, splits and input data, plus image identity and environment. Architecture `s390x` is insufficient to identify the provider; a Community Cloud dashboard capture is required. Record `lscpu`, `cpacfinfo` where available, CLI OpenSSL and the OpenSSL used by `cryptography`.

The English package/API changed to `screening` / `screening-paillier-v2`. Rebuild both containers together; an old Spanish endpoint is not a compatible peer. Generate credentials in an appropriate external directory and keep existing deployments' vaults and keys paired.

## 3. View the UI through SSH

**Frontend placement:** the Hospital process serves both the interactive form and its API. Its vault is the persistent Docker volume mounted at `/var/lib/screening`, with the AES key outside the repo. The separate public pitch/forecast/plan stays on Netlify. See [DEPLOYMENT.md](DEPLOYMENT.md) for ownership and storage details.

The hospital binds to VM loopback by default. From the laptop:

```bash
ssh -L 8080:127.0.0.1:8080 USER@VM_IP
```

Open `http://127.0.0.1:8080`. Keep English labels and environment visible in the recording; use synthetic inputs only. `SCREENING_UI_PORT` can select another local Compose host port.

## 4. Capture evidence without secrets

| Evidence | Command or source |
|----------|-------------------|
| VM provider identity | LinuxONE Community Cloud dashboard, with access secrets hidden |
| Architecture | `uname -m` and `lscpu` |
| CPACF availability | `cpacfinfo -a` where installed |
| CLI and application OpenSSL | `openssl version -a`; measurement `openssl_of_cryptography` |
| Running containers | `docker compose -f docker/compose.yml ps` |
| Service-mounted files | `docker compose -f docker/compose.yml exec service ls /run/screening` |
| Operational logs | `docker compose -f docker/compose.yml logs service` |
| Synthetic UI and loaded model | Browser through SSH tunnel; `/api/state` |
| Effective package versions | `docker run --rm screening:dev dpkg -l 'python3-*'` |
| Model execution and resource use | Verification/measurement outputs and CPU/memory capture |

CPACF can accelerate AES, not Paillier. Do not claim measured hardware acceleration, Secure Execution or protection from the host administrator without actual evidence.

## 5. Final evidence record

Copy `submission/evidence/linuxone/RECORD.example.json` to `RECORD.json`; fill the actual owner/date and real screenshot names. Save new measurements under `submission/evidence/metrics/`. `make package FINAL=1` checks required records, substantive measurement results, clean provenance and actual PNG/JPEG files. It cannot certify screenshot content or an organizer decision.

## 6. Commit and hand off

Commit measurements and VM evidence. Update US-2.5, US-2.6, US-6.2 and US-6.3 only when their evidence exists. Replace local deck/script figures with actual VM results, preserving environment/version labels. Any code edit changes the source hash; earlier measurements remain evidence of their own commit. Follow [DELIVERY_PLAN.md](DELIVERY_PLAN.md) for freeze/submission deadlines.
