"""Resource library. Seeded once with the verified official Nasmo booklet
links; the teacher can add, edit, hide or delete resources afterwards."""
from __future__ import annotations

import hashlib
import re
import uuid

from .auth import AuthError, User, require_teacher
from .content.stages import OFFICIAL_OVERVIEW, STAGES
from .store import Store, utcnow

KINDS = ["Official Nasmo topic", "C++ reference", "Video", "Worksheet", "Code example",
         "Practice problems", "Training guide", "Algorithm review", "Other"]
INTERNAL_KIT = "internal:kit"


YOUTUBE_PLAYLIST = "https://www.youtube.com/playlist?list=PLL7r2mW751_A"

_EXTRAS = [  # (flag, id, title, url, description, sort)
    ("resources_extra_playlist_v1", "seed-youtube-playlist", "شرح حقيبة أولمبياد نسمو - تخصص المعلوماتية (قائمة تشغيل)",
     YOUTUBE_PLAYLIST, "Playlist of about 35 explanation videos for the Nasmo Olympiad kit (Informatics). "
                       "Use it as a reference next to the lab missions.", 6),
]


def _ensure_extras(store: Store) -> int:
    """Resources added after the first release. Each one is inserted once (a flag remembers it), so
    a teacher who hides or deletes it never sees it come back."""
    n = 0
    if not store.get("settings", {"key": "resources_retire_channel_v1"}):   # the channel card was removed on request
        store.delete("resources", {"id": "seed-youtube-channel"})
        store.upsert("settings", {"key": "resources_retire_channel_v1", "value": "1"})
    for flag, rid, title, url, desc, sort in _EXTRAS:
        if store.get("settings", {"key": flag}):
            continue
        store.upsert("resources", {
            "id": rid, "stage_id": "all", "kind": "Video", "title": title, "url": url,
            "description": desc, "source": "Teacher-provided", "visible": True, "sort": sort,
            "created_at": utcnow()})
        store.upsert("settings", {"key": flag, "value": "1"})
        n += 1
    return n


def seed_resources(store: Store) -> int:
    """Insert the built-in verified resources the first time only."""
    extra = _ensure_extras(store) if (store.get("settings", {"key": "resources_seeded"}) or store.select("resources", limit=1)) else 0
    flag = store.get("settings", {"key": "resources_seeded"})
    if flag or store.select("resources", limit=1):
        return extra
    n = 0
    now = utcnow()

    def add(rid, stage_id, kind, title, url, desc, source, sort):
        nonlocal n
        store.upsert("resources", {
            "id": rid, "stage_id": stage_id, "kind": kind, "title": title, "url": url,
            "description": desc, "source": source, "visible": True, "sort": sort,
            "created_at": now})
        n += 1

    add("seed-kit", "all", "Training guide", "Interactive Kit - Training Guide",
        INTERNAL_KIT, "The visual training guide of the lab (opens inside the platform).",
        "NASMO INFORMATICS LAB", 0)
    add("seed-overview", "all", "Training guide", "Nasmo booklets - Introduction",
        OFFICIAL_OVERVIEW, "Official introduction to the Nasmo Informatics booklets.",
        "Official - Nasmo booklets", 1)
    sort = 10
    for s in STAGES:
        for title, desc, url in s["topics"]:
            if not url:
                continue
            rid = "seed-" + hashlib.sha1(url.encode()).hexdigest()[:10]
            add(rid, s["id"], "Official Nasmo topic", title, url, desc,
                "Official - Nasmo booklets", sort)
            sort += 1
    store.upsert("settings", {"key": "resources_seeded", "value": "1"})
    return n + _ensure_extras(store)


def list_resources(store: Store, stage_id: str | None = None, kind: str | None = None,
                   query: str = "", include_hidden: bool = False) -> list[dict]:
    where: dict = {}
    if not include_hidden:
        where["visible"] = True
    if kind and kind != "All":
        where["kind"] = kind
    rows = store.select("resources", where, order=[("sort", "asc"), ("title", "asc")])
    if stage_id and stage_id != "all":
        rows = [r for r in rows if r["stage_id"] in (stage_id, "all")]
    q = (query or "").strip().lower()
    if q:
        rows = [r for r in rows if q in (r["title"] or "").lower()
                or q in (r.get("description") or "").lower()]
    return rows


def _validate(title: str, url: str, stage_id: str, kind: str):
    title = (title or "").strip()
    url = (url or "").strip()
    if len(title) < 3 or len(title) > 120:
        raise AuthError("Title must be 3-120 characters.")
    if url != INTERNAL_KIT and not re.match(r"^https?://[^\s]+\.[^\s]+$", url):
        raise AuthError("Please enter a full link starting with http:// or https://")
    if stage_id not in {"all", *[s["id"] for s in STAGES]}:
        raise AuthError("Unknown stage.")
    if kind not in KINDS:
        raise AuthError("Unknown resource type.")
    return title, url


def add_resource(store: Store, actor: User, title, url, stage_id, kind, description="") -> dict:
    require_teacher(actor)
    title, url = _validate(title, url, stage_id, kind)
    row = {"id": str(uuid.uuid4()), "stage_id": stage_id, "kind": kind, "title": title,
           "url": url, "description": (description or "").strip()[:400],
           "source": "Added by teacher", "visible": True, "sort": 500, "created_at": utcnow()}
    store.insert("resources", row)
    return row


def update_resource(store: Store, actor: User, rid: str, title, url, stage_id, kind,
                    description="", visible=True) -> None:
    require_teacher(actor)
    title, url = _validate(title, url, stage_id, kind)
    store.update("resources", {"id": rid}, {
        "title": title, "url": url, "stage_id": stage_id, "kind": kind,
        "description": (description or "").strip()[:400], "visible": bool(visible)})


def delete_resource(store: Store, actor: User, rid: str) -> None:
    require_teacher(actor)
    store.delete("resources", {"id": rid})
