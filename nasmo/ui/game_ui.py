"""HTML builders for the game layer (no Streamlit imports)."""
from __future__ import annotations

import random

from .. import game as G
from .art import stage_art
from .components import compact, esc


# ------------------------------------------------------------- mascot
def mascot(mood: str = "happy", size: int = 120, level: int = 1, cls: str = "") -> str:
    """Nova the robot. mood: happy | cheer | think | sad. Eyes blink, antenna glows."""
    glow = ["#7db4ff", "#6fe0a0", "#f5c542", "#ff9ad0", "#c4b5fd", "#ffb36b", "#7df0ff", "#ffd84d"][min(max(level, 1), 8) - 1]
    mouth = {"happy": '<path d="M52 82 Q64 94 76 82" fill="none" stroke="#2b1a90" stroke-width="4" stroke-linecap="round"/>',
             "cheer": '<path d="M50 80 Q64 100 78 80 Z" fill="#2b1a90"/>',
             "think": '<path d="M54 86 L74 86" stroke="#2b1a90" stroke-width="4" stroke-linecap="round"/>',
             "sad": '<path d="M52 90 Q64 80 76 90" fill="none" stroke="#2b1a90" stroke-width="4" stroke-linecap="round"/>'}[mood]
    arms = ('<g class="nl-wave"><path d="M96 112 L118 86" stroke="#c9bdff" stroke-width="9" stroke-linecap="round"/><circle cx="119" cy="84" r="7" fill="#ffd84d"/></g>'
            if mood == "cheer" else '<path d="M96 116 L112 128" stroke="#c9bdff" stroke-width="9" stroke-linecap="round"/>')
    crown = ('<path d="M44 20 L52 4 L64 16 L76 4 L84 20 Z" fill="#f5c542" stroke="#b8860b" stroke-width="2"/>' if level >= 8 else "")
    return (f'<svg class="nl-nova {cls}" width="{size}" height="{int(size * 1.15)}" viewBox="0 0 130 150" role="img" aria-label="Nova the robot">'
            f'{crown}<line x1="64" y1="26" x2="64" y2="40" stroke="#c9bdff" stroke-width="4"/>'
            f'<circle class="nl-ant" cx="64" cy="22" r="7" fill="{glow}"/>'
            '<rect x="26" y="40" width="76" height="62" rx="26" fill="#efeaff" stroke="#c9bdff" stroke-width="3"/>'
            '<rect x="35" y="50" width="58" height="34" rx="16" fill="#2b1a90"/>'
            '<g class="nl-eyes"><ellipse cx="51" cy="66" rx="7" ry="9" fill="#7df0ff"/><ellipse cx="77" cy="66" rx="7" ry="9" fill="#7df0ff"/></g>'
            f'{mouth}'
            '<rect x="40" y="104" width="48" height="30" rx="12" fill="#c9bdff"/>'
            f'<circle cx="64" cy="119" r="6" fill="{glow}"/>'
            f'<path d="M32 112 L16 128" stroke="#c9bdff" stroke-width="9" stroke-linecap="round"/>{arms}'
            '</svg>')


def speech(text: str, mood: str = "happy", level: int = 1, size: int = 84) -> str:
    return compact(f'''<div class="nl-root"><div class="nl-nova-say">{mascot(mood, size, level, "nl-bob")}
<div class="bubble">{esc(text)}</div></div></div>''')


# ------------------------------------------------------------ HUD
def hud_html(state: dict, name: str) -> str:
    chips = (f'<span class="nl-gchip">⚡ <b>{state["xp"]}</b> XP</span>'
             f'<span class="nl-gchip">⭐ <b>{state["stars"]}</b> stars</span>'
             f'<span class="nl-gchip{" hot" if state["streak"] >= 2 else ""}">🔥 <b>{state["streak"]}</b> day streak</span>'
             f'<span class="nl-gchip">🏆 <b>{state["trophies_unlocked"]}/{len(state["trophies"])}</b> trophies</span>'
             f'<span class="nl-gchip">🎒 <b>{state["loot_collected"]}/{len(state["loot"])}</b> loot</span>')
    nxt = (f'{state["xp_to_next"]} XP to <b>{esc(state["next_rank"])}</b>' if state["next_rank"]
           else "Top rank reached. You are a legend!")
    return compact(f'''<div class="nl-root"><section class="nl-hud">
<div class="av">{mascot("happy", 92, state["level"], "nl-bob")}</div>
<div class="body"><div class="who">{esc(name)}</div>
<div class="rank">{state["rank_icon"]} Level {state["level"]} · {esc(state["rank"])}</div>
<div class="xpbar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="{state["level_pct"]}"><i style="width:{state["level_pct"]}%"></i></div>
<div class="nx">{nxt}</div><div class="chips">{chips}</div></div></section></div>''')


