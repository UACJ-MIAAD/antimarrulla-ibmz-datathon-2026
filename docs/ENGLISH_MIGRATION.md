# English release migration

The captain requires English throughout authored code, comments, tests, runtime messages, UI, website, plans, documentation and deliverables. This release migrates the existing implementation together; it does not change the trained coefficients or claim new LinuxONE evidence.

## Coordinated deployment

Deploy hospital, service and measurement client from the same reviewed release commit. The English wire contract is `screening-paillier-v2`; Spanish v1 peers are incompatible and must not be mixed.

| Previous interface | English release |
|---|---|
| `src/tamizaje/` | `src/screening/` |
| `src/datos/` | `src/data_prep/` |
| `artefactos/` | `artifacts/` |
| `protocolo`, `servicio`, `boveda`, `medir`, `verificar` | `protocol`, `service`, `vault`, `measure`, `verify` |
| `make medir`, `make medir-api` | `make measure`, `make measure-api` |
| VM measurement targets | `make measure-docker FINAL=1`, `make measure-api-docker FINAL=1` |
| Two-host rehearsal | `make rehearse-two-hosts` |
| Service evaluation URL | `/v2/evaluate` |
| Hospital endpoints | `/api/state`, `/api/synthetic`, `/api/evaluate` |
| Current evidence | `submission/evidence/` |
| Website status | English keys, `schema_version: 2`, increasing `rev` |

Environment variables now use `SCREENING_*`, `SERVICE_*`, `TLS_CLIENT_*`, `VAULT_*` and `MODEL_JSON`; see [LINUXONE.md](LINUXONE.md) and Docker Compose for exact values. Generate fresh English certificate bundles outside Git. Never mount the hospital private key or vault key at the risk service.

## Preservation and scope

Original datasets, source field names/codes, proper names, source URLs, the team logo and original event documents retain their original spelling. The original `data/` paths remain stable to preserve source lineage. English comments and explanations describe them. Immutable historical measurements/screenshots remain under `submission/evidencias/`; its archive indexes are translated and obsolete templates retired. New records use the English evidence schema. Local audit history and the personal untracked PowerPoint are excluded from release packaging.

`submission/evidence/local/english_preservation.json` verifies 49 original data/evidence files unchanged, seven artifact numeric streams unchanged and nine regenerated CSV outputs identical byte for byte. Model/split metadata fields are English, so their file hashes intentionally changed even though numeric content did not. New provenance must use the translated release hashes.

## Verification

- `make verify`: **90 passed**, including actual 21-feature Paillier checks, TLS integration, vault, measurement and two-host audit tests. Model retraining matches exactly on the Mac.
- `make verify-docker`: **86 passed, 4 Git-dependent skips** in Ubuntu 24.04 arm64; model differences below 10^-13. This exercises the apt dependency route, not s390x execution.
- Isolated English Docker demo and smoke test pass; the minimal app image excludes CDC data, tests, sklearn and private keys.
- Actual English UI screenshot: `submission/evidence/local/english_demo_synthetic_C.png`; synthetic C yields approximately 66.3% model output.
- The release-gate regression prevents a **partial** clone check from closing full independent review.
- English decks retain 8/19/17 slides. Historical idea scores remain AI simulations. The old raster smurfing figure is rebuilt as an editable English chart using its six literal illustrative amounts; the ranking deck retains its original embedded workbooks, formulas and numeric cells with translated labels. The ranking overview explicitly fills 22 mutually exclusive theme intersections with structural zeros, preserving every original nonblank score; these are not missing judge scores.

The full forecast rerun reproduces all 222 series after canonical key ordering; see `submission/evidence/local/english_forecast_reproduction.json`. The video editing draft is 170 seconds, with no audio and an explicitly labeled pending-LinuxONE slate. See the current plan and evidence record for browser and package checks. All measurements must state their actual platform and release commit. A language scan supplements review; it is not proof of clinical validity or organizer approval.

## Team work still required

A teammate must review the migrated release commit and answer [REVIEW.md](REVIEW.md). Run on the real LinuxONE VM, provide provider/architecture/labs evidence, record authorized English narration and VM/model footage, confirm AI-use attribution/publication and submit via the registered leader. The 170-second silent editing draft remains a draft.

The portal deadline is **October 18, 2026, 16:30 UTC**; internal target **13:00 UTC**. Neither the migration nor the portal opening resolves the actual labs-before-coding chronology. Keep [TIMELINE.md](TIMELINE.md) factual. Netlify and its badge remain.

## New English execution evidence

Clean inference code commit `5412abe`: 2,000/2,000 stratified CDC integers match exactly; float/fixed-point/encrypted AUC is 0.808383. Maximum logit error is 4.50×10^-8 within the applicable sample bound 7.9×10^-8. The separate 200-request synthetic Docker API run matches 200/200 expected integers, with client p50 149.015 ms and p95 183.317 ms. See `submission/evidence/metrics/`. These are local Mac/arm64 and Docker runs. Later changes to protocol help text, an ENSANUT console label and ZIP documentation are recorded separately; the inference computation and model are unchanged. Final LinuxONE evidence must use its actual reviewed release commit.

The reduced ENSANUT experiment also reproduces exactly except for its execution timestamp, including all weights, sample counts and reported metrics. No microdata is redistributed.

Full verification record: [ENGLISH_VALIDATION.md](ENGLISH_VALIDATION.md). The extracted code ZIP passes all 90 tests and model verification. Final-mode packaging correctly remains blocked by the real external evidence requirements.
