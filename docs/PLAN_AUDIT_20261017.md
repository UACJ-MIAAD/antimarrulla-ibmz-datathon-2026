# Plan audit and ownership handoff — October 17, 2026

Scope: all 40 existing stories, required delivery checklist, actual remote history, final package gates and requested public system diagrams. This is an automated evidence audit, not an independent teammate approval. Story counts are progress indicators, not release readiness.

## Remote and integration status

The remote check found main at **679c287**, including English PR 9, the PR 11 audit fixes and Yazmin's PR 10 UI corrections. PR 11 was merged by jrebull at **20:42:57 UTC / 16:42:57 EDT**. That initial check was superseded during validation: Carlos's PR 12 merged as **b04fadb** at 21:00:21 UTC, adding concurrency, macOS host identification and a raw legacy two-host report. Those main changes are integrated here. Yazmin's **PR 13** (`feat/demo-ui-redesign`) subsequently merged at 21:24:20 UTC as **ef1e21d**, with passing CI and no independent GitHub review. This update includes that main version; Yazmin keeps visual-review/video ownership. Pin its changed runtime HTML hash before final measurements. No independent GitHub review is recorded for PRs 9/11/12/13. Earlier status saying audit fixes awaited integration is stale and has been corrected in the current plan.

## All story groups reviewed

| Stories | Evidence assessment | Next action / owner |
|---------|---------------------|---------------------|
| US-1.1–1.5 | Repo, decisions, source preparation and mart exist | Preserve source provenance and limits; Javier |
| US-1.6 | Attendance remains unconfirmed | Obtain actual confirmation from all four; Javier coordinates |
| US-1.7 | Download/check and exploratory ENSANUT preparation exist | Keep separate from MVP clinical validation; no new experiment |
| US-2.1, 2.5, 2.6 | Reported server run and legacy s390x UI exist; complete provider/version/transport/measurement evidence absent | Álvaro supplies original English VM evidence and record |
| US-2.2 | Both lab completion records/screenshots remain missing | Actual dates/owners/evidence from participants; preserve chronology |
| US-2.3 | Optional CKKS availability/build not completed on s390x | Defer; Paillier is the approved delivered path |
| US-2.4 | Key separation implemented and tested in local containers | Do not imply protection from the shared VM administrator |
| US-3.1–3.3 | Model, fixed-point protocol and same-sample local numerical comparisons exist | Carlos reruns final process/API measurements on the agreed real VM version |
| US-3.4 | Granite is unimplemented | Defer; retain current factor explanations |
| US-3.5 | Separate reduced ENSANUT experiment is recorded | Keep transfer and calibration limitations visible |
| US-4.1 | Shared splits exist; owned EDA review is still open | Yazmin closes with an authored/reviewed analysis; do not fabricate completion |
| US-4.2–4.3 | Sourced figures and aggregate map exist | Keep geography/population distinctions and ratio limits |
| US-5.1–5.3, 5.5 | 222-series pipeline reproduced; dashboard combinations checked | Freeze exploratory demo scope; remove stale claim that current data were interpolated |
| US-5.4 | Calculator works; project unit cost/source are null | Remains open; Yazmin supplies a defensible source only if already available |
| US-6.1, 6.4 | English synthetic UI, coded form and PR 10 polish are implemented | Preserve baseline; final footage belongs to the VM/video stream |
| US-6.2–6.3 | Complete local flow; final English VM rehearsal/evidence missing | Álvaro/Carlos execute; Javier coordinates recording |
| US-6.5 | Original legacy report now supplied in PR 12: 200/200, 10/10, p50/p95 and matching historical source/model hashes; full wire-log directories absent | Carlos preserves full original logs and provider/version provenance; optional second host cannot block the one-VM MVP |
| US-7.1, 7.4, 7.7 | English deck/PDF and original optional flowchart exist | Add requested web atlas separately; final VM screenshots remain US-7.2 |
| US-7.2–7.3 | Local screenshots and silent 170-second draft exist | Yazmin/Javier replace VM placeholder, record authorized English audio, verify public video |
| US-7.5 | Public reproducible code exists; final evidence/review incomplete | Secure teammate review and final version; Javier coordinates |
| US-7.6 | Submission and registered-leader confirmation not established | Leader checks dashboard, all four review and submit before internal target |
| US-7.8 | Hospital UI is reachable by team SSH; public interactive prototype is absent and optional | Do not expose the Hospital API to finish an optional checkbox |
| US-7.9 | English implementation complete; narration and independent sign-off still open | Human English release review and real English footage/audio |
| New US-7.10 | Requested web system/component/data diagrams | Javier/Codex owns static explanation and validation; no runtime or model change |