# ---------------------------------------------------------- world map
def stars_row(n: int, total: int = 3, small: bool = False) -> str:
    return ('<span class="nl-stars%s">' % (" sm" if small else "")
            + "".join(f'<i class="{"on" if i < n else ""}">★</i>' for i in range(total)) + "</span>")


def world_card_html(stage: dict, idx: int, total: int, done: int | None, stars: int, current: bool) -> str:
    name, emoji, line = G.WORLDS[stage["id"]]
    pct = 0 if not done or not total else round(100 * done / total)
    meta = f"{total} Missions" if done is None else f"{done}/{total} Missions"
    star_html = "" if done is None else f'<div class="wst">{stars_row(round(stars / max(1, total)))}</div>'
    crown = '<span class="crown" title="World cleared">👑</span>' if (done and total and done == total) else ""
    here = '<span class="here">YOU ARE HERE</span>' if current else ""
    return compact(f'''<div class="nl-root"><article class="nl-world{" cur" if current else ""}" style="--i:{idx}">
<div class="wtop"><span class="wnum">{stage["num"]}</span>{here}{crown}</div>
<div class="wart">{stage_art(stage["id"])}</div>
<div class="wname"><span class="we">{emoji}</span> {esc(name)}</div>
<div class="wsub">{esc(stage["title"])} · {esc(stage["subtitle"])}</div>
<div class="wline">{esc(line)}</div>
<div class="wfoot"><div class="ring" style="--p:{pct}"><b>{pct}%</b></div><div class="wmeta"><b>{esc(meta)}</b>{star_html}</div></div>
</article></div>''')


# ------------------------------------------------------- quest path
def quest_node_html(i: int, mission: dict, status: str, stars: int, current: bool, loot: tuple[str, str]) -> str:
    state = "done" if status == "completed" else ("cur" if current else "open")
    face = "✓" if state == "done" else ("▶" if state == "cur" else str(i + 1))
    sub = (stars_row(stars, small=True) if state == "done"
           else ('<span class="nl-tag cur">Next quest</span>' if state == "cur"
                 else ('<span class="nl-tag warn">In progress</span>' if status == "in_progress" else "")))
    reward = f'<span class="rw" title="Reward">{loot[1]} {esc(loot[0])}</span>'
    return compact(f'''<div class="nl-root"><div class="nl-quest {state}">
<div class="node">{face}</div>
<div class="qb"><div class="qh"><span class="qn">QUEST {i + 1}</span>{sub}</div>
<h4>{esc(mission["title"])}</h4><p>{esc(mission["summary"])}</p>
<div class="qf">{reward}<span class="steps">{len(mission["steps"])} steps</span></div></div>
</div></div>''')


def world_end_html(cleared: bool, name: str, emoji: str) -> str:
    return compact(f'''<div class="nl-root"><div class="nl-worldend{" on" if cleared else ""}">
<div class="ic">{"👑" if cleared else "🔒"}</div><div><b>{esc(name)} {"cleared!" if cleared else "crown"}</b>
<small>{"You are a conqueror of this world." if cleared else "Finish every quest here to win the crown."}</small></div></div></div>''')


# --------------------------------------------------------- mission HUD
def quest_steps_html(mission: dict, results: dict, idx: int) -> str:
    out = []
    for i, s in enumerate(mission["steps"]):
        done = bool(results.get(s["id"], {}).get("passed"))
        cls = "done" if done else ("on" if i == idx else "")
        out.append(f'<span class="s {cls}">{"✓" if done else i + 1}</span>')
    xp_left = sum(G.XP_STEP for s in mission["steps"] if not results.get(s["id"], {}).get("passed"))
    return compact(f'''<div class="nl-root"><div class="nl-qsteps"><div class="path">{'<em></em>'.join(out)}</div>
<div class="pot">🎁 Finish for +{G.XP_MISSION} XP and up to 3 ★</div></div></div>''')


# -------------------------------------------------------------- effects
def confetti(n: int = 26, seed: int = 7) -> str:
    rnd = random.Random(seed)
    colors = ["#f5c542", "#ff7ac0", "#7db4ff", "#6fe0a0", "#c4b5fd", "#ffb36b"]
    bits = "".join(
        f'<i style="--x:{rnd.randint(-46, 46)}vw;--r:{rnd.randint(-540, 540)}deg;--c:{rnd.choice(colors)};'
        f'--d:{rnd.uniform(0, .5):.2f}s;--s:{rnd.randint(7, 13)}px"></i>' for _ in range(n))
    return f'<div class="nl-confetti" aria-hidden="true">{bits}</div>'


def correct_banner(xp: int, first_try: bool, seed: int, combo: int = 0, text: str = "") -> str:
    extra = ' <span class="ft">First try bonus!</span>' if first_try else ""
    cmb = f'<span class="cmb">🔥 {combo} in a row</span>' if combo >= 2 else ""
    return compact(f'''<div class="nl-root"><div class="nl-win">{confetti(18, seed)}
<div class="xp">+{xp} XP{extra}</div>{cmb}
<div class="say">{mascot("cheer", 70, 1, "nl-bob")}<span>{esc(text or "Correct!")}</span></div></div></div>''')


