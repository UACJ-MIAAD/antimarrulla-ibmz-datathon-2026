# Carlos: reported audit summary and remote timings

**The supplied summary reports audit 10/10 and exact results 200/200; original audit files remain pending.** This updates the earlier [partial run record](carlos_20261017_reported.md) without replacing its historical observations. The captain supplied the image and October 17 chat; message timezone is unspecified. No new Carlos commit or audit upload was found on the remote at registration.

## Figures and their sources

| Measure | Reported value | Source and scope |
|---------|---------------|------------------|
| Completed audit checks | 10 / 10 | Presentation image; individual checks/exit status not supplied |
| Exact results | 200 / 200 | Image and operator report; reference definition awaits original summary |
| Total per record | Mean ≈650 ms | Carlos’s 15:55:11 message, sequential concurrency 1 |
| Hospital encryption | ≈140 ms | Same rounded component report |
| Network plus service | ≈500 ms | Includes network and service, not pure CPU time |
| Hospital decryption | ≈10 ms | Same rounded component report |
| Service evaluation | 18.6 ms / record | Image; statistic/aggregation and full provenance unspecified |
| Sequential throughput | ≈92 records/min | Operator report; reciprocal of 0.65 s is ≈92.3/min |
| Batch duration | Image: ≈2 min | 200 × 0.65 s is 130 s; approximate labels are consistent |
| Example displayed probability | 5.0% | One illustrated record; not the earlier synthetic C example |
| Input/output ciphertext length | 1,233 decimal digits each | Image labels and truncated number samples |
| Plaintext on server | Reported counter: 0 | Summary of an unspecified audit scope, not independently verified |

The rounded components sum to 650 ms. These are **reported mean/illustrative values**, not measured p50/p95 in this registration. Do not subtract differently scoped values to invent network-only latency. The direct hospital client test also must not be described as a full browser/UI/vault measurement without its original scope.

## Wording for final material

Carlos previously described the inputs as synthetic. The image’s title uses “real patient”; replace this wording in new English material with **“One synthetic record from the measured run”**, after confirming the sample definition from the original report. The existing image remains unchanged as source evidence.

The service returns an **encrypted linear score**. Hospital decrypts and applies sigmoid to display the probability. “Audit 10/10” and a zero-plaintext counter are useful reported results, but require the detailed audit, exact version, wire/hash checks and host evidence before independent acceptance. They do not constitute a formal proof of no exposure or clinical accuracy. The 5.0% illustrated result is separate from the earlier profile-C result of 66.3%; no supplied request ID matches the samples.

## Carlos’s final comparison

Compare the **screening model**, not the separate E5 forecast: floating point versus fixed point versus Paillier on exactly the same labeled CDC sample. Decrypted integer equality tests encryption correctness; fixed-point versus floating-point error tests quantization. Report the logit bound, probability error and same-sample metrics separately. Synthetic records test arithmetic/transport but cannot provide observed clinical labels or AUC.

Use the reviewed combined English branch/commit. A plain `git pull` of `main` still retrieves the older Spanish implementation at registration. Both peers and the measurement client must use the same English v2 release; preserve existing outputs and any uncommitted work before switching. Run `make verify-docker`, `make demo-docker`, `make measure-docker FINAL=1` and `make measure-api-docker FINAL=1` on the target VM, as described in [LINUXONE.md](../../../docs/LINUXONE.md). The final English release still requires independent teammate review.

## Remaining evidence

Collect `hospital_summary.json`, the final audit JSON/Markdown and exit status, complete code/model/protocol identifiers, timing distributions/sample scope, corroborated host identities and provider evidence if LinuxONE is claimed. US-6.5 remains in progress. This does not change the approved one-VM/two-container MVP.

Original image SHA-256: `0868e41bd67c384066d730aa48b2e12d043d0acd3c7b03b37cdc500ae4d5dad5`. Pixels are preserved locally under the ignored `submission/evidence/private/` directory; this English record and its [JSON companion](carlos_20261017_audit_summary_reported.json) are the published registration.
