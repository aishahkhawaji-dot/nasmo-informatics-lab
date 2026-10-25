"""Printable internal training certificate (standalone HTML; use the Print button and choose
"Save as PDF"). Four designs; the student picks one. All of them carry the same text and the same
"internal, not official" statement."""
from __future__ import annotations

import html as _html

from .. import config

DESIGNS = {  # key -> (name, one-line description)
    "royal": ("Royal Purple", "Classic double border in the lab's purple and blue."),
    "galaxy": ("Galaxy Night", "Dark space sky with glowing stars and neon accents."),
    "gold": ("Golden Honor", "Warm cream paper, gold frame and a laurel seal."),
    "adventure": ("Adventure Quest", "Bright and playful, with the Nova robot and stars."),
}
DEFAULT_DESIGN = "royal"


def _e(s) -> str:
    return _html.escape(str(s or ""), quote=True)


def _stars_svg(n: int = 5, color: str = "#f5c542", size: int = 26) -> str:
    pts = "12,2 15,9 22,9.5 16.5,14 18.5,21.5 12,17.5 5.5,21.5 7.5,14 2,9.5 9,9"
    return "".join(f'<svg width="{size}" height="{size}" viewBox="0 0 24 24"><polygon points="{pts}" fill="{color}"/></svg>'
                   for _ in range(n))


def _seal_svg(fill: str, ring: str, text: str) -> str:
    return (f'<svg class="seal" viewBox="0 0 120 120" width="112" height="112" aria-hidden="true">'
            f'<circle cx="60" cy="60" r="56" fill="{ring}"/><circle cx="60" cy="60" r="46" fill="{fill}" stroke="#fff" stroke-width="2" stroke-dasharray="3 4"/>'
            f'<polygon points="60,26 68,48 91,48 72,62 79,84 60,70 41,84 48,62 29,48 52,48" fill="#fff"/>'
            f'<text x="60" y="102" text-anchor="middle" font-size="8" font-weight="700" fill="#fff" letter-spacing="2">{text}</text></svg>')


def _robot_svg() -> str:
    return ('<svg class="robot" viewBox="0 0 130 150" width="120" height="138" aria-hidden="true">'
            '<line x1="64" y1="26" x2="64" y2="40" stroke="#c9bdff" stroke-width="4"/><circle cx="64" cy="22" r="7" fill="#ff7ac0"/>'
            '<rect x="26" y="40" width="76" height="62" rx="26" fill="#fff" stroke="#8a63e6" stroke-width="3"/>'
            '<rect x="35" y="50" width="58" height="34" rx="16" fill="#2b1a90"/>'
            '<ellipse cx="51" cy="66" rx="7" ry="9" fill="#7df0ff"/><ellipse cx="77" cy="66" rx="7" ry="9" fill="#7df0ff"/>'
            '<path d="M50 80 Q64 100 78 80 Z" fill="#fff" opacity=".0"/><path d="M52 82 Q64 94 76 82" fill="none" stroke="#ff7ac0" stroke-width="4" stroke-linecap="round"/>'
            '<rect x="40" y="104" width="48" height="30" rx="12" fill="#c9bdff"/><circle cx="64" cy="119" r="6" fill="#ff7ac0"/>'
            '<path d="M32 112 L16 128" stroke="#c9bdff" stroke-width="9" stroke-linecap="round"/>'
            '<path d="M96 112 L118 86" stroke="#c9bdff" stroke-width="9" stroke-linecap="round"/><circle cx="119" cy="84" r="7" fill="#ffd84d"/></svg>')


_BASE = """
*{box-sizing:border-box}
body{margin:0;font-family:'IBM Plex Sans Arabic','Segoe UI',Tahoma,Arial,sans-serif;padding:16px;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.bar{text-align:center;margin-bottom:12px}
.bar button{font:600 16px 'IBM Plex Sans Arabic','Segoe UI',sans-serif;padding:10px 24px;border:0;border-radius:99px;background:#4f29b6;color:#fff;cursor:pointer}
.sheet{max-width:980px;margin:0 auto;text-align:center;position:relative;overflow:hidden}
.name{display:inline-block;min-width:50%;padding:0 28px 6px;font-weight:700}
.meta{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
.stats{display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin-top:14px}
.stats span{padding:4px 14px;border-radius:99px;font-size:14px;font-weight:600}
.ar{direction:rtl;font-weight:600}
@media print{body{padding:0}.bar{display:none}@page{size:A4 landscape;margin:8mm}}
@media (max-width:640px){.sheet{padding:26px 18px!important}h1{font-size:28px!important}.name{font-size:30px!important}}
"""

_PREVIEW_CSS = """
body{zoom:.37;padding:4px;pointer-events:none;user-select:none}
.wm{position:absolute;inset:0;display:grid;place-items:center;font-size:150px;font-weight:700;letter-spacing:14px;
    color:rgba(120,120,140,.20);transform:rotate(-16deg);z-index:9}
"""

