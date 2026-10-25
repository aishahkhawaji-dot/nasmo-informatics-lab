"""Hand-built SVG art: icons, the hero laptop and the five stage illustrations.
Everything here is original vector drawing made for this project (the
organisation logos are NOT redrawn - they are the supplied image files)."""
from __future__ import annotations


def _svg(body: str, vb: str, cls: str = "", extra: str = "") -> str:
    return (f'<svg class="{cls}" viewBox="{vb}" xmlns="http://www.w3.org/2000/svg" '
            f'aria-hidden="true" focusable="false" {extra}>{body}</svg>')


# ------------------------------------------------------------------ icons
_ICON_PATHS = {
    "cap": '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11.5v4.2c0 1.2 2.7 2.8 6 2.8s6-1.6 6-2.8v-4.2"/><path d="M22 9v6"/>',
    "teacher": '<rect x="9" y="3" width="13" height="9" rx="1.5"/><path d="M12 15l-1.5 6M19 15l1.5 6M15.5 12v3"/><circle cx="5" cy="7" r="2.4"/><path d="M1.5 20v-4.5a3.5 3.5 0 0 1 7 0V20"/>',
    "home": '<path d="M3 11l9-8 9 8"/><path d="M5 10v10h5v-6h4v6h5V10"/>',
    "trophy": '<path d="M8 3h8v6a4 4 0 0 1-8 0z"/><path d="M8 5H4v1.5A3.5 3.5 0 0 0 8 10M16 5h4v1.5A3.5 3.5 0 0 1 16 10"/><path d="M12 13v4M8 21h8M9.5 17h5"/>',
    "cert": '<path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4"/><path d="M9 11h7M9 14h7"/><circle cx="12" cy="18" r="1.6"/>',
    "book": '<path d="M12 6c-2-1.5-5-2-9-2v14c4 0 7 .5 9 2 2-1.5 5-2 9-2V4c-4 0-7 .5-9 2z"/><path d="M12 6v14"/>',
    "info": '<circle cx="12" cy="12" r="9.5"/><path d="M12 11v6"/><circle cx="12" cy="7.6" r="0.6" fill="currentColor"/>',
    "brain": '<path d="M9 4a3 3 0 0 0-3 3 3 3 0 0 0-2 5 3 3 0 0 0 2 5 3 3 0 0 0 6 1V5a2.5 2.5 0 0 0-3-1z"/><path d="M15 4a3 3 0 0 1 3 3 3 3 0 0 1 2 5 3 3 0 0 1-2 5 3 3 0 0 1-6 1"/><path d="M9 9.5c1 0 2 .5 3 1.5M15 9.5c-1 0-2 .5-3 1.5M9 14.5c1 0 2-.5 3-1.5"/>',
    "code": '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "school": '<path d="M12 2v3M12 3.5l4 1.2-4 1.2"/><path d="M4 21V10l8-4 8 4v11"/><path d="M2 21h20M9 21v-5h6v5"/><path d="M8 11.5h2M14 11.5h2M8 14h2M14 14h2"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "moon": '<path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5z"/>',
    "logout": '<path d="M9 4H5v16h4M16 8l4 4-4 4M20 12H9"/>',
    "users": '<circle cx="9" cy="8" r="3.2"/><path d="M3 20v-1.5a5.5 5.5 0 0 1 11 0V20"/><circle cx="17" cy="9" r="2.4"/><path d="M16 14.2a4.5 4.5 0 0 1 5.5 4.3V20"/>',
    "chart": '<path d="M4 20V10M10 20V4M16 20v-8M22 20H2"/>',
    "settings": '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1"/>',
    "list": '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
    "check": '<path d="M4 12.5l5 5L20 6.5"/>',
    "lock": '<rect x="5" y="10" width="14" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
    "external": '<path d="M14 4h6v6M20 4l-9 9M18 14v6H4V6h6"/>',
    "play": '<path d="M7 4l13 8-13 8z"/>',
}


def icon(name: str, size: int = 22, stroke: float = 1.9, cls: str = "") -> str:
    body = _ICON_PATHS[name]
    return (f'<svg class="nl-ico {cls}" width="{size}" height="{size}" viewBox="0 0 24 24" '
            f'fill="none" stroke="currentColor" stroke-width="{stroke}" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true" focusable="false">{body}</svg>')


