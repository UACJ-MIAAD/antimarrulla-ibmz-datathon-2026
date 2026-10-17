# Project decision record

Inputs: [candidate ideas](IDEAS.md) and the [simulated blind ranking](Idea_Ranking_Antimarrulla.pptx). The ranking used AI-simulated judges; its scores are not official event scores or evidence of clinical performance.

## Meeting

| Field | Value |
|-------|-------|
| Date | October 17, 2026, before the internal 07:00 Ciudad Juárez start |
| Participants | Javier, Álvaro, Carlos, Yazmin |
| Moderator | Javier Augusto Rebull Saucedo |

Three simulated judge profiles (IBM Z expert, AI for Good leader and AI/security researcher) scored eleven anonymized ideas using the 40-point rubric.

| Rank | Idea | Theme | /40 | AI innovation /20 | Feasibility /5 |
|------|------|-------|----:|------------------:|---------------:|
| 1 | Borderless transfers: remittances and OFAC/AML | T1/T2 | 29.3 | 13.7 | 3.0 |
| **2** | **Encrypted-data diabetes screening** | **T2** | **29.0** | **15.0** | **2.7** |
| 3 | Federated remittance fraud detection | T2 | 28.3 | 13.0 | 4.0 |
| 4 | SPEI fraud shield | T1 | 28.0 | 12.0 | 4.7 |
| 5 | Post-quantum banking scanner | T2 | 27.3 | 10.7 | 3.7 |

## Selected project

Privacy-preserving screening (original planning name retained in historical evidence). Theme **T2 · AI Secured: Innovation Without Exposure**. The service evaluates encrypted inputs; the hospital retains its private key and sees the result.

Selection reasons: strong Theme 2 fit; highest simulated innovation subtotal; consistent 29/40 across the three profiles; a measurable encrypted-versus-plaintext comparison; relevant Mexican diabetes context and existing team familiarity with SINAVE/EDR data. These are reasons for choosing the idea, not a prediction of winning.

The first-ranked remittance idea had a riskier three-layer scope and ambiguous theme fit. Federated fraud was visually demonstrable but familiar. SPEI fraud was feasible but less original in the simulated comparison.

## Main technical risk and response

TenSEAL/SEAL may not build on s390x. **Paillier with pure-Python `phe` is the MVP** and is sufficient for logistic regression. At H2, check optional CKKS availability; if unavailable, keep Paillier without changing the MVP. The project does not require a different fallback idea.

| MVP by H18 | Optional after MVP | Out of scope |
|------------|--------------------|--------------|
| Public-data logistic regression | CKKS via TenSEAL/OpenFHE | Definitive clinical diagnosis |
| Paillier inference on actual LinuxONE | Granite explanation | Private patient data |
| Split-screen ciphertext/hospital demo | SINAVE/EDR map and E5 extensions | Mobile app |
| Same-sample accuracy and sequential latency | Additional throughput experiments | Encrypted training |
| Two containers and actual platform evidence | Second physical/virtual host | Protection from the trusted demo host administrator |

## Intended platform use

Ubuntu 24.04 s390x containers on LinuxONE Community Cloud. Hospital holds Paillier/vault keys; the service has no Paillier private key. Homomorphic modular arithmetic uses integers thousands of bits long. Mutual TLS protects transport and AES-256-GCM protects vault records. OpenSSL may use CPACF on the platform, but the application has not demonstrated effective acceleration. CLI `openssl speed` alone does not establish application acceleration. Required labs and optional Granite remain distinct from an implemented feature claim.

## Data

CDC UCI 891 supplies 253,680 public survey records and 21 predictors for model training. Source terms are documented in [DATA_SOURCES.md](DATA_SOURCES.md) and [data/README.md](../data/README.md). SINAVE incidence and INEGI/DGIS death data support Mexican context. The label concerns reported diagnosis; the model is not a future-diabetes or mortality predictor.

## Agreement record

| Member | Agreement recorded |
|--------|--------------------|
| Javier Augusto Rebull Saucedo | |
| Álvaro Hernández Jarquín | |
| Carlos Enrique Gonzalez Moran | |
| Yazmin Ivonne Flores Martinez | |

## Decisions retained after external audits

| Topic | Decision | Consequence |
|-------|----------|-------------|
| E5 and CKKS | Retain as optional extensions | Paillier/H18 demo remain the MVP; pause extensions if H12 flow is missing |
| AI disclosure | Removed from README; publication location is still a team decision | Local draft is not completed disclosure; recorded rules require transparency |
| Trust boundary | Hospital and service share one demo VM | Administrator is trusted; synthetic demo inputs only |
| Contact emails | Retain with prior team agreement | No removal during translation |
| Hosting | Keep Netlify and its badge | No paid-plan purchase or hosting migration |
| Language | Captain requires English code, comments, site, documents and deliverables | Coordinated migration, verification and new release evidence; preserve historical records |
