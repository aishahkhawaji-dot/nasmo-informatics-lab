"""Game layer: XP, ranks, stars, trophies, loot and streak.

Everything here is DERIVED from rows that are already saved (mission_progress and
attempts), so there is no second source of truth, no schema change, and the
numbers can never drift from the real progress. All functions are pure.
"""
from __future__ import annotations

import hashlib
from datetime import date, datetime, timedelta, timezone

from .content.stages import STAGES

# ----------------------------------------------------------------- tuning
XP_STEP = 10            # every solved step
XP_STEP_FIRST_TRY = 5   # extra when the step was solved with no wrong answer
XP_MISSION = 100        # finishing a mission
XP_PER_STAR = 20        # bonus per star of the mission

# (minimum XP, title, emoji) - level N is the N-th row
RANKS = [
    (0,    "Code Rookie",     "🐣"),
    (200,  "Bit Explorer",    "🧭"),
    (500,  "Loop Ranger",     "🌀"),
    (900,  "Logic Knight",    "🛡️"),
    (1400, "Array Wizard",    "🧙"),
    (1950, "Algorithm Hero",  "🦸"),
    (2600, "Graph Master",    "🕸️"),
    (3300, "Nasmo Champion",  "👑"),
]

WORLDS = {  # stage id -> (world name, emoji, short quest line)
    "f":  ("Code Camp",      "🏕️", "Light the campfire: learn the basics."),
    "s1": ("Logic Forest",   "🌲", "Find your way through patterns and puzzles."),
    "s2": ("Data Caves",     "⛏️", "Dig up sets, maps and fast sorting."),
    "s3": ("Mystic Maze",    "🌀", "Search every path and remember the best."),
    "s4": ("Graph Galaxy",   "🪐", "Connect the stars: graphs and trees."),
}

# one collectible per mission slot (built-in missions are 20; extras cycle)
LOOT = [
    ("Pixel Cape", "🦸"), ("Golden Keyboard", "⌨️"), ("Bug Net", "🥅"), ("Turbo Sneakers", "👟"),
    ("Crystal Compiler", "💎"), ("Rocket Mouse", "🖱️"), ("Magic Semicolon", "✨"), ("Robo Pet", "🤖"),
    ("Lucky Loop", "🍀"), ("Binary Medal", "🎖️"), ("Neon Headset", "🎧"), ("Code Compass", "🧭"),
    ("Star Map", "🗺️"), ("Dragon Debugger", "🐉"), ("Time Crystal", "⏳"), ("Hero Shield", "🛡️"),
    ("Wizard Hat", "🎩"), ("Comet Pen", "🖊️"), ("Galaxy Badge", "🪐"), ("Champion Crown", "👑"),
]

TIER_NAMES = {0: "Bronze", 1: "Silver", 2: "Gold"}


# ------------------------------------------------------------------ rows
def _results(row: dict | None) -> dict:
    return dict((row or {}).get("step_results") or {})


def mission_stars(mission: dict, row: dict | None) -> int:
    """0 until the mission is completed; then 3/2/1 stars by wrong answers."""
    if not row or row.get("status") != "completed":
        return 0
    wrong = sum(int(r.get("wrong", 0)) for r in _results(row).values())
    return 3 if wrong == 0 else 2 if wrong <= 2 else 1


def _first_try_steps(rows: dict[str, dict]) -> int:
    return sum(1 for r in rows.values() for x in _results(r).values()
               if x.get("passed") and int(x.get("wrong", 0)) == 0)


def _solved_steps(rows: dict[str, dict]) -> int:
    return sum(1 for r in rows.values() for x in _results(r).values() if x.get("passed"))


def _comeback(rows: dict[str, dict]) -> bool:
    return any(x.get("passed") and int(x.get("wrong", 0)) >= 2
               for r in rows.values() for x in _results(r).values())


def _coder_steps(rows: dict[str, dict]) -> int:
    return sum(1 for r in rows.values() for x in _results(r).values()
               if x.get("passed") and x.get("code"))


def loot_for(mission: dict, index: int) -> tuple[str, str]:
    if mission.get("custom") or index >= len(LOOT):
        h = int(hashlib.sha1(str(mission["id"]).encode()).hexdigest(), 16)
        return LOOT[h % len(LOOT)]
    return LOOT[index]