# --------------------------------------------------------------- hero art
def hero_laptop() -> str:
    """The laptop (screen with real code text, keyboard, books, plant, pencil)."""
    vb = "0 0 740 470"
    code = [
        ('#e9a8ff', '#include <bits/stdc++.h>'),
        ('#8fb4ff', 'using namespace std;'),
        ('', ''),
        ('#ffd27a', 'int main() {'),
        ('#ffffff', '  cout << "Think. Code. Compete.";'),
        ('#ff9ac8', '  return 0;'),
        ('#ffd27a', '}'),
    ]
    lines = ""
    y = 26
    for color, text in code:
        if text:
            safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            lines += f'<text x="26" y="{y}" fill="{color}">{safe}</text>'
        y += 19
    gutter = "".join(f'<text x="8" y="{26 + i * 19}" fill="#5d57a8" font-size="11">{i + 1}</text>'
                     for i in range(7))
    body = f'''
<defs>
  <linearGradient id="lp-screen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#241a6b"/><stop offset="1" stop-color="#150f45"/></linearGradient>
  <linearGradient id="lp-lid" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#d9d0f5"/><stop offset="1" stop-color="#f4f0ff"/></linearGradient>
  <linearGradient id="lp-deck" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e4dcfb"/><stop offset="1" stop-color="#c9bdf0"/></linearGradient>
  <linearGradient id="lp-b1" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#6a3fd0"/><stop offset="1" stop-color="#4f29b6"/></linearGradient>
  <linearGradient id="lp-b2" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff7ac0"/><stop offset="1" stop-color="#e04aa3"/></linearGradient>
  <linearGradient id="lp-leaf" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#c9a7ff"/><stop offset="1" stop-color="#ff9ad0"/></linearGradient>
  <filter id="lp-shadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="14" stdDeviation="14" flood-color="#4f29b6" flood-opacity=".28"/></filter>
</defs>
<ellipse cx="410" cy="440" rx="330" ry="22" fill="#4f29b6" opacity=".12"/>
<g class="nl-sway">
  <path d="M70 330 C40 270 60 220 105 190 C110 240 100 290 70 330z" fill="url(#lp-leaf)" opacity=".95"/>
  <path d="M85 335 C70 285 110 235 165 225 C150 280 130 315 85 335z" fill="#b48cff" opacity=".85"/>
  <path d="M55 340 C20 300 20 255 45 225 C70 255 75 300 55 340z" fill="#ffb3dc" opacity=".9"/>
</g>
<g filter="url(#lp-shadow)">
  <!-- lid back -->
  <polygon points="235,150 585,112 598,330 232,318" fill="url(#lp-lid)"/>
  <!-- screen -->
  <polygon points="249,162 574,127 585,318 247,306" fill="url(#lp-screen)"/>
</g>
<g transform="matrix(0.97 -0.105 0.034 0.97 252 163)" font-family="Consolas,'Courier New',monospace" font-size="13">
  {gutter}{lines}
  <rect x="36" y="128" width="8" height="14" fill="#fff" opacity=".85" class="nl-caret"/>
</g>
<!-- deck -->
<polygon points="232,318 598,330 722,412 130,404" fill="url(#lp-deck)"/>
<polygon points="130,404 722,412 722,426 130,418" fill="#a995e0"/>
<!-- keys -->
<g fill="#f6f2ff" opacity=".95">
  {"".join(f'<polygon points="{ax},{ay} {bx},{by} {bx2},{by2} {ax2},{ay2}"/>' for ax, ay, bx, by, bx2, by2, ax2, ay2 in _key_rows())}
</g>
<polygon points="395,386 478,388 486,401 388,400" fill="#d7ccf5"/>
<!-- books -->
<g>
  <polygon points="22,402 228,408 232,432 26,428" fill="url(#lp-b1)"/>
  <polygon points="22,402 228,408 232,415 26,409" fill="#8a63e6"/>
  <polygon points="34,376 218,381 222,404 38,400" fill="url(#lp-b2)"/>
  <polygon points="34,376 218,381 222,388 38,383" fill="#ff9ad0"/>
  <polygon points="46,352 206,356 210,380 50,376" fill="#3a2395"/>
  <polygon points="46,352 206,356 210,362 50,358" fill="#7c5bd6"/>
</g>
<!-- pencil -->
<g transform="rotate(-8 640 440)">
  <rect x="588" y="428" width="120" height="9" rx="2" fill="#6a3fd0"/>
  <polygon points="708,428 730,432.5 708,437" fill="#f6dcc2"/>
  <polygon points="722,430.4 730,432.5 722,434.6" fill="#e04aa3"/>
</g>
'''
    return _svg(body, vb, "nl-laptop")


