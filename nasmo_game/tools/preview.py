"""Render the lab's home page as a plain static page (no Streamlit) so the
visual design can be checked in a real browser and compared with the mock-up.
Usage: python tools/preview.py out_dir"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from nasmo.content.stages import STAGES
from nasmo.ui import components as C, style


def page(theme="light", logged_in=False):
    cards = ""
    for i, s in enumerate(STAGES):
        done = (1 if i == 0 else 0) if logged_in else None
        cards += f'<div>{C.stage_card_html(s, i, 4, done)}</div>'
    chips = "".join(f'<div>{C.quick_chip_html(l, sub, ic, c1, c2)}</div>' for l, sub, ic, c1, c2 in [
        ("Interactive Kit", "Training guide", "brain", "#35c6e8", "#3b82f6"), ("Resources", "Official topics", "book", "#ff7ac0", "#e0457f"),
        ("About", "The lab", "info", "#6c8cff", "#3a4fd8"), ("Student Login", "Start learning", "cap", "#ffd166", "#e09a1a"),
        ("Teacher Login", "Manage students", "teacher", "#b18cff", "#6f4ef2")])
    tabs = "".join(f'<div>{C.tab_html(l, ic, l == "Home")}</div>' for l, ic in [("Home", "home"), ("Resources", "book")]) \
        + f'<div>{C.tab_html("Start", "play", False, plus=True)}</div>' \
        + "".join(f'<div>{C.tab_html(l, ic, False)}</div>' for l, ic in [("Kit", "brain"), ("Login", "cap")])
    side = (C.side_logo_html() + C.login_card_html("student") + C.login_card_html("teacher")
            + "".join(C.nav_item_html(l, ic, l == "Home") for l, ic in
                      [("Home", "home"), ("My Progress", "trophy"), ("Certificates", "cert"), ("Resources", "book"), ("About", "info")])
            + '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:0 0 0"><div class="pvb">Dark</div><div class="pvb">Motion: on</div></div>' + C.deco_card_html())
    btns = ('<div style="display:flex;gap:16px;margin-top:6px;flex-wrap:wrap">'
            '<button class="nl-pv-kit">Interactive Kit<br>Training Guide</button>'
            '<button class="nl-pv-go">Start Your Journey →</button></div>')
    extra = """<style>
    .nl-pv-kit,.nl-pv-go{font:600 19px 'IBM Plex Sans Arabic','Segoe UI',sans-serif;border-radius:999px;padding:10px 26px;min-height:64px;cursor:pointer}
    .nl-pv-kit{border:2px solid var(--pink);background:rgba(255,255,255,.6);color:var(--ink);min-width:270px;text-align:left}
    .nl-pv-go{border:0;background:linear-gradient(135deg,var(--primary-2),var(--primary));color:#fff;min-width:330px;font-size:21px}
    .pv-chips{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}.pv-tabs{display:none}
    @media(max-width:900px){.pv-chips{grid-template-columns:1fr 1fr}.pv-tabs{display:grid;grid-template-columns:repeat(5,1fr);position:fixed;left:0;right:0;bottom:0;background:linear-gradient(180deg,rgba(60,38,170,.96),rgba(40,22,130,.98));border-top:1px solid var(--line);z-index:9}}
    .wrap{display:grid;grid-template-columns:300px minmax(0,1fr);min-height:100vh}
    .side{background:var(--side);border-right:1px solid var(--line);padding:0 14px 14px;display:flex;flex-direction:column;gap:8px}.pvb{height:38px;border:1px solid var(--line);border-radius:12px;background:var(--lav);display:grid;place-items:center;font:600 14px sans-serif;color:var(--ink)}
    .main .hero-btns{margin-top:26px;position:relative;z-index:6}
    @media(max-width:900px){.wrap{grid-template-columns:1fr}.side{display:none}.main .hero-btns{margin-top:10px}}
    </style>"""
    return f"""<!doctype html><html lang="en" data-nl="{theme}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>preview</title>
{style.build_css_static(theme)}{extra}</head><body>
<div class="wrap"><aside class="side">{side}</aside>
<main class="main">{C.header_html()}
<div class="nl-hero-shell">{C.hero_html()}<div class="hero-btns">{btns}</div></div>
<div style="padding:16px 26px"><div class="pv-chips">{chips}</div><div class="nl-chips-title" style="margin-top:18px">Choose your stage</div><div class="nl-stage-grid">{cards}</div></div></main>
<nav class="pv-tabs">{tabs}</nav></div></body></html>"""


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    (out / "home_light.html").write_text(page("light"), encoding="utf-8")
    (out / "home_dark.html").write_text(page("dark", True), encoding="utf-8")
