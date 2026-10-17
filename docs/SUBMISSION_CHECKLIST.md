# Submission checklist

> Owner: Javier (coordination), with Álvaro reviewing technical evidence and Yazmin reviewing video/PDF. Start the final review at H21. Portal closes **October 18, 2026, 16:30 UTC / 12:30 EDT / 10:30 Ciudad Juárez / 18:30 SAST**. Internal target: **13:00 UTC / 09:00 EDT / 07:00 Ciudad Juárez**.

The submission window is **October 16, 23:45 UTC → October 18, 16:30 UTC**, from the event notice supplied by the captain. [Open the team dashboard now](https://hack2skill.com/event/datathon-2026). This confirms the submission window, not the permitted coding start or labs order. Follow [DELIVERY_PLAN.md](DELIVERY_PLAN.md) for owners and fallbacks. Form polish and a second VM remain optional.

## English release gate — mandatory, US-7.9

- [x] Code identifiers, module/file names authored by the team, comments and docstrings are in English; imports/callers migrated together
- [x] Tests, CLI/Makefile help, API/log/error messages and runtime contracts reviewed in English
- [x] README, guides, notebooks, source explanations and AI declaration in English
- [x] Demo UI, public site, forecast dashboard, plan and validation errors in English
- [x] Slides, exported PDF and flowchart in English and visually checked
- [ ] Video narration/captions and Hack2Skill title/description in English; preserve the exact required title and proper names
- [x] Original source identifiers/raw data and historical evidence preserved; English explanations provided
- [x] Automated English code checks pass (90 host; 86 Ubuntu plus four Git-dependent skips); local measurements at clean code 5412abe are recorded. Final LinuxONE measurements/captures still required
- [ ] Independent teammate signs off on the English release and records the reviewed commit

English implementation and existing artifacts are translated and checked; see [ENGLISH_MIGRATION.md](ENGLISH_MIGRATION.md). Final English narration, teammate sign-off, real LinuxONE evidence and submission remain open. Checked boxes describe implementation evidence, not human approval.

## Prerequisites

- [ ] All four completed the [kick-off attendance form](https://forms.gle/hxTYwzJRqgwnWaPn8)
- [ ] Watch the recommended [LinuxONE setup recording](https://www.youtube.com/watch?v=y9rZwSq8pw8)
- [ ] Lab record in `submission/evidence/labs/RECORD.json`, with real dates and screenshots
- [ ] Lab 1: *Predictive AI Hybrid AI scenarios (multi-model)*
- [ ] Lab 2: *Predictive AI + Generative AI*
- [ ] Screenshots of both labs in `submission/evidence/`
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
- [ ] Team approves and publishes its AI-use declaration; the English local draft `submission/AI_USE.md` remains excluded from Git and draft ZIPs
- [ ] All four confirm additional tools/tasks, including the unconfirmed “Muse” entry, and understand the submitted code
- [x] English architecture diagram exists and is visually checked in `submission/flowchart/architecture.pdf`
- [x] Decision document exists in [DECISION.md](DECISION.md)

## LinuxONE evidence

Save real screenshots and records under `submission/evidence/`.

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
- [ ] Public link works without a login; `submission/VIDEO_RECORD.json` completed

## Required PDF and optional material

- [x] English deck exported as **`Los Antimarrulla_IBM Z Datathon 2026 Project.pdf`**
- [x] Align with [submission/SLIDES.md](../submission/SLIDES.md)
- [x] English flowchart included if submitted (optional)
- [ ] Accessible prototype included if submitted (optional)
- [x] Results slide uses real, versioned measurements
- [x] Community impact slide includes sources and appropriate population limits

## Demo rehearsal

- [ ] Timed full rehearsal at H19
- [x] Synthetic demo profiles ready; English labels and validation checked
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
