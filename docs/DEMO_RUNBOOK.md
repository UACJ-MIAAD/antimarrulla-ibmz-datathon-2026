# Demo runbook and closing timeline

Operational guide for the last stretch: what to record, in which order, with which commands, and what to say when judges ask. It complements the [delivery plan](DELIVERY_PLAN.md), the [video script](../submission/PITCH.md), the [video storyboard](../submission/VIDEO.md) and the [LinuxONE guide](LINUXONE.md). It does not change any decision and does not mark anything as done.

## 1. Closing timeline

Status at 2026-10-18 00:00 UTC (17 Oct, 18:00 Ciudad Juárez): `main` (`be9b27e`, model `logistic-cdc19-v1`, 19 features) passes `make verify` (104 tests), `make verify-docker`, the app-image inspection, the containerized demo smoke test (synthetic A/B/C exact) and the same-host two-host rehearsal. `make package` reports only external gaps: LinuxONE measurements and screenshots, both labs, the narrated video, independent review and the AI-use declaration.

| Ciudad Juárez | UTC | Owner | Block | Done when |
|---------------|-----|-------|-------|-----------|
| 17 Oct 18:00–21:00 | 00:00–03:00 | Carlos + Álvaro | Pin the release commit; on the VM run the reviewed `make evidence-run` in §3; capture the four screenshots | Measurement JSON/MD committed; `submission/evidence/linuxone/RECORD.json` filled |
| 17 Oct 18:00–21:00 | 00:00–03:00 | Javier | Labs record with real dates; decide on the organizer question ([TIMELINE.md](TIMELINE.md)); AI-use decision | `submission/evidence/labs/RECORD.json`; AI declaration location decided |
| 17 Oct 18:00–21:00 | 00:00–03:00 | Yazmin | Two timed read-throughs of [PITCH.md](../submission/PITCH.md); slide check | Narration ≤ 170 s with transitions |
| 17 Oct 21:00–01:00 | 03:00–07:00 | Álvaro + Javier | Record segments 5b and 6b on the VM (see §4) | Raw screen recordings saved outside Git |
| 17 Oct 21:00–01:00 | 03:00–07:00 | A teammate who did not author the code | Clean-clone review with [REVIEW.md](REVIEW.md) | Row with name, date, commit and commands |
| **18 Oct 01:00 (H18)** | **07:00** | All | Demo capture complete; video scope frozen | No new footage after this point |
| 18 Oct 01:00–03:00 | 07:00–09:00 | Yazmin + Javier | Edit the video with voices; replace local numbers in deck/PDF/site with the LinuxONE run | `ffprobe` ≤ 180 s; public URL opens without login |
| **18 Oct 03:00 (H20)** | **09:00** | All | Feature freeze: fixes, documentation and editing only | — |
| 18 Oct 03:00–06:30 | 09:00–12:30 | All four | `make package FINAL=1`; all four review the package | Final gate passes with no pending items |
| **18 Oct 07:00** | **13:00** | Registered leader | Submit in Hack2Skill; save the confirmation screenshot | Confirmation stored |
| 18 Oct 10:30 | 16:30 | — | Hard portal deadline | Keep the 3½-hour buffer |

If a block slips, cut in this order: second VM run, form polish, deck refresh with new numbers (keep the local numbers clearly labelled), then everything else. Never cut the LinuxONE footage, the narrated video or the leader's submission.

## 2. Pre-flight before recording

- [ ] Same commit on every machine involved: `git rev-parse --short HEAD`; no local changes in `src/`, `tests/`, `docker/` or `Makefile`.
- [ ] Terminal font ≥ 16 pt, dark theme, window 1920×1080; browser zoom 110 %.
- [ ] No tokens, passwords, private keys, IP addresses you do not want public, or notification pop-ups on screen.
- [ ] SSH tunnel open: `ssh -L 8080:127.0.0.1:8080 USER@VM_IP`.
- [ ] Synthetic profiles only. Say "One synthetic record from the measured run", never "real patient".
- [ ] Microphone checked; room quiet; script open on a second screen.

## 3. Commands on the VM (in this order)

```bash
git fetch origin
git switch -c demo/final-evidence APPROVED_COMMIT
make evidence-run PY=python3
```

`make evidence-run` runs `verify-docker`, `image-inspect`, `demo-docker`, `measure-docker FINAL=1` and `measure-api-docker FINAL=1`, keeps every log and system identity, and pushes the run to a branch `evidence/s390x_n<process>_api<requests>_<UTC>` that CI validates (see [LINUXONE.md §2](LINUXONE.md)). Read the [preflight audit](EVIDENCE_PREFLIGHT_AUDIT.md) first; `516bb59` requires the hardening fix before final use. Output is sanitized and printed after each step. The demo stays up for recording. For a short live terminal test use `make demo-test N=20 FINAL=1` after prewarming the images; run the 16,000-record profile before the pitch ([profiles](BENCHMARK_PROFILES.md)). The individual `make` targets still work for debugging.

