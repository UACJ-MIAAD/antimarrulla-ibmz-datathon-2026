# Submission checklist

> Owner: Javier (coordination), with Álvaro reviewing technical evidence and Yazmin reviewing video/PDF. Start the final review at H21. Portal closes **October 18, 2026, 16:30 UTC / 12:30 EDT / 10:30 Ciudad Juárez / 18:30 SAST**. Internal target: **13:00 UTC / 09:00 EDT / 07:00 Ciudad Juárez**.

The submission window is **October 16, 23:45 UTC → October 18, 16:30 UTC**, from the event notice supplied by the captain. [Open the team dashboard now](https://hack2skill.com/event/datathon-2026). This confirms the submission window, not the permitted coding start or labs order. Follow [PLAN_CIERRE.md](PLAN_CIERRE.md) for owners and fallbacks. Form polish and a second VM remain optional.

## English release gate — mandatory, US-7.9

- [ ] Code identifiers, module/file names authored by the team, comments and docstrings are in English; imports/callers migrated together
- [ ] Tests, CLI/Makefile help, API/log/error messages and runtime contracts reviewed in English
- [ ] README, guides, notebooks, source explanations and AI declaration in English
- [ ] Demo UI, public site, forecast dashboard, plan and validation errors in English
- [ ] Slides, exported PDF and flowchart in English and visually checked
- [ ] Video narration/captions and Hack2Skill title/description in English; preserve the exact required title and proper names
- [ ] Original source identifiers/raw data and historical evidence preserved; English explanations provided
- [ ] `make verify` and `make verify-docker` pass on the translated release commit; final measurements/captures use that commit
- [ ] Independent teammate signs off on the English release and records the reviewed commit

These boxes are deliberately open. Translating the plan does not complete the code, deck or video migration.

## Prerequisites

- [ ] All four completed the [kick-off attendance form](https://forms.gle/hxTYwzJRqgwnWaPn8)
- [ ] Watch the recommended [LinuxONE setup recording](https://www.youtube.com/watch?v=y9rZwSq8pw8)
- [ ] Lab record in `submission/evidencias/labs/REGISTRO.json`, with real dates and screenshots
- [ ] Lab 1: *Predictive AI Hybrid AI scenarios (multi-model)*
- [ ] Lab 2: *Predictive AI + Generative AI*
- [ ] Screenshots of both labs in `submission/evidencias/`
- [ ] LinuxONE Community Cloud VM accessible to all four, registered with code `SSF2026`
- [ ] Captain resolves the factual chronology question with the organizer if needed; no invented exceptions or dates

## Repository

- [x] Public GitHub repository (HTTP 200 without a session, checked October 17)
- [ ] Event-window history reviewed with frequent, reviewable commits; chronology issues documented
- [ ] No final all-project dump
- [ ] Branches merged through PRs with another member's review
- [ ] `main` runs end to end
- [x] Large raw datasets and ENSANUT microdata are not tracked (checked October 17)
- [x] No credentials, keys or tokens found in the October 17 review; demo secrets remain outside the repo
- [x] `LICENSE` present

## README and documentation

- [x] Project problem, solution, IBM Z scope and run instructions exist; English review remains open above
- [ ] Quickstart run by a teammate who did not author the code
- [x] Pinned requirements exist; s390x uses the Ubuntu apt route
- [x] Dataset source/license instructions in `data/README.md`
- [x] Open-source libraries and resource links documented
- [x] AI declaration exists separately in [submission/USO_IA.md](../submission/USO_IA.md), linked from the submission text
- [ ] All four confirm additional tools/tasks, including the unconfirmed “Muse” entry, and understand the submitted code
- [x] Architecture diagram exists in `submission/flowchart/arquitectura.pdf`; English review remains open
- [x] Decision document exists in [DECISION.md](DECISION.md)

## LinuxONE evidence

Save real screenshots and records under `submission/evidencias/`.

- [ ] Running VM shown in the Community Cloud dashboard
- [ ] `uname -m` reports `s390x`
- [ ] `lscpu` and `cpacfinfo` if installed
- [ ] OpenSSL CLI version and the library version used by `cryptography`
- [ ] AES-256-GCM measured inside the application; no unmeasured CPACF acceleration claim
- [ ] Plaintext/encrypted numerical error and encrypted sample size measured on LinuxONE
- [ ] Model training on LinuxONE
- [ ] Inference/service running on LinuxONE
- [ ] Containers running on LinuxONE
- [ ] Key handling, encryption and access boundaries shown
- [ ] CPU/memory and timing evidence recorded
- [ ] JSON/MD commit, code/model hashes and image match the translated release

## Required video

- [ ] At most 180 seconds; target 170 seconds
- [ ] English narration and any captions/on-screen explanations
- [ ] Problem, supporting data, solution and IBM Z usage covered
- [ ] Technology stack, LinuxONE instance and model visible on screen
- [ ] Working demo included
- [ ] Recorded during the event weekend
- [ ] Clear audio and authorized voices
- [ ] Public link works without a login; `submission/VIDEO_REGISTRO.json` completed

## Required PDF and optional material

- [ ] English deck exported as **`Los Antimarrulla_IBM Z Datathon 2026 Project.pdf`**
- [ ] Align with [submission/SLIDES.md](../submission/SLIDES.md)
- [ ] English flowchart included if submitted (optional)
- [ ] Accessible prototype included if submitted (optional)
- [ ] Results slide uses real, versioned measurements
- [ ] Community impact slide includes sources and appropriate population limits

## Demo rehearsal

- [ ] Timed full rehearsal at H19
- [ ] Synthetic demo profiles ready; English labels and validation checked
- [ ] Backup demo recording ready
- [ ] LinuxONE session open and working before recording

## Hack2Skill submission

The registered team leader submits from the team dashboard after all four review. [Process walkthrough](https://youtu.be/KIYu1iqtXTU), provided by the SSF SME on October 17: open final submission, enter details/problem, link the GitHub repo, attach/link the <=3-minute video, upload the PDF when requested, review and submit.

- [ ] Registered team leader confirmed and dashboard accessible
- [ ] All four reviewed the final English version
- [ ] Exact title: **`Los Antimarrulla_IBM Z Datathon 2026 Project`**
- [ ] Correct official theme selected
- [ ] English project details and problem statement
- [ ] Public final video link with LinuxONE/model evidence
- [ ] Required PDF uploaded
- [ ] Public repository link, or accepted code ZIP
- [ ] Open-source resource links included
- [ ] Optional flowchart/prototype attached if available
- [ ] All four members linked to the team
- [ ] `make package FINAL=1` succeeds after the English review and other gates
- [ ] Submit by **October 18, 07:00 Ciudad Juárez / 09:00 EDT**, 3 hours 30 minutes before closing
- [ ] Confirmation screenshot saved; final commit recorded: `______`

## Closing and follow-up

- [ ] Virtual closing ceremony: October 17, 23:00 Ciudad Juárez / October 18, 01:00 EDT
- [ ] Feedback survey/video before October 23
- [ ] Winners announcement: October 28, 08:00 Ciudad Juárez / 19:30 IST
- [ ] Team photo
