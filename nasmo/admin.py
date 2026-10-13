"""Teacher-only operations. Every public function starts with
`require_teacher(actor)` - the database is never reached for anyone else."""
from __future__ import annotations

import csv
import io
import random
import uuid
from datetime import datetime, timedelta, timezone

from . import auth
from .auth import AuthError, User, require_teacher
from .content.missions import MISSIONS, MCQ_TYPES
from .content.stages import STAGES, STAGE_BY_ID
from .progress import all_missions, summarize
from .store import Store, parse_ts, utcnow


# ------------------------------------------------------------- students
def _students(store: Store, include_demo: bool) -> list[dict]:
    rows = store.select("users", {"role": "student"}, order=[("created_at", "asc")])
    return rows if include_demo else [r for r in rows if not r.get("is_demo")]


def _all_progress(store: Store) -> dict[str, dict[str, dict]]:
    by_user: dict[str, dict[str, dict]] = {}
    for r in store.select("mission_progress"):
        by_user.setdefault(r["user_id"], {})[r["mission_id"]] = r
    return by_user


def student_overview(store: Store, actor: User, include_demo: bool = False) -> list[dict]:
    require_teacher(actor)
    missions = all_missions(store)
    progress = _all_progress(store)
    certs: dict[str, int] = {}
    for c in store.select("certificates", {"revoked": False}):
        certs[c["user_id"]] = certs.get(c["user_id"], 0) + 1
    out = []
    for u in _students(store, include_demo):
        rows = progress.get(u["id"], {})
        s = summarize(missions, rows)
        out.append({
            "id": u["id"], "username": u["username"], "display_name": u["display_name"],
            "active": bool(u.get("active", True)), "is_demo": bool(u.get("is_demo")),
            "created_at": u.get("created_at"), "last_login": u.get("last_login"),
            "last_activity": s["last_activity"], "completed": s["completed"],
            "total": s["total"], "percent": s["percent"], "avg_score": s["avg_score"],
            "stages": s["stages"], "certificates": certs.get(u["id"], 0),
        })
    return out


def needs_follow_up(store: Store, actor: User, overview: list[dict]) -> list[dict]:
    """Students with no recent activity, or stuck (>= 3 wrong tries on a step)."""
    require_teacher(actor)
    try:
        days = int(auth.get_setting(store, "inactive_days") or 7)
    except ValueError:
        days = 7
    limit = datetime.now(timezone.utc) - timedelta(days=days)
    progress = _all_progress(store)
    out = []
    for s in overview:
        if not s["active"]:
            continue
        reasons = []
        last = parse_ts(s["last_activity"]) or parse_ts(s["created_at"])
        if s["completed"] < s["total"] and last and last < limit:
            reasons.append(f"no activity for {days}+ days")
        for mid, row in progress.get(s["id"], {}).items():
            if row.get("status") == "completed":
                continue
            for sid, sr in (row.get("step_results") or {}).items():
                if not sr.get("passed") and int(sr.get("wrong", 0)) >= 3:
                    reasons.append(f"stuck on {mid} / step {sid} ({sr['wrong']} wrong tries)")
        if reasons:
            out.append({**s, "reasons": reasons[:3]})
    return out


def dashboard(store: Store, actor: User, include_demo: bool = False) -> dict:
    require_teacher(actor)
    ov = student_overview(store, actor, include_demo)
    ids = {s["id"] for s in ov}
    try:
        days = int(auth.get_setting(store, "inactive_days") or 7)
    except ValueError:
        days = 7
    limit = datetime.now(timezone.utc) - timedelta(days=days)
    active = 0
    for s in ov:
        t = parse_ts(s["last_activity"])
        if t and t >= limit:
            active += 1
    att = [a for a in store.select("attempts", order=[("created_at", "desc")], limit=500)
           if a["user_id"] in ids]
    names = {s["id"]: s["display_name"] for s in ov}
    correct = sum(1 for a in att if a["correct"])
    stage_dist = []
    for st in STAGES:
        vals = [s["stages"][st["id"]] for s in ov]
        stage_dist.append({
            "stage": st, "avg_percent": round(sum(v["percent"] for v in vals) / len(vals)) if vals else 0,
            "students_done": sum(1 for v in vals if v["total"] and v["completed"] == v["total"]),
            "students_started": sum(1 for v in vals if v["started"]),
        })
    scored = [s["avg_score"] for s in ov if s["completed"]]
    return {
        "students": ov, "total_students": len(ov), "active_students": active,
        "missions_completed": sum(s["completed"] for s in ov),
        "avg_progress": round(sum(s["percent"] for s in ov) / len(ov)) if ov else 0,
        "avg_score": round(sum(scored) / len(scored)) if scored else 0,
        "stage_distribution": stage_dist,
        "follow_up": needs_follow_up(store, actor, ov),
        "recent": [{"name": names.get(a["user_id"], "?"), "mission": a["mission_id"],
                    "step": a["step_id"], "correct": bool(a["correct"]),
                    "at": a["created_at"]} for a in att[:10]],
        "attempts_total": len(att),
        "accuracy": round(100 * correct / len(att)) if att else 0,
        "certificates": len([c for c in store.select("certificates", {"revoked": False})
                             if c["user_id"] in ids]),
    }


