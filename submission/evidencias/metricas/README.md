# Historical measurement records

The original JSON/Markdown files in this directory remain unchanged. Each belongs to the commit, model hash, data hash and actual environment recorded inside it. Preserve the original schema and text when citing that run.

The English release writes new JSON/Markdown under `submission/evidence/metrics/` using `make measure` and `make measure-api`; the VM equivalents are `make measure-docker FINAL=1` and `make measure-api-docker FINAL=1`. Deploy both English v2 peers and the measurement client from the same reviewed commit.

Do not rename a local measurement as LinuxONE evidence or silently translate historical measured records. English summaries must identify the original run separately.
