"""HTML builders for the lab's visual components (no Streamlit imports, so
they can also be rendered in a plain browser for visual checks)."""
from __future__ import annotations

import base64
import html as _html
import re
from functools import lru_cache

from .. import config
from ..content.stages import STAGES
from . import art
from .art import icon


def esc(s) -> str:
    return _html.escape(str(s if s is not None else ""), quote=True)


def compact(markup: str) -> str:
    """Streamlit's markdown turns lines indented by 4+ spaces into code blocks
    and blank lines end an HTML block - strip both."""
    out = []
    for line in markup.splitlines():
        line = line.strip()
        if line:
            out.append(line)
    return "\n".join(out)


@lru_cache(maxsize=16)
def data_uri(filename: str) -> str:
    p = config.ASSETS_DIR / filename
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "svg": "image/svg+xml"}[p.suffix.lower().lstrip(".")]
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


# ----------------------------------------------------------------- header
def header_html() -> str:
    return compact(f'''
<div class="nl-root"><header class="nl-header">
  <div class="nl-credit">{art.teacher_badge()}
    <div class="nl-credit-text"><small>تصميم المعلمة</small><b>{esc(config.TEACHER_CREDIT_AR)}</b></div></div>
  <div class="nl-vsep"></div>
  <div class="nl-school">{icon("school", 30, 1.6)}<div class="nl-school-text">{esc(config.SCHOOL_AR)}</div></div>
  <div class="nl-vsep"></div>
  <div class="nl-grow"></div>
  <div class="nl-vsep"></div>
  <div class="nl-logos">
    <img class="nl-logo-inst" src="{data_uri('tuwaiq_moe.jpg')}" alt="Tuwaiq Academy - Ministry of Education">
  </div>
</header></div>''')


# ------------------------------------------------------------------- hero
def hero_html() -> str:
    return compact(f'''
<div class="nl-root"><div class="nl-hero">
  <div class="nl-hero-text">
    <div class="nl-welcome">Welcome to</div>
    <h1 class="nl-title">Nasmo Informatics</h1>
    <div class="nl-title-row"><span class="nl-ar-block"><span class="nl-ar-title" lang="ar">{esc(config.APP_NAME_AR)}</span><span class="nl-ar-tag" lang="ar">{esc(config.TAGLINE_AR)}</span></span></div>
    <div class="nl-tcc"><span>{icon("brain", 26, 1.7)}Think</span><span>{icon("code", 26, 1.9)}Code</span><span>{icon("trophy", 26, 1.7)}Compete</span></div>
    <p class="nl-lede">An interactive learning environment to prepare students for Nasmo Informatics 2 Competition — C++ Track (Fundamentals and Stages 1–4).</p>
  </div>
  <div class="nl-hero-art" aria-hidden="true"><div class="nl-art-box">
    {art.hero_laptop()}
    <span class="nl-fl nl-fl-code">{art.float_code()}</span>
    <span class="nl-fl nl-fl-trophy">{art.float_trophy()}</span>
    <span class="nl-fl nl-fl-note">Small Steps<br>Big Programs<i></i></span>
    <span class="nl-fl nl-fl-chart">{art.float_chart()}</span>
    <span class="nl-fl nl-fl-sq a"></span><span class="nl-fl nl-fl-sq b"></span><span class="nl-fl nl-fl-sq c"></span><span class="nl-fl nl-fl-sq d"></span>
    <span class="nl-fl nl-fl-spark a">{art.sparkle("#ffffff")}</span><span class="nl-fl nl-fl-spark b">{art.sparkle("#ff9ad0")}</span><span class="nl-fl nl-fl-spark c">{art.sparkle("#b39bff")}</span>
  </div></div>
</div></div>''')


# ------------------------------------------------------------ stage cards
def stage_card_html(stage: dict, idx: int, total: int, completed: int | None) -> str:
    """completed=None -> visitor (no progress shown, only the mission count)."""
    if completed is None:
        pct, meta, hint = 0, f"{total} Missions", ""
    else:
        pct = round(100 * completed / total) if total else 0
        meta = f"{completed}/{total} Missions"
        hint = ""
    return compact(f'''
<div class="nl-root"><article class="nl-card" style="--i:{idx}">
  <div class="nl-card-top"><span class="nl-badge">{stage["num"]:02d}</span>{art.stage_art(stage["id"])}</div>
  <h3>{esc(stage["title"])}</h3>
  <h4>{esc(stage["subtitle"])}</h4>
  <p style="min-height:2.6em;color:#d8c8f4">{esc(stage["desc"])}</p>
  <div class="nl-card-foot">
    <div class="nl-bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="{pct}" aria-label="{esc(stage["title"])} progress"><i style="width:{pct}%"></i></div>
    <div class="nl-card-meta"><b>{esc(meta)}</b></div>
  </div>
</article></div>''')


