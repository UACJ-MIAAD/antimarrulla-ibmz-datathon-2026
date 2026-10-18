"""Presentation diagrams for the pitch deck (slides 3, 4 and 5).

Writes deterministic SVGs to submission/deck_diagrams/ using the deck theme (IBM dark, Arial).
Render PNGs with: rsvg-convert -z 2 file.svg -o file.png (transparent background).
Standard library only. Numbers shown come from the committed model and local measurements.
"""
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "submission", "deck_diagrams")
BLUE, LBLUE, GREEN, LGREEN, AMBER, VIOLET = "#0F62FE", "#78A9FF", "#24A148", "#6FDC8C", "#F1C21B", "#A56EFF"
INK, MUTED, CARD, CARD2, LINE = "#F4F4F4", "#A8B3C7", "#1A1A24", "#232634", "#3D4459"
FONT = "Arial, Helvetica, sans-serif"
MONO = "Menlo, 'DejaVu Sans Mono', monospace"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class SVG:
    def __init__(self, w, h):
        self.w, self.h, self.parts = w, h, []

    def add(self, s):
        self.parts.append(s)

    def rect(self, x, y, w, h, fill=CARD, stroke=None, sw=2, r=18, dash=None, opacity=1):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" fill-opacity="{opacity}"{st}{d}/>')

    def text(self, x, y, s, size=26, fill=INK, weight="normal", anchor="start", family=FONT, spacing=None):
        ls = f' letter-spacing="{spacing}"' if spacing else ""
        self.add(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{ls}>{esc(s)}</text>')

    def rich(self, x, y, runs, size=26, anchor="start", family=FONT):
        "runs: [(text, fill, weight, baseline_shift)]"
        spans = "".join(
            f'<tspan fill="{f}" font-weight="{w}"' + (f' baseline-shift="{b}" font-size="{size * 0.68:.0f}"' if b else "") + f">{esc(t)}</tspan>"
            for t, f, w, b in runs)
        self.add(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" text-anchor="{anchor}" xml:space="preserve">{spans}</text>')

    def arrow(self, x1, y1, x2, y2, color=LBLUE, sw=5, head=18):
        import math
        a = math.atan2(y2 - y1, x2 - x1)
        bx, by = x2 - head * math.cos(a), y2 - head * math.sin(a)
        lx, ly = bx + head * 0.55 * math.sin(a), by - head * 0.55 * math.cos(a)
        rx, ry = bx - head * 0.55 * math.sin(a), by + head * 0.55 * math.cos(a)
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>')
        self.add(f'<polygon points="{x2},{y2} {lx:.1f},{ly:.1f} {rx:.1f},{ry:.1f}" fill="{color}"/>')

    def pill(self, cx, cy, label, color, size=24, pad=22, family=FONT, fill=None, weight="bold"):
        w = len(label) * size * (0.60 if family == MONO else 0.56) + 2 * pad
        h = size * 1.75
        self.rect(cx - w / 2, cy - h / 2, w, h, fill="#14141C", r=h / 2)
        self.rect(cx - w / 2, cy - h / 2, w, h, fill=fill or color, r=h / 2, opacity=1 if fill else 0.18, stroke=color, sw=2)
        self.text(cx, cy + size * 0.36, label, size, color if not fill else INK, weight, "middle", family)
        return w

    # Icons are drawn in a 48x48 box centered on (cx, cy).
    def badge(self, cx, cy, kind, color, r=34):
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/>')
        s = r / 34
        g = f'<g transform="translate({cx - 24 * s:.1f},{cy - 24 * s:.1f}) scale({s:.3f})" fill="none" stroke="#FFFFFF" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round">'
        icons = {
            "key": '<circle cx="17" cy="24" r="7"/><path d="M24 24h15M34 24v6M39 24v4"/>',
            "lock": '<rect x="13" y="22" width="22" height="16" rx="3"/><path d="M17 22v-5a7 7 0 0 1 14 0v5"/><circle cx="24" cy="30" r="1.6" fill="#fff"/>',
            "server": '<rect x="11" y="11" width="26" height="11" rx="2.5"/><rect x="11" y="26" width="26" height="11" rx="2.5"/><path d="M16 16.5h.1M16 31.5h.1"/>',
            "fx": '<path d="M28 12c-4 0-5 3-5.5 6L20 32c-.5 3-2 5-5 5"/><path d="M15 21h12M29 26l7 9M36 26l-7 9"/>',
            "chart": '<path d="M11 36h27"/><path d="M13 30l7-8 6 5 10-12"/>',
            "vault": '<rect x="11" y="12" width="26" height="24" rx="3"/><circle cx="24" cy="24" r="5"/><path d="M24 19v-2M24 31v-2M19 24h-2M31 24h-2"/>',
            "log": '<path d="M15 13h18M15 21h18M15 29h12M15 37h8"/>',
            "clinic": '<path d="M12 37V17l12-6 12 6v20z"/><path d="M24 20v9M19.5 24.5h9"/>',
            "shield": '<path d="M24 11l12 5v8c0 7-5 12-12 14-7-2-12-7-12-14v-8z"/><path d="M19 24l4 4 6-7"/>',
        }
        self.add(g + icons[kind] + "</g>")

    def save(self, name):
        os.makedirs(OUT, exist_ok=True)
        body = "\n".join(self.parts)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}">\n'
               f"<title>{esc(name)}</title>\n{body}\n</svg>\n")
        with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
            f.write(svg)


