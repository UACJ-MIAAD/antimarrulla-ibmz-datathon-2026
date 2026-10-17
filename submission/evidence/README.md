# Current English release evidence

English release outputs belong here. Original evidence under `submission/evidencias/` is an immutable historical archive: preserve its language, values, filenames and hashes. Never relabel a Mac/arm64 run as LinuxONE.

- `local/`: actual English UI screenshot with synthetic patient C, local Docker aarch64.
- `metrics/`: new process/API measurements with code, model, split and environment provenance.
- `linuxone/`: actual s390x/provider evidence; currently pending.
- `labs/`: actual completion dates, owners and screenshots; currently pending.
- `two_hosts/`: strict two-real-host audit; currently pending and optional.
- `instance/`: project-specific tests on the real instance; currently pending.

Copy each `RECORD.example.json` to `RECORD.json` only after gathering the real evidence. Examples are incomplete templates, not completion records. Use the release commit from `docs/ENGLISH_MIGRATION.md`.
