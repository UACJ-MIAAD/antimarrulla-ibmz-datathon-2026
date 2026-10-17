# System diagrams and storage dictionary

Owner: Javier / documentation and public site. This atlas documents the implemented English runtime at `b04fadb`; it does not certify deployment. The static site and documentation additions do not change the screening source hash or trained model. Final LinuxONE evidence must still identify the code actually executed.

## Public atlas

Open [all diagrams](https://antimarrulla-tamizaje.netlify.app/architecture). Each diagram is a standalone, downloadable SVG with a text equivalent on the page. No external diagram renderer, CDN or patient API is required.

| Diagram | Implementation reference |
|---------|--------------------------|
| Complete screening flow | `src/screening/hospital.py`, `protocol.py` |
| Deployment and trust boundaries | `docker/compose.yml`, `docs/DEPLOYMENT.md` |
| Hospital component | `hospital.py`, `schema.py` |
| Risk-service component | `service.py`, `protocol.py` |
| Cryptography and numerical contract | `contract.py`, `protocol.py` |
| Operational vault schema | `vault.py`, `hospital.py` |
| Analytical data model | `src/data_prep/care_stage_mart.py`, `docs/DATA_MODEL.md` |
| Screening model lifecycle | `data.py`, `train.py`, `ensanut.py` |
| E5 forecasting pipeline | `forecast.py`, `site/forecast.html` |
| Evidence and release flow | `service.py`, `two_hosts.py`, `package.py` |

## Operational database: actual persisted schema

There is no SQL engine or relational patient database. The Hospital container writes one encrypted envelope per synthetic evaluation to `/var/lib/screening/vault.jsonl`, in the persistent `vault` Docker volume. There is no CURP field, patient table, record-editing endpoint or cross-source patient relationship.

| Persisted field | Type | Visibility and meaning |
|-----------------|------|------------------------|
| `id` | String | Visible random 32-hex evaluation/request identifier; used as AES-GCM associated data |
| `nonce` | Base64 string | Visible random 12-byte nonce; reuse is rejected against known file nonces |
| `ct` | Base64 string | AES-256-GCM ciphertext with its authentication tag |

The decrypted JSON payload contains the following fields. They are not plaintext columns on disk.

| Encrypted payload field | Type | Meaning |
|-------------------------|------|---------|
| `synthetic` | Boolean | Demo evaluation marker, currently true |
| `profile` | String | Synthetic profile or custom-input label |
| `input` | Object | The 21 feature-name/integer pairs |
| `probability` | Number | Hospital-interpreted screening score |
| `risk_high` | Boolean | Comparison with the validation threshold |
| `date` | Number | Evaluation Unix timestamp |

The AES key is a separate external 32-byte file mounted read-only. Paillier keys are generated in Hospital memory; the service never receives the private key. Paillier keys are not the vault key. Restarting Hospital generates another Paillier key pair; existing vault records remain readable with the retained AES key. No automated backup, key recovery or vault migration is claimed. The vault does not encrypt operational logs, service audit files or the entire VM disk.

## Analytical database: files, grain and relationships

These are logical file relationships, not enforced SQL foreign keys. Original official field names remain unchanged.

| Entity/file | Logical key or grain | Relationship |
|-------------|----------------------|--------------|
| `data/catalogos/entidades.csv` | `cve_ent`, 32 state codes | One state to many annual mart rows; one state to one geometry feature |
| `data/marts/cascada_entidad_anio.csv` | `(cve_ent, anio)`, 256 rows | 32 states × 2017–2024; aggregates independent sources |
| `data/geo/estados_mx.geojson` | `cve_ent`, 32 features | Lookup by state code, not by patient |
| SINAVE products | State/region/national × week × sex × diabetes type | Notifications aggregated to state/year for the mart; weekly series separately feed E5 |
| Death aggregates | Registration/occurrence year × residence state × sex × age × cause | Mart requires matching occurrence/registration years and E10–E14 |
| Discharge aggregates | Year × treatment state × institution × sex × age × reason × condition | Treatment geography differs from residence and notification geography |
| SIS aggregates | Facility CLUES × month | Monthly treatment/control averages; annual exam counts |
| IMSS screening | Delegation × year | Delegation-to-state lookup from the state catalog |
| CONAPO population | Municipality × sex × year × age band | Annual state denominators after aggregation |
| `site/assets/care_stages.json` | English public presentation of state/year indicators | Export for public map; not a new linked patient cohort |
| `site/assets/forecast.json` | `(kind, level, id, sex)`, 222 series | Aggregate histories, forecasts, evaluation and scenarios; no patient IDs |

CDC training rows, ENSANUT local microdata and the synthetic hospital vault are separate stores. They have no person-level foreign keys to the Mexican aggregate mart. Do not represent matching state/year totals as the same people moving through a care cascade.

## Rebuild and review

```bash
python3 tools/build_diagrams.py
```

The builder uses only the Python standard library and deterministically writes `site/architecture.html` and ten `site/assets/diagrams/*.svg` files. Review node descriptions against the referenced source, check arrow routing and labels in the browser, and verify desktop/mobile navigation. The baseline identifier is deliberately fixed until a runtime change requires a new architecture review. The existing optional submission flowchart remains in `submission/flowchart/architecture.*`; this atlas expands the web explanation without replacing historical artifacts.
