# Álvaro: legacy UI screenshot reporting Linux s390x

**Partial legacy evidence, not final English-release verification.** The captain supplied a browser screenshot alongside Álvaro’s October 17, 15:53:01 statement that the application runs well on the server. The message timezone is unspecified.

## Directly visible observations

| Item | Displayed value |
|------|-----------------|
| Browser address | `127.0.0.1:8080` |
| Service status | `ok` |
| Application-reported architecture/system | `s390x` / Linux |
| Public-key size | 2048 bits |
| Protocol / model / schema | `tamizaje-paillier-v1` / `logistico-cdc21-v1` / `cdc21-v1` |
| UI | Spanish; synthetic-patient banner; 21 editable features |
| Synthetic profile C | 66.3% risk; displayed threshold 12.3%; rounded logit 0.6745 |
| Integer score | `674486224` |
| Request | 26,785 bytes; UI reports 21 ciphertexts |

This is useful evidence of a supplied application screen reporting Linux s390x and a completed synthetic-profile result. Architecture is an application-reported value, not an independently verified hardware/provider identity. Neither `uname`/`lscpu` nor a Community Cloud dashboard is visible. A loopback URL does not establish the host identity or an SSH tunnel.

The screenshot visibly uses the older Spanish **v1** application. It cannot certify the final English **v2** release. Complete commit/hashes, negotiated TLS, vault persistence and latency statistics are absent. Keep this capture separate from Carlos’s reported 200-record laptop/server experiment until their versions and hosts can be matched.

## Data decision recorded from the supplied chat

Carlos raised the idea of collecting real CURPs from the web and then explicitly abandoned it. The team keeps **synthetic patients and identifiers** for the demo. Use existing random 32-hex request IDs and synthetic profiles. A display label such as `DEMO-001` may be used if needed; it must not replace the protocol request ID. CURP is not one of the 21 predictors. This records the team’s decision; it does not claim an organizer ruling about disqualification.

## Next evidence to collect

Álvaro and Carlos should preserve this legacy run, deploy matching containers from the reviewed English release, and capture the English UI plus `/api/state`. Collect provider, architecture, containers, OpenSSL and complete version/hash evidence, then run both final measurement modes. Fill `submission/evidence/linuxone/RECORD.json` with actual evidence only. The final English video must use new English footage rather than relabeling this screenshot. Relevant stories remain in progress.

## Source preservation

The original browser image remains unchanged in the ignored local `submission/evidence/private/` directory. It includes unrelated browser bookmarks and historical Spanish UI, so this registration publishes only the relevant English observations. SHA-256: `51a623aa75ed62258f356bce56b55558efa4907fde5d68055763fb18c924fe14`. See the [structured record](alvaro_20261017_legacy_ui_reported.json).