def _key_rows():
    rows = []
    # perspective key grid on the deck: 4 rows
    top_y, bot_y = 331, 380
    rows_n = 4
    for r in range(rows_n):
        t0 = r / rows_n
        t1 = (r + 0.78) / rows_n
        y0 = top_y + (bot_y - top_y) * t0
        y1 = top_y + (bot_y - top_y) * t1
        # left/right x at a given y along the deck edges
        def edge(y):
            f = (y - 318) / (404 - 318)
            return 232 + (130 - 232) * f + 10, 598 + (722 - 598) * f - 12
        lx0, rx0 = edge(y0)
        lx1, rx1 = edge(y1)
        n = 13
        for c in range(n):
            a = c / n
            b = (c + 0.82) / n
            ax = lx0 + (rx0 - lx0) * a
            bx = lx0 + (rx0 - lx0) * b
            ax2 = lx1 + (rx1 - lx1) * a
            bx2 = lx1 + (rx1 - lx1) * b
            rows.append((round(ax, 1), round(y0, 1), round(bx, 1), round(y0 + 0.4, 1),
                         round(bx2, 1), round(y1, 1), round(ax2, 1), round(y1, 1)))
    return rows


def float_code() -> str:
    return _svg('<path d="M34 28L12 50l22 22M66 28l22 22-22 22M56 22L44 78" fill="none" stroke="currentColor" '
                'stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>', "0 0 100 100", "nl-fg")


def float_trophy() -> str:
    return _svg('<path d="M32 18h36v26a18 18 0 0 1-36 0z" fill="#fff" opacity=".95"/>'
                '<path d="M32 24H16v6a14 14 0 0 0 16 14M68 24h16v6a14 14 0 0 1-16 14" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round"/>'
                '<rect x="46" y="60" width="8" height="14" fill="#fff"/><rect x="34" y="74" width="32" height="8" rx="3" fill="#fff"/>'
                '<path d="M42 28l3 10 5-6 5 6 3-10" fill="none" stroke="#ff7ac0" stroke-width="3" stroke-linejoin="round"/>',
                "0 0 100 100", "nl-fg")


def float_chart() -> str:
    return _svg('<rect x="14" y="62" width="14" height="26" rx="3" fill="#7c5bd6"/>'
                '<rect x="36" y="46" width="14" height="42" rx="3" fill="#4d95ff"/>'
                '<rect x="58" y="30" width="14" height="58" rx="3" fill="#7c5bd6"/>'
                '<rect x="80" y="14" width="14" height="74" rx="3" fill="#4d95ff"/>'
                '<path d="M10 94h92" stroke="#b9a8f0" stroke-width="3" stroke-linecap="round"/>',
                "0 0 110 100", "nl-fg")


def sparkle(color: str = "#fff") -> str:
    return _svg(f'<path d="M50 0C54 30 70 46 100 50 70 54 54 70 50 100 46 70 30 54 0 50 30 46 46 30 50 0z" fill="{color}"/>',
                "0 0 100 100", "nl-fg")


# ----------------------------------------------------------- stage cards
def stage_art(stage_id: str) -> str:
    return {"f": _art_fundamentals, "s1": _art_modular, "s2": _art_flow,
            "s3": _art_mountain, "s4": _art_graph}[stage_id]()


