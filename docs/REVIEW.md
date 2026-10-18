# Independent teammate code review

PRs 1/2 entered main by a captain exception without independent teammate review. PRs 3/4 were also merged through earlier captain decisions. PRs 5/6 were merged by their own author, AzraelNogo. These facts remain recorded; an exception or AI audit is not another member's technical approval.

## Run a clean, pinned clone

```bash
git clone https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026.git review
cd review
git checkout RELEASE_COMMIT
make verify
make demo
make measure-api
make demo-down
```

Use the release commit under review, including the English migration. Record commands, exit results and environment. All four must understand the final code and AI assistance before submission.

## Read in this order

1. `src/screening/schema.py` and `contract.py`: input codes, integer scale and overflow bound.
2. `src/screening/protocol.py`: private-key hospital and keyless service; English v2 wire contract.
3. `tests/test_protocol.py`: required correctness checks a)–e).
4. `service.py`, `hospital.py`, `vault.py`, provenance and measurement modules, and `docker/compose.yml`.
5. English UI/documentation, artifact schemas, run commands and submission materials.

## Questions every member should answer

1. Why are the 19 inputs unscaled integers while weights use scale 10^9?
2. What does exact decrypted-integer equality prove, and what does the floating-point error bound prove?
3. Where are the Paillier private key and AES vault key? Which container receives each?
4. What does the risk service see and what is logged?
5. Who can read hospital memory in the same-VM demo? Why is the administrator trusted?
6. What does AES-256-GCM encrypt, and what logs/disks/backups does the application not encrypt?
7. What can CPACF accelerate? Has this application's effective use been measured on LinuxONE?
8. Why choose the threshold on validation rather than test? What does PPV 29.7% mean?
9. What did the reduced ENSANUT experiment evaluate, and why does it not validate the 19-feature MVP?
10. How do `make measure`, `make measure-api` and the direct two-host audit differ?
11. Why must English v2 endpoints, model/schema files, UI and measurement client use the same commit?

## Review record

| Member | Date and time | Commands run | Comments |
|--------|---------------|--------------|----------|
| Yazmin Flores | 2026-10-17 14:39 EDT | Clean clone and `make verify` with Python 3.12, commit `32a5af1`, no file changes | **Partial:** confirms the clone runs; protocol reading and comprehension questions remain open |
| _pending_ | | | |

A full review must identify the commit, scope, commands and findings. Yazmin's partial check does not certify the later English release. Keep partial checks labeled partial; the current independent review remains open.

PR 11, including audit fixes and Yazmin's PR 10, was merged by jrebull on October 17 at 20:42:57 UTC as `679c287`. Its GitHub review list is also empty. Passing CI and the captain's merge do not close independent teammate review. The diagram/plan update retains this gate and does not add a human signature.

## Yazmin form integration

PR 8 (`09cadf5`) is incorporated into English PR 9 with its authored commit preserved. The automated integration audit and local verification are recorded in [YAZMIN_INTEGRATION.md](YAZMIN_INTEGRATION.md). Yazmin authored this form; her earlier clone check remains partial and does not approve the combined release. PR 9 was merged by jrebull on October 17 at 20:12 UTC as `d71d363`, with no GitHub review recorded. Another teammate’s complete review of the submitted release remains required; the merge itself is not that approval.

PR 12 (concurrency, macOS host identity and raw historical audit) was merged by its author AzraelNogo at 21:00:21 UTC as `b04fadb`, also with no GitHub review recorded. Review remains open. Yazmin's PR 13 redesign/charts subsequently merged by jrebull at 21:24:20 UTC as ef1e21d, also without a recorded GitHub review. The same independent release review remains open.

PR 14 diagram/documentation atlas was merged at 21:26:06 UTC as b38a69f. Documentation-only changes do not close the existing independent review or final runtime evidence gates.

## Captain-authorized closing integration — October 18, 2026

The captain explicitly instructed the integration agent to validate and merge all remaining work into `main` in this chat. This authorizes the merge exception for PRs 19 (evidence preflight), 20 (benchmark profiles and live redacted output), and 21 (Hospital frontend readiness). The GitHub review lists for all three PRs were empty when checked. This authorization does **not** constitute independent teammate technical approval, and the release review gate stays open.

Combined runtime checkpoint: `3a896e4d6b5d4dc2040f129fc803b40cd259e7e1`, which already includes streaming fix `bc02b81`. Validate the combined source and green GitHub checks before the ordered merge. Preserve the authored commits using merge commits. Documentation changes do not change the screening runtime hash. Rebuild both peers and the measurement client from the resulting pinned `main` before recording final LinuxONE evidence. No final VM run, provider proof, lab completion or narrated video is certified by this merge.

The same captain instruction to finish validation and leave all fixes in main also authorizes the urgent measurement-container ownership correction. Both measurement clients now use the host UID/GID instead of image UID 10001. This automated validation and merge exception does not close independent teammate review.
