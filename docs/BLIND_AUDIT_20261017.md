# Fresh evidence audit — October 17, 2026

## Verdict

**The time-series dashboard is a working exploratory demo. The complete project is not ready for final submission.** A sourced budget and the original extended E5 feature list are not complete. The immediate priority is the final English LinuxONE evidence, labs/review/disclosure records, narrated video and submission access.

This audit used the current remote, repository, actual public browser, fresh tests and a full forecast rerun rather than treating earlier status statements or screenshots as acceptance. It is an automated code/evidence review, not an independent teammate's approval or an organizer eligibility decision.

## Current release and deployment

- PR 9 merged at **October 17, 20:12 UTC / 16:12 EDT** as `d71d3635c05ca9209a3195eef76cfb8e2c26a45c`, by `jrebull`. No GitHub review is recorded.
- Baseline main passes **90 tests**, reproduces the screening model exactly on macOS, and has successful GitHub verify/image checks. The English implementation is in main; earlier instructions saying main was Spanish are historical.
- Production `https://antimarrulla-tamizaje.netlify.app/forecast` returns HTTP 200 and renders in English. The public forecast JSON matches the repository **byte for byte**. Production plan was rev 31 at the start of this audit.
- Netlify transforms HTML links/injects its badge, so HTML byte inequality alone is not evidence of a stale application. The actual browser was tested.
- Audit corrections are isolated on `codex/blind-status-audit`, submitted separately for review. The production baseline and corrected preview are distinct releases.

## What was independently exercised

| Area | Result |
|------|--------|
| Public dashboard | All **222** combinations: 2 types × 3 sex categories × 37 geographies; chart, totals, evaluation and normal illustrative budgets rendered without NaN/undefined values |
| Corrected dashboard | All 222 combinations checked again, including four quarterly budget rows and annual scenarios; no normal rendering failures |
| Budget controls | No budget without both cost/source; extreme overflow rejected after correction; illustrative UI cost 100 is not a sourced project cost |
| Failed data load | An isolated 404 fixture shows a readable error and disables unusable controls |
| Mobile | Actual 390 × 844 viewport; document width 390, cards 358 pixels, no horizontal page overflow |
| Forecast reproduction | Complete 222-series forecast and nested evaluation rerun; every series and metadata value match after canonical `(kind, level, id, sex)` ordering. Array order differs because of the historical language migration; numbers do not |
| Input quality | All 222 current fitting arrays are finite, weekly and complete; **zero missing observations** |
| Host verification after corrections | **97 passed**; screening model retraining exact |
| Ubuntu apt route after corrections | **93 passed, 4 skipped**; skips require Git, absent from the image. This is arm64, not s390x evidence |
| Isolated app containers | A/B/C synthetic smoke passes; image contains model/UI and excludes CDC, tests, sklearn and private keys |
| Synthetic evidence rehearsal | **20/20 exact integers**, `REHEARSAL PASSED`; same host, not evidence of two real hosts or LinuxONE |
| Submission gate | Final packaging rejects missing original VM/lab/video/review/disclosure records, as it should |
| Presentation structures | Three PPTX archives intact, with 8/19/17 slides. Existing render evidence retained; this audit did not claim a new visual review in PowerPoint |

Evidence: `submission/evidence/local/blind_forecast_ui_checks.json`, `blind_forecast_reproduction.json`, `blind_audit_validation.json`, `blind_forecast_dashboard.png` and `blind_forecast_mobile.png`.

## Findings and corrections

| Priority | Finding | Resolution |
|----------|---------|------------|
| P1 | In audit mode, service HTTP 200 was sent before wire evidence/log capture. A fresh full test failed because a successful request's evidence file did not yet exist | Capture before acknowledging success; return HTTP 503 if evidence storage fails. New regression verifies the failure path. Exact response bytes are reused for capture and transmission |
| P1 | Full-series interpolation before model selection/outer cuts could use holdout values for a missing observation immediately before a cut | Current data have no gaps. Reject missing/non-finite observations and nonweekly calendars until fold-local imputation is implemented. Current inputs, model selections and forecast values stay unchanged |
| P2 | A valid numeric input such as `1e308` generated `$∞` budget totals | Require finite unit cost/products in the UI; reject nonpositive/non-finite cost and blank source in the forecasting CLI |
| P2 | Documentation promised quarterly costs, but the UI only showed annual budget scenarios | Add four quarterly base-budget rows; label the source as user-supplied and unverified |
| P2 | Failed forecast download left a largely empty screen without a useful explanation | Check HTTP status and show a loading/failure state |
| P2 | Quarterly sums differed slightly from the aggregate without an explanation in the dashboard | Explain independent weekly rounding. In current output 177/222 series differ by at most six cases; no forecast values were rewritten |
| P2 | Residual Spanish error/log/fallback labels, archive suffix and clock element IDs remained | Translate those authored labels/IDs consistently; preserve actual raw source names and historical evidence |
| P2 | Some current instructions still described main as untranslated or awaiting the PR 9 merge | Record the actual merge while keeping the missing independent review open |

