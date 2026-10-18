# Hack2Skill submission text

The registered team leader submits through the team dashboard after all four review. This file prepares the English text; it does not confirm a portal submission. Window: October 16, 23:45 UTC through October 18, 16:30 UTC. Internal target: October 18, 13:00 UTC.

## Required title

`Los Antimarrulla_IBM Z Datathon 2026 Project`

## Theme

T2 · AI Secured: Innovation Without Exposure

## Short description

Privacy-preserving screening evaluates diabetes risk on encrypted data. The hospital encrypts 19 indicators with Paillier and retains the private key. A risk service designed for IBM LinuxONE evaluates a logistic model without decrypting the inputs, returning a ciphertext that only the hospital can open.

## Problem

ENSANUT 2022 reports that 18.3% of adults in Mexico have diabetes and about one in three is unaware of it. DGIS/INEGI microdata records 112,577 diabetes deaths in 2024. In SSA diabetes admissions, 11,550 discharges included a lower-limb amputation, 18.4% of 62,771 admissions. These are different populations and events, not a linked patient cohort. Hospitals need ways to evaluate screening models while limiting disclosure of patient records to an external service.

## Solution

1. The hospital validates the 19 original integer feature codes and encrypts them with a 2048-bit Paillier public key.
2. The keyless service evaluates the fixed-point logit: `Enc(z) = product(Enc(x_i)^W_i) * Enc(B)`, then rerandomizes the result.
3. The hospital decrypts the integer, applies the sigmoid and shows the risk and largest model contributions. This demonstrates screening, not diagnosis, future disease prediction or mortality prediction.

The held-out CDC test split has ROC-AUC 0.825, sensitivity 0.807, specificity 0.689 and PPV 0.296 (model `logistic-cdc19-v1`, 19 features), with threshold chosen on validation. The local benchmark of this model at clean commit `be9b27e` matched 2,000/2,000 decrypted integers, with AUC 0.806525 in all three variants and maximum logit error 3.37×10^-8. The two-container API matched 200/200 synthetic inputs, with client p50 114.8 ms and p95 118.2 ms. These are Mac/arm64 and Docker results. Add actual translated-release LinuxONE measurements before submission; keep their platform and commit labels.

## IBM Z / LinuxONE

The approved deployment design uses two Ubuntu 24.04 s390x containers: hospital with its private key and AES-256-GCM vault; risk service without private keys; mutual TLS 1.3 between them. Homomorphic evaluation uses modular arithmetic on integers thousands of bits long. The demo shares a VM, so its administrator is trusted and synthetic inputs are required. Intended production separation places the hospital component on hospital premises; this is a design, not a deployed clinical system.

**LinuxONE execution/provider evidence remains pending.** Add the actual release commit, VM screenshots and outputs of `make measure-docker FINAL=1` and `make measure-api-docker FINAL=1`. CPACF is a platform capability; application acceleration has not been demonstrated.

## Stack

Python 3.12 · scikit-learn · python-paillier (`phe`) + gmpy2 · cryptography · mutual TLS 1.3 · AES-256-GCM · Docker · Ubuntu 24.04 · Make.

## Links and completion checks

| Field | Value |
|-------|-------|
| Public repository | https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026 |
| Final video, <=3 minutes | **Pending:** English script/editing draft exists; authorized narration, actual LinuxONE footage and public access verification remain required |
| Required PDF | [Official project PDF](Los%20Antimarrulla_IBM%20Z%20Datathon%202026%20Project.pdf) |
| Optional flowchart | [Architecture](flowchart/architecture.pdf) |
| Optional prototype | `make demo`, then `http://127.0.0.1:8080`; no public prototype URL is established |
| Open-source resources | [Credits](../README.md#open-source-credits) |
| AI use | Team publication decision pending; separate local English draft: `submission/AI_USE.md` |

Complete `submission/VIDEO_RECORD.json` and the [submission checklist](../docs/SUBMISSION_CHECKLIST.md). Keep the final video URL identical in this file and the record. Save the portal confirmation screenshot.
