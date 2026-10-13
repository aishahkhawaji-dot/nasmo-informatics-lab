"""Discussion board: students ask and answer each other, the teacher moderates.

Rules (all enforced here, not in the page):
* any signed-in user can read, ask, answer and say thanks; names are the display names.
* a question has a title and text; replies hang under it. One table (forum_posts): parent_id is
  None for a question and the question id for a reply.
* the question's author (or the teacher) can mark ONE reply as the accepted answer.
* a teacher can pin, close/reopen and delete anything. A student can delete only her own reply, or
  her own question while nobody else has answered it.
* a closed question accepts no new replies from students.
* anti-spam: at most RATE_MAX posts per RATE_WINDOW minutes per student.
* text is stored as typed; the page escapes it when drawing (see render_text)."""
from __future__ import annotations

import html
import re
import uuid
from datetime import datetime, timedelta, timezone

from .auth import AuthError, PermissionDenied, User, require_teacher
from .store import Store, parse_ts, utcnow

TITLE_MAX = 120
TITLE_MIN = 5
BODY_MAX = 1500
BODY_MIN = 3
RATE_MAX = 6
RATE_WINDOW = 10          # minutes


def _need_user(actor: User | None) -> User:
    if actor is None or not actor.active:
        raise PermissionDenied("Please sign in.")
    return actor


def _clean(text: str, lo: int, hi: int, what: str) -> str:
    text = (text or "").replace("\r\n", "\n").strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "".join(c for c in text if c == "\n" or c == "\t" or ord(c) >= 32)
    if len(text) < lo:
        raise AuthError(f"Please write the {what}.")
    if len(text) > hi:
        raise AuthError(f"The {what} is too long (maximum {hi} characters).")
    return text


def _throttle(store: Store, actor: User) -> None:
    if actor.is_teacher:
        return
    limit = datetime.now(timezone.utc) - timedelta(minutes=RATE_WINDOW)
    recent = [p for p in store.select("forum_posts", {"user_id": actor.id})
              if (parse_ts(p.get("created_at")) or limit) > limit]
    if len(recent) >= RATE_MAX:
        raise AuthError(f"You are posting very fast. Please wait a few minutes (maximum {RATE_MAX} posts in {RATE_WINDOW} minutes).")


def _new(store: Store, actor: User, parent_id, title, body) -> dict:
    return store.insert("forum_posts", {
        "id": str(uuid.uuid4()), "user_id": actor.id, "parent_id": parent_id, "title": title, "body": body,
        "pinned": False, "closed": False, "accepted": False, "created_at": utcnow()})


def ask(store: Store, actor: User, title: str, body: str) -> dict:
    _need_user(actor)
    title = _clean(title, TITLE_MIN, TITLE_MAX, "question title")
    if "\n" in title:
        title = " ".join(title.split())
    body = _clean(body, BODY_MIN, BODY_MAX, "question details")
    _throttle(store, actor)
    return _new(store, actor, None, title, body)


def reply(store: Store, actor: User, question_id: str, body: str) -> dict:
    _need_user(actor)
    q = store.get("forum_posts", {"id": question_id})
    if not q or q.get("parent_id"):
        raise AuthError("This question no longer exists.")
    if q.get("closed") and not actor.is_teacher:
        raise AuthError("This discussion is closed.")
    body = _clean(body, BODY_MIN, BODY_MAX, "reply")
    _throttle(store, actor)
    return _new(store, actor, question_id, "", body)


def _names(store: Store, ids: set[str]) -> dict[str, dict]:
    out = {}
    for u in store.select("users"):
        if u["id"] in ids:
            out[u["id"]] = {"name": u["display_name"], "teacher": u["role"] == "teacher"}
    return out


def list_questions(store: Store, actor: User, search: str = "") -> list[dict]:
    """Pinned first, then by latest activity. Each item has the counts the list needs."""
    _need_user(actor)
    posts = store.select("forum_posts")
    qs = [p for p in posts if not p.get("parent_id")]
    reps: dict[str, list[dict]] = {}
    for p in posts:
        if p.get("parent_id"):
            reps.setdefault(p["parent_id"], []).append(p)
    who = _names(store, {p["user_id"] for p in qs})
    term = (search or "").strip().lower()
    out = []
    for q in qs:
        rs = reps.get(q["id"], [])
        if term and term not in (q["title"] + " " + q["body"]).lower():
            continue
        last = max([q["created_at"]] + [r["created_at"] for r in rs])
        out.append({**q, "author": who.get(q["user_id"], {}).get("name", "—"),
                    "author_teacher": who.get(q["user_id"], {}).get("teacher", False),
                    "replies": len(rs), "answered": any(r.get("accepted") for r in rs),
                    "last_activity": last})
    out.sort(key=lambda x: (not x["pinned"], _neg(x["last_activity"])))
    return out


def _neg(ts: str):
    d = parse_ts(ts)
    return -(d.timestamp() if d else 0)