Evidence to keep on screen or in screenshots: Community Cloud dashboard with the VM, `uname -m` (s390x) and `lscpu`, `docker compose -f docker/compose.yml ps`, `openssl version -a`, and the measurement summary that ends the API run.

## 4. On-screen run of show (matches the script timings)

| Segment | Time | On screen | Action |
|---------|------|-----------|--------|
| 1–4 | 0:00–1:15 | Slides 1–4 | Narration only |
| 5 | 1:15–1:30 | Slide 5 (architecture) | — |
| 5b | 1:30–1:45 | VM terminal | Show the dashboard tab, then type `uname -m`, `docker compose -f docker/compose.yml ps`, and open `http://127.0.0.1:8080/api/state` to show the loaded model hash |
| 6 | 1:45–1:55 | Slide 6 (results) | — |
| 6b | 1:55–2:15 | Hospital UI through the tunnel | Choose **Synthetic C** → wait for the result (63.3 % with `logistic-cdc19-v1`); point at the 19 ciphertexts on the service side, the risk and factors on the hospital side, and the timing breakdown |
| 7–11 | 2:15–2:49 | Slides 7–11 (screens as B-roll, model, time-series forecast, roadmap, impact) | Optional: two seconds of the live forecast dashboard on slide 8 |

Keep the environment label visible in 6b. If the recording is not from LinuxONE, the label must say so.

## 5. Fallback ladder

1. **VM reachable but slow:** record anyway; timings will be higher (Carlos's laptop → s390x audit measured p50 ≈ 607 ms per record, mostly network). Say "measured on this run", not a benchmark.
2. **VM unreachable:** record the same flow with `make demo-docker` locally and label it "local container run". Show Carlos's approved two-host audit (Mac hospital → s390x service, 10/10 checks, 200/200 exact) as LinuxONE-side evidence, stating it ran the earlier `037ee1b` release with the 21-feature model.
3. **Live demo fails during judging:** switch to the recorded video; do not improvise numbers.

Never relabel a local capture as LinuxONE.

## 6. Questions judges are likely to ask

| Question | Short answer | Evidence |
|----------|--------------|----------|
| What does IBM Z add beyond hosting Docker? | The homomorphic step is heavy modular arithmetic on 2,048-bit keys (4,096-bit ciphertexts); the target is a hardened, isolated platform for the risk service. We have not benchmarked CPACF or claimed hardware acceleration. | [PROJECT.md](PROJECT.md), measurement files |
| What actually ran on s390x? | Carlos's audit: the risk service in a container on Linux s390x, hospital on a separate Mac, 200/200 exact integers, 10/10 checks. That audit used the earlier 21-feature model; the final 19-feature release run is the one recorded tonight. | [CARLOS_REMOTE_AUDIT.md](CARLOS_REMOTE_AUDIT.md) |
| Where are the keys? | Paillier private key only in hospital memory; AES vault key mounted read-only into the hospital; the service has neither. | [System diagrams](../site/architecture.html) |
| Can the service see anything? | It sees ciphertexts, the public key, request IDs, sizes and timing. It never sees feature values or the decrypted score. | Audit checks 4–7 |
| What if the server is malicious? | Out of scope for the demo: mutual TLS authenticates the channel, not the computation; the same-VM administrator is trusted. | [PROJECT.md](PROJECT.md) trust boundary |
| Does encryption cost accuracy? | No for the encrypted step: decrypted integers equal the fixed-point reference exactly; fixed point vs float differs by < 10⁻⁷ in the logit; AUC identical on the same sample. | Measurement JSON |
| How fast is it? | Locally ≈ 0.11–0.12 s per patient end to end with 19 features, dominated by encryption; the remote s390x run was ≈ 0.6 s because of the network. | Measurement files |
| Is it clinically valid in Mexico? | No. It screens a survey label. A separate reduced ENSANUT experiment reached AUC ≈ 0.77 but underestimated risk; recalibration would be required. | [ENSANUT_EXPERIMENT.md](ENSANUT_EXPERIMENT.md) |
| Why logistic regression? | Its score is linear, which Paillier evaluates exactly; non-linear models would need CKKS or other schemes, which we did not integrate. | [PROJECT.md](PROJECT.md) |
| What is E5? | An optional, unencrypted 52-week forecast of notified cases; its bands under-cover and it needs a sourced unit cost for budgets. | [FORECAST.md](FORECAST.md) |

## 7. Claims to avoid

- "Runs on LinuxONE" before the English release run is recorded.
- "CPACF accelerates" anything.
- "Diagnosis", "predicts future diabetes", "validated in Mexico".
- "Nobody can see the patient" without the trust-boundary sentence.
- "Real patient" for any demo record.
