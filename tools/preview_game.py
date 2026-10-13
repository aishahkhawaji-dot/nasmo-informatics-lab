"""Static preview of the game components (no Streamlit) for visual checks.
Usage: python tools/preview_game.py out.html [dark|light]"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from nasmo import game as G
from nasmo.content.missions import MISSIONS
from nasmo.content.stages import STAGES
from nasmo.ui import game_ui as GU, style, components as C

def row(m, wrong=0):
    return {"status": "completed", "step_results": {s["id"]: {"passed": True, "wrong": wrong, "attempts": 1, "score": 100} for s in m["steps"]}, "score": 100}

def page(theme="dark"):
    rows = {m["id"]: row(m, i % 3) for i, m in enumerate(MISSIONS[:7])}
    st = G.compute(MISSIONS, rows, ["2026-10-09", "2026-10-08"])
    worlds = "".join(f'<div>{GU.world_card_html(s, i, 4, min(4, max(0, 7 - i * 4)), 0 if i > 1 else 8, i == 1)}</div>' for i, s in enumerate(STAGES))
    quests = "".join(GU.quest_node_html(i, MISSIONS[i], "completed" if i < 2 else "new", 3 - i if i < 2 else 0, i == 2, G.loot_for(MISSIONS[i], i)) + '<div style="height:10px"></div>' for i in range(4))
    gain = {"xp": 190, "trophies": [t for t in st["trophies"] if t["unlocked"]][:2], "level_up": True, "worlds": ["f"]}
    vict = GU.victory_html(MISSIONS[0], 3, 100, gain, st, st["loot"][0], "")
    trophies = "".join(f'<div>{GU.trophy_card_html(t)}</div>' for t in st["trophies"][:8])
    loot = "".join(f'<div>{GU.loot_card_html(x, "Some mission")}</div>' for x in st["loot"][:10])
    steps = GU.quest_steps_html(MISSIONS[0], {MISSIONS[0]["steps"][0]["id"]: {"passed": True}}, 1)
    win = GU.correct_banner(15, True, 5, 3, "Correct! Clean solve. Step score: 100%.")
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>p</title>{style.build_css_static(theme)}
<style>body{{background:var(--bg);color:var(--text);padding:20px;max-width:1400px;margin:auto;font-family:'Segoe UI',sans-serif}}.g5{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}}.g4{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}h2{{color:var(--ink)}}</style></head><body>
{GU.hud_html(st, "Sara")}{GU.speech("Your next quest is waiting. Ready?", "happy", st["level"])}
<h2>Worlds</h2><div class="g5">{worlds}</div><h2>Quests</h2>{steps}{win}{quests}{GU.world_end_html(False, "Code Camp", "🏕️")}
<h2>Victory</h2>{vict}<h2>Trophies</h2><div class="g4">{trophies}</div><h2>Loot</h2><div class="g5">{loot}</div>{GU.rank_ladder_html(st)}</body></html>"""

if __name__ == "__main__":
    pathlib.Path(sys.argv[1]).write_text(page(sys.argv[2] if len(sys.argv) > 2 else "dark"), encoding="utf-8")