def student_detail(store: Store, actor: User, student_id: str) -> dict:
    require_teacher(actor)
    u = store.get("users", {"id": student_id, "role": "student"})
    if not u:
        raise AuthError("Student not found.")
    missions = all_missions(store, include_inactive=True)
    rows = {r["mission_id"]: r for r in store.select("mission_progress", {"user_id": student_id})}
    attempts = store.select("attempts", {"user_id": student_id},
                            order=[("created_at", "desc")], limit=100)
    return {"user": {k: u[k] for k in ("id", "username", "display_name", "created_at",
                                       "last_login", "active", "is_demo")},
            "summary": summarize([m for m in missions if m["active"]], rows),
            "missions": missions, "rows": rows, "attempts": attempts,
            "certificates": store.select("certificates", {"user_id": student_id})}


def delete_student(store: Store, actor: User, student_id: str) -> None:
    require_teacher(actor)
    u = store.get("users", {"id": student_id})
    if not u or u["role"] != "student":
        raise AuthError("Student not found.")
    for table in ("mission_progress", "attempts", "certificates", "sessions"):
        store.delete(table, {"user_id": student_id})
    store.delete("users", {"id": student_id})


def export_csv(store: Store, actor: User, include_demo: bool = False) -> bytes:
    """UTF-8 with BOM so Excel on Windows shows Arabic names correctly."""
    require_teacher(actor)
    ov = student_overview(store, actor, include_demo)
    buf = io.StringIO()
    w = csv.writer(buf)
    head = ["username", "name", "registered", "last_activity", "missions_completed",
            "missions_total", "progress_percent", "avg_score", "certificates", "demo"]
    head += [f"{s['title']}_percent" for s in STAGES]
    w.writerow(head)
    for s in ov:
        w.writerow([s["username"], s["display_name"], s["created_at"], s["last_activity"] or "",
                    s["completed"], s["total"], s["percent"], s["avg_score"], s["certificates"],
                    "yes" if s["is_demo"] else "no"] +
                   [s["stages"][st["id"]]["percent"] for st in STAGES])
    return ("﻿" + buf.getvalue()).encode("utf-8")


def export_attempts_csv(store: Store, actor: User, include_demo: bool = False) -> bytes:
    require_teacher(actor)
    users = {u["id"]: u for u in _students(store, include_demo)}
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["time", "username", "name", "mission", "step", "correct", "answer"])
    for a in store.select("attempts", order=[("created_at", "asc")]):
        u = users.get(a["user_id"])
        if u:
            w.writerow([a["created_at"], u["username"], u["display_name"], a["mission_id"],
                        a["step_id"], "yes" if a["correct"] else "no", a.get("answer") or ""])
    return ("﻿" + buf.getvalue()).encode("utf-8")


# --------------------------------------------------------------- missions
def set_mission_active(store: Store, actor: User, mission_id: str, active: bool) -> None:
    require_teacher(actor)
    if any(m["id"] == mission_id for m in MISSIONS):
        store.upsert("mission_overrides", {"mission_id": mission_id, "active": bool(active)})
    elif store.get("custom_missions", {"id": mission_id}):
        store.update("custom_missions", {"id": mission_id}, {"active": bool(active)})
    else:
        raise AuthError("Mission not found.")


