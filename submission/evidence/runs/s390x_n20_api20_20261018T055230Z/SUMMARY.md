# Evidence run s390x_n20_api20_20261018T055230Z

**VALID DIAGNOSTIC ONLY (insufficient release sample)** · status `passed` · arch `s390x` · commit `b50f6cc` · operator bidallei · 2026-10-18T05:52:30Z → 2026-10-18T05:53:52Z

Model `e32420ac99fd` · code `59a38c39df3c`

| Step | Exit | Seconds | Log |
|---|---:|---:|---|
| verify | 0 | 49.6 | [logs/01_verify.log](logs/01_verify.log) |
| image_inspect | 0 | 0.8 | [logs/02_image_inspect.log](logs/02_image_inspect.log) |
| demo | 0 | 1.5 | [logs/03_demo.log](logs/03_demo.log) |
| measure_process | 0 | 22.3 | [logs/04_measure_process.log](logs/04_measure_process.log) |
| measure_api | 0 | 7.2 | [logs/05_measure_api.log](logs/05_measure_api.log) |

Declared profile: process 20 labeled CDC records; API 20 synthetic requests; release-sized sample: False. Counts and scopes are separate.

Smoke: Synthetic A 1.5% · Synthetic B 15.2% · Synthetic C 63.3%

Process: 20/20 exact · encrypted ROC-AUC 0.980392 · max logit error 2.23e-08 · encrypt p50 242.328 ms · `submission/evidence/metrics/measurement_process_s390x-container_20261018T055323Z.json`
API: 20/20 exact · client p50 266.291 ms · p95 269.827 ms · 225.4 patients/min · `submission/evidence/metrics/measurement_api_s390x-container_20261018T055345Z.json`

Hashes check internal consistency; they are not signed execution attestation. Provider identity and independent teammate review remain separate release gates.
