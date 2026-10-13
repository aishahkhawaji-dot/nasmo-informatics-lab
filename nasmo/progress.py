"""Missions catalogue (built-in + teacher-made), answer submission and progress.

Every progress read/write goes through functions that check the actor:
a student can only touch their own rows; a teacher can read anyone's.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from .auth import (PermissionDenied, User, require_self_or_teacher, require_teacher)
from .content.missions import MISSIONS, MISSION_BY_ID, MCQ_TYPES
from .content.stages import STAGES, STAGE_BY_ID
from .grading import GradeResult, grade_step, score_for
from .store import Store, StoreError, utcnow


# ------------------------------------------------------------- catalogue
def _overrides(store: Store) -> dict[str, bool]:
    return {r["mission_id"]: bool(r["active"]) for r in store.select("mission_overrides")}


def all_missions(store: Store, include_inactive: bool = False) -> list[dict]:
    """Built-in missions (in stage order) followed by teacher-made ones.
    Each item gets `active` and `custom` flags."""
    ov = _overrides(store)
    out: list[dict] = []
    for m in MISSIONS:
        active = ov.get(m["id"], True)
        if active or include_inactive:
            out.append({**m, "active": active, "custom": False})
    for row in store.select("custom_missions", order=[("created_at", "asc")]):
        active = bool(row.get("active", True))
        if active or include_inactive:
            out.append({
                "id": row["id"], "stage": row["stage_id"], "title": row["title"],
                "summary": row.get("summary") or "Teacher-made mission.",
                "topics": [], "steps": row.get("steps") or [],
                "active": active, "custom": True})
    order = {s["id"]: i for i, s in enumerate(STAGES)}
    out.sort(key=lambda m: order.get(m["stage"], 99))  # stable: keeps built-in first
    return out


def stage_missions(store: Store, stage_id: str, include_inactive: bool = False) -> list[dict]:
    return [m for m in all_missions(store, include_inactive) if m["stage"] == stage_id]


def get_mission(store: Store, mission_id: str, include_inactive: bool = False) -> dict | None:
    for m in all_missions(store, include_inactive):
        if m["id"] == mission_id:
            return m
    return None


# ------------------------------------------------------------- submission
@dataclass
class SubmitResult:
    correct: bool
    feedback: str = ""
    feedback_ar: str = ""
    saved: bool = False
    save_error: str = ""
    preview: bool = False
    attempts: int = 0
    wrong: int = 0
    step_score: int = 0
    mission_completed: bool = False
    mission_score: int = 0
    reveal: bool = False           # show the full explanation
    needs_code: bool = False
    already_passed: bool = False


def _blank_row(user_id: str, mission: dict) -> dict:
    now = utcnow()
    return {"user_id": user_id, "mission_id": mission["id"], "stage_id": mission["stage"],
            "status": "in_progress", "score": 0, "step_results": {},
            "started_at": now, "completed_at": None, "last_activity": now}


def get_progress_row(store: Store, actor: User, user_id: str, mission_id: str) -> dict | None:
    require_self_or_teacher(actor, user_id)
    return store.get("mission_progress", {"user_id": user_id, "mission_id": mission_id})


def submit_answer(store: Store, actor: User, mission_id: str, step_id: str,
                  answer, code: str | None = None) -> SubmitResult:
    """Grade and (for students) save an answer. Teachers get a preview: the
    answer is graded but nothing is stored."""
    if actor is None or not actor.active:
        raise PermissionDenied("Please sign in.")
    mission = get_mission(store, mission_id)
    if not mission:
        raise StoreError("This mission is not available.")
    step = next((s for s in mission["steps"] if s["id"] == step_id), None)
    if not step:
        raise StoreError("This step does not exist.")

    gr: GradeResult = grade_step(step, answer, code)
    res = SubmitResult(correct=gr.correct, feedback=gr.feedback,
                       feedback_ar=gr.feedback_ar, needs_code=gr.needs_code)

    if actor.is_teacher:                       # preview mode
        res.preview = True
        res.reveal = True
        return res

    # empty / too-short input, or a right answer without code, is not an attempt
    if gr.incomplete or gr.needs_code:
        return res

    try:
        row = store.get("mission_progress", {"user_id": actor.id, "mission_id": mission_id}) \
            or _blank_row(actor.id, mission)
        results = dict(row.get("step_results") or {})
        sr = dict(results.get(step_id) or {"passed": False, "attempts": 0, "wrong": 0, "score": 0})
        res.already_passed = bool(sr.get("passed"))
        sr["attempts"] = int(sr.get("attempts", 0)) + 1
        if gr.correct:
            if not sr.get("passed"):
                sr["passed"] = True
                sr["score"] = score_for(int(sr.get("wrong", 0)))
                sr["passed_at"] = utcnow()
        else:
            if not sr.get("passed"):
                sr["wrong"] = int(sr.get("wrong", 0)) + 1
        stored_answer = str(answer if answer is not None else "")[:2000]
        if step["type"] in MCQ_TYPES and answer not in (None, ""):
            try:
                stored_answer = f"option {int(answer) + 1}: " + str(step["options"][int(answer)])[:200]
            except (ValueError, IndexError):
                pass
        sr["last_answer"] = stored_answer
        if code:
            sr["code"] = code[:6000]
        sr["last_at"] = utcnow()
        results[step_id] = sr

        done = all(results.get(s["id"], {}).get("passed") for s in mission["steps"])
        scores = [results[s["id"]]["score"] for s in mission["steps"]
                  if results.get(s["id"], {}).get("passed")]
        row["step_results"] = results
        row["last_activity"] = utcnow()
        row["stage_id"] = mission["stage"]
        if done:
            if row.get("status") != "completed":
                row["completed_at"] = utcnow()
            row["status"] = "completed"
            row["score"] = round(sum(scores) / len(scores)) if scores else 0
        else:
            row["status"] = "in_progress"
            row["score"] = round(sum(scores) / len(scores)) if scores else 0

        store.upsert("mission_progress", row)
        store.insert("attempts", {
            "id": str(uuid.uuid4()), "user_id": actor.id, "mission_id": mission_id,
            "step_id": step_id, "stage_id": mission["stage"], "answer": stored_answer,
            "correct": gr.correct, "score": sr["score"] if gr.correct else 0,
            "created_at": utcnow()})

        res.saved = True
        res.attempts = sr["attempts"]
        res.wrong = int(sr.get("wrong", 0))
        res.step_score = int(sr.get("score", 0))
        res.mission_completed = bool(done)
        res.mission_score = int(row["score"])
        res.reveal = gr.correct or res.wrong >= 2
    except StoreError as e:
        res.saved = False
        res.save_error = str(e)
        res.reveal = gr.correct
    return res


# --------------------------------------------------------------- progress
def user_rows(store: Store, actor: User, user_id: str) -> dict[str, dict]:
    require_self_or_teacher(actor, user_id)
    return {r["mission_id"]: r for r in store.select("mission_progress", {"user_id": user_id})}


def summarize(missions: list[dict], rows: dict[str, dict]) -> dict:
    """Progress numbers computed from real rows (no placeholders)."""
    stages = {}
    for s in STAGES:
        ms = [m for m in missions if m["stage"] == s["id"]]
        done = [m for m in ms if rows.get(m["id"], {}).get("status") == "completed"]
        scores = [rows[m["id"]]["score"] for m in done]
        stages[s["id"]] = {
            "total": len(ms), "completed": len(done),
            "percent": round(100 * len(done) / len(ms)) if ms else 0,
            "avg_score": round(sum(scores) / len(scores)) if scores else 0,
            "started": sum(1 for m in ms if m["id"] in rows),
        }
    total = sum(v["total"] for v in stages.values())
    completed = sum(v["completed"] for v in stages.values())
    all_scores = [rows[m["id"]]["score"] for m in missions
                  if rows.get(m["id"], {}).get("status") == "completed"]
    last = max((r.get("last_activity") or "" for r in rows.values()), default="") or None
    return {
        "stages": stages, "total": total, "completed": completed,
        "remaining": total - completed,
        "percent": round(100 * completed / total) if total else 0,
        "avg_score": round(sum(all_scores) / len(all_scores)) if all_scores else 0,
        "last_activity": last,
    }


def user_progress(store: Store, actor: User, user_id: str) -> dict:
    missions = all_missions(store)
    rows = user_rows(store, actor, user_id)
    out = summarize(missions, rows)
    out["rows"] = rows
    out["missions"] = missions
    return out


def next_mission_id(store: Store, actor: User, user_id: str) -> str | None:
    """First mission (in lab order) that is not completed - 'Continue learning'."""
    missions = all_missions(store)
    rows = user_rows(store, actor, user_id)
    for m in missions:
        if rows.get(m["id"], {}).get("status") != "completed":
            return m["id"]
    return None


def mission_status(rows: dict[str, dict], mission_id: str) -> str:
    r = rows.get(mission_id)
    if not r:
        return "new"
    return r.get("status", "new")


def neighbours(missions: list[dict], mission_id: str) -> tuple[str | None, str | None]:
    ids = [m["id"] for m in missions]
    if mission_id not in ids:
        return None, None
    i = ids.index(mission_id)
    return (ids[i - 1] if i > 0 else None, ids[i + 1] if i < len(ids) - 1 else None)


# ------------------------------------------------------------------ game
def game_state(store: Store, actor: User, user_id: str, missions: list[dict] | None = None,
               rows: dict[str, dict] | None = None) -> dict:
    """XP / rank / stars / trophies for one student (derived, see game.py)."""
    from . import game
    missions = missions if missions is not None else all_missions(store)
    rows = rows if rows is not None else user_rows(store, actor, user_id)
    dates = [a.get("created_at") or "" for a in store.select("attempts", {"user_id": user_id})]
    return game.compute(missions, rows, dates)
