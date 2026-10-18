# Hospital frontend readiness

The Hospital UI now supports single-patient demonstrations, synthetic browser API batches and commands for recorded VM evidence. The public Netlify pitch/forecast site remains separate. Deploy both peers/client from the same reviewed commit; a stale Hospital without `/api/test-config` cannot provide the new test modes.

## Readiness matrix

| Mode | Frontend behavior | Validation |
|---|---|---|
| A / B / C | Encrypt and evaluate one predefined synthetic record; withhold a result if the integer reference check fails | Actual browser: 1.5%, 15.2%, 63.3%; threshold 12.2% |
| Random | Evaluate one random synthetic record | Actual browser success |
| Custom | Validate all 19 coded fields before POST | Actual browser: fractional BMI blocked; valid integer entry evaluated |
| 20 API requests | Deterministic synthetic records, 3 excluded warmups, progress, exactness and separate browser/Hospital timings | Actual browser: 20/20 exact, JSON download verified against source hash |
| 200 API requests | Same sequential batch flow, bounded recent-history charts | Actual browser: 200/200 exact; recent history limited to 200 of 221 observations |
| 2,000 / 16,000 API requests | Explicit selectable counts; tab must remain open; stop after current request and export available | Selectors and the exact request loop checked with simulated requests; **no actual large run performed** |
| Recorded CDC profiles 20 / 200 / 2,000 / 16,000 | Show the corresponding VM command and separate CDC/API counts; small profiles labeled diagnostic | All four generated commands inspected; API count override inspected; command copy verified |
| Cancellation | Finish the current request, then stop; preserve completed vault writes | Actual browser cancellation during warmup; simulated cancellation after five measured results |
| Connection failure | Stop, show FAILED and unlock controls; no automatic retry | Owned preview stopped: FAILED 0/20; service restored and a new 20/20 run completed |
| Wrong integer / identity / duplicate result | Stop immediately; never report completion | Simulated engine checks; single-score guard test withholds the result |
| Mobile / export | Readable controls; no document overflow; diagnostic JSON contains no patient vectors, ciphertexts or keys | 375 px viewport → 375 px document; desktop reviewed; actual file download parsed |

## Meaning of the checks

Hospital recomputes the fixed-point reference **inside its own trusted boundary** and returns an exactness flag plus model/code hashes to its authorized browser. No plaintext/reference is sent to the risk service. This diagnostic check is included in Hospital interpretation time. It is not cryptographic attestation or protection from the VM administrator. The independent command-line measurement still computes its own reference.

Browser batches use seeds 2026 onward, matching the CLI API sequence with three excluded warmups. They have no clinical labels or AUC and are always exported as `browser-api-diagnostic-v1`; they do not satisfy the final release evidence gate. Browser timings include HTTP/JSON/browser overhead and are displayed separately from Hospital timings. Batch percentiles use linear interpolation. The session charts retain only the latest 200 observations, draw at most 20, and label that scope.

Every batch checks Hospital/service identity before starting, checks each measured result's identity/exactness/unique ID and checks identity again before successful completion. A timeout or lost response stops without retry, because the server might already have written the vault. Cancellation is not rollback. Do not reload/close the tab during a browser batch. Recorded VM runs remain the appropriate delivery evidence path.

## Operator steps

1. Independently review the prerequisite evidence/profile PRs and the frontend fix. Pin the approved latest commit and rebuild both endpoints/client together.
2. Start with `make demo-docker`; reach Hospital through the existing SSH tunnel. A/B/C, Random and the 19-field form are at the top.
3. Open **Test modes**. For the pitch choose 20 browser requests or one profile C. Use 200 for a short diagnostic before recording.
4. For the formal 16,000-record CDC comparison, copy the **Recorded evidence on the VM** command and run it in the VM terminal. Default API count remains 200; the checkbox explicitly requests the same count for API. Do not run a large batch and a formal benchmark simultaneously.
5. Download diagnostics when needed, but use the recorded runner's logs/manifest/summary, provider screenshots and independent review for final delivery.

The frontend does not execute shell commands, launch a CDC experiment inside the browser, publish evidence branches, certify provider identity or send the final submission. The supplied actual diagnostics are local native macOS checks, not container or LinuxONE performance results.

## Verification

- Native `make verify`: **187 passed**, model reproduced.
- Ubuntu arm64 `make verify-docker`: **133 passed, 8 skipped**, model reproduced. The Node browser-state-machine test is skipped in the dev image; native and CI verify exercise it.
- Browser state-machine simulations cover all four counts, warmups, exactness, duplicates, identity changes, cancellation, failed requests, unsupported sizes, offline startup, percentile calculation and withholding a failed single score.
- [Actual 20-request diagnostic](../submission/evidence/local/frontend_browser_api_20.json) and [validation record](../submission/evidence/local/frontend_readiness_validation.json).

Both desktop/mobile proof screenshots are available locally under `dist/frontend-validation/`. The intentional outage produced a network error; the final reloaded preview had no console errors or warnings. The model file and weights are unchanged. Source changes require fresh final measurements at the approved commit.