def solution_flow():
    "Slide 3: hospital (steps 1 and 4) and risk service (steps 2 and 3) across the trust boundary."
    s = SVG(2426, 440)
    # Hospital zone
    s.rect(4, 4, 1010, 432, fill=GREEN, opacity=0.07, stroke=GREEN, sw=3, r=26)
    s.badge(56, 58, "key", GREEN, 28)
    s.text(100, 68, "HOSPITAL · holds the private key", 30, LGREEN, "bold", spacing=1.5)
    # Service zone
    s.rect(1412, 4, 1010, 432, fill=BLUE, opacity=0.08, stroke=LBLUE, sw=3, r=26)
    s.badge(1464, 58, "server", BLUE, 28)
    s.text(1508, 68, "RISK SERVICE on LinuxONE · no private key", 30, LBLUE, "bold", spacing=1.5)

    def step(x, y, n, title, line1, line2, color):
        s.rect(x, y, 930, 150, fill=CARD, stroke=LINE, sw=2, r=18)
        s.add(f'<circle cx="{x + 52}" cy="{y + 75}" r="30" fill="{color}"/>')
        s.text(x + 52, y + 86, n, 32, "#FFFFFF", "bold", "middle")
        s.text(x + 104, y + 58, title, 34, INK, "bold")
        s.text(x + 104, y + 98, line1, 25, MUTED)
        s.text(x + 104, y + 131, line2, 25, MUTED)

    step(40, 104, "1", "Encrypt the 19 answers", "Paillier 2048-bit public key; the key pair", "never leaves the hospital container", GREEN)
    step(40, 270, "4", "Decrypt and explain", "σ(z / 10⁹) → risk 63.3% for synthetic C;", "threshold 12.2% → prioritize a glucose test", GREEN)
    step(1452, 104, "2", "Evaluate on ciphertexts", "Enc(z) = ∏ Enc(xᵢ)^Wᵢ · Enc(B)  (mod n²)", "integer weights × 10⁹ · exact, no decryption", BLUE)
    step(1452, 270, "3", "Return one ciphertext", "rerandomized Enc(z); the service never sees", "an answer, the probability or the flag", BLUE)
    # Trust boundary and channel
    s.add(f'<line x1="1213" y1="20" x2="1213" y2="420" stroke="{AMBER}" stroke-width="3" stroke-dasharray="12 10"/>')
    s.pill(1213, 40, "mutual TLS 1.3", AMBER, 24)
    s.arrow(985, 179, 1438, 179, LBLUE, 6, 22)
    s.pill(1213, 140, "19 ciphertexts · 24 KB", VIOLET, 25, family=FONT)
    s.arrow(1438, 345, 985, 345, LGREEN, 6, 22)
    s.pill(1213, 306, "Enc(z) · 1.4 KB", VIOLET, 25)
    s.pill(1213, 400, "ciphertexts only", AMBER, 22)
    s.save("slide3_solution_flow")


