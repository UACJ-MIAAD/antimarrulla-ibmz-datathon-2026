# Candidate ideas — planning record

**Selected:** Idea A, now Privacy-preserving screening. [DECISION.md](DECISION.md) and [PROJECT.md](PROJECT.md) define the actual implementation. The exploratory proposals below are historical ideas, not claims of implemented capabilities.

The team considered three initial Theme 2 ideas and eight additional ideas: SPEI fraud, triage, insurance, border crossings, anonymization, CFDI, post-quantum scanning and remittances with OFAC/AML. Eleven ideas were ranked by three AI-simulated blind judges; see [the ranking deck](Idea_Ranking_Antimarrulla.pptx).

| Idea | One-line concept | Guide/lab connection |
|------|------------------|---------------------|
| A: encrypted medical inference | Evaluate diabetes risk without disclosing patient inputs to the service | Sensitive Data Protection; predictive hybrid/multi-model lab |
| B: federated remittance fraud | Three simulated banks learn together without sharing transaction rows | Sensitive Data Protection/Fraud Detection; predictive hybrid lab |
| C: private support assistant | Confidential guidance with encrypted transport and no plaintext logs | Secure AI; predictive/generative lab |

## Platform constraints

The technical criterion requires actual LinuxONE Community Cloud execution, open-source AI/ML and screenshots supporting claimed container/security/compute capabilities. Secure Execution, Hyper Protect, Crypto Express and on-chip AI acceleration may not be exposed by the VM. Check availability before promising them. The selected implementation guarantees none of these capabilities and does not claim protection from its trusted demo administrator.

## Idea A: encrypted medical inference

Clinical records are sensitive and difficult to share. The proposal explores privacy-preserving diabetes screening rather than definitive diagnosis.

Original proposal: hospital encrypts inputs, LinuxONE computes in a protected environment or homomorphically, and only the hospital decrypts the result. The original brainstorming also mentioned encrypted training and CKKS; the selected scope **uses public plaintext training and Paillier inference only**. Hardware AES acceleration or confidential execution was conditional on platform availability, not a completed feature.

Demo concept: split screen with ciphertexts at the server and risk at the hospital, same-sample AUC and measured latency. Suggested datasets were CDC BRFSS/UCI 891 (about 250,000 records) or Pima (768 records); CDC was selected. Difficulty: medium-high, driven by encryption parameters, speed and s390x library support.

| Risk | Planned mitigation |
|------|--------------------|
| Homomorphic library unavailable on s390x | Pure-Python Paillier; optional CKKS check at H2 |
| Slow inference | Small linear model, measured sample and sequential timings |
| Excessive medical claims | Screening terminology and explicit clinical/population limits |

## Idea B: simplified federated remittance fraud

Each institution sees only part of the fraud problem. The proposal uses three simulated banks with local training; only model weights/updates reach a central FedAvg aggregator. Optional differential-privacy noise was considered. Updates alone do not establish privacy against every attack.

The intended LinuxONE role is the trusted aggregator and possibly global-model inference. Encrypt transport and assess any confidential-compute capability before claiming it. No actual federated system was built for this submission.

Demo concept: bank-specific recall before/after rounds and a central panel showing weights rather than transaction rows. Improvement must be measured, not guaranteed. Suggested data: synthetic PaySim or PCA-anonymized ULB credit-card fraud, partitioned non-identically across banks. Estimated difficulty: medium; a light SGD/logistic implementation avoids heavy frameworks.

| Risk | Planned mitigation |
|------|--------------------|
| Federation offers no improvement | Measure results on non-identical partitions |
| Extreme imbalance | Report recall/AP with an appropriate validation strategy |
| Appears to be only averaging | Explain the threat model and show exactly what the aggregator receives |

## Idea C: private support assistant

The proposal addresses sensitive requests from vulnerable people who fear disclosure. It considered encrypted client/server communication, protected processing, no plaintext query logs and verified official guidance. End-to-end privacy against administrators would require actually available confidential execution and a demonstrated threat model; ordinary TLS alone would not establish that property.

Demo concept: user-visible conversation beside ciphertext-only operational evidence, plus a plaintext-log search. Suggested knowledge base: team-curated official resources and synthetic example questions, never real private conversations. Verify any current resource through its official provider before using it. The prototype alternative is intent classification plus retrieval; a large generative model on s390x was considered high risk in 24 hours.

| Risk | Planned mitigation |
|------|--------------------|
| LLM unavailable or slow | Light intent model/retrieval; LLM optional |
| Incorrect sensitive guidance | Reviewed bounded responses and verified official resources |
| Weak data/methodology evidence | Explicit intent-classification evaluation |
| Ethical risk | Clear professional/emergency-care limits; no private conversation dataset |

This proposal is not an operational helpline or a recommendation of unverified services.

## Original decision matrix

At the initial meeting, all four members score 1–5 and record the average. This blank matrix is the historical template, not a completed vote.

| Idea | 24-hour feasibility | Demo strength | IBM Z role | Social value | Decision |
|------|:-------------------:|:-------------:|:----------:|:------------:|:--------:|
| A: encrypted inference | | | | | |
| B: federated fraud | | | | | |
| C: private assistant | | | | | |

An idea scoring only 1–2 on feasibility is excluded. Break ties by demo strength, then captain decision. Limit the decision meeting to fifteen minutes. The recorded simulated ranking and final selection are in DECISION.md.
