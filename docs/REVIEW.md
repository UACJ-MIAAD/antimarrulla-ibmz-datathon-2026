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

1. Why are the 21 inputs unscaled integers while weights use scale 10^9?
2. What does exact decrypted-integer equality prove, and what does the floating-point error bound prove?
3. Where are the Paillier private key and AES vault key? Which container receives each?
4. What does the risk service see and what is logged?
5. Who can read hospital memory in the same-VM demo? Why is the administrator trusted?
6. What does AES-256-GCM encrypt, and what logs/disks/backups does the application not encrypt?
7. What can CPACF accelerate? Has this application's effective use been measured on LinuxONE?
8. Why choose the threshold on validation rather than test? What does PPV 29.7% mean?
9. What did the reduced ENSANUT experiment evaluate, and why does it not validate the 21-feature MVP?
10. How do `make measure`, `make measure-api` and the direct two-host audit differ?
11. Why must English v2 endpoints, model/schema files, UI and measurement client use the same commit?

## Review record

| Member | Date and time | Commands run | Comments |
|--------|---------------|--------------|----------|
| Yazmin Flores | 2026-10-17 14:39 EDT | Clean clone and `make verify` with Python 3.12, commit `32a5af1`, no file changes | **Partial:** confirms the clone runs; protocol reading and comprehension questions remain open |
| _pending_ | | | |

A full review must identify the commit, scope, commands and findings. Yazmin's partial check does not certify the later English release. Keep partial checks labeled partial; the current independent review remains open.