def chest_html(item: dict | None) -> str:
    emoji = item["emoji"] if item else "🎁"
    name = esc(item["name"]) if item else "Loot"
    return compact(f'''<div class="nl-chest"><div class="loot"><span class="le">{emoji}</span></div>
<svg viewBox="0 0 120 100" width="150" height="125" aria-hidden="true">
<rect x="14" y="44" width="92" height="46" rx="8" fill="#8a4b12" stroke="#4a2608" stroke-width="3"/>
<rect x="14" y="60" width="92" height="8" fill="#f5c542"/><rect x="54" y="56" width="12" height="18" rx="3" fill="#f5c542" stroke="#4a2608" stroke-width="2"/>
<g class="lid"><path d="M14 44 Q14 14 60 14 Q106 14 106 44 Z" fill="#a55f1b" stroke="#4a2608" stroke-width="3"/><rect x="14" y="38" width="92" height="8" fill="#f5c542"/></g>
</svg><b class="ln">{name}</b></div>''')


def victory_html(mission: dict, stars: int, score: int, gain: dict, state: dict, loot_item: dict | None, tag: str) -> str:
    trophies = "".join(f'<div class="nl-newtro"><span>{t["icon"]}</span><div><b>New trophy: {esc(t["title"])}</b><small>{esc(t["desc"])}</small></div></div>'
                       for t in gain["trophies"])
    lvl = (f'<div class="nl-levelup"><span>{state["rank_icon"]}</span><div><b>LEVEL UP! Level {state["level"]}</b>'
           f'<small>You are now a {esc(state["rank"])}.</small></div></div>') if gain["level_up"] else ""
    worlds = "".join(f'<div class="nl-newtro world"><span>{G.WORLDS[w][1]}</span><div><b>{esc(G.WORLDS[w][0])} cleared!</b>'
                     '<small>You earned the world crown.</small></div></div>' for w in gain["worlds"])
    mood = "cheer"
    msg = {3: "Perfect run! Three stars and no slips.", 2: "Great job! Two stars. Can you get all three?",
           1: "Mission complete! Replay it for more stars."}.get(stars, "Mission complete!")
    return compact(f'''<div class="nl-root"><section class="nl-victory">{confetti(40, 11)}
<div class="vt">Mission completed!</div><h2>{esc(mission["title"])}</h2>
<div class="vstars">{"".join(f'<i class="{"on" if i < stars else ""}" style="--k:{i}">★</i>' for i in range(3))}</div>
<div class="vsay">{mascot(mood, 96, state["level"], "nl-bob")}<span>{esc(msg)}</span></div>
<div class="vrows"><div><small>XP earned</small><b>+{gain["xp"]}</b></div><div><small>Stars</small><b>{stars}/3</b></div><div><small>Score</small><b>{score}%</b></div></div>
{chest_html(loot_item)}{lvl}{worlds}{trophies}{tag}</section></div>''')


# --------------------------------------------------------- trophy room
def trophy_card_html(t: dict) -> str:
    pct = round(100 * t["have"] / t["target"]) if t["target"] else 0
    state = "on" if t["unlocked"] else "off"
    prog = "Unlocked" if t["unlocked"] else f'{t["have"]}/{t["target"]}'
    return compact(f'''<div class="nl-root"><div class="nl-trophy {state}"><div class="ti">{t["icon"] if t["unlocked"] else "🔒"}</div>
<b>{esc(t["title"])}</b><small>{esc(t["desc"])}</small>
<div class="tb"><i style="width:{pct}%"></i></div><span class="tp">{prog}</span></div></div>''')


def loot_card_html(x: dict, mission_title: str) -> str:
    if not x["collected"]:
        return compact(f'''<div class="nl-root"><div class="nl-loot off"><div class="li">❔</div><b>???</b><small>Complete: {esc(mission_title)}</small></div></div>''')
    return compact(f'''<div class="nl-root"><div class="nl-loot on {x["tier"].lower()}"><div class="li">{x["emoji"]}</div>
<b>{esc(x["name"])}</b><small>{x["tier"]} · {esc(mission_title)}</small></div></div>''')


def rank_ladder_html(state: dict) -> str:
    rows = []
    for i, (need, title, ic) in enumerate(G.RANKS):
        cls = "on" if state["level"] > i + 1 else ("cur" if state["level"] == i + 1 else "")
        rows.append(f'<div class="rk {cls}"><span class="ri">{ic}</span><b>{esc(title)}</b><small>{need} XP</small></div>')
    return f'<div class="nl-root"><div class="nl-ladder">{"".join(rows)}</div></div>'