def _art_fundamentals() -> str:
    body = '''
<defs>
 <linearGradient id="a1-scr" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a1d7a"/><stop offset="1" stop-color="#150f45"/></linearGradient>
 <linearGradient id="a1-leaf" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#c9a7ff"/><stop offset="1" stop-color="#ff9ad0"/></linearGradient>
</defs>
<g class="nl-sway"><path d="M196 104C176 70 188 40 214 22 220 54 214 82 196 104z" fill="url(#a1-leaf)"/><path d="M204 106C196 78 222 52 252 48 244 80 232 98 204 106z" fill="#b48cff" opacity=".85"/></g>
<rect x="70" y="14" width="138" height="82" rx="8" fill="#e2d9fb"/>
<rect x="76" y="20" width="126" height="70" rx="5" fill="url(#a1-scr)"/>
<text x="139" y="68" text-anchor="middle" font-family="Poppins,'IBM Plex Sans Arabic',Arial,sans-serif" font-weight="700" font-size="30" fill="#fff" class="nl-pulse">C++</text>
<rect x="64" y="96" width="150" height="10" rx="5" fill="#b9a8f0"/>
<rect x="30" y="64" width="32" height="40" rx="3" fill="#4f29b6" class="nl-bob2"/><rect x="36" y="58" width="32" height="40" rx="3" fill="#7c5bd6" class="nl-bob"/>
<rect x="24" y="100" width="200" height="8" rx="4" fill="#8a63e6" opacity=".55"/>'''
    return _svg(body, "0 0 260 120", "nl-card-art")


def _art_modular() -> str:
    body = '''
<defs><linearGradient id="a2-p" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff9ad0"/><stop offset="1" stop-color="#e04aa3"/></linearGradient>
<linearGradient id="a2-b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5aa2ff"/><stop offset="1" stop-color="#3a62e6"/></linearGradient></defs>
<g stroke="#4f6ae8" stroke-width="2" fill="none" stroke-linecap="round" stroke-dasharray="5 5" class="nl-flow">
<path d="M70 38h40M150 38h20v28M110 82h-24M62 54v14M170 66v10h26"/></g>
<rect x="24" y="22" width="44" height="32" rx="6" fill="#c7b6f7" class="nl-bob2"/>
<rect x="112" y="24" width="44" height="30" rx="6" fill="url(#a2-b)" class="nl-bob"/>
<text x="134" y="44" text-anchor="middle" font-size="18" fill="#fff" font-family="Arial" font-weight="700">✱</text>
<rect x="64" y="70" width="38" height="32" rx="6" fill="url(#a2-b)" class="nl-bob2"/>
<text x="83" y="93" text-anchor="middle" font-size="26" fill="#fff" font-family="Arial" font-weight="700">+</text>
<rect x="180" y="52" width="68" height="34" rx="6" fill="#fff" stroke="#ff7ac0" stroke-width="2" class="nl-bob"/>
<text x="214" y="75" text-anchor="middle" font-size="11" fill="#4f29b6" font-family="Consolas,monospace" font-weight="700">(a + b) % m</text>
<rect x="32" y="84" width="22" height="22" rx="5" fill="#ffd3ec" class="nl-drift"/>'''
    return _svg(body, "0 0 260 120", "nl-card-art")


def _art_flow() -> str:
    body = '''
<defs><linearGradient id="a3-p" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7c5bd6"/><stop offset="1" stop-color="#4f29b6"/></linearGradient></defs>
<g stroke="#4f6ae8" stroke-width="2" fill="none" stroke-linecap="round" stroke-dasharray="5 5" class="nl-flow">
<path d="M104 30h-24v30M130 30h22M190 46v16M140 80h-34M60 76v22"/></g>
<rect x="36" y="14" width="46" height="30" rx="5" fill="#2f4be0" class="nl-bob2"/>
<rect x="104" y="12" width="64" height="38" rx="6" fill="url(#a3-p)" class="nl-bob"/>
<rect x="116" y="24" width="40" height="5" rx="2.5" fill="#fff" opacity=".8"/><rect x="116" y="34" width="26" height="5" rx="2.5" fill="#fff" opacity=".5"/>
<rect x="152" y="58" width="76" height="36" rx="18" fill="#ff7ac0" opacity=".9" class="nl-bob"/>
<circle cx="190" cy="76" r="12" fill="#fff"/><path d="M190 69v8l5 3" stroke="#e04aa3" stroke-width="2.4" fill="none" stroke-linecap="round" class="nl-tick"/>
<rect x="76" y="62" width="64" height="38" rx="6" fill="url(#a3-p)" class="nl-bob2"/>
<rect x="88" y="74" width="40" height="5" rx="2.5" fill="#fff" opacity=".8"/>
<rect x="30" y="92" width="34" height="18" rx="5" fill="#c7b6f7" class="nl-drift"/>'''
    return _svg(body, "0 0 260 120", "nl-card-art")


