# Yazmin's form integrated into the English release

Source: [PR 8](https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026/pull/8), `yazflores`, commit `09cadf5ef63a83a485e67e4a206f4dde80c7fa09`. Integrated through a merge preserving that commit and its authorship into [PR 9](https://github.com/UACJ-MIAAD/antimarrulla-ibmz-datathon-2026/pull/9). This automated integration review does not replace another teammate's release approval.

## Review and resolution

| Finding | Resolution |
|---------|------------|
| PR 8 changes the retired `src/tamizaje/ui/index.html` and calls the Spanish API | Retain the English path `src/screening/ui/index.html`; port every caller and response field to the English v2 contract. Do not restore the retired package. |
| The previous English editor lacked Yazmin's coded answers, grouped questions and inline validation | Preserve her five groups, 21 controls, explicit source codes, required/integer/range checks, busy-button protection, selected-profile state, service indicator, light/dark CSS and risk/threshold meter. |
| Random evaluation could leave the editor displaying the previous profile's values | Refill from `hospital.input` in the completed response, so the form matches the evaluated input. |
| Income labels could be mistaken for current local currency | Identify the categories as annual household income in 2015 US dollars. Explain that the UCI dataset recodes BRFSS responses. |
| Source metadata needed review | Checked age categories, education, income and heavy-drinking definitions against the [CDC 2015 codebook](https://www.cdc.gov/brfss/annual_data/2015/pdf/codebook15_llcp.pdf), pages 22, 26, 112 and 119. Sex and binary codes follow the recoded [UCI 891 dataset](https://archive.ics.uci.edu/dataset/891/cdc+diabetes+health+indicators), not the original BRFSS answer numbers. |
| A schema error still contained Spanish wording | Translate the missing/unexpected-feature error in `schema.py`. |
| Phone-width layout had not been checked | Verify the 390-pixel layout, keep the editor within the viewport and link error text through `aria-describedby`. |

The model, weights, threshold, feature order, raw datasets and original measured evidence are unchanged. The source hash changes with this integration; final LinuxONE measurements must identify the combined release commit. Existing `5412abe` measurements remain historical local measurements, with their original provenance.

## Validation

- `make verify`: **90 passed**, model reproduction exact on macOS arm64.
- `make verify-docker`: **86 passed, 4 skipped**, model reproduced within 4.69e-14 in Ubuntu 24.04 arm64. The four skipped tests require Git, absent from the image.
- Isolated Docker demo: synthetic profiles A/B/C pass smoke checks with exact decrypted integers, mutual TLS and the vault. This is local evidence, not LinuxONE evidence.
- Actual browser: profile C gives **66.3%**; changing its BMI from 36 to 30 gives **57.8%**. BMI 150 is rejected; BMI 30.5 is rejected; an empty age selection is required. Invalid submissions preserve the previous result. Random input repopulates all 21 controls. Valid evaluation restores enabled buttons and shows all timing fields.
- At 390 × 844, document width is 390 pixels and result panels stack in one column. No browser warnings or errors were observed during the walkthrough.
- Captures: `submission/evidence/local/yazmin_form_integrated_C.png` and `yazmin_form_mobile.png`. Both are synthetic, local Docker screenshots.

US-6.4's synthetic form implementation is complete. Clinical usability studies, calibration in Mexico, real LinuxONE execution, final release review and video completion are separate claims and remain unproven/open where applicable. PR 8's earlier verification does not approve PR 9.

## Immediate handoff

Javier should spend the next 30 minutes on release coordination: confirm the registered Hack2Skill leader and access; agree on one combined commit with Carlos and Álvaro; secure a human review; collect actual lab/attendance evidence; and rehearse the English script with Yazmin. Do not spend this block on CKKS, Granite, a second VM or more form polish.

Carlos and Álvaro should run the combined English commit on the real LinuxONE VM, using `docs/LINUXONE.md`, and commit measurements plus provider/architecture/model/demo screenshots. Yazmin and Javier should prepare English narration immediately, then replace the draft's LinuxONE slate with actual footage. The internal submission target remains October 18 at 13:00 UTC; the hard deadline is 16:30 UTC.