# ---------------------------------------------------------------- streak
def streak_days(attempt_dates: list[str], today: date | None = None) -> int:
    """Consecutive days with at least one saved answer, ending today or yesterday."""
    today = today or datetime.now(timezone.utc).date()
    days = set()
    for s in attempt_dates:
        try:
            days.add(date.fromisoformat(str(s)[:10]))
        except ValueError:
            continue
    if not days:
        return 0
    cur = today if today in days else today - timedelta(days=1)
    n = 0
    while cur in days:
        n += 1
        cur -= timedelta(days=1)
    return n


# ------------------------------------------------------------ trophies
def _trophy_defs(missions: list[dict]) -> list[dict]:
    d = [
        dict(id="first_step", title="First Spark", desc="Solve your first step", icon="🪄", key="steps", target=1),
        dict(id="sharp_start", title="Sharp Shooter", desc="Solve 5 steps on the first try", icon="🎯", key="first_try", target=5),
        dict(id="steps_25", title="Step Climber", desc="Solve 25 steps", icon="🧗", key="steps", target=25),
        dict(id="mission_1", title="Mission Maker", desc="Complete your first mission", icon="🚩", key="done", target=1),
        dict(id="mission_3", title="Hat-trick", desc="Complete 3 missions", icon="🎩", key="done", target=3),
        dict(id="mission_5", title="High Five", desc="Complete 5 missions", icon="🖐️", key="done", target=5),
        dict(id="mission_10", title="Code Champion", desc="Complete 10 missions", icon="🏆", key="done", target=10),
        dict(id="perfect_1", title="Perfectionist", desc="Finish a mission with 3 stars", icon="🌟", key="perfect", target=1),
        dict(id="stars_10", title="Star Collector", desc="Collect 10 stars", icon="⭐", key="stars", target=10),
        dict(id="stars_30", title="Galaxy Keeper", desc="Collect 30 stars", icon="🌌", key="stars", target=30),
        dict(id="comeback", title="Never Give Up", desc="Solve a step after two wrong tries", icon="💪", key="comeback", target=1),
        dict(id="coder", title="C++ Coder", desc="Solve a step by writing code", icon="⌨️", key="coder", target=1),
        dict(id="streak_3", title="On Fire", desc="Learn 3 days in a row", icon="🔥", key="streak", target=3),
        dict(id="streak_7", title="Unstoppable", desc="Learn 7 days in a row", icon="🚀", key="streak", target=7),
    ]
    for s in STAGES:
        if any(m["stage"] == s["id"] for m in missions):
            name = WORLDS[s["id"]][0]
            d.append(dict(id=f"world_{s['id']}", title=f"{name} Conqueror", desc=f"Complete every mission in {name}",
                          icon=WORLDS[s["id"]][1], key=f"world_{s['id']}", target=1))
    n = len(missions)
    if n:
        d.append(dict(id="all", title="Nasmo Legend", desc="Complete every mission", icon="👑", key="done_all", target=1))
    return d


