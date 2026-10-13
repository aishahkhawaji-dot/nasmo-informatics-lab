"""Discussion board page (students and teachers)."""
from __future__ import annotations

from ..ui.sx import st
from .. import auth, forum
from ..i18n import tr
from ..store import StoreError
from ..ui import components as C
from ..ui import layout as L
from ..ui import session as S

esc = C.esc


def _when(ts) -> str:
    return str(ts or "")[:16].replace("T", " ") or "—"


def _say(kind: str, text: str) -> None:
    st.session_state["fm_msg"] = (kind, text)


def _do(fn, *args, ok: str = "") -> bool:
    """Run a forum action from a button; show errors as a message instead of crashing."""
    try:
        fn(*args)
    except (auth.AuthError, auth.PermissionDenied, StoreError) as e:
        _say("bad", str(e))
        return False
    if ok:
        _say("ok", ok)
    return True


def _show_msg() -> None:
    m = st.session_state.pop("fm_msg", None)
    if m:
        L.note(m[0], m[1])


def _badge(text: str, cls: str = "") -> str:
    return f'<span class="fm-badge {cls}">{esc(tr(text))}</span>'


def _who(p: dict) -> str:
    t = f' <span class="fm-badge teach">{esc(tr("Teacher"))}</span>' if p.get("author_teacher") else ""
    return f"<b dir=auto>{esc(p['author'])}</b>{t}"


def _open(qid: str) -> None:
    S.go("forum", thread=qid)


def _back() -> None:
    S.go("forum")


# ------------------------------------------------------------------ list
def _list(store, user) -> None:
    _show_msg()
    if user.is_teacher:
        n = forum.new_questions(store, user)
        if n:
            L.note("warn", f"{n} new post(s) from students since your last visit.")
        forum.mark_seen(store, user)
    with st.expander("✍ Ask a question", expanded=False):
        with st.form("fm_ask", clear_on_submit=True):
            title = st.text_input("Question title", max_chars=forum.TITLE_MAX, placeholder="e.g. Why does my loop run forever?",
                                  key="fm_title")
            body = st.text_area("Details (you can paste code between ``` lines)", height=140, max_chars=forum.BODY_MAX, key="fm_body")
            go = st.form_submit_button("Post question", type="primary")
        if go:
            try:
                q = forum.ask(store, user, title, body)
            except (auth.AuthError, auth.PermissionDenied, StoreError) as e:
                L.note("bad", str(e))
            else:
                _say("ok", "Your question was posted.")
                S.go("forum", thread=q["id"])
                st.rerun()
    term = st.text_input("Search the board", key="fm_search", placeholder="Search by a word in the title or details")
    qs = forum.list_questions(store, user, term)
    if not qs:
        L.note("", "No questions yet. Be the first to ask." if not term else "Nothing matches your search.")
        return
    for q in qs:
        badges = ""
        if q["pinned"]:
            badges += _badge("📌 Pinned", "pin")
        if q["answered"]:
            badges += _badge("✓ Answered", "ok")
        if q["closed"]:
            badges += _badge("🔒 Closed", "shut")
        meta = f"{_who(q)} · {esc(_when(q['created_at']))} · {q['replies']} {esc(tr('replies'))}"
        with st.container(key=f"fmq_{q['id']}"):
            st.markdown(f'<div class="nl-root" data-notr="1"><div class="fm-card{" pinned" if q["pinned"] else ""}">'
                        f'<div class="fm-badges">{badges}</div><h3 class="fm-title" dir="auto">{esc(q["title"])}</h3>'
                        f'<div class="fm-meta">{meta}</div></div></div>', unsafe_allow_html=True)
            st.button("Open discussion", key=f"fm_open_{q['id']}", on_click=_open, args=(q["id"],))


# ---------------------------------------------------------------- thread
def _post_html(p: dict, is_question: bool) -> str:
    cls = "fm-post q" if is_question else "fm-post" + (" best" if p.get("accepted") else "")
    flag = _badge("✓ Accepted answer", "ok") if p.get("accepted") else ""
    head = f'<h2 class="fm-qtitle" dir="auto">{esc(p["title"])}</h2>' if is_question else ""
    thanks = f'<span class="fm-thanks">👍 {p["thanks"]}</span>' if p["thanks"] else ""
    return (f'<div class="nl-root" data-notr="1"><div class="{cls}">{flag}{head}'
            f'<div class="fm-body" dir="auto">{forum.render_text(p["body"])}</div>'
            f'<div class="fm-meta">{_who(p)} · {esc(_when(p["created_at"]))} {thanks}</div></div></div>')


