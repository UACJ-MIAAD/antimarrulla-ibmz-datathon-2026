# LinuxONE runbook (s390x)

Actual LinuxONE execution and provider evidence remain **unverified**. Local Mac/Ubuntu containers and GitHub x86_64 CI do not replace them. Owner: Álvaro, with Carlos for measurements. Use the translated release commit throughout. The optional [two-host test](TWO_HOSTS.md) is separate from the approved one-VM/two-container MVP.

## 0. Prerequisites

- [ ] Both required labs completed, with actual dates and screenshots in `submission/evidence/labs/`
- [ ] SSH access for the operator; no private keys, tokens or passwords in Git, screenshots or chat
- [ ] Registered leader and submission access confirmed
- [ ] Same translated commit for hospital, service, measurements and recording

The labs-before-coding chronology remains disclosed in [TIMELINE.md](TIMELINE.md). Do not infer an organizer waiver.

## 1. Prepare the VM

```bash
sudo apt-get update
sudo apt-get install -y git make docker.io docker-compose-v2
sudo usermod -aG docker "$USER"
# Log out and back in before using the Docker group.
git clone https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026.git
cd antimarrulla-ibmz-datathon-2026
git checkout RELEASE_COMMIT
```

Ubuntu 24.04 `python3-*` apt packages support s390x; only pure-Python `phe` is installed through pip in the image. No native pip wheels are required on the host.

## 2. Verify, start and measure

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