def get_thread(store: Store, actor: User, question_id: str) -> dict | None:
    _need_user(actor)
    q = store.get("forum_posts", {"id": question_id})
    if not q or q.get("parent_id"):
        return None
    rs = store.select("forum_posts", {"parent_id": question_id}, order=[("created_at", "asc")])
    ids = [q["id"]] + [r["id"] for r in rs]
    thanks = [t for t in store.select("forum_thanks") if t["post_id"] in ids]
    who = _names(store, {q["user_id"]} | {r["user_id"] for r in rs})

    def dress(p):
        mine = [t for t in thanks if t["post_id"] == p["id"]]
        w = who.get(p["user_id"], {})
        return {**p, "author": w.get("name", "—"), "author_teacher": w.get("teacher", False),
                "thanks": len(mine), "thanked_by_me": any(t["user_id"] == actor.id for t in mine),
                "mine": p["user_id"] == actor.id}
    rep = [dress(r) for r in rs]
    rep.sort(key=lambda r: (not r["accepted"], r["created_at"]))
    return {"question": dress(q), "replies": rep}


def thank(store: Store, actor: User, post_id: str) -> bool:
    """Toggle 'this helped me'. Returns True when it is now on."""
    _need_user(actor)
    p = store.get("forum_posts", {"id": post_id})
    if not p:
        raise AuthError("This post no longer exists.")
    if p["user_id"] == actor.id:
        raise AuthError("You cannot thank your own post.")
    where = {"post_id": post_id, "user_id": actor.id}
    if store.get("forum_thanks", where):
        store.delete("forum_thanks", where)
        return False
    store.upsert("forum_thanks", {**where, "created_at": utcnow()})
    return True


def accept(store: Store, actor: User, reply_id: str) -> bool:
    """The question's author (or the teacher) marks one reply as the accepted answer (toggle)."""
    _need_user(actor)
    r = store.get("forum_posts", {"id": reply_id})
    if not r or not r.get("parent_id"):
        raise AuthError("This reply no longer exists.")
    q = store.get("forum_posts", {"id": r["parent_id"]})
    if not q or not (actor.is_teacher or q["user_id"] == actor.id):
        raise PermissionDenied("Only the person who asked (or the teacher) can accept an answer.")
    was = bool(r.get("accepted"))
    store.update("forum_posts", {"parent_id": q["id"]}, {"accepted": False})
    if not was:
        store.update("forum_posts", {"id": reply_id}, {"accepted": True})
    return not was


def set_flag(store: Store, actor: User, question_id: str, flag: str, value: bool) -> None:
    require_teacher(actor)
    if flag not in ("pinned", "closed"):
        raise AuthError("Unknown option.")
    q = store.get("forum_posts", {"id": question_id})
    if not q or q.get("parent_id"):
        raise AuthError("This question no longer exists.")
    store.update("forum_posts", {"id": question_id}, {flag: bool(value)})


def delete_post(store: Store, actor: User, post_id: str) -> None:
    _need_user(actor)
    p = store.get("forum_posts", {"id": post_id})
    if not p:
        return
    if not actor.is_teacher:
        if p["user_id"] != actor.id:
            raise PermissionDenied("You can delete only your own posts.")
        if not p.get("parent_id") and store.select("forum_posts", {"parent_id": post_id}):
            raise AuthError("Others already answered this question, so only the teacher can delete it.")
    ids = [post_id]
    if not p.get("parent_id"):
        ids += [r["id"] for r in store.select("forum_posts", {"parent_id": post_id})]
    for i in ids:
        store.delete("forum_thanks", {"post_id": i})
        store.delete("forum_posts", {"id": i})


# ------------------------------------------------------------ teacher "new questions" counter
def _seen_key(actor: User) -> str:
    return "forumseen:" + actor.id


def new_questions(store: Store, actor: User) -> int:
    """Questions and replies by students since the teacher last opened the board."""
    require_teacher(actor)
    row = store.get("settings", {"key": _seen_key(actor)})
    since = parse_ts(row["value"]) if row else None
    students = {u["id"] for u in store.select("users", {"role": "student"})}
    n = 0
    for p in store.select("forum_posts"):
        if p["user_id"] not in students:
            continue
        t = parse_ts(p["created_at"])
        if since is None or (t and t > since):
            n += 1
    return n


def mark_seen(store: Store, actor: User) -> None:
    require_teacher(actor)
    store.upsert("settings", {"key": _seen_key(actor), "value": utcnow()})


# ---------------------------------------------------------------------------- drawing
_FENCE = re.compile(r"```(?:[a-zA-Z+#]*)\n?(.*?)```", re.S)


def render_text(text: str) -> str:
    """Escape everything, then turn ```code``` into a code block and newlines into <br>.
    The result is safe to put inside HTML (only <pre><code> and <br> are ever produced)."""
    text = text or ""
    parts, pos = [], 0
    for m in _FENCE.finditer(text):
        parts.append(_para(text[pos:m.start()]))
        parts.append('<pre class="fm-code" dir="ltr"><code>' + html.escape(m.group(1).strip("\n")) + "</code></pre>")
        pos = m.end()
    parts.append(_para(text[pos:]))
    return "".join(parts)


def _para(chunk: str) -> str:
    chunk = chunk.strip("\n")
    return html.escape(chunk).replace("\n", "<br>") if chunk else ""