def paillier_dot():
    "Slide 4: the encrypted dot product the service computes."
    s = SVG(1310, 480)
    s.rect(2, 2, 1306, 476, fill=CARD, stroke="#4A6FB5", sw=2.5, r=20)
    s.text(36, 54, "THE PAILLIER PROPERTY", 26, LBLUE, "bold", spacing=3)
    s.rich(36, 108, [("Enc(a)·Enc(b) = Enc(a+b)", INK, "bold", None)], 34, family=MONO)
    s.rich(1274, 108, [("Enc(a)", INK, "bold", None), ("k", INK, "bold", "super"), (" = Enc(k·a)", INK, "bold", None)], 34, anchor="end", family=MONO)
    x = 36
    for t in ("1", "2", None, "19"):
        if t is None:
            s.text(x + 26, 228, "···", 44, MUTED, "bold", anchor="middle")
            x += 56
            continue
        s.rect(x, 166, 206, 96, fill=VIOLET, opacity=0.16, stroke=VIOLET, sw=2.5, r=14)
        s.badge(x + 36, 214, "lock", VIOLET, 21)
        s.rich(x + 66, 226, [("Enc(x", INK, "bold", None), (t, INK, "bold", "sub"), (")", INK, "bold", None)], 30, family=MONO)
        s.rich(x + 202, 156, [("W", AMBER, "bold", None), (t, AMBER, "bold", "sub")], 30, anchor="end", family=MONO)
        x += 222
    s.text(x - 4, 226, "·", 40, MUTED, "bold", anchor="middle")
    s.rect(x + 12, 166, 176, 96, fill=VIOLET, opacity=0.16, stroke=VIOLET, sw=2.5, r=14)
    s.badge(x + 48, 214, "lock", VIOLET, 21)
    s.text(x + 130, 226, "Enc(B)", 30, INK, "bold", anchor="middle", family=MONO)
    s.arrow(x + 200, 214, x + 250, 214, LBLUE, 6, 18)
    s.rect(x + 258, 166, 190, 96, fill=BLUE, stroke=LBLUE, sw=2.5, r=14)
    s.text(x + 353, 226, "Enc(z)", 32, "#FFFFFF", "bold", anchor="middle", family=MONO)
    s.rect(36, 300, 1238, 146, fill=GREEN, opacity=0.08, stroke=GREEN, sw=2, r=16)
    s.badge(96, 373, "key", GREEN, 32)
    s.rich(150, 362, [("Hospital decrypts ", INK, "bold", None), ("z = W·x + B", LGREEN, "bold", None), ("  →  risk = σ(z / 10⁹)", INK, "bold", None)], 34)
    s.text(150, 410, "Exact: decrypted z matched the fixed-point reference on 2,000/2,000 CDC records.", 26, MUTED)
    s.save("slide4_paillier_dot")


def architecture():
    "Slide 5: containers on LinuxONE, channels and what stays where."
    s = SVG(1340, 760)
    s.rect(4, 4, 1332, 752, fill=BLUE, opacity=0.06, stroke=BLUE, sw=4, r=28)
    s.badge(56, 56, "server", BLUE, 30)
    s.text(104, 67, "IBM LinuxONE · s390x · Ubuntu 24.04 · Docker", 34, INK, "bold")
    s.pill(1236, 54, "demo VM", AMBER, 24)

    def box(x, y, w, h, color, light, title, subtitle):
        s.rect(x, y, w, h, fill=color, opacity=0.08, stroke=color, sw=3, r=22, dash="14 10")
        s.text(x + 26, y + 50, title, 33, light, "bold")
        s.text(x + 26, y + 84, subtitle, 24, MUTED)

    def row(x, y, w, icon, color, title, line):
        s.rect(x, y, w, 118, fill=CARD, stroke=LINE, sw=2, r=16)
        s.badge(x + 50, y + 59, icon, color, 30)
        s.text(x + 98, y + 50, title, 29, INK, "bold")
        s.text(x + 98, y + 88, line, 24, MUTED)

    box(28, 104, 528, 530, GREEN, LGREEN, "Hospital container", "the only holder of the private key")
    row(50, 214, 484, "key", GREEN, "Paillier private key", "generated and kept in memory")
    row(50, 344, 484, "lock", GREEN, "Encrypt · decrypt · explain", "python-paillier + gmpy2")
    row(50, 474, 484, "vault", GREEN, "Encrypted vault", "AES-256-GCM · read-only key file")

    box(784, 104, 528, 530, LBLUE, LBLUE, "Risk service", "public key and public weights only")
    row(806, 214, 484, "fx", BLUE, "Homomorphic logit", "∏ Enc(xᵢ)^Wᵢ · Enc(B) mod n²")
    row(806, 344, 484, "chart", BLUE, "Model logistic-cdc19-v1", "19 integer weights × 10⁹")
    row(806, 474, 484, "log", BLUE, "Minimal logs", "request IDs, milliseconds, bytes")

    s.text(670, 262, "19 ciphertexts", 25, INK, "bold", anchor="middle")
    s.arrow(564, 286, 776, 286, VIOLET, 7, 22)
    s.text(670, 324, "24 KB", 24, MUTED, anchor="middle")
    s.text(670, 412, "Enc(z)", 25, INK, "bold", anchor="middle")
    s.arrow(776, 436, 564, 436, LGREEN, 7, 22)
    s.text(670, 474, "1.4 KB", 24, MUTED, anchor="middle")
    s.pill(670, 556, "mTLS 1.3", AMBER, 25)
    s.text(670, 604, "client certificates", 21, MUTED, anchor="middle")

    s.text(28, 684, "Browser → SSH tunnel → hospital UI/API on VM loopback (port 8080). The service never sees an answer, the probability or the flag.", 22, MUTED)
    s.text(28, 724, "Demo: both containers share one VM and a trusted administrator · Production: the hospital container runs on hospital premises.", 22, AMBER)
    s.save("slide5_architecture")


if __name__ == "__main__":
    solution_flow()
    paillier_dot()
    architecture()
    print("wrote", os.path.abspath(OUT))
