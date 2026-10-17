# English video script · Privacy-preserving screening

Editable deck: [English pitch](Los_Antimarrulla_Screening_Pitch.pptx). Eight slides; English speaker notes accompany each slide. Hard limit: **180 seconds**. Editing target: **170 seconds**, including actual instance/model footage. Spoken text is approximately 300 words; rehearse with the screen transitions.

| # | Segment | Duration | Cumulative | Speaker |
|---|---------|---------:|-----------:|---------|
| 1 | Introduction | 10 s | 0:10 | Yazmin |
| 2 | Problem | 25 s | 0:35 | Yazmin |
| 3 | Solution | 20 s | 0:55 | Carlos |
| 4 | Homomorphic encryption | 25 s | 1:20 | Carlos |
| 5 | IBM Z and LinuxONE screen | 30 s | 1:50 | Álvaro |
| 6 | Actual demo | 35 s | 2:25 | Javier |
| 7 | Data and model | 8 s | 2:33 | Yazmin |
| 8 | Impact and close | 17 s | 2:50 | Yazmin |

## 1. Introduction

We are Los Antimarrulla from UACJ. Our project evaluates diabetes screening risk on encrypted data. It is designed for IBM LinuxONE under AI Secured.

## 2. Problem

In Mexico, 18.3 percent of adults have diabetes, and about one in three does not know it. In 2024, 112 thousand diabetes deaths were registered. Hospitals need better screening, but sharing patient records with an external AI service creates privacy concerns. Can the model work without seeing those records?

## 3. Solution

The hospital encrypts 21 indicators and keeps the private key. The risk service computes on ciphertexts. Only the hospital decrypts the score and displays its largest contributing factors. This is screening to prioritize a glucose test, not a diagnosis.

## 4. Homomorphic encryption

Paillier lets us add encrypted values and multiply them by known model weights without decrypting. The server computes the encrypted logit; the hospital applies the sigmoid. Mutual TLS 1.3 protects transport, and AES-256-GCM protects hospital vault records.

## 5. IBM Z

The design uses two containers: a hospital holding the key and a keyless risk service. The demo shares one VM, so its administrator is trusted. Homomorphic evaluation uses modular arithmetic on integers thousands of bits long.

*Show actual LinuxONE provider/VM identity, `uname -m`, running containers and the loaded model. State that it runs on LinuxONE only after this execution is recorded. Otherwise retain “designed for LinuxONE.”*

## 6. Actual demo

The service sees 21 ciphertexts and returns an encrypted score. The hospital sees the risk, threshold decision and contributing factors. Our historical local test matched all 2,000 fixed-point reference integers, with the same AUC in plaintext and encrypted evaluation.

*Replace or supplement this sentence with the measured translated-release LinuxONE results. Record the synthetic profile C flow; keep the environment label visible.*

## 7. Data and model

We trained on 253 thousand public CDC responses. Test AUC is 0.83, with 80 percent sensitivity. Patient inputs reach the risk service only as ciphertexts.

## 8. Impact and close

More than 11 thousand SSA diabetes admissions included an amputation in 2024. We want earlier screening with less disclosure. The service sees ciphertexts; the hospital sees the result. Thank you.

## Recording checks

- [ ] Actual LinuxONE/model footage and measured release results inserted; no local image relabeled
- [ ] English narration and on-screen labels checked
- [ ] Two timed rehearsals, <=170 seconds with transitions
- [ ] Instance, containers and model visible for at least ten seconds in total
- [ ] OpenSSL/architecture evidence saved; no unmeasured CPACF claim
- [ ] Describe survey screening, not a clinical diagnosis or future disease prediction
- [ ] Audio and authorized voices checked
- [ ] Final file <=180 seconds by `ffprobe`; public URL verified without a login
- [ ] Official PDF and video record updated

For questions: ENSANUT used a separate reduced model, AUC about 0.77, with underestimated risk. It does not validate the 21-feature MVP in Mexico.