def _art_mountain() -> str:
    body = '''
<defs><linearGradient id="a4-m1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8a63e6"/><stop offset="1" stop-color="#4f29b6"/></linearGradient>
<linearGradient id="a4-m2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c9b6ff"/><stop offset="1" stop-color="#7c5bd6"/></linearGradient></defs>
<polygon points="0,120 70,46 120,96 170,34 260,120" fill="url(#a4-m2)" opacity=".75"/>
<polygon points="40,120 130,22 230,120" fill="url(#a4-m1)"/>
<polygon points="130,22 108,50 120,46 130,58 142,46 154,52" fill="#fff" opacity=".9"/>
<g class="nl-flag"><path d="M130 22V4" stroke="#4f29b6" stroke-width="2.4" stroke-linecap="round"/><path d="M130 4l22 6-22 7z" fill="#ff7ac0"/></g>
<g stroke="#fff" stroke-width="1.6" opacity=".8"><path d="M96 62l-8 12 10 4 -6 12"/><path d="M166 70l8 12-8 6"/></g>
<circle cx="96" cy="62" r="4" fill="#fff" class="nl-pulse"/><circle cx="166" cy="70" r="4" fill="#fff" class="nl-pulse2"/>
<ellipse cx="60" cy="24" rx="20" ry="7" fill="#fff" opacity=".55" class="nl-drift"/><ellipse cx="210" cy="36" rx="16" ry="6" fill="#fff" opacity=".45" class="nl-drift2"/>
<path d="M0 118h260" stroke="#b9a8f0" stroke-width="2"/>'''
    return _svg(body, "0 0 260 120", "nl-card-art")


def _art_graph() -> str:
    body = '''
<g stroke="#7c9bf0" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-dasharray="5 5" class="nl-flow">
<path d="M130 24L72 56M130 24L190 54M72 56L50 96M72 56L112 92M190 54L168 94M190 54L226 88M112 92L168 94"/></g>
<circle cx="130" cy="24" r="12" fill="#4d95ff" class="nl-bob"/>
<circle cx="72" cy="56" r="11" fill="#4f29b6" class="nl-bob2"/>
<circle cx="190" cy="54" r="12" fill="#7c5bd6" class="nl-bob"/>
<circle cx="50" cy="96" r="9" fill="#ff7ac0" class="nl-bob2"/>
<circle cx="112" cy="92" r="11" fill="#4d95ff" class="nl-bob2"/>
<circle cx="168" cy="94" r="10" fill="#ff7ac0" class="nl-bob"/>
<circle cx="226" cy="88" r="9" fill="#4f29b6" class="nl-bob"/>
<circle cx="130" cy="24" r="4" fill="#fff"/><circle cx="190" cy="54" r="4" fill="#fff"/>'''
    return _svg(body, "0 0 260 120", "nl-card-art")


def sidebar_mountain() -> str:
    body = '''
<defs><linearGradient id="sm1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8a63e6"/><stop offset="1" stop-color="#4f29b6"/></linearGradient>
<linearGradient id="sm2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#dccdff"/><stop offset="1" stop-color="#9a7ce8"/></linearGradient></defs>
<polygon points="0,110 60,52 100,86 150,40 220,110" fill="url(#sm2)" opacity=".85"/>
<polygon points="70,110 140,18 230,110" fill="url(#sm1)"/>
<polygon points="140,18 122,42 132,40 140,52 150,40 160,44" fill="#fff" opacity=".9"/>
<g class="nl-flag"><path d="M140 18V2" stroke="#3a2395" stroke-width="2.2" stroke-linecap="round"/><path d="M140 2l20 5-20 6z" fill="#ff7ac0"/></g>'''
    return _svg(body, "0 0 230 112", "nl-side-art")


def teacher_badge() -> str:
    """Small person-with-laptop mark for the header credit (original drawing)."""
    body = ('<circle cx="34" cy="20" r="10" fill="none" stroke="currentColor" stroke-width="4"/>'
            '<path d="M14 62v-8a20 20 0 0 1 40 0v8" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>'
            '<path d="M46 56l30-4 8 14-34 6z" fill="currentColor"/>'
            '<path d="M52 60l24-3" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/>')
    return _svg(body, "0 0 96 80", "nl-teacher-badge")