# ---------------------------------------------------------------- sidebar
def login_card_html(kind: str) -> str:
    if kind == "student":
        return compact(f'''<div class="nl-root"><div class="nl-login"><span class="ic">{icon("cap", 36, 1.6)}</span>
<span class="tx"><b>Student Login</b><small>Start your learning journey</small></span><span class="go">{icon("arrow", 20, 2.2)}</span></div></div>''')
    return compact(f'''<div class="nl-root"><div class="nl-login teacher"><span class="ic">{icon("teacher", 38, 1.6)}</span>
<span class="tx"><b>Teacher Login</b><small>Access dashboard and manage students</small></span><span class="go">{icon("arrow", 20, 2.2)}</span></div></div>''')


def nav_item_html(label: str, icon_name: str, active: bool) -> str:
    return compact(f'<div class="nl-root"><div class="nl-nav{" on" if active else ""}">{icon(icon_name, 26, 1.7)}<span>{esc(label)}</span></div></div>')


def who_html(user) -> str:
    role = "Teacher" if user.is_teacher else "Student"
    return compact(f'''<div class="nl-root"><div class="nl-who"><small>Signed in as</small><b>{esc(user.display_name)}</b>
<span class="role">{role}</span></div></div>''')


def deco_card_html() -> str:
    return compact(f'''<div class="nl-root"><div class="nl-deco"><div class="ar" lang="ar">نُفَكِّر .. نبرمج .. ننافس</div>
<div class="en">Think .. Code .. Compete</div>{art.sidebar_mountain()}</div></div>''')


# --------------------------------------------------------------- generic
def progress_bar_html(pct: int, label: str = "") -> str:
    return (f'<div class="nl-mini-bar"><div class="nl-bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" '
            f'aria-valuenow="{pct}"><i style="width:{pct}%"></i></div><span>{esc(label or str(pct) + "%")}</span></div>')


def kpis_html(items: list[tuple[str, str]]) -> str:
    cells = "".join(f'<div class="nl-kpi"><b>{esc(v)}</b><span>{esc(k)}</span></div>' for k, v in items)
    return compact(f'<div class="nl-root"><div class="nl-kpis">{cells}</div></div>')


def table_html(headers: list[str], rows: list[list[str]], raw_cols: set[int] | None = None) -> str:
    """rows hold plain text unless the column index is in raw_cols (trusted HTML)."""
    raw_cols = raw_cols or set()
    th = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = ""
    for r in rows:
        body += "<tr>" + "".join(
            f"<td>{c if i in raw_cols else esc(c)}</td>" for i, c in enumerate(r)) + "</tr>"
    return compact(f'<div class="nl-root"><div class="nl-scroll"><table class="nl-table"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div></div>')


def code_block_html(code: str) -> str:
    # NOT compacted: indentation inside code matters. Use a <pre>-like div with escaped text,
    # and protect it from markdown by encoding line breaks as <br> and spaces as &nbsp;.
    lines = []
    for ln in code.split("\n"):
        e = esc(ln).replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;").replace("  ", "&nbsp;&nbsp;")
        lines.append(e if e else "&nbsp;")
    return f'<div class="nl-root"><div class="nl-code" dir="ltr" style="white-space:normal">{"<br>".join(lines)}</div></div>'


def topic_cards_html(topics: list[tuple[str, str, str | None]]) -> str:
    cells = ""
    for title, desc, url in topics:
        if url:
            cells += (f'<a class="nl-topic" href="{esc(url)}" target="_blank" rel="noopener noreferrer"><b>{esc(title)}</b>'
                      f'<span>{esc(desc)}</span><em>Open official topic ↗</em></a>')
        else:
            cells += (f'<div class="nl-topic"><b>{esc(title)}</b><span>{esc(desc)}</span>'
                      f'<em style="color:var(--muted)">Practised in the lab missions (no official page)</em></div>')
    return compact(f'<div class="nl-root"><div class="nl-topic-grid">{cells}</div></div>')


def stages_options() -> list[tuple[str, str]]:
    return [(s["id"], s["title"] if s["id"] == "f" else f'{s["title"]} - {s["subtitle"]}') for s in STAGES]


# ----------------------------------------------------- quick chips / tab bar
def quick_chip_html(label: str, sub: str, icon_name: str, c1: str, c2: str) -> str:
    return compact(f'''<div class="nl-root"><div class="nl-qchip" style="--c1:{c1};--c2:{c2}"><span class="tile">{icon(icon_name, 26, 1.8)}</span>
<span><b>{esc(label)}</b><small>{esc(sub)}</small></span></div></div>''')


def tab_html(label: str, icon_name: str, active: bool, plus: bool = False) -> str:
    if plus:
        return compact(f'<div class="nl-root"><div class="nl-tab plus"><span class="pl">{icon(icon_name, 28, 2)}</span></div></div>')
    return compact(f'<div class="nl-root"><div class="nl-tab{" on" if active else ""}">{icon(icon_name, 24, 1.7)}<span class="t">{esc(label)}</span></div></div>')


def side_logo_html() -> str:
    return (f'<div class="nl-root"><div class="nl-side-logo"><img src="{data_uri('nasmo_logo_420.png')}" '
            f'alt="NASMO INFORMATICS - Think. Code. Compete."></div></div>')
