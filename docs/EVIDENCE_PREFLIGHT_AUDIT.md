# Evidence runner preflight audit

Audited baseline: `516bb593dfa0fe969c2c0c7e30852adebd5b881b`.
Decision: **hold the final VM run until the hardening PR is reviewed and merged.** No actual s390x run or closing measurements were launched during this audit.

## Baseline claims verified

- `516bb59` is on remote `main`. GitHub verify run [39094143431](https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026/actions/runs/39094143431) succeeded: **111 native tests**, **100 tests plus 5 skipped in Ubuntu x86_64**, model reproduction and container smoke. Those are different test environments and counts.
- At audit time, GitHub reported **no runs of the separate `evidence` workflow**, and the checkout contained no recorded run directory. The claimed Mac rehearsal was not independently replayed from a persisted run bundle in this audit. Existing local measurement artifacts are separate evidence.
- The executable source hash at both `be9b27e` and `516bb59` is `db2086ee2fcf99a4ad8943cb78f269f0f92f881993c911a36b694945e3ef39fd`. Documentation commits between them do not change that hash.
- The current model is **logistic-cdc19-v1, 19 features**, model SHA-256 `e32420ac99fd10d30a3a65a225a43d84d4bfd7208c6f3b7656611893729575ac`. Its synthetic probabilities round to **A 1.5%, B 15.2%, C 63.3%**. Historical 21-feature/C 66.3% evidence remains historical.

## Findings and corrections

| Priority | Reproduced problem at baseline | Correction |
|---|---|---|
| P1 | Changing both measurement samples/results to **1/1** and updating their hashes produced **zero validation errors**. | Require exactly 2,000 process patients and 200 deployed API requests in the runner and final package. |
| P1 | A recorded commit unavailable to Git was only a warning; the fake-commit fixture was explicitly considered VALID. | Missing commits fail. Recompute executable source hash and compare exact model bytes at the recorded commit. |
| P1 | Redaction removed a PEM private-key header but retained its body. Output was also printed before redaction. | Remove entire PEM blocks, including truncated blocks; sanitize output before display/file publication. |
| P1 | Public IPv6, bearer/basic credentials, URL credentials and generic token/password fields were missed; measurement files and API state bypassed log redaction. | Broaden scanning/redaction and include generated measurements, state, manifest, publication errors and files staged for upload. |
| P1 | A/B/C smoke values were parsed but never compared to the actual model. | Recompute probabilities and require matching smoke host/model identity. |
| P1 | Required host/API evidence could be absent; shell collection failures were ignored. | Require system records, successful collection commands and consistency across uname, measurement environments, API state and remote code/model/private-key status. |
| P1 | Process/API content checks accepted incomplete numerical reports and stale/replayed artifacts. | Check finite error bounds, matching float/fixed/encrypted AUC, valid API percentiles, measurement timestamps inside the run, and model/code/host consistency. |
| P1 | An existing unrelated staged file would enter the evidence commit. | Require an empty index before running and again before publication; stage only checked regular run/measurement files. |
| P1 | Commit/push/bundle failure could be hidden by a successful runner exit; bundle creation was unchecked. | Propagate publication failure; check bundle creation; restore the original branch. Failed runs still publish diagnostic logs with invalid status. |
| P2 | The default 600-second pilot budget can silently reduce the sample below 2,000. | Request a 3,600-second budget, 2,000 maximum patients and 200 internal HTTPS requests; fail validation if 2,000 process patients were not actually measured. The time budget is not a completion guarantee. |
| P2 | Step order/commands and log exit markers were not correlated with the manifest; arbitrary/symlink paths were accepted. | Enforce exactly ordered required steps, command and exit markers, bounded regular file paths, and reject malformed input. |
| P2 | An empty evidence branch passed CI; PR changes to tools could show a green evidence job without any VM run. | Evidence pushes require at least one recorded run. A tool-only PR may have no runs; its ordinary verify job tests the validator. CI success must retain this scope. |
| P2 | The code ZIP omitted `tools/evidence.py`; documentation ZIPs omitted recorded run logs. | Include tools/workflow source and recorded run files in the respective packages. Personal PowerPoint remains excluded. |
| P2 | Generated API measurement Markdown still contained two Spanish labels. | New outputs use English. Preserve historical files unchanged. These edits change the executable source hash; rebuild and measure the reviewed release. |
| P2 | VM instructions pulled before switching branches, omitted host Python installation, and suggested plaintext credential storage. | Switch first, pull with `--ff-only`, pin the approved release; install host Python 3 and use existing SSH or GitHub CLI authentication. |

## Verification and limits

Regression tests use synthetic fixtures, temporary Git repositories and a local bare remote. They cover valid evidence, one-patient and inexact samples, changed logs/smoke values, missing commits/system records, inconsistent AUC/hosts/code, invalid numerical values, stale timestamps, unsafe paths, secrets, no-run rejection, preservation of unrelated staged work, failed-step recording, successful publication and failed-push bundle recovery. No evidence branch was created on GitHub as a test.

Native verification and Ubuntu container verification are run separately. Ubuntu omits the runner module tests because `tools/` and Git metadata are intentionally absent from the dev image; the native/CI verify job exercises those tests. A first sandboxed native attempt could not bind localhost TLS sockets; rerunning with localhost permissions resolves that environmental limitation. Final local results: **147 native tests passed** with model reproduction; **103 Ubuntu arm64 tests passed, 5 skipped**, with model reproduction. The 57 targeted recorder/package tests passed. See the PR for remote CI status. The new executable hash is `423c299381239116472471347d720f9c558e3fe95bacdf4c8fc6d15c4be2e319`; the model hash above is unchanged.

Draft code/documentation ZIPs were built and their manifests verified; the code ZIP contains the runner/workflow and excludes the personal PowerPoint. The package remains DRAFT: no closing evidence was fabricated. After committed fixes, the release still needs both actual LinuxONE measurements, four VM/provider screenshots plus owner/date, two lab records, the final narrated/public video, independent teammate review and the approved AI declaration. Human-owned submission access and the submission receipt remain separate.

**Trust limit:** file hashes establish consistency with a manifest. They do not prevent someone rewriting both files and manifest, attest to physical execution, prove the cloud provider, or replace independent review. Common-secret scanning cannot recognize arbitrary undisclosed credentials. This is an auditable recording workflow, not cryptographic remote attestation.

## Next actions

1. Another teammate reviews the hardening PR and its CI; merge through the normal PR flow. Use the newly approved commit rather than `516bb59`.
2. Carlos and Álvaro fetch and pin that exact approved commit on a **named** VM branch; verify `uname -m` is `s390x`, host Python 3, Docker/Compose, Git name/email and push credentials.
3. Run `make evidence-run PY=python3` once on the VM. Each step prints sanitized output on completion; measurements can be quiet for several minutes. Keep its returned branch name and exit status. A bundle is a fallback requiring transfer, not a successful upload.
4. Review that branch's strict CI and original logs plus the Community Cloud/UI screenshots. Keep failed/rehearsal runs on diagnostic branches; only include the valid approved run in the release PR.
5. Update README, deck/PDF, script and site from the approved run's summary. Complete lab/video/AI/review records, run `make package FINAL=1`, have all four review and let the registered leader submit. Internal target: October 18 13:00 UTC; portal deadline: 16:30 UTC.
