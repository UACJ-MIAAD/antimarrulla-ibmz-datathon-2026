# Carlos's original remote audit — evidence reconciliation

PR 12, merged by AzraelNogo on October 17 at 21:00:21 UTC, supplies the original JSON/Markdown audit and one ciphertext request/response example. Main is now `b04fadb`. The original Spanish files are historical execution evidence and remain byte-for-byte intact; this English explanation does not rewrite them.

Source report: `submission/evidence/two_hosts/auditoria_20261017T194931Z.json` and `.md`. Execution audit timestamp: **2026-10-17 19:49:31 UTC**. This upgrades the earlier chat-only registration to an inspectable original report. It does not turn the historical Spanish v1 run into the final English v2 run.

## What the original report establishes within its scope

The report records a Mac arm64 hospital client and a Linux s390x container service, Paillier 2048 bits, mutual TLS 1.3, 200 measured deterministic synthetic inputs plus three warmups, **200/200 exact fixed-point integers**, and ten passing audit checks. There are no clinical labels or AUC for this synthetic sample. The maximum probability difference from floating point is **6.75154 × 10^-9**.

| Hospital-observed component | p50 ms | p95 ms | Mean ms |
|-----------------------------|-------:|-------:|--------:|
| Total direct encrypted round trip | 606.919 | 804.967 | 650.537 |
| Encryption | 140.821 | 146.996 | 140.858 |
| Network plus service | 456.395 | 648.271 | 500.978 |
| Decryption | 8.501 | 10.711 | 8.701 |

This is the direct two-host client path, not UI → Hospital API → vault. The approximate reciprocal of mean latency is 92 sequential records/minute; it is not a measured concurrent throughput or the new parallel runner's result. A separate earlier graphic's 18.6 ms service figure is not independently derived from this table.

## Checks performed during this plan audit

- Historical commit `037ee1be38f75a4ddd5e22d58687fdc20692778a` exists in local Git.
- Reconstructed SHA-256 of its 22 sorted `src/tamizaje` Python/HTML files is **642f6555c80357ed2b4202c55c3f2531fbb0b6bd32880155397a5ae04a586501**, exactly matching both endpoints in the report.
- SHA-256 of that commit's `artefactos/modelo/modelo_logistico_v1.json` is **0455e46245761df61fd717dfaa57da8ff4815ef0edd9b34f719d97e23e79ddb2**, exactly matching the report.
- The supplied example request has 21 valid Paillier ciphertext group members, a 2048-bit modulus and exponent zero; the response ID matches the request.
- All ten recorded checks are marked successful. Their full historical recomputation requires the original 203-request hospital log and corresponding service evidence directories, which are not included in this compact export.

The source report explicitly says Community Cloud provider identity still needs corroboration. It describes legacy `tamizaje`/Spanish v1 with an older source/model serialization hash. The latest English runtime, measurements and provider/screenshots must retain their own commit/hash identity. Do not overwrite these files, translate their wire fields or relabel them as current English execution.

## Ownership and follow-up

Carlos preserves the complete original logs outside Git and supplies any reviewed additional summary needed for inspection. Álvaro supplies provider identity and final English UI/container/architecture/OpenSSL captures. Final process and Hospital API/vault measurements remain required on the agreed English release. The new PR 12 parallel runner is tested separately; the historical run above used concurrency one.

Yazmin's PR 13 (`feat/demo-ui-redesign`) is still an active UI workstream with passing CI at the check. It changes an HTML file included by `provenance.hash_code()`. Coordinate any merge with the measurement owners before pinning the final runtime; do not label the old report with the redesign's code hash. This diagram branch does not take over that redesign.
