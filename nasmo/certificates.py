"""Internal training certificates.

These are certificates of the NASMO INFORMATICS LAB training programme only.
They are NOT official certificates of the Nasmo competition, Mawhiba or any
other body, and every certificate says so on its face.

Rules (automatic):
  * Stage certificate : all active missions of the stage are completed and the
                        average mission score is >= the pass score (default 60,
                        teacher can change it in Settings).
  * Lab certificate   : every stage certificate rule holds for all five stages.
"""
from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timezone

from . import auth
from .auth import User, require_self_or_teacher, require_teacher
from .content.stages import STAGES
from .progress import all_missions, summarize, user_rows
from .store import Store, utcnow

LAB_KEY = "lab:complete"


def _pass_score(store: Store) -> int:
    try:
        return max(0, min(100, int(auth.get_setting(store, "cert_pass_score") or 60)))
    except ValueError:
        return 60


def definitions() -> list[dict]:
    defs = []
    for s in STAGES:
        label = s["title"] if s["id"] == "f" else f'{s["title"]} - {s["subtitle"]}'
        defs.append({"key": f"stage:{s['id']}", "stage_id": s["id"],
                     "title": f"{label} - Training Completion"})
    defs.append({"key": LAB_KEY, "stage_id": None,
                 "title": "Nasmo Informatics Lab - Full Training Completion"})
    return defs


def eligibility(store: Store, actor: User, user_id: str) -> list[dict]:
    require_self_or_teacher(actor, user_id)
    missions = all_missions(store)
    rows = user_rows(store, actor, user_id)
    summ = summarize(missions, rows)
    need = _pass_score(store)
    out = []
    stage_ok = {}
    for d in definitions():
        if d["stage_id"]:
            st = summ["stages"][d["stage_id"]]
            ok = st["total"] > 0 and st["completed"] == st["total"] and st["avg_score"] >= need
            stage_ok[d["stage_id"]] = ok
            progress = f'{st["completed"]}/{st["total"]} missions'
            avg = st["avg_score"]
            reason = (f'Completed all {st["total"]} missions with an average score of {avg}%.'
                      if ok else "")
            if st["total"] and st["completed"] == st["total"] and not ok:
                progress += f' - average {avg}% (needs {need}%)'
        else:
            ok = all(stage_ok.get(s["id"]) for s in STAGES)
            progress = f'{summ["completed"]}/{summ["total"]} missions'
            reason = (f'Completed all {summ["total"]} missions in the five stages with an '
                      f'average score of {summ["avg_score"]}%.' if ok else "")
        out.append({**d, "eligible": bool(ok), "progress": progress, "reason": reason})
    return out


def list_certificates(store: Store, actor: User, user_id: str) -> list[dict]:
    require_self_or_teacher(actor, user_id)
    return store.select("certificates", {"user_id": user_id}, order=[("issued_at", "asc")])


def sync_certificates(store: Store, actor: User, user_id: str) -> list[dict]:
    """Issue every certificate the student has newly earned. Returns the new ones."""
    require_self_or_teacher(actor, user_id)
    have = {c["cert_key"] for c in store.select("certificates", {"user_id": user_id})}
    new = []
    year = datetime.now(timezone.utc).year
    for e in eligibility(store, actor, user_id):
        if e["eligible"] and e["key"] not in have:
            row = {"id": str(uuid.uuid4()), "user_id": user_id, "cert_key": e["key"],
                   "title": e["title"], "reason": e["reason"],
                   "serial": f"NIL-{year}-{secrets.token_hex(4).upper()}",
                   "issued_at": utcnow(), "revoked": False}
            store.insert("certificates", row)
            new.append(row)
    return new


def set_revoked(store: Store, actor: User, cert_id: str, revoked: bool) -> None:
    require_teacher(actor)
    store.update("certificates", {"id": cert_id}, {"revoked": bool(revoked)})
