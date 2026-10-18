# Evidence run s390x_n2000_api200_20261018T063121Z

**VALID** · status `passed` · arch `s390x` · commit `b50f6cc` · operator bidallei · 2026-10-18T06:31:21Z → 2026-10-18T06:42:50Z

Model `e32420ac99fd` · code `59a38c39df3c`

| Step | Exit | Seconds | Log |
|---|---:|---:|---|
| verify | 0 | 49.8 | [logs/01_verify.log](logs/01_verify.log) |
| image_inspect | 0 | 0.9 | [logs/02_image_inspect.log](logs/02_image_inspect.log) |
| demo | 0 | 1.5 | [logs/03_demo.log](logs/03_demo.log) |
| measure_process | 0 | 582.1 | [logs/04_measure_process.log](logs/04_measure_process.log) |
| measure_api | 0 | 54.7 | [logs/05_measure_api.log](logs/05_measure_api.log) |

Declared profile: process 2000 labeled CDC records; API 200 synthetic requests; release-sized sample: True. Counts and scopes are separate.

Smoke: Synthetic A 1.5% · Synthetic B 15.2% · Synthetic C 63.3%

Process: 2000/2000 exact · encrypted ROC-AUC 0.806525 · max logit error 3.37e-08 · encrypt p50 236.588 ms · `submission/evidence/metrics/measurement_process_s390x-container_20261018T063214Z.json`
API: 200/200 exact · client p50 263.299 ms · p95 267.553 ms · 227.6 patients/min · `submission/evidence/metrics/measurement_api_s390x-container_20261018T064156Z.json`

Hashes check internal consistency; they are not signed execution attestation. Provider identity and independent teammate review remain separate release gates.
