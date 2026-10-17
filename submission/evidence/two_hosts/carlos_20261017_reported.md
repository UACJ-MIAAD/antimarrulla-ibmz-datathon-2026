# Carlos: reported laptop-to-server encrypted test

**Status: reported execution with partial screenshot evidence; strict audit pending.** Recorded from the captain-supplied October 17 conversation. Operator: Carlos Enrique Gonzalez Moran. Message times have no established timezone. The calendar date comes from conversation context, not a visible date in the image.

## Operator report

Carlos states that he sent **200 synthetic records from a laptop to a server**, encrypted them for server-side processing and received the results back. His 15:34 message reports **200/200 identical results**. At 15:33 he says an audit is running to check that the service saw only encrypted data. No completed audit report appears in this attachment.

## Directly visible terminal evidence

| Processed / planned | Identical comparisons | Last request |
|---------------------|-----------------------|--------------|
| 25 / 200 | 25 / 25 | 612 ms |
| 50 / 200 | 50 / 50 | 597 ms |
| 75 / 200 | 75 / 75 | 667 ms |
| 100 / 200 | 100 / 100 | 616 ms |
| 125 / 200 | 125 / 125 | 608 ms |

The terminal image stops at **125/200**; the final 200/200 count is an attributed chat report. These five times are individual last-request observations, not p50/p95 or a throughput estimate. The image contains Spanish output and clipped hash fragments; a complete release commit, source/model hashes and English v2 compatibility cannot be recovered from it.

## What this record does and does not establish

This records useful progress on the optional remote encrypted flow, US-6.5. Its status remains **in progress**. The supplied material does not independently establish two distinct real hosts, two VMs, LinuxONE/provider identity, a completed ciphertext-only audit, private-key isolation, the exact equality reference, or coverage of the full Hospital UI/API/vault flow. Do not describe it as 200 clinically correct predictions, no information loss in general, or a formal proof of no exposure.

Keep the approved one-VM/two-container MVP and frontend placement in [DEPLOYMENT.md](../../../docs/DEPLOYMENT.md). Carlos's laptop/server experiment is separate; it does not change that deployment decision.

## Follow-up owned by Carlos, with Álvaro

Preserve the existing run before rerunning anything. Supply the hospital summary, final audit JSON/Markdown and exit status; complete commit/code/model/protocol identifiers at both ends; host/architecture/provider evidence where claimed; and the complete timing summary with its operation scope. Keep credentials and bulk raw wire files outside Git. If this run used the older Spanish contract, retain its original provenance and run final English release evidence separately. See [TWO_HOSTS.md](../../../docs/TWO_HOSTS.md).

## Source preservation

The original screenshot remains byte-for-byte in the ignored local directory `submission/evidence/private/`. It contains unrelated personal conversation, so it is not published or packaged. SHA-256: `8b283499035167892230d264164520ec696e67c7fb7a9db1f6123c4dd14252a8`. The [structured English record](carlos_20261017_reported.json) preserves the relevant observations and their limits.