def _thread(store, user, qid: str) -> None:
    th = forum.get_thread(store, user, qid)
    if th is None:
        L.note("bad", "This question no longer exists.")
        st.button("← Back to the board", key="fm_back0", on_click=_back)
        return
    q, reps = th["question"], th["replies"]
    st.button("← Back to the board", key="fm_back", on_click=_back)
    _show_msg()
    b = ""
    if q["pinned"]:
        b += _badge("📌 Pinned", "pin")
    if q["closed"]:
        b += _badge("🔒 Closed", "shut")
    if b:
        st.markdown(f'<div class="nl-root" data-notr="1"><div class="fm-badges">{b}</div></div>', unsafe_allow_html=True)
    st.markdown(_post_html(q, True), unsafe_allow_html=True)

    def actions(p: dict, is_q: bool) -> None:
        cols = st.columns(4)
        i = 0
        if not p["mine"]:
            cols[i].button("👍 Helped me" if not p["thanked_by_me"] else "👍 Thanks sent", key=f"fm_thx_{p['id']}",
                           on_click=_do, args=(forum.thank, store, user, p["id"]))
            i += 1
        if not is_q and (user.is_teacher or q["mine"]):
            cols[i].button("✓ Accept answer" if not p["accepted"] else "Remove accepted mark", key=f"fm_acc_{p['id']}",
                           on_click=_do, args=(forum.accept, store, user, p["id"]))
            i += 1
        if user.is_teacher or p["mine"]:
            cols[i].button("🗑 Delete", key=f"fm_del_{p['id']}", on_click=_delete, args=(store, user, p["id"], is_q))

    actions(q, True)
    if user.is_teacher:
        c1, c2, _ = st.columns(3)
        c1.button("Unpin" if q["pinned"] else "📌 Pin", key="fm_pin",
                  on_click=_do, args=(forum.set_flag, store, user, qid, "pinned", not q["pinned"]))
        c2.button("Reopen discussion" if q["closed"] else "🔒 Close discussion", key="fm_close",
                  on_click=_do, args=(forum.set_flag, store, user, qid, "closed", not q["closed"]))
    st.markdown(f'<div class="nl-root"><h2 class="nl-h2">{esc(tr("Answers"))} · {len(reps)}</h2></div>', unsafe_allow_html=True)
    if not reps:
        L.note("", "No answers yet. Can you help?")
    for r in reps:
        with st.container(key=f"fmr_{r['id']}"):
            st.markdown(_post_html(r, False), unsafe_allow_html=True)
            actions(r, False)
    if q["closed"] and not user.is_teacher:
        L.note("", "This discussion is closed.")
        return
    with st.form("fm_reply", clear_on_submit=True):
        body = st.text_area("Your answer (you can paste code between ``` lines)", height=130, max_chars=forum.BODY_MAX, key="fm_reply_body")
        go = st.form_submit_button("Post answer", type="primary")
    if go:
        try:
            forum.reply(store, user, qid, body)
        except (auth.AuthError, auth.PermissionDenied, StoreError) as e:
            L.note("bad", str(e))
        else:
            _say("ok", "Your answer was posted.")
            st.rerun()


def _delete(store, user, post_id: str, is_question: bool) -> None:
    if _do(forum.delete_post, store, user, post_id, ok="Deleted."):
        if is_question:
            S.go("forum")


def page(store) -> None:
    user = S.current_user()
    L.header()
    with st.container(key="pagepad"):
        L.page_title("Discussion Board", "Ask your classmates, help each other, and learn together. Be kind and keep it about the lab.")
        try:
            qid = st.session_state.get("params", {}).get("thread")
            if qid:
                _thread(store, user, qid)
            else:
                _list(store, user)
        except (StoreError, auth.AuthError, auth.PermissionDenied) as e:
            L.note("bad", str(e))
        L.footer()