Evidence-mode acknowledgment now includes evidence-capture work before the client receives success. `service_ms` remains model-evaluation time; client latency and pure compute are still distinct operations. Preserve earlier measurements under their original version and scope. New source hashes require the agreed final commit at both endpoints and the measurement client.

## Is E5 at 100%?

| Scope | Status |
|-------|--------|
| Existing 222-series exploratory forecast demo | **Ready to demonstrate**, with limitations visible |
| Filters, 52-week horizon, bridge weeks, chart/bands, quarterly cases and evaluation | Implemented and exercised |
| Interactive quarterly/annual budget calculator | Implemented after audit fixes; uses user assumptions |
| Real project budget with documented unit cost | **Open**: artifact `unit_cost_mxn` and `source_cost` are null |
| Calibrated 80/95% coverage | **Not established**; bands explicitly exploratory |
| Original extras: map, combined T1+T2, SARIMA/Prophet, LinuxONE E5 fitting | **Not implemented**; freeze this optional scope for delivery |

The published horizon is October 19, 2026 through October 11, 2027, preceded by eleven bridge weeks after the last observed week, July 27, 2026. No new observed data were invented.

T2 national/all outer evaluation gives **9.11% SMAPE for h12–63**. The **6.93%** value is model-selection error, not that separate evaluation. Level-average h12–63 SMAPE is 13.07% national, 25.03% regional and 59.70% state across types/sexes; sparse T1 series inflate the state average. Two overlapping outer origins provide limited evidence.

Nominal 80% bands actually cover 63.6% nationally, 65.3% regionally and 63.2% at state level; nominal 95% coverage is 86.5%, 80.9% and 79.1%. Retain the exploratory label. Signed-error central bands can exclude the point prediction in six 80% series; this is not a lower/upper crossing, and must not be cosmetically changed to imply better calibration. Sum-of-upper-band scenarios are not joint annual intervals.

## Required work still open

The original Carlos audit JSON/Markdown, complete timing distributions and executed host/version/provider evidence are absent from the repository. The supplied 10/10 and 200/200 graphic remains a reported result. Álvaro's supplied UI reports s390x but shows legacy Spanish v1; it is not final English v2/provider verification.

Final mode also lacks real `submission/evidence/linuxone/RECORD.json`, both lab records/screenshots, final public <=180-second video with authorized English audio, full independent teammate review and the team-approved published AI declaration. Attendance/leader/submission confirmations remain to be established. The existing silent draft, screenshots and partial clone check do not close these requirements.

The factual coding/labs chronology remains open in `TIMELINE.md`; this audit does not infer a waiver or disqualification.

## Where Javier should go next

1. **Coordinate one final version and evidence handoff.** Have another member review the audit-fix PR; agree on a single commit. Carlos preserves/uploads the original 200-record audit and runs final process/API measurements with Álvaro on that version. Álvaro captures actual English UI, provider, architecture, containers, model and OpenSSL evidence.
2. **Record with Yazmin now.** Rehearse the existing English script, record authorized narration and assemble the <=180-second video as actual VM footage arrives. Use synthetic record wording. E5 can appear briefly as an optional planning demo; it should not displace the encrypted flow.
3. **Secure submission logistics.** Confirm the registered Hack2Skill leader/dashboard, all four members, real lab/attendance records and the team's AI-publication decision. Then rerun the final package gate, review public links and submit.

Internal submission target: **October 18, 09:00 EDT / 07:00 Ciudad Juárez / 13:00 UTC**. Hard deadline: **12:30 EDT / 10:30 Ciudad Juárez / 16:30 UTC**. Keep the 3-hour-30-minute buffer.
