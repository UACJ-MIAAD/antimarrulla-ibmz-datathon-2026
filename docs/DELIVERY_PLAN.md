# Delivery plan and immediate team actions

> Updated October 17, 2026. Local implementation is verified. LinuxONE evidence, both labs, independent teammate review, the final video, and the English release review remain open. Reports in chat are not completion evidence. Story status lives in `site/status.json`.

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

## Where to start now

**Javier / coordination: use the next 30 minutes to secure the release, real VM evidence and the video.** Yazmin’s PR 8 form is now integrated into the English release in PR 9; US-6.4 is complete for synthetic inputs. See [YAZMIN_INTEGRATION.md](YAZMIN_INTEGRATION.md). Confirm the registered leader and dashboard access; agree on the combined commit with Carlos and Álvaro; secure a human review; collect lab/attendance evidence; then rehearse the English script with Yazmin. Protect the submission buffer. Further form polish and optional extensions are lower priority.

| Priority | Owner | Next concrete action | Completion evidence |
|----------|-------|----------------------|---------------------|
| 1 | Carlos, with Álvaro | Agree on the translated release commit; run `make verify-docker`, `make demo-docker`, `make measure-docker FINAL=1` and `make measure-api-docker FINAL=1` on the real VM | Measurement JSON/MD, commit and hashes, Community Cloud dashboard and screenshots declared in `submission/evidence/linuxone/RECORD.json` |
| 1 | Whole team; Javier coordinates | Confirm both labs and attendance with real dates; decide whether to send the factual question to the organizer | `submission/evidence/labs/RECORD.json`, screenshots and organizer response if applicable; never alter history |
| 1 | English workstream owners | Review the completed English migration; finish narration and teammate sign-off for US-7.9 | English review of code/comments, UI, documentation and deliverables, with tests on the final commit |
| 2 | Teammate other than the author | Run the pinned clone and review protocol, keys, data, limits and the language migration using `docs/REVIEW.md` | GitHub review and record with name, date, commit and commands; no self-approval or AI approval as a team member |
| 2 | Yazmin and Javier | Record the model and demo on LinuxONE, record English narration and assemble a 170–180-second video | Audio/video file, `ffprobe` duration, public link tested without a login and `submission/VIDEO_RECORD.json` |
| 3 | Carlos, with Álvaro | Preserve Carlos’s reported 200-record synthetic laptop/server run: collect its hospital summary, final audit and full version/host evidence; run final English evidence separately if needed | [Latest reported summary](../submission/evidence/two_hosts/carlos_20261017_audit_summary_reported.md): image reports audit 10/10 and exact results 200/200; Carlos reports mean 650 ms/record (≈92/min). Original audit, host evidence and matching versions remain required; US-6.5 stays open. |
| Done locally | Yazmin; Javier integrates | PR 8 grouped, coded form integrated with English v2; move to the English video and visual review | docs/YAZMIN_INTEGRATION.md; synthetic desktop/mobile screenshots. Does not certify clinical usability or LinuxONE execution. |
| 4 | Javier and all four teammates | Pin the final version; align PDF/site/script; confirm AI attribution; build the final package and submit through the registered leader | English gate complete, `make package FINAL=1`, working public links and Hack2Skill confirmation screenshot |

## Final numerical comparison

Carlos’s requested last test should compare floating-point, fixed-point and Paillier **screening** predictions on the same labeled CDC sample; E5 forecasting is a separate unencrypted module. Use the reviewed combined English release at both endpoints/client. Main still contains the earlier Spanish implementation at this registration, so a plain pull of main is insufficient. Preserve the current remote-run outputs; collect original audit/measurement artifacts before rerunning. See [latest Carlos report](../submission/evidence/two_hosts/carlos_20261017_audit_summary_reported.md).

## Latest server progress and demo identifiers

Álvaro’s supplied screenshot shows the legacy Spanish v1 UI reporting Linux s390x, service `ok` and synthetic C at 66.3%. This is partial progress; it does not establish provider identity or final English v2 execution. [Evidence record](../submission/evidence/linuxone/alvaro_20261017_legacy_ui_reported.md). Álvaro and Carlos should preserve that run, rebuild both peers from the reviewed English release, and capture the English UI plus complete provider/version/measurement evidence.

The team abandoned collecting real CURPs from the web. Demo patients and identifiers remain synthetic; use the existing random request IDs. Do not add identity fields to the 21-feature model.

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

If the second VM fails, use the one-VM MVP without claiming host separation. If form polish fails, use the existing synthetic profiles and 21-feature editor, translated into English. If a sourced unit cost is missing, E5 keeps exploratory case forecasts and bands without a budget. Missing screenshots, narration or LinuxONE runs must remain open with an owner; a draft or Mac measurement does not replace them.

Respect the existing rest rota in [ROLES.md](ROLES.md). Before resting, leave a commit, status and the next owner. Branch updates are not production releases. Keep Netlify and its badge.
