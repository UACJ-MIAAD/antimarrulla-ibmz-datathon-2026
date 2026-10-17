"""Build the public architecture atlas using only the Python standard library.

Run from any directory: python3 tools/build_diagrams.py
SVGs and HTML are deterministic. This tool does not modify runtime code or data.
"""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site/assets/diagrams"
REPO = "https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026"
BASE = "b04fadb"

# Each node is title, detail lines, and ownership color. Edges reference node indices.
DIAGRAMS = [
    dict(id="system", title="The complete screening flow", group="System", intro="Synthetic feature values cross the risk-service boundary as ciphertexts; the service returns an encrypted score. Public protocol metadata remains visible.", source=["src/screening/hospital.py", "src/screening/protocol.py"], nodes=[
        ("1 / Synthetic input", ["21 integer-coded indicators", "Browser → Hospital API"], "hospital"),
        ("2 / Validate and encrypt", ["Hospital validates feature ranges", "Paillier public key → 21 ciphertexts"], "hospital"),
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
        ("3 / Validate original codes", ["Exactly 21 integers in schema order", "Reject missing, extra or invalid values"], "hospital"),
        ("4 / Prepare encrypted request", ["Generate a random 32-hex request ID", "Encrypt with hospital Paillier key"], "hospital"),
        ("5 / Call the risk service", ["Mutual TLS 1.3 and server verification", "POST /v2/evaluate"], "service"),
        ("6 / Validate and decrypt response", ["Match ID, model, schema and exponent", "Recover exact fixed-point integer"], "hospital"),
        ("7 / Interpret and store", ["Probability, threshold, contributions", "Save encrypted synthetic evaluation"], "storage"),
        ("8 / Return the UI result", ["Show ciphertext samples and risk", "Show component timings"], "hospital"),
    ], note="The Hospital API is reached through SSH in the team demo. The static public site does not accept patient evaluations."),
    dict(id="service", title="Risk-service component", group="Components", intro="The service holds the public model and its TLS identity. It receives encrypted input values and returns an encrypted linear score.", source=["src/screening/service.py", "src/screening/protocol.py"], nodes=[
        ("1 / Authenticate transport", ["Mutual TLS, minimum TLS 1.3", "Require a trusted client certificate"], "service"),
        ("2 / Check HTTP request", ["POST /v2/evaluate; JSON body", "Reject unsupported or oversized input"], "service"),
        ("3 / Validate the wire contract", ["Version, model, schema and request ID", "Public key, 21 ciphertexts, exponent 0"], "service"),
        ("4 / Check arithmetic bounds", ["Validate ciphertext group membership", "Verify fixed-point overflow bound"], "service"),
        ("5 / Evaluate without decryption", ["Homomorphic weighted sum + intercept", "Re-randomize the encrypted score"], "service"),
        ("6 / Capture optional audit evidence", ["Exact wire bytes, hashes and metadata", "Capture failure → HTTP 503"], "storage"),
        ("7 / Return successful response", ["HTTP 200 only after audit capture", "Ciphertext result plus service_ms"], "service"),
        ("8 / Operational logging", ["Request ID, timing and byte counts", "Audit mode adds transport metadata"], "service"),
    ], note="Encrypted values hide feature contents from the service; public keys, identifiers, message sizes, model metadata and timing remain visible. Audit checks are scoped observations, not proof against a malicious host administrator."),
    dict(id="protocol", title="Cryptography and numerical contract", group="Components", intro="Paillier protects the linear score. The sigmoid and threshold are applied only after hospital decryption.", source=["src/screening/contract.py", "src/screening/protocol.py"], nodes=[
        ("1 / Export the trained model", ["Fold training-only standardization", "Float weights w and intercept b"], "model"),
        ("2 / Quantize model parameters", ["W = round(10^9 × w)", "B = round(10^9 × b)"], "model"),
        ("3 / Encrypt original inputs", ["21 unscaled integer CDC codes", "Paillier 2048 bits; exponent = 0"], "hospital"),
        ("4 / Service computes Enc(z)", ["z = B + sum(W[i] × x[i])", "Only additions and known scalars"], "service"),
        ("5 / Hospital decrypts z", ["Exact match to fixed-point reference", "Separate float quantization bound"], "hospital"),
        ("6 / Hospital interprets z", ["logit = z / 10^9; p = sigmoid(logit)", "Compare p with validation threshold"], "hospital"),
    ], note="Exact encrypted/fixed-point agreement does not imply zero floating-point quantization error. The schema-wide logit error bound is approximately 1.03 × 10^-7. CKKS and Granite are not integrated."),
    dict(id="vault", title="Operational database: the encrypted vault", group="Data", intro="The implemented operational store is an append-only JSONL file, not a relational database. Every saved evaluation has an encrypted payload.", source=["src/screening/vault.py", "src/screening/hospital.py", "docker/compose.yml"], nodes=[
        ("Hospital payload / in memory", ["synthetic, profile, input (21 fields)", "probability, risk_high, date"], "hospital"),
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
    dict(id="model", title="Screening model and experiment lifecycle", group="Components", intro="Training uses public CDC survey records. ENSANUT is a separate exploratory reduced model; it does not validate the 21-feature demo clinically.", source=["src/screening/data.py", "src/screening/train.py", "src/screening/ensanut.py"], nodes=[
        ("1 / CDC UCI 891", ["253,680 public survey records", "Target + 21 original-coded features"], "model"),
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

COLORS = {"hospital": "#6fdc8c", "service": "#78a9ff", "storage": "#d4bbff", "public": "#ffcf70", "model": "#79d7de"}


def build_svg(d):
    """Lay out short readable nodes with explicit, numbered directional edges."""
    rows = (len(d["nodes"]) + 1) // 2
    height = 40 + rows * 202
    positions = []
    for i in range(len(d["nodes"])):
        row, col = divmod(i, 2)
        if row % 2:
            col = 1 - col
        positions.append((30 + col * 530, 28 + row * 202))
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1040 {height}" role="img" aria-labelledby="title desc">',
         f'<title id="title">{escape(d["title"])}</title><desc id="desc">{escape(d["intro"])}</desc>',
         '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#a8b8cd"/></marker></defs>',
         f'<rect width="1040" height="{height}" fill="#10141e" rx="16"/>']
    for a, b in d.get("edges", list(zip(range(len(positions)-1), range(1,len(positions))))):
        ax, ay = positions[a]; bx, by = positions[b]
        if ay == by:
            x1, x2 = (ax+450, bx) if ax < bx else (ax, bx+450)
            path = f"M{x1} {ay+76} H{x2}"
        elif ax == bx:
            path = f"M{ax+225} {ay+152} V{by}"
        else:
            # The analytical merge uses the center gutter, outside the cards.
            path = f"M{ax+225} {ay+152} V{ay+177} H{bx+225} V{by}"
        s.append(f'<path d="{path}" fill="none" stroke="#a8b8cd" stroke-width="2.4" marker-end="url(#arrow)"/>')
    for (title, lines, owner), (x,y) in zip(d["nodes"], positions):
        c = COLORS[owner]
        s.extend([f'<g transform="translate({x} {y})"><rect width="450" height="152" rx="12" fill="#1a2232" stroke="{c}" stroke-opacity=".6"/>',
                  f'<rect x="0" y="16" width="4" height="120" rx="2" fill="{c}"/>',
                  f'<text x="20" y="34" fill="{c}" font-family="system-ui, sans-serif" font-size="21" font-weight="650">{escape(title)}</text>'])
        for j,line in enumerate(lines):
            s.append(f'<text x="20" y="{72+j*30}" fill="#e8edf5" font-family="system-ui, sans-serif" font-size="19">{escape(line)}</text>')
        s.append('</g>')
    s.append('</svg>')
    return '\n'.join(s) + '\n'


def build_page():
    cards = []
    for i,d in enumerate(DIAGRAMS, 1):
        links = ' · '.join(f'<a href="{REPO}/blob/{BASE}/{p}">{escape(p)}</a>' for p in d["source"])
        steps = ''.join(f'<li><b>{escape(t)}</b> — {escape("; ".join(lines))}</li>' for t,lines,_ in d["nodes"])
        cards.append(f'''<section class="card" id="{d['id']}" aria-labelledby="h-{d['id']}">
<div class="card-head"><div><span class="eyebrow">{d['group']} / {i:02}</span><h2 id="h-{d['id']}">{d['title']}</h2></div><a class="open" href="assets/diagrams/{d['id']}.svg" target="_blank" rel="noopener">Open SVG ↗</a></div>
<p class="intro">{d['intro']}</p><figure><div class="diagram" tabindex="0" role="region" aria-label="{d['title']} diagram, scroll horizontally on a small screen"><img src="assets/diagrams/{d['id']}.svg" alt="{d['title']}. Text equivalent follows." width="1040" height="{40+((len(d['nodes'])+1)//2)*202}" loading="{'eager' if i==1 else 'lazy'}"></div><figcaption>Follow the arrows. On small screens, scroll the diagram or open the SVG at full size.</figcaption></figure>
<p class="boundary">{d['note']}</p><details><summary>Read the components and steps</summary><ol>{steps}</ol></details><p class="source">Implementation references · {links}</p></section>''')
    nav = ''.join(f'<a href="#{d["id"]}">{d["title"]}</a>' for d in DIAGRAMS)
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>System diagrams · Los Antimarrulla</title><meta name="description" content="Implemented screening architecture, component flowcharts, encrypted vault schema and analytical data model."><link rel="icon" href="assets/logo.png">
<style>
:root{color-scheme:dark;--bg:#0e0e13;--card:#171b25;--line:#303a4d;--text:#e8edf5;--muted:#b0bdd0;--blue:#91baff}*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:20px}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.6 system-ui,-apple-system,Segoe UI,sans-serif}a{color:var(--blue);text-underline-offset:4px}a:focus-visible,summary:focus-visible,.diagram:focus-visible{outline:3px solid #ffcf70;outline-offset:4px}.wrap{max-width:1160px;margin:auto;padding:28px 24px 60px}header nav{display:flex;gap:20px;flex-wrap:wrap}h1{font-size:clamp(36px,5.3vw,60px);line-height:1.07;letter-spacing:-.035em;margin:28px 0 18px;max-width:850px}h2{font-size:clamp(23px,3vw,30px);line-height:1.25;margin:4px 0 0}.eyebrow{color:var(--blue);font-size:12px;letter-spacing:.14em;text-transform:uppercase}.subtitle{color:var(--muted);font-size:19px;max-width:850px}.status,.boundary{border-left:3px solid #ffcf70;padding:10px 16px;background:#222127;border-radius:0 8px 8px 0}.status{margin:22px 0}.legend{display:flex;gap:10px 24px;flex-wrap:wrap;margin:24px 0}.legend span{font-size:14px}.legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:8px}.index{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px 20px;padding:20px;background:var(--card);border:1px solid var(--line);border-radius:12px;margin-bottom:34px}.index a{font-size:14px}.card{border:1px solid var(--line);border-radius:16px;background:var(--card);padding:24px;margin:0 0 28px;min-width:0}.card-head{display:flex;justify-content:space-between;align-items:center;gap:16px}.open{flex-shrink:0;font-size:14px}.intro{color:var(--muted);margin:14px 0 20px}figure{margin:0}.diagram{overflow-x:auto;border-radius:12px;background:#10141e}.diagram img{display:block;width:100%;min-width:820px;height:auto}figcaption,.source{font-size:12px;color:var(--muted);margin:8px 0 18px}.source{overflow-wrap:anywhere;margin-top:18px}.boundary{font-size:14px;margin:20px 0}summary{cursor:pointer;color:var(--blue)}details ol{padding-left:22px}details li{margin:9px 0;font-size:14px}footer{color:var(--muted);font-size:14px;margin-top:35px}@media(max-width:600px){.wrap{padding:20px 14px 40px}.card{padding:18px 14px}.card-head{align-items:flex-start;flex-direction:column;gap:10px}.index{grid-template-columns:1fr}.subtitle{font-size:17px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media print{body{background:white;color:black}.card{break-inside:avoid;background:white;border:1px solid #aaa}.index,header nav,.open{display:none}.diagram img{min-width:0}.source,.intro,footer{color:#333}a{color:#164a89}}
</style></head><body><main class="wrap"><header><nav aria-label="Project navigation"><a href="index.html">← Project and plan</a><a href="forecast.html">Forecast dashboard</a><a href="''' + REPO + '''">Repository</a></nav><p class="eyebrow" style="margin-top:32px">Los Antimarrulla / IBM Z Datathon 2026</p><h1>One system.<br>Every boundary visible.</h1><p class="subtitle">Ten implementation diagrams: the complete flow, deployment, independent components, encrypted storage and analytical data relationships.</p><p class="status"><b>Implementation map, not deployment certification.</b> Based on the English runtime merged in <code>b04fadb</code>. Local tests and containers are verified. Final English LinuxONE evidence, labs, human review and the narrated video remain open. Two containers on the same VM share a trusted administrator.</p></header>
<div class="legend" aria-label="Diagram colors">''' + ''.join(f'<span><i style="background:{c}"></i>{label}</span>' for (label,c) in [('Hospital / plaintext boundary',COLORS['hospital']),('Risk service / ciphertexts',COLORS['service']),('Stored artifact',COLORS['storage']),('Public / aggregate data',COLORS['public']),('Model / computation',COLORS['model'])]) + '''</div><nav class="index" aria-label="Diagram index">''' + nav + '</nav>' + '\n'.join(cards) + '''<footer><p>No live patient information is loaded here. These diagrams are static, downloadable SVGs with text alternatives; no external diagram library is required.</p><p><a href="index.html#plan">Current delivery plan</a> · <a href="''' + REPO + '''/blob/codex/system-diagrams/docs/SYSTEM_DIAGRAMS.md">Diagram guide and storage dictionary</a></p></footer></main></body></html>
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for d in DIAGRAMS:
        (OUT / (d["id"] + ".svg")).write_text(build_svg(d), encoding="utf-8")
    (ROOT / "site/architecture.html").write_text(build_page(), encoding="utf-8")
    print(f"Built {len(DIAGRAMS)} SVG diagrams and site/architecture.html")


if __name__ == "__main__":
    main()