def add_custom_mission(store: Store, actor: User, stage_id: str, title: str, summary: str,
                       question: str, options: list[str], correct_index: int,
                       explain_en: str = "", explain_ar: str = "", code: str = "") -> dict:
    """Teacher-made mission with one multiple-choice step."""
    require_teacher(actor)
    if stage_id not in STAGE_BY_ID:
        raise AuthError("Choose a stage.")
    title = (title or "").strip()
    question = (question or "").strip()
    opts = [o.strip() for o in options if o and o.strip()]
    if len(title) < 3 or len(title) > 80:
        raise AuthError("Title must be 3-80 characters.")
    if len(question) < 5:
        raise AuthError("Please write the question.")
    if not (2 <= len(opts) <= 6):
        raise AuthError("Give between 2 and 6 answer options.")
    if not (0 <= int(correct_index) < len(opts)):
        raise AuthError("Choose which option is correct.")
    step = {"id": "a", "type": "choice", "prompt": question, "code": (code or "").strip() or None,
            "options": opts, "answer": int(correct_index), "hint": "",
            "explain_en": (explain_en or "").strip() or "See the correct option highlighted above.",
            "explain_ar": (explain_ar or "").strip() or "راجعي الخيار الصحيح الموضّح.",
            "verify": None}
    row = {"id": "c-" + uuid.uuid4().hex[:10], "stage_id": stage_id, "title": title,
           "summary": (summary or "").strip()[:200], "steps": [step], "active": True,
           "created_at": utcnow()}
    store.insert("custom_missions", row)
    return row


def delete_custom_mission(store: Store, actor: User, mission_id: str) -> None:
    require_teacher(actor)
    if not store.get("custom_missions", {"id": mission_id}):
        raise AuthError("Only teacher-made missions can be deleted.")
    store.delete("custom_missions", {"id": mission_id})
    store.delete("mission_progress", {"mission_id": mission_id})


# ------------------------------------------------------------- demo data
DEMO_PREFIX = "demo_"
DEMO_NAMES = ["Demo Student A", "Demo Student B", "Demo Student C",
              "Demo Student D", "Demo Student E", "Demo Student F"]


def load_demo_data(store: Store, actor: User) -> int:
    """Create clearly-marked demo students with sample progress (no real data).
    They cannot sign in. Returns the number of students created."""
    require_teacher(actor)
    rng = random.Random(2026)
    missions = all_missions(store)
    created = 0
    for i, name in enumerate(DEMO_NAMES, start=1):
        username = f"{DEMO_PREFIX}{i}"
        if store.get("users", {"username": username}):
            continue
        u = auth.create_demo_user(store, actor, username, name)
        created += 1
        reach = [0, 4, 9, 14, 20, 7][i - 1]          # how many missions this student finished
        now = datetime.now(timezone.utc)
        for k, m in enumerate(missions[:reach]):
            when = now - timedelta(days=(0 if i != 6 else 12) + (reach - k) * 0.1)
            results, scores = {}, []
            for st in m["steps"]:
                wrong = rng.choice([0, 0, 1, 2])
                sc = max(40, 100 - 20 * wrong)
                results[st["id"]] = {"passed": True, "attempts": wrong + 1, "wrong": wrong,
                                     "score": sc, "last_answer": "(demo)", "last_at": when.isoformat(timespec="seconds")}
                scores.append(sc)
                for w in range(wrong + 1):
                    store.insert("attempts", {
                        "id": str(uuid.uuid4()), "user_id": u.id, "mission_id": m["id"],
                        "step_id": st["id"], "stage_id": m["stage"], "answer": "(demo)",
                        "correct": w == wrong, "score": sc if w == wrong else 0,
                        "created_at": when.isoformat(timespec="seconds")})
            store.insert("mission_progress", {
                "user_id": u.id, "mission_id": m["id"], "stage_id": m["stage"],
                "status": "completed", "score": round(sum(scores) / len(scores)),
                "step_results": results, "started_at": when.isoformat(timespec="seconds"),
                "completed_at": when.isoformat(timespec="seconds"),
                "last_activity": when.isoformat(timespec="seconds")})
        if i == 2 and len(missions) > reach:        # one student stuck on a step
            m = missions[reach]
            store.insert("mission_progress", {
                "user_id": u.id, "mission_id": m["id"], "stage_id": m["stage"],
                "status": "in_progress", "score": 0,
                "step_results": {m["steps"][0]["id"]: {"passed": False, "attempts": 4, "wrong": 4,
                                                       "score": 0, "last_answer": "(demo)"}},
                "started_at": utcnow(), "completed_at": None, "last_activity": utcnow()})
    return created


def remove_demo_data(store: Store, actor: User) -> int:
    require_teacher(actor)
    demo = store.select("users", {"is_demo": True})
    for u in demo:
        for table in ("mission_progress", "attempts", "certificates", "sessions"):
            store.delete(table, {"user_id": u["id"]})
        store.delete("users", {"id": u["id"]})
    return len(demo)