_CSS = {
"royal": """
body{background:#f3efff;color:#1d1550}
.sheet{background:#fff;border:10px double #4f29b6;border-radius:6px;padding:44px 56px}
.sheet:before{content:"";position:absolute;inset:10px;border:2px solid #4d95ff;opacity:.35;pointer-events:none}
h1{margin:0;font-size:35px;color:#4f29b6}.lab{font-size:18px;color:#5b5a85;margin-top:4px}
.ar{font-size:22px;margin:6px 0 22px}.cert{font-size:18px;color:#5b5a85;margin:18px 0 6px}
.name{font-size:44px;border-bottom:2px solid #4d95ff;margin:6px 0 10px}
.what{font-size:24px;font-weight:600;margin:18px 0 6px}.why{font-size:16px;color:#5b5a85;max-width:720px;margin:0 auto}
.meta{margin-top:34px;font-size:14px;color:#5b5a85}.sign{margin-top:26px;font-size:15px}.sign b{display:block;font-size:18px}
.stats span{background:#efe9ff;color:#4f29b6}
.seal{position:absolute;right:30px;top:26px;width:88px;height:88px}
.disc{margin-top:22px;font-size:12.5px;color:#7a79a0;border-top:1px dashed #c9c3ee;padding-top:10px}
""",
"galaxy": """
body{background:#0b0630;color:#fff}
.sheet{background:radial-gradient(circle at 18% 12%,rgba(125,240,255,.22),transparent 38%),radial-gradient(circle at 85% 90%,rgba(255,122,192,.28),transparent 42%),linear-gradient(160deg,#1b1070,#2b1a90 55%,#12084f);
  border:3px solid #7df0ff;border-radius:22px;padding:46px 56px;box-shadow:0 0 0 8px #0b0630,0 0 0 11px #ff7ac0,0 0 40px rgba(125,240,255,.45)}
.dots{position:absolute;inset:0;background-image:radial-gradient(#fff 1px,transparent 1.6px),radial-gradient(#cdbbff 1px,transparent 1.4px);background-size:90px 90px,140px 140px;background-position:10px 20px,60px 70px;opacity:.55;pointer-events:none}
.sheet>*{position:relative}.sheet>.dots{position:absolute}
h1{margin:0;font-size:35px;color:#fff;text-shadow:0 0 18px rgba(125,240,255,.8)}.lab{font-size:18px;color:#cdbbff;margin-top:4px}
.ar{font-size:22px;margin:6px 0 22px;color:#ffd0ea}.cert{font-size:18px;color:#cdbbff;margin:18px 0 6px}
.name{font-size:46px;color:#ffd84d;text-shadow:0 0 20px rgba(255,216,77,.6);border-bottom:2px solid #ff7ac0;margin:6px 0 10px}
.what{font-size:24px;font-weight:600;margin:18px 0 6px;color:#7df0ff}.why{font-size:16px;color:#e4dcff;max-width:720px;margin:0 auto}
.meta{margin-top:34px;font-size:14px;color:#cdbbff}.sign{margin-top:26px;font-size:15px;color:#e4dcff}.sign b{display:block;font-size:18px;color:#fff}
.stats span{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.3);color:#fff}
.seal{position:absolute;right:30px;top:26px;width:88px;height:88px}
.disc{margin-top:22px;font-size:12.5px;color:#b9aee8;border-top:1px dashed rgba(255,255,255,.3);padding-top:10px}
""",
"gold": """
body{background:#efe6d2;color:#3b2a10}
.sheet{background:radial-gradient(circle at 50% 0,#fffdf6,#fbf3dd);border:3px solid #b8860b;padding:44px 56px;
  box-shadow:inset 0 0 0 10px #fbf3dd,inset 0 0 0 12px #d4a017,inset 0 0 0 20px #fbf3dd,inset 0 0 0 21px #b8860b}
h1{margin:0;font-family:'Playfair Display',Georgia,'Times New Roman',serif;font-size:42px;color:#7a5200;letter-spacing:1px}
.lab{font-size:18px;color:#8a6a2e;margin-top:4px;font-family:Georgia,serif;font-style:italic}
.ar{font-size:22px;margin:6px 0 22px;color:#7a5200}.cert{font-size:18px;color:#8a6a2e;margin:18px 0 6px;font-family:Georgia,serif;font-style:italic}
.name{font-family:'Playfair Display',Georgia,serif;font-size:46px;color:#3b2a10;border-bottom:2px solid #d4a017;margin:6px 0 10px}
.what{font-size:24px;font-weight:600;margin:18px 0 6px;color:#7a5200}.why{font-size:16px;color:#6b5530;max-width:720px;margin:0 auto}
.meta{margin-top:30px;font-size:14px;color:#8a6a2e}.sign{margin-top:22px;font-size:15px;color:#6b5530}.sign b{display:block;font-size:18px;color:#3b2a10}
.stats span{background:#f3e3b3;color:#7a5200}
.seal{display:block;margin:16px auto 0}
.disc{margin-top:18px;font-size:12.5px;color:#9a8458;border-top:1px dashed #d9c48a;padding-top:10px}
""",
"adventure": """
body{background:#ffe9f6;color:#2b1a90}
.sheet{background:linear-gradient(135deg,#fff6d6 0%,#ffe0f1 48%,#dfeeff 100%);border:8px solid #ff7ac0;border-radius:34px;padding:40px 56px;box-shadow:0 0 0 6px #fff,0 0 0 12px #4d95ff}
.conf{position:absolute;inset:0;pointer-events:none;background-image:radial-gradient(#ff7ac0 4px,transparent 5px),radial-gradient(#4d95ff 4px,transparent 5px),radial-gradient(#f5c542 4px,transparent 5px);background-size:120px 120px,170px 170px,210px 210px;background-position:10px 20px,70px 80px,120px 30px;opacity:.28}
.sheet>*{position:relative}.sheet>.conf{position:absolute}
h1{margin:0;font-size:35px;color:#e04aa3}.lab{font-size:18px;color:#4f29b6;margin-top:4px;font-weight:600}
.ar{font-size:22px;margin:6px 0 16px;color:#2b1a90}.cert{font-size:18px;color:#4f29b6;margin:10px 0 6px}
.name{font-size:46px;color:#2b1a90;border-bottom:4px dotted #ff7ac0;margin:6px 0 10px}
.what{font-size:26px;font-weight:700;margin:16px 0 6px;color:#4f29b6}.why{font-size:16px;color:#4a3d8f;max-width:720px;margin:0 auto}
.meta{margin-top:26px;font-size:14px;color:#4f29b6}.sign{margin-top:18px;font-size:15px;color:#4a3d8f}.sign b{display:block;font-size:18px;color:#2b1a90}
.stats span{background:#fff;border:2px solid #ff7ac0;color:#2b1a90}
.robot{position:absolute;left:28px;top:24px;width:96px;height:110px}.seal{position:absolute;right:30px;top:26px;width:88px;height:88px}
.starsrow{display:flex;justify-content:center;gap:6px;margin:6px 0}
.disc{margin-top:18px;font-size:12.5px;color:#6a5fb0;border-top:2px dashed #ffb3dc;padding-top:10px}
@media (max-width:640px){.robot,.seal{display:none}}
""",
}


