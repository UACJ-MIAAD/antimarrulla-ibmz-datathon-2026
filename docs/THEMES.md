# Official themes

Teams choose a problem under **AI for Good** and explain why IBM Z/LinuxONE is useful for that design. The selected project uses **Theme 2**. [IDEAS.md](IDEAS.md) preserves the candidate discussion; it does not represent implemented scope.

## 1. Real-Time AI for Critical Decisions

“Detect. Decide. Respond.” Analyze streaming data and support time-sensitive decisions where latency matters. The platform rationale is high transaction volume and inference near operational data.

Guide examples: fraud, health prioritization, insurance risk, supply chains and system anomalies. Candidate examples include pre-authorization card fraud, emergency-call prioritization, factory sensor failure alerts and border-wait congestion warnings. Actual latency must be measured; a platform description is not a benchmark.

## 2. AI Secured: Innovation Without Exposure

“Powerful AI. Protected Data.” Protect sensitive information through encryption, confidential computation, federated learning, synthetic data or differential privacy.

Guide examples: sensitive data protection, cybersecurity, identity/access, secure assistants and post-quantum security. Candidate examples include encrypted medical inference, federated institutional models, assistants avoiding plaintext logs and synthetic-data generation.

The selected screening project uses Paillier inference on ciphertexts, hospital-owned keys and mutual TLS. LinuxONE hardware capabilities are relevant context; available or measured capabilities must be distinguished. The approved demo shares a trusted-admin VM and does not claim protection from that administrator. Encryption applies to inference, not encrypted training.

## 3. Wildcard: Beyond the Obvious

“Your boldest AI + Data Idea.” Address an important problem outside the other themes with a responsible, technically ambitious AI/data solution.

Guide examples: accessibility, education, sustainability, community impact, intelligent automation and new AI/data combinations. Candidate examples include Juárez–El Paso air-quality analysis, early support for university dropouts, open-data public transport routing and plain-language access to public services.

## Choosing a theme

| Main source of value | Theme |
|----------------------|-------|
| Decision speed | Theme 1 |
| Using sensitive data with less exposure | Theme 2 |
| An ambitious problem outside both | Theme 3 |

For every theme, show actual implementation, clear beneficiaries, sourced data and a credible platform role. The existing planning record cites the 2025 urban-route safety index (URSI) as an example, not as code to reuse.
