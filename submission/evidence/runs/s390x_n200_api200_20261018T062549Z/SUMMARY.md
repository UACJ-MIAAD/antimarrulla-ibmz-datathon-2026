# Evidence run s390x_n200_api200_20261018T062549Z

**VALID DIAGNOSTIC ONLY (insufficient release sample)** · status `passed` · arch `s390x` · commit `b50f6cc` · operator bidallei · 2026-10-18T06:25:49Z → 2026-10-18T06:29:33Z

Model `e32420ac99fd` · code `59a38c39df3c`

| Step | Exit | Seconds | Log |
|---|---:|---:|---|
| verify | 0 | 50.4 | [logs/01_verify.log](logs/01_verify.log) |
| image_inspect | 0 | 0.9 | [logs/02_image_inspect.log](logs/02_image_inspect.log) |
| demo | 0 | 1.5 | [logs/03_demo.log](logs/03_demo.log) |
| measure_process | 0 | 115.5 | [logs/04_measure_process.log](logs/04_measure_process.log) |
| measure_api | 0 | 54.9 | [logs/05_measure_api.log](logs/05_measure_api.log) |

Declared profile: process 200 labeled CDC records; API 200 synthetic requests; release-sized sample: False. Counts and scopes are separate.

Smoke: Synthetic A 1.5% · Synthetic B 15.2% · Synthetic C 63.3%

Process: 200/200 exact · encrypted ROC-AUC 0.841362 · max logit error 2.4e-08 · encrypt p50 235.091 ms · `submission/evidence/metrics/measurement_process_s390x-container_20261018T062643Z.json`
API: 200/200 exact · client p50 264.497 ms · p95 269.838 ms · 226.4 patients/min · `submission/evidence/metrics/measurement_api_s390x-container_20261018T062839Z.json`

Hashes check internal consistency; they are not signed execution attestation. Provider identity and independent teammate review remain separate release gates.
