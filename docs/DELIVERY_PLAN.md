# Delivery plan and immediate team actions

> Updated October 18, 2026. Local implementation is verified. LinuxONE evidence, both labs, independent teammate review, the final video, and the English release review remain open. Reports in chat are not completion evidence. Story status lives in `site/status.json`.

## Evidence runner preflight gate

**Linux measurement ownership hotfix:** measurement clients must run with the invoking host UID/GID. If an older run fails sanitizing `measurement_api_*.json` with PermissionError, preserve its metrics/logs and repair ownership as documented in [LINUXONE.md](LINUXONE.md#measurement-file-ownership-recovery). Retry profile 20 from fixed main before the larger profiles; incomplete runs are not final evidence. This Makefile-only runtime-launch fix preserves screening/model hashes.

**Do not launch the closing run from `516bb59`.** The [preflight audit](EVIDENCE_PREFLIGHT_AUDIT.md) reproduced false acceptance of a one-patient run and an unavailable commit, incomplete private-key redaction, and weak smoke/system/publication checks. PRs 19–21 harden these gates, configure the benchmark profiles and prepare the Hospital frontend. The captain has authorized their ordered integration into main after validation and green CI; independent teammate technical review remains open (see REVIEW.md). Pin the resulting main commit for both containers, client and recording. No final s390x measurement was launched during this audit.

Hospital frontend readiness: individual A/B/C/random/custom paths and actual 20/200 browser batches validated locally; large counts tested by simulation only. Progress, stop-on-failure, cancellation, source identity/exactness, command copy and export are prepared. Rebuild the latest reviewed source on the VM; no new LinuxONE evidence is claimed. [Readiness matrix](FRONTEND_READINESS.md).

Prepared test sizes: **20 / 200 / 2,000 / 16,000**, with exact declared counts and diagnostic/release scope. `make evidence-suite PY=python3` runs all four in order; `make demo-test N=20 FINAL=1` is the short synthetic API demonstration. The larger CDC profiles use 200 deployed API requests by default; `API_N=16000` explicitly requests the longer API test. See [BENCHMARK_PROFILES.md](BENCHMARK_PROFILES.md). No 16,000-record test result is claimed from the supplied chat.

Carlos and Álvaro: first verify the reviewed runner, host Python 3, Docker/Compose, Git identity and push credentials; then run `make evidence-run PROFILE=20 PY=python3` on the real VM. If it passes with zero checker errors, continue with PROFILE=200, PROFILE=2000 and finally PROFILE=16000. The 2,000-record run is the required release-sized baseline; 16,000 is the larger comparison. Do not run evidence-suite after already completing 20 unless intentionally repeating it. Javier: coordinate independent review, provider/lab records, AI publication decision and video. Preserve failed runs as diagnostics; never promote a Mac rehearsal or consistency check into LinuxONE/provider evidence. Authored output labels and the code ZIP now include the evidence tooling; these fixes change the executable source hash while preserving model weights.

## Confirmed submission window

Source: the event notice supplied by the team captain, **IBM Z Datathon — Project Submissions (LIVE NOW)**, for [Hack2Skill](https://hack2skill.com/event/datathon-2026).

| Milestone | UTC | EDT (New York) | Ciudad Juárez | SAST |
|-----------|-----|----------------|---------------|------|
| Submissions open | October 16, 23:45 | October 16, 19:45 | October 16, 17:45 | October 17, 01:45 |
| Internal submission target | October 18, 13:00 | October 18, 09:00 | October 18, 07:00 | October 18, 15:00 |
| Submissions close | **October 18, 16:30** | **October 18, 12:30** | **October 18, 10:30** | **October 18, 18:30** |

The portal is already open. The registered team leader should open the submission dashboard now and check access and required fields. Submit by the internal target, leaving a 3-hour-30-minute buffer. This notice establishes the submission window; it does not establish the permitted coding start or waive the labs prerequisite. Preserve the factual history in [TIMELINE.md](TIMELINE.md).

## Mandatory English release requirement

**All authored project material must be in English:** source code identifiers and comments, docstrings, tests, logs and error messages, command help, UI labels, website and plan, documentation and notebooks, diagrams, slides/PDF, video narration/captions, and the Hack2Skill submission. This is the captain's instruction; it is not attributed to an event rule without evidence.

Proper names, the required submission title, verbatim quotations, original source datasets and their official identifiers retain their original spelling. Explain source fields in English. Preserve historical evidence, timestamps, commits and measured JSON unchanged; translate through new versioned outputs rather than rewriting evidence. Existing Spanish code/module names and contracts require a coordinated migration with imports, CLI/Makefile references, schemas, tests and documentation updated together.

**English implementation and existing artifacts are complete and verified.** Code, tests, messages, UI, website, documentation, three decks, PDF, flowchart and the 170-second silent editing draft are translated. See [ENGLISH_MIGRATION.md](ENGLISH_MIGRATION.md). **US-7.9 remains in progress for final English narration and independent teammate sign-off.** It is a release gate, not an optional feature.

| English workstream | Owner | Acceptance evidence |
|--------------------|-------|---------------------|
| Code, identifiers, comments, tests, CLI, API/log messages and runtime contracts | Carlos and Álvaro; Javier integrates | Reviewed diff; imports and contracts updated together; `make verify` and `make verify-docker` pass on the translated commit |
| README, technical guides, notebooks, data explanations and AI declaration | Javier with each technical owner | English review of all authored release files and resource links; source names preserved |
| Demo UI, public site, dashboard and plan | Javier; Yazmin reviews wording | Browser walkthrough of both demo and public pages, including validation errors and evidence details |
| Pitch deck, PDF, diagram, video and submission text | Yazmin and Javier | English slides/diagram and narration; PDF visually checked; video <=180 seconds; public links verified |

Freeze the translated code commit **before** the final LinuxONE measurement and video capture. Translation changes source hashes even when the algorithm is unchanged. Keep local measurements from `65ae4ef` labeled as that version; rerun final evidence against the release commit. Complete the English review alongside the LinuxONE work, before the H20 freeze; after H20, fix remaining language defects without adding features.

## Current audited status — October 17

The English release and audit corrections are merged into main (`679c287`, PRs 9 and 11). PR 11 includes Yazmin's PR 10 UI corrections and was merged by jrebull on October 17 at 20:42:57 UTC. Neither merge has a recorded independent GitHub review. A subsequent remote update merged Carlos's PR 12 as main `b04fadb` and opened Yazmin's PR 13. The original legacy remote audit is now available; see [CARLOS_REMOTE_AUDIT.md](CARLOS_REMOTE_AUDIT.md). PR 13 was subsequently merged by jrebull at 21:24:20 UTC as current main `ef1e21d`; it also includes calibration, decision and browser-session charts. Yazmin retains visual review/video ownership. E5 is ready as an **exploratory forecast demonstration**, while its sourced budget remains open; freeze its optional scope. See [PLAN_AUDIT_20261017.md](PLAN_AUDIT_20261017.md) for all story groups, ownership and remaining gates.

Merged audit corrections save evidence before successful HTTP acknowledgment, reject missing forecast observations until fold-local imputation exists, and improve budget validation, quarterly display, loading errors and English text. They preserve model/forecast values but changed runtime source hashes. PR 12 then changed the runner/host identification; agree on a current main release with runtime content `ef1e21d` or a later coordinated runtime for new VM evidence. PR 13 changed the runtime HTML hash. The diagram/documentation branch does not change screening runtime code or require rerunning numerical measurements solely for those docs.

**Unclaimed documentation work now advanced by Javier/Codex:** the public diagram atlas, storage dictionary, plan reconciliation and links from the project/forecast pages. See [SYSTEM_DIAGRAMS.md](SYSTEM_DIAGRAMS.md). This expands the requested explanation without taking over Carlos/Álvaro's active measurements or Yazmin's video work. No additional forecasting feature, SQL migration or public Hospital endpoint is scheduled.

**Javier’s next action is delivery coordination and recording:** preserve Carlos's full original log directories (the compact audit is now tracked) and obtain actual English VM captures from Álvaro; confirm leader/dashboard access and real lab/attendance records; rehearse and record the English script with Yazmin; resolve the team’s AI-publication decision. The remaining blockers are evidence and final deliverables, not an absent time-series demo.

## Where to start now

Minute-by-minute closing timeline, on-screen run of show and judge Q&A: [DEMO_RUNBOOK.md](DEMO_RUNBOOK.md).


**Javier / coordination: use the next 30 minutes to secure the release, real VM evidence and the video.** Yazmin's form and PR 10 polish are integrated into main through PRs 9/11; US-6.4 is complete for synthetic inputs. Confirm the registered leader/dashboard access; pin the resulting main release containing PRs 19–21 before the final measurements; secure a human review; collect original lab/attendance and Carlos audit records; rehearse the English script with Yazmin. Protect the submission buffer. The website diagrams can be reviewed independently while the runtime remains stable.

| Priority | Owner | Next concrete action | Completion evidence |
|----------|-------|----------------------|---------------------|
| 1 | Carlos, with Álvaro | Agree on the translated release commit; run `make verify-docker`, `make demo-docker`, `make measure-docker FINAL=1` and `make measure-api-docker FINAL=1` on the real VM | Measurement JSON/MD, commit and hashes, Community Cloud dashboard and screenshots declared in `submission/evidence/linuxone/RECORD.json` |
| 1 | Whole team; Javier coordinates | Confirm both labs and attendance with real dates; decide whether to send the factual question to the organizer | `submission/evidence/labs/RECORD.json`, screenshots and organizer response if applicable; never alter history |
| 1 | English workstream owners | Review the completed English migration; finish narration and teammate sign-off for US-7.9 | English review of code/comments, UI, documentation and deliverables, with tests on the final commit |
| 2 | Teammate other than the author | Run the pinned clone and review protocol, keys, data, limits and the language migration using `docs/REVIEW.md` | GitHub review and record with name, date, commit and commands; no self-approval or AI approval as a team member |
| 2 | Yazmin and Javier | Record the model and demo on LinuxONE, record English narration and assemble a 170–180-second video | Audio/video file, `ffprobe` duration, public link tested without a login and `submission/VIDEO_RECORD.json` |
| 3 | Carlos, with Álvaro | Preserve Carlos's 200-record legacy laptop/server audit and full original log directories; collect provider evidence and a separate final English run | [Original audit reconciliation](CARLOS_REMOTE_AUDIT.md): 200/200 exact, ten reported checks pass, p50 606.919 ms, p95 804.967 ms, mean 650.537 ms. Historical source/model hashes match Git. Full original logs, provider evidence and final English versions remain required; US-6.5 stays open. |
| Done locally | Yazmin; Javier integrates | PR 8 grouped, coded form integrated with English v2; move to the English video and visual review | docs/YAZMIN_INTEGRATION.md; synthetic desktop/mobile screenshots. Does not certify clinical usability or LinuxONE execution. |
| 4 | Javier and all four teammates | Pin the final version; align PDF/site/script; confirm AI attribution; build the final package and submit through the registered leader | English gate complete, `make package FINAL=1`, working public links and Hack2Skill confirmation screenshot |

## Final numerical comparison

Carlos's requested last test should compare floating-point, fixed-point and Paillier **screening** predictions on the same labeled CDC sample; E5 forecasting is a separate unencrypted module. Use the reviewed current cdc19-v1 runtime at both endpoints/client. The old `ef1e21d` checkpoint predates the 19-feature release and is not the final-run pin. Fetch and pin the agreed commit; rebuild both endpoints and the measurement client together. Earlier reports saying main was Spanish or the audit PR was unmerged describe earlier checkpoints. Preserve the original remote-run outputs before rerunning. See [latest Carlos report](../submission/evidence/two_hosts/carlos_20261017_audit_summary_reported.md).

## Latest server progress and demo identifiers

Álvaro’s supplied screenshot shows the legacy Spanish v1 UI reporting Linux s390x, service `ok` and synthetic C at 66.3%. This is partial progress; it does not establish provider identity or final English v2 execution. [Evidence record](../submission/evidence/linuxone/alvaro_20261017_legacy_ui_reported.md). Álvaro and Carlos should preserve that run, rebuild both peers from the reviewed English release, and capture the English UI plus complete provider/version/measurement evidence.

The team abandoned collecting real CURPs from the web. Demo patients and identifiers remain synthetic; use the existing random request IDs. Do not add identity fields to the 19-feature model.

## Frontend and storage deployment decision

Serve the interactive form and API together in the Hospital container on the approved shared VM. Keep the encrypted vault in Hospital’s persistent Docker volume and its key outside the repository. The public presentation, aggregate map, forecast and plan stay on Netlify. Team members reach Hospital through SSH; a public interactive prototype is optional and remains unimplemented. Owners and exact flow: [DEPLOYMENT.md](DEPLOYMENT.md). This placement decision does not establish completed LinuxONE deployment or measurements.

## Commands and scope

Follow [LINUXONE.md](LINUXONE.md) for VM instructions. The project-specific check is `make instance-claims`, or `python tests/instance/05_test_claims.py` with the configured Python environment. It imports the real code and saves provenance in `submission/evidence/instance/`. Direct invocation does not install dependencies; the VM operator may use `tests/instance/run_all.sh`, which includes installation.

The English release uses coordinated English command and protocol names. `make measure` compares floating point, fixed point and Paillier on the same CDC sample and times the plaintext/fixed-point logit in microseconds per patient. Encrypted evaluation is measured separately from encryption, network, decryption and the vault. Plaintext logit cost and a full HTTPS round trip are different operations.

The demo and two-host rehearsal use **synthetic inputs by default**. `DATA=cdc` explicitly selects publicly anonymized CDC data for benchmarking. Synthetic inputs verify numerical correctness and transport; they do not have invented clinical labels or AUC. The approved MVP uses two containers on one VM with the host administrator inside the trust boundary. A second VM remains optional.

## Checkpoints and fallback

| Checkpoint | EDT (New York) | Ciudad Juárez | Decision |
|------------|----------------|---------------|----------|
| H12 check | October 17, 21:00 | October 17, 19:00 | If the real LinuxONE flow is missing, pause form polish, second VM, Granite and CKKS; focus Carlos and Álvaro on the MVP |
| H18 demo | October 18, 03:00 | October 18, 01:00 | Capture the English demo and evidence; freeze video scope |
| H20 freeze | October 18, 05:00 | October 18, 03:00 | Fixes, documentation and editing only; no new features |
| Internal submission target | October 18, 09:00 | October 18, 07:00 | Registered leader submits after all four review |
| Confirmed portal deadline | October 18, 12:30 | October 18, 10:30 | Hard deadline; keep the 3-hour-30-minute buffer |

If the second VM fails, use the one-VM MVP without claiming host separation. If form polish fails, use the existing synthetic profiles and 19-feature editor, translated into English. If a sourced unit cost is missing, E5 keeps exploratory case forecasts and bands without a budget. Missing screenshots, narration or LinuxONE runs must remain open with an owner; a draft or Mac measurement does not replace them.

Respect the existing rest rota in [ROLES.md](ROLES.md). Before resting, leave a commit, status and the next owner. Branch updates are not production releases. Keep Netlify and its badge.
