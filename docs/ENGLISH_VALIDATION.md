# English release validation

Validated on October 17, 2026. This is automated engineering verification, not independent teammate approval or evidence of real LinuxONE execution.

| Check | Result |
|---|---|
| macOS `make verify` | 90 passed; exported model reproduced exactly |
| Ubuntu 24.04 arm64 `make verify-docker` | 86 passed, four Git-dependent tests skipped because the dev image contains no Git executable; model differences <10^-13 |
| Fresh clone with fresh pinned environment | 90 passed; verified source tree identical to migration commit 5412abe |
| Extracted code ZIP `make verify` | 90 passed; all manifest SHA-256 entries verified; source-data README included |
| Minimal app image inspection | Passed: model/UI included; CDC, tests, sklearn and private keys excluded |
| Isolated English container smoke | Three synthetic profiles passed through hospital → mTLS service → decryption → vault |
| Single-host two-host rehearsal | 20/20 exact; explicit REHEARSAL verdict; strict real-host separation remains open |
| Process benchmark, clean code 5412abe | 2,000/2,000 exact; all three AUCs 0.808383; max logit error 4.50×10^-8 within sample bound 7.9×10^-8 |
| Deployed API benchmark, clean code 5412abe | 200/200 synthetic integers exact; client p50 149.015 ms, p95 183.317 ms |
| ENSANUT rerun | Identical except execution timestamp, including model, sample counts and metrics |
| E5 full rerun | All 222 series identical after matching canonical type/level/ID/sex keys |
| Data reproduction | Nine CSV outputs identical byte for byte |
| Preservation | 49 original data/measurement/screenshot files unchanged; archive indexes translated and obsolete templates retired |
| Deliverables | Three English editable decks (8/19/17 slides), official eight-page PDF and one-page flowchart rendered/visually checked |
| Video editing draft | 170.0 seconds, silent; LinuxONE placeholder clearly labeled |
| Browser | English demo/form errors, map, plan filters, slide viewer and forecast/budget controls checked; no current console errors |
| Preview | English Netlify preview, plan rev 26 at 70%; PDF matches local bytes; media URLs versioned |
| Final package gate | Expected rejection: actual LinuxONE/labs evidence, full teammate review, published AI declaration and final narrated public video remain missing |

All new measurements are local Mac/arm64 plus Docker and identify their actual commit, code/model/split/data hashes. Code 5412abe was measured cleanly. Commit b7329c8 subsequently fixes help/console wording and ZIP source-data documentation; it changes no model or inference computation and also passes the full suites. Run the final LinuxONE measurement against the reviewed deployed commit, not against a mixed pair of endpoints.

Original historical evidence remains under `submission/evidencias/`; current evidence and templates use `submission/evidence/`. Private audits, local AI drafts and the personal untracked PowerPoint are excluded from ZIPs and the PR. Neither test success nor portal opening resolves the factual labs-before-coding chronology.

## Review and submission

PR: https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026/pull/9

Preview: https://english-release--antimarrulla-tamizaje.netlify.app

Follow `docs/DELIVERY_PLAN.md`, `docs/REVIEW.md` and `docs/LINUXONE.md`. Another member must review before merge. Final authorized English narration/VM footage and the registered leader's actual submission remain team actions. Internal target: October 18, 13:00 UTC; portal closes 16:30 UTC.