# ----------------------------------------------------------------- state
def compute(missions: list[dict], rows: dict[str, dict], attempt_dates: list[str] | None = None,
            today: date | None = None) -> dict:
    """Full game state for one student."""
    stars_by: dict[str, int] = {}
    xp = 0
    for m in missions:
        row = rows.get(m["id"])
        res = _results(row)
        for x in res.values():
            if x.get("passed"):
                xp += XP_STEP + (XP_STEP_FIRST_TRY if int(x.get("wrong", 0)) == 0 else 0)
        stars = mission_stars(m, row)
        stars_by[m["id"]] = stars
        if stars:
            xp += XP_MISSION + XP_PER_STAR * stars
    done = [m for m in missions if stars_by.get(m["id"])]
    stars_total = sum(stars_by.values())
    perfect = sum(1 for v in stars_by.values() if v == 3)
    streak = streak_days(attempt_dates or [], today)

    level = 1
    for i, (need, _, _) in enumerate(RANKS):
        if xp >= need:
            level = i + 1
    rank = RANKS[level - 1]
    nxt = RANKS[level] if level < len(RANKS) else None
    cur_floor = rank[0]
    pct = 100 if nxt is None else min(100, round((xp - cur_floor) / (nxt[0] - cur_floor) * 100))

    worlds_done: dict[str, bool] = {}
    for s in STAGES:
        ms = [m for m in missions if m["stage"] == s["id"]]
        worlds_done[s["id"]] = bool(ms) and all(stars_by.get(m["id"]) for m in ms)

    metrics = {"steps": _solved_steps(rows), "first_try": _first_try_steps(rows), "done": len(done),
               "perfect": perfect, "stars": stars_total, "comeback": 1 if _comeback(rows) else 0,
               "coder": _coder_steps(rows), "streak": streak,
               "done_all": 1 if missions and len(done) == len(missions) else 0}
    for sid, ok in worlds_done.items():
        metrics[f"world_{sid}"] = 1 if ok else 0

    trophies = []
    for t in _trophy_defs(missions):
        have = min(t["target"], int(metrics.get(t["key"], 0)))
        trophies.append({**t, "have": have, "unlocked": have >= t["target"]})

    loot = []
    for i, m in enumerate(missions):
        name, emoji = loot_for(m, i)
        s = stars_by.get(m["id"], 0)
        loot.append({"mission_id": m["id"], "stage": m["stage"], "name": name, "emoji": emoji,
                     "collected": s > 0, "tier": TIER_NAMES.get(max(0, s - 1), "Bronze") if s else ""})

    return {"xp": xp, "level": level, "rank": rank[1], "rank_icon": rank[2],
            "next_rank": nxt[1] if nxt else None, "xp_to_next": (nxt[0] - xp) if nxt else 0,
            "level_pct": pct, "stars": stars_total, "stars_by": stars_by, "streak": streak,
            "missions_done": len(done), "missions_total": len(missions),
            "trophies": trophies, "trophies_unlocked": sum(1 for t in trophies if t["unlocked"]),
            "loot": loot, "loot_collected": sum(1 for x in loot if x["collected"]),
            "worlds_done": worlds_done, "first_try_steps": metrics["first_try"]}


def snapshot(state: dict) -> dict:
    """What can be celebrated later: compare two snapshots with `new_since`."""
    return {"level": state["level"], "rank": state["rank"],
            "trophies": {t["id"] for t in state["trophies"] if t["unlocked"]},
            "loot": {x["mission_id"] for x in state["loot"] if x["collected"]},
            "worlds": {k for k, v in state["worlds_done"].items() if v},
            "xp": state["xp"], "stars": state["stars"]}


def new_since(before: dict, after: dict, state_after: dict) -> dict:
    by_id = {t["id"]: t for t in state_after["trophies"]}
    loot_by = {x["mission_id"]: x for x in state_after["loot"]}
    return {"xp": after["xp"] - before["xp"],
            "stars": after["stars"] - before["stars"],
            "level_up": after["level"] > before["level"],
            "level": after["level"], "rank": after["rank"],
            "trophies": [by_id[i] for i in sorted(after["trophies"] - before["trophies"]) if i in by_id],
            "loot": [loot_by[i] for i in sorted(after["loot"] - before["loot"]) if i in loot_by],
            "worlds": sorted(after["worlds"] - before["worlds"])}


# ------------------------------------------------------------- mascot talk
CHEERS = ["Nice! That is exactly right.", "Boom! Your brain is on fire.", "Clean solve. Keep going!",
          "Yes! You are leveling up.", "Great thinking, coder!", "That one was tricky and you got it."]
RETRIES = ["Almost there. Read it once more.", "No problem, every coder tries again.",
           "Check the hint if you want a nudge.", "Look at the code line by line."]


def pick(lines: list[str], seed: str) -> str:
    h = int(hashlib.sha1(seed.encode()).hexdigest(), 16)
    return lines[h % len(lines)]


def mission_xp(mission: dict, row: dict | None) -> int:
    """XP this one mission is worth for this row (0 until completed)."""
    stars = mission_stars(mission, row)
    if not stars:
        return 0
    xp = XP_MISSION + XP_PER_STAR * stars
    for x in _results(row).values():
        if x.get("passed"):
            xp += XP_STEP + (XP_STEP_FIRST_TRY if int(x.get("wrong", 0)) == 0 else 0)
    return xp
