# Roles, responsibilities and rest rota

> Four team members. Another member must review each PR. Current priorities and English workstreams are in [DELIVERY_PLAN.md](DELIVERY_PLAN.md); story status is in [site/status.json](../site/status.json).

## Current release requirements

The submission portal is open from **October 16, 2026, 23:45 UTC** until **October 18, 16:30 UTC** (12:30 EDT / 10:30 Ciudad Juárez / 18:30 SAST). Keep the internal target of **October 18, 13:00 UTC / 09:00 EDT / 07:00 Ciudad Juárez**. The opening of submissions does not establish the permitted coding start or resolve the labs chronology.

**All authored release material must be in English**, including code, comments, UI, documentation, diagrams, slides/PDF, narration and submission text. Complete US-7.9 alongside VM evidence; pin the translated release commit before final tests, measurements and recording. This is the captain's instruction. Historical evidence and source identifiers retain their original form.

## Team owners

### Javier Augusto Rebull Saucedo — coordination, documentation, integration and submission

- Confirm the registered Hack2Skill leader and dashboard access now.
- Maintain the English README, delivery plan, checklist, source credits and AI declaration with technical owners.
- Integrate English UI/site/plan changes and coordinate the language review; do not mark all material English until reviewed.
- Coordinate independent PR review, H18 demo, H20 freeze and submission after all four review.
- Escalate blockers after 30 minutes and protect the video/submission buffer.

### Álvaro Hernández Jarquín — LinuxONE infrastructure, hospital and encryption

- Provide VM/SSH access for all four and Ubuntu 24.04 Docker support on s390x.
- Complete labs with Carlos and Yazmin; record actual completion dates and screenshots.
- Verify hospital key isolation, mutual TLS 1.3 and the AES-256-GCM vault before the H8 rest block.
- Own the infrastructure/hospital portion of the English code, comments, CLI and log migration with Carlos.
- Run the translated release on the real VM and capture provider dashboard, architecture, containers, OpenSSL and p50/p95 measurements. CPACF acceleration must remain unclaimed unless actually measured.
- Operate the hospital in the optional two-host test and review the final technical checklist.

### Carlos Enrique Gonzalez Moran — ML model, protocol and risk service

- Complete both required labs with Álvaro and Yazmin.
- Own logistic regression, the feature contract (21 features at H5; 19 in `cdc19-v1`), fixed-point weights and Paillier inference; preserve the H11 handoff before rest.
- Lead the English code/test/contract migration with Álvaro, updating imports, callers, schemas and tests together.
- Compare plaintext/fixed-point/encrypted outputs on the same sample and measure plaintext logit cost separately from the full HTTPS flow.
- Run the actual project tests and measurements on the pinned translated LinuxONE release; keep random seeds and dependencies reproducible.
- Granite/CKKS remain optional and unimplemented; resume only after MVP evidence, English release review and video are secure.

### Yazmin Ivonne Flores Martinez — data, English narrative and pitch

- Own CDC exploratory analysis, splits, Mexican statistics and source/population explanations.
- Form implementation US-6.4 is integrated from Yazmin’s PR 8 into English PR 9 and verified locally; see [YAZMIN_INTEGRATION.md](YAZMIN_INTEGRATION.md). Move next to English narration and real LinuxONE demo footage with Javier. Further form polish is optional.
- Translate and review slides, diagram and PDF; assemble the <=180-second English video with Javier.
- Use actual LinuxONE/model footage and versioned measurements; do not relabel local screenshots as VM evidence.
- Keep sensitive data out of the repository and review the English AI declaration and final submission text.

## Existing 24-hour schedule

Internal H0 is **October 17, 07:00 Ciudad Juárez / 09:00 EDT**, distinct from the portal opening. H18 is October 18, 01:00 Juárez; H24 is October 18, 07:00 Juárez, the internal submission target. This rota is retained as planning history; it does not certify that labs preceded coding. Follow [TIMELINE.md](TIMELINE.md) for actual facts.

| Hours | Javier | Álvaro | Carlos | Yazmin |
|-------|--------|--------|--------|--------|
| 0–1 | Scope, decision and owners | VM/repo access | Model plan | Data/pitch plan |
| 1–3 | Collect lab evidence | Labs; Paillier on s390x; optional CKKS check | Required labs | Labs; CDC exploratory analysis |
| 3–5 | Stand-up and UI outline | Two containers | Logistic regression | Splits and feature schema handed to Carlos at H5 |
| 5–8 | Rest | TLS 1.3 and AES-256-GCM vault | Numerical contract; XGBoost only if time remains | Official statistics and map |
| 8–11 | Stand-up; split-screen UI | Rest | Complete encrypted flow before H11 | Impact slide; optional E5/ENSANUT |
| 11–12 | Split-screen UI | Connect the service | Rest | Optional experiments |
| 12–14 | H12 full-flow checkpoint; UI integration; English docs/site | Connected service and VM evidence; English infrastructure review | Rest | English slides and screenshots |
| 14–16 | UI integration; English release coordination | Latency, ciphertext sizes; English code review with Carlos | Same-sample metrics; English code/tests/contracts | Rest |
| 16–18 | Demo readiness; integrate language changes | VM screenshots; optional flowchart | Metrics and service handoff | Rest until H17, then final English script |
| 18 | **Working demo** | | | |
| 18–20 | Rehearsal and English checklist | Final measurements and screenshots | Final metrics table | Backup demo recording; English visual review |
| 20 | **Feature freeze** | | | |
| 20–22 | English README and clean release | Independent technical review | Dependencies and reproducibility | English video, PDF and visual checks |
| 22–24 | Registered leader submits after all four review | Final review | Final review | Final review |

Each person starts an optional extension only after delivering their MVP work. If the H12 request → encrypted evaluation → decryption → UI flow is missing, pause extensions: Álvaro integrates, Javier handles the UI, Yazmin prepares evidence/pitch, and Carlos returns to Paillier after H14. English release work is mandatory and cannot be replaced by an extra.

## Rest rota

| Hours | Resting | On duty |
|-------|---------|---------|
| 5–8 | Javier | Álvaro, Carlos, Yazmin |
| 8–11 | Álvaro | Javier, Carlos, Yazmin |
| 11–14 | Carlos | Javier, Álvaro, Yazmin |
| 14–17 | Yazmin | Javier, Álvaro, Carlos |

Before resting, commit/push, update status and leave the next owner a clear handoff. Javier remains available for the H16–18 demo push and H22–24 submission. Take ten-minute breaks every two hours and reassign work if fatigue affects execution.