## Work advanced without taking over active teammates

1. Build a public atlas with ten source-referenced SVG diagrams and readable text equivalents.
2. Document the actual encrypted vault schema and aggregate file relationships. No invented SQL database or patient linkage.
3. Link the atlas from the home page and forecast dashboard, including mobile-accessible entry links.
4. Reconcile merged PR status, current test counts, forecast gap handling and diagram evidence in the plan/checklist.

The website documentation remains reviewable in PR 14. This does not change the screening runtime hash, trained coefficients, observed data or published forecast numbers. Do not require a fresh 2,000-patient run merely because public documentation changed. Record the actual runtime commit and hashes for final VM runs.

Verification for this update: **98 host tests pass** after integrating PR 12, including its parallel-worker regression, with exact model reproduction; all ten SVGs render with text inside their cards; deterministic rebuild/local file links pass; desktop page width is 1280/1280 and mobile 390/390, with diagram-only scrolling and expandable text. See `submission/evidence/local/system_diagrams_validation.json`. After adding completed US-7.10, the plan has 41 stories: 23 done, 13 in progress, 5 pending. This does not close any release gate.

One low-priority English review item remains in the runtime: `contract.py` contains the developer error string `expected ... pesos` rather than `weights`. Keep it assigned to Carlos's coordinated final English review; this static documentation change deliberately leaves active measurement code unchanged. Do not claim independent language sign-off is complete.

## Required delivery blockers, not optional features

The final package gate currently identifies twelve missing records/checks: process and Hospital API measurements on LinuxONE; four VM screenshots (provider, uname/lscpu, containers, OpenSSL); VM owner/date; lab 1 and lab 2 records; final public <=180-second video with authorized audio; complete independent teammate review; approved published AI declaration linked from the submission text. Attendance, leader access, all-four final review and submission receipt also need human confirmation. A passing machine gate alone cannot establish those external facts.

The original Carlos report now supplies p50/p95; source/model hashes and the example ciphertext request were checked against historical Git. The complete audit cannot be replayed without the full original logs. See [CARLOS_REMOTE_AUDIT.md](CARLOS_REMOTE_AUDIT.md). Earlier screenshots retain their original reported-only scope. The legacy server screenshot reports s390x but does not establish Community Cloud identity or final English v2. Keep both reports without upgrading their status. Coding/labs chronology remains factual and unresolved; no invented waiver or retrospective dates.

## Javier's next 30 minutes

1. Confirm who is the registered leader and open Hack2Skill's submission form. Check required links/uploads before the deadline.
2. Confirm Carlos and Álvaro use current main `ef1e21d` (or the same agreed later runtime), and collect original JSON/Markdown records plus English VM/provider captures. Preserve their current work; do not ask for a new model or new feature.
3. Record the existing English script with Yazmin while VM footage arrives. Show the encrypted screening flow first; E5 is an optional short segment. Show the model and instance explicitly.
4. Obtain actual lab/attendance dates, independent teammate review, and the team's AI-publication decision. These need people; an automated audit cannot complete them.

Internal target: **October 18, 09:00 EDT / 13:00 UTC / 07:00 Ciudad Juárez**. Portal closes **12:30 EDT / 16:30 UTC / 10:30 Ciudad Juárez**. Preserve the 3-hour-30-minute buffer. Defer Granite, CKKS, new E5 models/maps, SQL migration and public Hospital hosting.

Final merged-UI check: native local Hospital and real mutual-TLS service serve PR 13 at ef1e21d. Synthetic C remains 66.3%, with 21 answer rows, 21 ciphertexts plus Enc(z), calibration/session charts and BMI-range validation; a batch of ten random synthetic inputs completes and the 375px UI has no page overflow or console errors. Local Docker rebuild failed because the engine returned HTTP 500, so no new local Docker success is claimed. Prior/new PR CI container results remain separate evidence.
