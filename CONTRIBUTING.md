# Contribution guide · Los Antimarrulla

## 1. Language and release requirements

**All authored project material must be in English**, as instructed by the captain: code identifiers, comments/docstrings, tests, logs/errors, CLI help, UI/site, notebooks, documentation, diagrams, slides, video and submission text. Use English for new commits and PR descriptions.

Keep proper names, the exact required submission title, official source identifiers and verbatim quotations intact. Never rewrite historical commits, dates, measured evidence or raw data to translate them. Explain source fields in English. Coordinate identifier/module/schema changes with every import, caller, CLI target and test; validate the same translated commit before recording final LinuxONE evidence. See US-7.9 and [DELIVERY_PLAN.md](docs/DELIVERY_PLAN.md). The language migration remains open until the team reviews all release material.

## 2. Branches

- `main` must remain runnable. No direct pushes to `main`.
- Use a branch for each contributor or change, such as `javier/coordination`, `feat/base-model` or `fix/demo-crash`.
- Use descriptive prefixes only (`feat/`, `fix/`, `docs/`, `demo/`, `chore/`; `evidence/` is created by `make evidence-run`). Do not use tool or assistant names such as `codex/` or `claude/` in branch names.

## 3. Pull requests

- Every change enters `main` through a pull request.
- **Review by another team member is required.** Read, run and understand the change; self-review is not independent review.
- Prefer small PRs. Split changes larger than approximately 300 lines into reviewable parts when possible.
- Use a clear English title describing the resulting behavior and record relevant verification.
- After H20, accept fixes, documentation and pitch updates only. No new features.

## 4. Commits and history

Use English, in the form `type: description`, for example `fix: reject mismatched remote code` or `docs: update the submission window`.

Commit frequently and keep changes reviewable. Project code must follow the event's permitted coding window. Preserve existing factual history; do not rebase published `main`, force-push, backdate commits or import code from previous projects. Check the system clock. The submission portal opening does not by itself establish the permitted coding start; the unresolved facts are recorded in [TIMELINE.md](docs/TIMELINE.md).

## 5. Notebooks

- VM work must be committed and pushed; files left only on a VM are not release evidence.
- Restart and run all cells before committing; remove oversized outputs.
- Put reusable code in `src/`; notebooks import the project implementation so their results match verification.

## 6. Data and secrets

- Do not commit large datasets or sensitive records. Follow [data/README.md](data/README.md).
- Keep credentials, keys and tokens outside version control, in ignored local configuration.
- If a secret is exposed, notify the team and rotate it before cleaning the exposure. Never print secret values in reports.
- The demo uses synthetic patients. Explicit CDC benchmarks use publicly anonymized survey data.

## 7. Team cadence and submission

Follow [DELIVERY_PLAN.md](docs/DELIVERY_PLAN.md) and [ROLES.md](https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026/blob/archive/working-docs-20261018/docs/ROLES.md).

- Stand-up every four hours; ask for help after 30 minutes blocked.
- H18: working demo. H20: feature freeze.
- Registered team leader submits after all four review.
- Portal window: October 16, 2026, 23:45 UTC through October 18, 2026, 16:30 UTC.
- Internal target: October 18, 13:00 UTC (09:00 EDT / 07:00 Ciudad Juárez), leaving 3 hours 30 minutes.
- Complete the English release review, labs, LinuxONE evidence, independent review and final video before submission.
