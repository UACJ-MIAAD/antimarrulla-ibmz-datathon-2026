"""Build the public architecture atlas using only the Python standard library.

Run from any directory: python3 tools/build_diagrams.py
SVGs and HTML are deterministic. This tool does not modify runtime code or data.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site/assets/diagrams"
REPO = "https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026"
BASE = "ef1e21d"

# Each node is title, detail lines, and ownership color. Edges reference node indices.
DIAGRAMS = [
    dict(id="system", title="The complete screening flow", group="System", intro="Synthetic feature values cross the risk-service boundary as ciphertexts; the service returns an encrypted score. Public protocol metadata remains visible.", source=["src/screening/hospital.py", "src/screening/protocol.py"], nodes=[
        ("1 / Synthetic input", ["19 integer-coded indicators", "Browser → Hospital API"], "hospital"),
        ("2 / Validate and encrypt", ["Hospital validates feature ranges", "Paillier public key → 19 ciphertexts"], "hospital"),
        ("3 / Evaluate encrypted features", ["Mutual TLS 1.3 → risk service", "Compute the integer linear score"], "service"),
        ("4 / Decrypt at the hospital", ["Service returns one ciphertext", "Private key stays in hospital memory"], "hospital"),
        ("5 / Interpret the score", ["Scale 10^9 → sigmoid → threshold", "Show probability and contributions"], "hospital"),
        ("6 / Save, then return to the UI", ["AES-256-GCM encrypted vault record", "Hospital returns the synthetic result"], "storage"),
    ], note="This predicts the CDC reported prediabetes/diabetes label for screening. It does not predict future onset or mortality, and it is not a diagnosis."),
    dict(id="deployment", title="Where each component lives", group="System", intro="The approved MVP uses two containers on one VM. A second host is optional; the VM administrator remains trusted.", source=["docker/compose.yml", "docs/DEPLOYMENT.md"], nodes=[
        ("Team browser", ["Local browser on an operator laptop", "Synthetic demo only"], "hospital"),
        ("SSH tunnel", ["Laptop loopback → VM loopback", "VM: 127.0.0.1:8080"], "hospital"),
        ("Hospital container / VM", ["Serves frontend + API on port 8080", "Paillier private key lives in memory"], "hospital"),
        ("Risk-service container / same VM", ["Internal Docker network, port 8443", "TLS identity; no Paillier private key"], "service"),
        ("Hospital vault / Docker volume", ["/var/lib/screening/vault.jsonl", "AES key mounted from outside Git"], "storage"),
        ("Netlify / separate public site", ["Pitch, map, forecast, plan, diagrams", "No Hospital API or vault connection"], "public"),
    ], edges=[(0,1),(1,2),(2,3),(2,4)], note="No edge connects Netlify to the hospital. Actual final English LinuxONE execution, provider identity and measurements still require original evidence."),
    dict(id="hospital", title="Hospital component", group="Components", intro="The hospital owns plaintext validation, encryption, decryption, interpretation and encrypted storage. The browser is inside its trusted demo workflow.", source=["src/screening/hospital.py", "src/screening/schema.py"], nodes=[
        ("1 / Serve UI and metadata", ["GET / and /api/synthetic", "GET /api/state → service health"], "hospital"),
        ("2 / Receive synthetic evaluation", ["POST /api/evaluate", "Profile, random input or custom input"], "hospital"),
        ("3 / Validate original codes", ["Exactly 19 integers in schema order", "Reject missing, extra or invalid values"], "hospital"),
        ("4 / Prepare encrypted request", ["Generate a random 32-hex request ID", "Encrypt with hospital Paillier key"], "hospital"),
        ("5 / Call the risk service", ["Mutual TLS 1.3 and server verification", "POST /v2/evaluate"], "service"),
        ("6 / Validate and decrypt response", ["Match ID, model, schema and exponent", "Recover exact fixed-point integer"], "hospital"),
        ("7 / Interpret and store", ["Probability, threshold, contributions", "Save encrypted synthetic evaluation"], "storage"),
        ("8 / Return the UI result", ["Show ciphertext samples and risk", "Show component timings"], "hospital"),
    ], note="The Hospital API is reached through SSH in the team demo. The static public site does not accept patient evaluations."),
    dict(id="service", title="Risk-service component", group="Components", intro="The service holds the public model and its TLS identity. It receives encrypted input values and returns an encrypted linear score.", source=["src/screening/service.py", "src/screening/protocol.py"], nodes=[
        ("1 / Authenticate transport", ["Mutual TLS, minimum TLS 1.3", "Require a trusted client certificate"], "service"),
        ("2 / Check HTTP request", ["POST /v2/evaluate; JSON body", "Reject unsupported or oversized input"], "service"),
        ("3 / Validate the wire contract", ["Version, model, schema and request ID", "Public key, 19 ciphertexts, exponent 0"], "service"),
        ("4 / Check arithmetic bounds", ["Validate ciphertext group membership", "Verify fixed-point overflow bound"], "service"),
        ("5 / Evaluate without decryption", ["Homomorphic weighted sum + intercept", "Re-randomize the encrypted score"], "service"),
        ("6 / Capture optional audit evidence", ["Exact wire bytes, hashes and metadata", "Capture failure → HTTP 503"], "storage"),
        ("7 / Return successful response", ["HTTP 200 only after audit capture", "Ciphertext result plus service_ms"], "service"),
        ("8 / Operational logging", ["Request ID, timing and byte counts", "Audit mode adds transport metadata"], "service"),
    ], note="Encrypted values hide feature contents from the service; public keys, identifiers, message sizes, model metadata and timing remain visible. Audit checks are scoped observations, not proof against a malicious host administrator."),
    dict(id="protocol", title="Cryptography and numerical contract", group="Components", intro="Paillier protects the linear score. The sigmoid and threshold are applied only after hospital decryption.", source=["src/screening/contract.py", "src/screening/protocol.py"], nodes=[
        ("1 / Export the trained model", ["Fold training-only standardization", "Float weights w and intercept b"], "model"),
        ("2 / Quantize model parameters", ["W = round(10^9 × w)", "B = round(10^9 × b)"], "model"),
        ("3 / Encrypt original inputs", ["19 unscaled integer CDC codes", "Paillier 2048 bits; exponent = 0"], "hospital"),
        ("4 / Service computes Enc(z)", ["z = B + sum(W[i] × x[i])", "Only additions and known scalars"], "service"),
        ("5 / Hospital decrypts z", ["Exact match to fixed-point reference", "Separate float quantization bound"], "hospital"),
        ("6 / Hospital interprets z", ["logit = z / 10^9; p = sigmoid(logit)", "Compare p with validation threshold"], "hospital"),
    ], note="Exact encrypted/fixed-point agreement does not imply zero floating-point quantization error. The schema-wide logit error bound is approximately 1.03 × 10^-7. CKKS and Granite are not integrated."),
    dict(id="vault", title="Operational database: the encrypted vault", group="Data", intro="The implemented operational store is an append-only JSONL file, not a relational database. Every saved evaluation has an encrypted payload.", source=["src/screening/vault.py", "src/screening/hospital.py", "docker/compose.yml"], nodes=[
        ("Hospital payload / in memory", ["synthetic, profile, input (19 fields)", "probability, risk_high, date"], "hospital"),
        ("AES-256-GCM encryption", ["External 32-byte vault key", "Random 12-byte nonce; AAD = ID"], "hospital"),
        ("One persisted JSONL envelope", ["id: visible random request ID", "nonce: Base64; ct: Base64 + GCM tag"], "storage"),
        ("Hospital persistent volume", ["vault.jsonl → append, flush, fsync", "Survives container recreation"], "storage"),
        ("Authorized read in hospital", ["Read ID, nonce and ciphertext", "Authenticate with ID and decrypt"], "hospital"),
        ("Secret lifecycle / separate", ["AES key outside Git, mounted read-only", "Paillier key: memory, regenerated"], "hospital"),
    ], edges=[(0,1),(1,2),(2,3),(3,4)], note="Envelope ID and nonce are visible on disk. The vault protects its payload; it does not encrypt all VM disks, logs, audit files or backups. No patient table, CURP, SQL engine, record-editing API or key-recovery system is implemented."),
    dict(id="data-model", title="Analytical database: files and logical keys", group="Data", intro="This is the implemented file-based analytical model. Relationships describe aggregation and lookup keys; no SQL foreign-key constraints or patient-level joins exist.", source=["docs/DATA_MODEL.md", "src/data_prep/care_stage_mart.py"], nodes=[
        ("State dimension / catalog", ["entidades.csv: cve_ent (01–32)", "Names, region, IMSS delegation map"], "public"),
        ("Independent source aggregates", ["SINAVE, deaths, discharges, SIS", "IMSS screening + CONAPO population"], "public"),
        ("State/year analytical mart", ["cascada_entidad_anio.csv", "Logical key: (cve_ent, anio), 256 rows"], "storage"),
        ("Published care-stage data", ["care_stages.json: English view", "32 states × 2017–2024 indicators"], "public"),
        ("State geometry / map lookup", ["estados_mx.geojson: cve_ent", "32 polygons; state-code lookup"], "public"),
        ("Public aggregate map", ["Rates, counts and descriptive ratios", "Different populations, no care cohort"], "public"),
    ], edges=[(0,2),(1,2),(2,3),(3,5),(4,5)], note="One state has many state/year rows. Notifications use reporting geography, deaths residence and discharges treatment geography. Matching state/year does not mean the same people progress through a cascade. CDC and the hospital vault have no patient linkage to this mart."),
    dict(id="model", title="Screening model and experiment lifecycle", group="Components", intro="Training uses public CDC survey records. ENSANUT is a separate exploratory reduced model; it does not validate the 19-feature demo clinically.", source=["src/screening/data.py", "src/screening/train.py", "src/screening/ensanut.py"], nodes=[
        ("1 / CDC UCI 891", ["253,680 public survey records", "Target + 21 coded features; model uses 19"], "model"),
        ("2 / Shared stratified splits", ["70% training / 15% validation / 15% test", "Seed 2026; ID excluded from features"], "model"),
        ("3 / Fit on training only", ["Standardization + logistic regression", "Fold scaling into original-code weights"], "model"),
        ("4 / Select threshold on validation", ["Sensitivity target ≥80%", "No threshold tuning on the test split"], "model"),
        ("5 / Evaluate held-out test", ["AUC, AP, Brier, sensitivity, specificity", "Report repeated-profile limitations"], "model"),
        ("6 / Export and compare", ["Versioned model, schema and hashes", "Float vs fixed vs encrypted: same sample"], "storage"),
    ], note="The separate ten-feature ENSANUT experiment shows transfer limitations and underestimated risk. Synthetic demo inputs have no clinical labels; do not assign them an AUC."),
    dict(id="forecast", title="E5 time-series component", group="Components", intro="The optional forecast operates on aggregated notified cases. It is independent of the Paillier screening flow and uses no patient identifiers.", source=["src/screening/forecast.py", "site/forecast.html", "docs/FORECAST.md"], nodes=[
        ("1 / Read SINAVE weekly series", ["2 types × 3 sexes × 37 geographies", "222 series, observed from 2022"], "public"),
        ("2 / Validate observations", ["Finite, complete weekly calendars", "Current data: zero imputed gaps"], "model"),
        ("3 / Rolling-origin model selection", ["Compare seasonal naive and ETS", "Train using only data before each cut"], "model"),
        ("4 / Build forecast and bands", ["63 steps: 11 bridge + 52 display weeks", "Empirical error bands are exploratory"], "model"),
        ("5 / Reconcile geographic totals", ["National → region → state", "Sparse-series fallback if required"], "model"),
        ("6 / Outer pipeline evaluation", ["Two overlapping origins; limited evidence", "Publish error and actual band coverage"], "model"),
        ("7 / Export public JSON", ["e5_forecast_v1.json → forecast.json", "Static aggregate artifact on Netlify"], "storage"),
        ("8 / Dashboard and cost scenarios", ["Type, geography and sex filters", "Budget requires user cost + source"], "public"),
    ], note="Demo ready; not a calibrated planning guarantee. No project unit cost is established. E5 is not encrypted; CKKS, Prophet, SARIMA and LinuxONE forecast training remain outside the delivered demo."),
    dict(id="evidence", title="Evidence and release flow", group="Components", intro="Execution evidence must identify the code and environment actually measured. The public site reports status; it does not create missing VM or human evidence.", source=["src/screening/service.py", "src/screening/two_hosts.py", "src/screening/package.py"], nodes=[
        ("1 / Agree on a clean code version", ["Pin commit; record code/model hashes", "Build both endpoints from that version"], "model"),
        ("2 / Execute the real environment", ["Process and full Hospital API metrics", "Synthetic inputs for the demo"], "hospital"),
        ("3 / Preserve service audit files", ["Optional SERVICE_EVIDENCE mode", "Wire bytes + TLS/hash metadata"], "storage"),
        ("4 / Compare original run artifacts", ["Match request/response hashes and IDs", "Check exact integers and scoped claims"], "model"),
        ("5 / Collect human-owned records", ["VM/provider, labs, review, narration", "Leader access and AI-use approval"], "public"),
        ("6 / Build final delivery", ["Final gate rejects missing records", "Team reviews; registered leader submits"], "storage"),
    ], note="Service audit files are not the AES hospital vault and may include client IP/certificate identity. The direct two-host runner supports parallel hospital workers; it does not exercise the Hospital UI or vault. A same-host rehearsal is not proof of two-host deployment or LinuxONE."),
]

from technical_diagrams import RENDERERS
from diagram_page import build_page
import re


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    heights = {}
    for d in DIAGRAMS:
        svg = RENDERERS[d['id']]()
        heights[d['id']] = int(re.search(r'viewBox="0 0 1200 (\d+)"', svg).group(1))
        (OUT / (d['id'] + '.svg')).write_text(svg, encoding='utf-8')
    (ROOT / 'site/architecture.html').write_text(build_page(DIAGRAMS, REPO, BASE, heights), encoding='utf-8')
    print(f"Built {len(DIAGRAMS)} technical SVG views and architecture navigator")


if __name__ == '__main__':
    main()
