# Current English release evidence

English release outputs belong here. Original evidence under `submission/evidencias/` is an immutable historical archive: preserve its language, values, filenames and hashes. Never relabel a Mac/arm64 run as LinuxONE.

- `local/`: actual English UI screenshot with synthetic patient C, local Docker aarch64.
- `runs/`: recorded runs from `make evidence-run` (logs, system identity, manifest and `SUMMARY.md` per run; `INDEX.md` lists them). Each run arrives on its own `evidence/<run>` branch and is validated by CI before merging.
- `metrics/`: new process/API measurements with code, model, split and environment provenance.
- `linuxone/`: partial legacy UI evidence from Álvaro reports Linux s390x and synthetic C at 66.3%; see `linuxone/alvaro_20261017_legacy_ui_reported.md`. Actual provider identity and final English v2 execution/measurements remain pending.
- `labs/`: actual completion dates, owners and screenshots; currently pending.
- `two_hosts/`: optional remote-flow evidence. Carlos’s later supplied summary reports audit 10/10, exact results 200/200 and mean ≈650 ms per record; original audit and host/version evidence remain pending. See `two_hosts/carlos_20261017_audit_summary_reported.md` and the earlier terminal-progress record.
- `private/`: ignored local originals of team-chat attachments; excluded from publication and release packages. Publish attributed English summaries, preserving original hashes.
- `instance/`: project-specific tests on the real instance; currently pending.

Copy each `RECORD.example.json` to `RECORD.json` only after gathering the real evidence. Examples are incomplete templates, not completion records. Use the release commit from `docs/ENGLISH_MIGRATION.md`.
