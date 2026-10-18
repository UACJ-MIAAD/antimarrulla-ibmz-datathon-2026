# Hack2Skill submission

Copy each field into the portal in this order. Every text answer is checked to fit the 1024-character limit. The registered team leader submits; save the confirmation screenshot. Portal closes **October 18, 2026, 16:30 UTC** (12:30 EDT, 10:30 Ciudad Juárez).

Project title: `Los Antimarrulla_IBM Z Datathon 2026 Project`

## 1. Challenges

T2 · AI Secured: Innovation Without Exposure

## 2. What is the Problem you are trying to solve? (621/1024)

Diabetes affects 18.3% of adults in Mexico and about one in three does not know it (ENSANUT 2022); 112,577 diabetes deaths were registered in 2024 (INEGI/DGIS). Earlier screening means prioritizing confirmatory glucose tests, and AI risk models can help, but using an external AI service normally requires sending identifiable health records outside the hospital. That creates privacy, legal and trust barriers: either the model goes unused or patient records are exposed. Our question: can a hospital obtain an AI risk score from an external service without that service ever reading the patient's answers or the result?

## 3. How are you planning to solve the problem? (896/1024)

Two containers. The hospital container validates 19 integer-coded survey answers (blood pressure, cholesterol, BMI, age and other CDC BRFSS indicators), encrypts each with a 2048-bit Paillier public key and keeps the private key in memory. The risk service has no private key: it evaluates a logistic regression directly on ciphertexts, Enc(z) = ∏Enc(xi)^Wi·Enc(B) with integer weights ×10^9, rerandomizes and returns one ciphertext over mutual TLS 1.3. The hospital decrypts z, applies the sigmoid and a threshold chosen for ≥80% sensitivity, shows the largest contributions and stores the record in an AES-256-GCM vault. Model: CDC UCI 891 (253,680 records), test ROC-AUC 0.825; decrypted integers match the fixed-point reference exactly (2,000/2,000). Stack: Python 3.12, scikit-learn, python-paillier + gmpy2, cryptography, Docker on Ubuntu 24.04. Reproducible with make verify and make demo.

## 4. How does your solution leverage IBM Z / LinuxONE technologies? (957/1024)

The risk service is built for IBM LinuxONE (s390x). Both containers use Ubuntu 24.04 packages that run natively on s390x; the same images run on amd64/arm64 for development. Homomorphic evaluation is heavy modular exponentiation on 4,096-bit integers for every patient, which suits LinuxONE's large-integer and cryptographic strengths, and its isolation and security model fit a service that must never see plaintext health data. A one-command runner (make evidence-run) records tests, the demo, encrypted measurements, uname/lscpu/sysinfo and container logs on the LinuxONE VM and pushes them to GitHub, where CI validates architecture, exact results and code/model hashes. An earlier release already ran with the risk service on LinuxONE and the hospital on a laptop: 10/10 audit checks, 200/200 exact results. CPACF acceleration is a planned measurement, not yet claimed. Next: a shared LinuxONE risk service for many hospitals, each keeping its own key.

> If this release's LinuxONE runs are merged before submitting, replace the sentence that begins "An earlier release" with the measured result (for example: "This release ran on LinuxONE: 2,000/2,000 exact encrypted results and 200/200 exact API requests, p50 … ms").

## 5. What value does your solution deliver, and who will benefit from it? (830/1024)

Hospitals and public clinics can use external AI screening without sharing readable records: the service sees 19 ciphertexts, never an answer, the probability or the flag. Patients get earlier prioritization for a glucose test with less disclosure, which supports trust and health-data protection. Health systems can host models centrally on LinuxONE and serve many hospitals while each keeps its own key. Encryption does not change accuracy (identical AUC), and a round trip takes about a tenth of a second on a laptop. An optional dashboard forecasts weekly notified diabetes cases for 222 state/sex series, 52 weeks ahead, to plan screening capacity and budgets. The demo uses synthetic patients; clinical use needs recalibration on Mexican data and clinical and legal review, which our roadmap addresses with a hospital pilot.

## 6. Pitch deck (PDF upload, max 5 MB)

Upload [`submission/Los Antimarrulla_IBM Z Datathon 2026 Project.pdf`](Los%20Antimarrulla_IBM%20Z%20Datathon%202026%20Project.pdf) (2.8 MB, 11 slides).

## 7. Github Link of your Project

https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026

## 8. Video Submission Link (YouTube/Vimeo, max 3 minutes)

**Pending:** paste the public URL after upload, open it in a private window to confirm access, and record it in `submission/VIDEO_RECORD.json`. Script: [PITCH.md](PITCH.md); storyboard: [VIDEO.md](VIDEO.md).

## 9. Link to the pitch deck in PDF (if not uploaded)

https://antimarrulla-tamizaje.netlify.app/assets/Los%20Antimarrulla_IBM%20Z%20Datathon%202026%20Project.pdf

## 10. Link to all open-source resources used (872/1024)

Project: https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026 · python-paillier: https://github.com/data61/python-paillier · gmpy2: https://github.com/aleaxit/gmpy · cryptography: https://github.com/pyca/cryptography · scikit-learn: https://github.com/scikit-learn/scikit-learn · NumPy: https://github.com/numpy/numpy · pandas: https://github.com/pandas-dev/pandas · statsmodels: https://github.com/statsmodels/statsmodels · pytest: https://github.com/pytest-dev/pytest · Ubuntu image: https://hub.docker.com/_/ubuntu · Dataset, CDC Diabetes Health Indicators: https://archive.ics.uci.edu/dataset/891/cdc+diabetes+health+indicators · SINAVE bulletin: https://www.gob.mx/salud/acciones-y-programas/direccion-general-de-epidemiologia-boletin-epidemiologico · Full list with licenses: https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026#open-source-credits

## 11. Other documents (flowchart / architecture)

Architecture flowchart: https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026/blob/main/submission/flowchart/architecture.pdf · System diagrams: https://antimarrulla-tamizaje.netlify.app/architecture · Forecast dashboard: https://antimarrulla-tamizaje.netlify.app/forecast · Repository guide: https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026#readme