def _decor(design: str) -> str:
    if design == "royal":
        return _seal_svg("#4f29b6", "#4d95ff", "NASMO LAB")
    if design == "galaxy":
        return '<div class="dots"></div>' + _seal_svg("#ff7ac0", "#7df0ff", "NASMO LAB")
    if design == "gold":
        return ""
    return '<div class="conf"></div>' + _robot_svg() + _seal_svg("#e04aa3", "#f5c542", "NASMO LAB")


def certificate_html(cert: dict, student_name: str, design: str = DEFAULT_DESIGN, stats: dict | None = None,
                     preview: bool = False) -> str:
    """stats (optional): {"rank": str, "xp": int, "stars": int} shown as small badges.
    preview=True: a small, non-printable sample with a PREVIEW watermark (no print button) - it is only for
    choosing a design and can never be mistaken for an issued certificate."""
    if design not in DESIGNS:
        design = DEFAULT_DESIGN
    issued = str(cert.get("issued_at") or "")[:10]
    chips = ""
    if stats:
        chips = ('<div class="stats">'
                 f'<span>{_e(stats.get("rank"))}</span><span>{int(stats.get("xp", 0))} XP</span>'
                 f'<span>{int(stats.get("stars", 0))} ★</span></div>')
    star_row = f'<div class="starsrow">{_stars_svg(5)}</div>' if design == "adventure" else ""
    gold_seal = _seal_svg("#b8860b", "#d4a017", "NASMO LAB") if design == "gold" else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Certificate {_e(cert.get('serial'))}</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;600;700&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
<style>{_BASE}{_CSS[design]}{_PREVIEW_CSS if preview else ''}</style></head><body>
{"" if preview else '<div class="bar"><button onclick="window.print()">Print / Save as PDF</button></div>'}
<div class="sheet">
  {'<div class="wm">PREVIEW</div>' if preview else ""}
  {_decor(design)}
  {star_row}
  <h1>Certificate of Training Completion</h1>
  <div class="lab">{_e(config.APP_NAME)}</div>
  <div class="ar">{_e(config.APP_NAME_AR)} · {_e(config.TAGLINE_AR)}</div>
  <div class="cert">This is to certify that</div>
  <div class="name">{_e(student_name)}</div>
  <div class="what">{_e(cert.get('title'))}</div>
  <p class="why">{_e(cert.get('reason'))}</p>
  {chips}
  {gold_seal}
  <div class="meta"><span>Date: {_e(issued)}</span><span>Serial: {_e(cert.get('serial'))}</span></div>
  <div class="sign"><b>{_e(config.TEACHER_CREDIT_AR)}</b>{_e(config.SCHOOL_AR)}</div>
  <div class="disc">Internal training certificate issued by the lab. It is not an official certificate of the Nasmo
  Informatics competition, Tuwaiq Academy or the Ministry of Education.</div>
</div></body></html>"""
