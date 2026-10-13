"""Student pages: mission runner, My Progress, My Certificates, account."""
from __future__ import annotations

import re

from ..ui.sx import st
import streamlit.components.v1 as components

from .. import auth, config
from .. import certificates as certs
from .. import game as G
from ..content.missions import MCQ_TYPES, TYPE_LABELS, TYPE_LABELS_AR
from ..content.stages import STAGE_BY_ID, STAGES
from ..progress import (all_missions, game_state, get_mission, get_progress_row, neighbours,
                        next_mission_id, submit_answer, summarize, user_rows)
from ..store import StoreError
from ..ui import components as C
from ..ui import game_ui as GU
from ..ui import layout as L
from ..ui import session as S
from ..ui.certificate import certificate_html
from . import certgallery


def md_escape(text: str) -> str:
    return re.sub(r"([\\`*_{}\[\]<>#~$|])", r"\\\1", str(text))


def _fmt_time(ts) -> str:
    return str(ts or "")[:16].replace("T", " ") or "—"


# --------------------------------------------------------------- mission
def _step_dots(mission, results, idx) -> str:
    dots = ""
    for i, s in enumerate(mission["steps"]):
        done = bool(results.get(s["id"], {}).get("passed"))
        cls = "done" if done else ("on" if i == idx else "")
        mark = "✓ " if done else ""
        dots += f'<span class="nl-step-dot {cls}">{mark}Step {i + 1}</span>'
    return f'<div class="nl-root"><div class="nl-steps">{dots}</div></div>'


def _explanation(step) -> None:
    st.markdown(C.compact(f'''<div class="nl-root"><div class="nl-explain"><b>Explanation</b><div>{C.esc(step["explain_en"])}</div>
<div class="ar" lang="ar">{C.esc(step["explain_ar"])}</div></div></div>'''), unsafe_allow_html=True)


def _set_idx(key: str, value: int) -> None:
    st.session_state[key] = value


def mission_page(store) -> None:
    user = S.current_user()
    ss = st.session_state
    mid = ss["params"].get("mission")
    L.header()
    with st.container(key="pagepad"):
        mission = get_mission(store, mid, include_inactive=user.is_teacher) if mid else None
        if not mission:
            L.note("warn", "This mission is not available.")
            st.button("← Home", key="mm_home", on_click=S.go, args=("home",))
            return
        stage = STAGE_BY_ID[mission["stage"]]
        L.back_button(stage["title"], "stage", "back_stage", stage=mission["stage"])
        preview = user.is_teacher
        row = None
        if not preview:
            try:
                row = get_progress_row(store, user, user.id, mid)
            except StoreError as e:
                L.note("bad", f"Could not load your progress: {e}")
        results = dict((row or {}).get("step_results") or {})
        steps = mission["steps"]

        # teacher preview keeps its own in-session results
        if preview:
            for s in steps:
                r = ss.get(f"res_{mid}_{s['id']}")
                if r is not None and r.correct:
                    results[s["id"]] = {"passed": True}

        idx_key = f"m_{mid}_i"
        if not preview and f"before_{mid}" not in ss:
            try:      # what the student had BEFORE this mission, to celebrate only what is new
                ss[f"before_{mid}"] = G.snapshot(game_state(store, user, user.id))
            except StoreError:
                ss[f"before_{mid}"] = None
        if idx_key not in ss:
            first = next((i for i, s in enumerate(steps) if not results.get(s["id"], {}).get("passed")), 0)
            ss[idx_key] = first
        idx = ss[idx_key]
        all_passed = all(results.get(s["id"], {}).get("passed") for s in steps)

        L.page_title(mission["title"], mission["summary"],
                     chips=[stage["title"], f"{len(steps)} steps"] + (["Teacher preview - nothing is saved"] if preview else []))

        if idx >= len(steps):
            _finish(store, user, mission, results, all_passed, preview)
            return

        step = steps[idx]
        sid = step["id"]
        st.markdown(GU.quest_steps_html(mission, results, idx), unsafe_allow_html=True)
        st.markdown(C.compact(f'''<div class="nl-root"><span class="nl-qtype">{C.esc(TYPE_LABELS.get(step["type"], step["type"]))}</span>
<span class="nl-qtype nl-ar-s" lang="ar">{C.esc(TYPE_LABELS_AR.get(step["type"], ""))}</span>
<div class="nl-prompt">{C.esc(step["prompt"])}</div></div>'''), unsafe_allow_html=True)
        if step.get("code"):
            st.markdown(C.code_block_html(step["code"]), unsafe_allow_html=True)

        res_key = f"res_{mid}_{sid}"
        res = ss.get(res_key)
        db_passed = bool(results.get(sid, {}).get("passed"))
        solved = db_passed or (res is not None and res.correct and (res.saved or res.preview))

        if solved:
            fx_key = f"fx_{mid}_{sid}"
            if db_passed and res is None:
                L.note("ok", "You already solved this step.")
            elif res is not None and res.saved and not res.already_passed and fx_key not in ss:
                ss[fx_key] = True
                first_try = res.wrong == 0
                gain = G.XP_STEP + (G.XP_STEP_FIRST_TRY if first_try else 0)
                ss["combo"] = int(ss.get("combo", 0)) + 1
                st.markdown(GU.correct_banner(gain, first_try, abs(hash(fx_key)) % 997, ss["combo"],
                                              "Correct! " + G.pick(G.CHEERS, fx_key) + f" Step score: {res.step_score}%."),
                            unsafe_allow_html=True)
                L.play("correct")
            else:
                score = f" Step score: {res.step_score}%." if res is not None and res.saved else ""
                L.note("ok", "Correct!" + score)
            _explanation(step)
            last = idx == len(steps) - 1
            st.button("Finish mission ✓" if last else "Next step →", key=f"next_{mid}_{sid}",
                      type="primary", on_click=_set_idx, args=(idx_key, idx + 1))
            if idx > 0:
                st.button("← Previous step", key=f"prev_{mid}_{sid}", on_click=_set_idx, args=(idx_key, idx - 1))
            return

        # ---- answer inputs
        akey = f"ans_{mid}_{sid}"
        answer, code = None, None
        if step["type"] in MCQ_TYPES:
            opts = step["options"]
            answer = st.radio("Your answer", list(range(len(opts))), index=None,
                              format_func=lambda i: md_escape(opts[i]), key=akey)
        elif step["type"] == "solve":
            answer = st.text_input("Your final answer", key=akey, placeholder=step.get("placeholder") or "")
            code = st.text_area("Your C++ solution (saved for your teacher)", key=akey + "_code", height=220)
        elif step["type"] == "explain":
            answer = st.text_area("Your explanation", key=akey, height=150)
        else:
            answer = st.text_input("Your answer", key=akey, placeholder=step.get("placeholder") or "")

        if step.get("hint"):
            with st.expander("Need a hint?"):
                st.write(step["hint"])

        if st.button("Check answer", key=f"check_{mid}_{sid}", type="primary"):
            try:
                r = submit_answer(store, user, mid, sid, answer, code)
            except (StoreError, auth.PermissionDenied) as e:
                st.error(f"Could not check your answer: {e}")
                return
            ss[res_key] = r
            if r.mission_completed and not preview:
                try:
                    new = certs.sync_certificates(store, user, user.id)
                    if new:
                        ss[f"newcert_{mid}"] = [c["title"] for c in new]
                except StoreError:
                    pass
            st.rerun()

        if res is not None and not res.correct:
            ss["combo"] = 0
            snd_key = f"snd_{mid}_{sid}_{res.attempts}_{res.wrong}"
            if snd_key not in ss:
                ss[snd_key] = True
                L.play("wrong")
            L.note("bad", res.feedback or "Not quite - try again.")
            st.markdown(GU.speech(G.pick(G.RETRIES, f"{sid}{res.attempts}{res.wrong}"), "think"), unsafe_allow_html=True)
            if res.feedback_ar:
                st.markdown(f'<div class="nl-root"><div class="nl-ar-s" lang="ar">{C.esc(res.feedback_ar)}</div></div>',
                            unsafe_allow_html=True)
            if res.reveal:
                _explanation(step)
        elif res is not None and res.correct and not res.saved and not res.preview:
            L.note("warn", "Your answer is correct, but it could not be saved"
                           + (f" ({res.save_error})" if res.save_error else "")
                           + ". Press Check answer again to retry saving.")
        if idx > 0:
            st.button("← Previous step", key=f"prev2_{mid}_{sid}", on_click=_set_idx, args=(idx_key, idx - 1))
        L.footer()


def _finish(store, user, mission, results, all_passed, preview) -> None:
    ss = st.session_state
    mid = mission["id"]
    idx_key = f"m_{mid}_i"
    if not all_passed:
        L.note("warn", "Some steps are not solved yet, so the mission is not complete. Go back and finish them.")
        first = next(i for i, s in enumerate(mission["steps"]) if not results.get(s["id"], {}).get("passed"))
        st.button("Go to the unsolved step", key=f"gofirst_{mid}", on_click=_set_idx, args=(idx_key, first), type="primary")
        return
    if preview:
        L.note("ok", "Preview finished. Nothing was saved because you are signed in as a teacher.")
    else:
        row = get_progress_row(store, user, user.id, mid) or {}
        state = game_state(store, user, user.id)
        stars = G.mission_stars(mission, row)
        before = ss.get(f"before_{mid}")
        after = G.snapshot(state)
        gain = G.new_since(before, after, state) if before else {
            "xp": 0, "stars": 0, "level_up": False, "level": state["level"], "rank": state["rank"],
            "trophies": [], "loot": [], "worlds": []}
        gain["xp"] = G.mission_xp(mission, row)
        loot_item = next((x for x in state["loot"] if x["mission_id"] == mid), None)
        certs_html = "".join(f'<div class="nl-newtro"><span>📜</span><div><b>New certificate: {C.esc(t)}</b>'
                             '<small>Open My Certificates to view it.</small></div></div>'
                             for t in ss.get(f"newcert_{mid}", []))
        st.markdown(GU.victory_html(mission, stars, int(row.get("score", 0)), gain, state, loot_item, certs_html),
                    unsafe_allow_html=True)
        if f"cheered_{mid}" not in ss:
            ss[f"cheered_{mid}"] = True
            if stars == 3 or gain["level_up"] or gain["trophies"]:
                st.balloons()
            L.play("victory", *(["levelup"] if gain["level_up"] else []), *(["trophy"] if gain["trophies"] or gain["worlds"] else []),
                   stars=stars)
    missions = all_missions(store, include_inactive=preview)
    prev_id, next_id = neighbours(missions, mid)
    c1, c2, c3 = st.columns(3)
    with c1:
        if next_id:
            st.button("Next quest ▶", key=f"nm_{mid}", type="primary", on_click=S.go, args=("mission",),
                      kwargs={"mission": next_id})
    with c2:
        st.button("Back to the world", key=f"bs_{mid}", on_click=S.go, args=("stage",), kwargs={"stage": mission["stage"]})
    with c3:
        if not preview:
            st.button("Trophy Room 🏆", key=f"mp_{mid}", on_click=S.go, args=("trophies",))
        else:
            st.button("Review steps", key=f"rv_{mid}", on_click=_set_idx, args=(idx_key, 0))
    L.footer()


# -------------------------------------------------------------- progress
def progress_page(store) -> None:
    user = S.current_user()
    L.header()
    with st.container(key="pagepad"):
        L.page_title("My Progress", f"{user.display_name} · saved to your account")
        try:
            missions = all_missions(store)
            rows = user_rows(store, user, user.id)
            nxt = next_mission_id(store, user, user.id)
            attempts = store.select("attempts", {"user_id": user.id}, order=[("created_at", "desc")], limit=10)
        except StoreError as e:
            L.note("bad", f"Could not load your progress: {e}")
            return
        s = summarize(missions, rows)
        state = game_state(store, user, user.id, missions, rows)
        st.markdown(GU.hud_html(state, user.display_name), unsafe_allow_html=True)
        st.button("Open the Trophy Room 🏆", key="to_trophies", on_click=S.go, args=("trophies",))
        st.markdown(C.kpis_html([
            ("Missions completed", f"{s['completed']}/{s['total']}"),
            ("Missions remaining", str(s["remaining"])),
            ("Average score", f"{s['avg_score']}%" if s["completed"] else "—"),
            ("Last activity", _fmt_time(s["last_activity"])),
        ]), unsafe_allow_html=True)
        st.markdown(C.progress_bar_html(s["percent"], f"{s['percent']}% of the lab"), unsafe_allow_html=True)
        if nxt:
            m = get_mission(store, nxt)
            st.button(f"Continue learning: {m['title']} →", key="continue", type="primary",
                      on_click=S.go, args=("mission",), kwargs={"mission": nxt})
        elif s["total"]:
            L.note("ok", "You completed every mission. Well done!")
        st.markdown('<div class="nl-root"><h2 class="nl-h2">By stage</h2></div>', unsafe_allow_html=True)
        trs = []
        for stg in STAGES:
            v = s["stages"][stg["id"]]
            trs.append([stg["title"] if stg["id"] == "f" else f'{stg["title"]} - {stg["subtitle"]}',
                        f'{v["completed"]}/{v["total"]}', C.progress_bar_html(v["percent"]),
                        f'{v["avg_score"]}%' if v["completed"] else "—"])
        st.markdown(C.table_html(["Stage", "Missions", "Progress", "Average score"], trs, raw_cols={2}),
                    unsafe_allow_html=True)
        st.markdown('<div class="nl-root"><h2 class="nl-h2">Missions</h2></div>', unsafe_allow_html=True)
        trs = []
        for m in missions:
            r = rows.get(m["id"])
            status = {"completed": "Completed", "in_progress": "In progress"}.get((r or {}).get("status"), "Not started")
            tries = sum(int(x.get("attempts", 0)) for x in ((r or {}).get("step_results") or {}).values())
            trs.append([STAGE_BY_ID[m["stage"]]["title"], m["title"], status,
                        f'{r["score"]}%' if r and r["status"] == "completed" else "—", str(tries) if r else "—"])
        st.markdown(C.table_html(["Stage", "Mission", "Status", "Score", "Attempts"], trs), unsafe_allow_html=True)
        if attempts:
            st.markdown('<div class="nl-root"><h2 class="nl-h2">Recent answers</h2></div>', unsafe_allow_html=True)
            st.markdown(C.table_html(["When", "Mission", "Step", "Result"],
                                     [[_fmt_time(a["created_at"]), a["mission_id"], a["step_id"],
                                       "Correct" if a["correct"] else "Not yet"] for a in attempts]),
                        unsafe_allow_html=True)
        L.footer()


# ------------------------------------------------------------ trophy room
def trophies_page(store) -> None:
    user = S.current_user()
    L.header()
    with st.container(key="pagepad"):
        L.page_title("🏆 Trophy Room", "Everything you earn on your adventure lives here.")
        try:
            missions = all_missions(store)
            state = game_state(store, user, user.id, missions)
        except StoreError as e:
            L.note("bad", f"Could not load your trophies: {e}")
            return
        st.markdown(GU.hud_html(state, user.display_name), unsafe_allow_html=True)
        st.markdown('<div class="nl-root"><h2 class="nl-h2">Ranks</h2></div>', unsafe_allow_html=True)
        st.markdown(GU.rank_ladder_html(state), unsafe_allow_html=True)
        st.markdown(f'<div class="nl-root"><h2 class="nl-h2">Trophies · {state["trophies_unlocked"]}/{len(state["trophies"])}</h2></div>',
                    unsafe_allow_html=True)
        with st.container(key="grid4_trophies"):
            cols = st.columns(4)
            for i, t in enumerate(sorted(state["trophies"], key=lambda t: not t["unlocked"])):
                with cols[i % 4]:
                    st.markdown(GU.trophy_card_html(t), unsafe_allow_html=True)
        st.markdown(f'<div class="nl-root"><h2 class="nl-h2">Backpack · {state["loot_collected"]}/{len(state["loot"])}</h2>'
                    '<p class="nl-sub">Every quest you finish drops one item. More stars means a better frame.</p></div>',
                    unsafe_allow_html=True)
        titles = {m["id"]: m["title"] for m in missions}
        with st.container(key="grid5_loot"):
            cols = st.columns(5)
            for i, x in enumerate(state["loot"]):
                with cols[i % 5]:
                    st.markdown(GU.loot_card_html(x, titles.get(x["mission_id"], "")), unsafe_allow_html=True)
        nxt = next_mission_id(store, user, user.id)
        if nxt:
            st.button("Keep adventuring ▶", key="tr_continue", type="primary",
                      on_click=S.go, args=("mission",), kwargs={"mission": nxt})
        L.footer()


# ----------------------------------------------------------- account settings

def account_page(store) -> None:
    user = S.current_user()
    L.header()
    with st.container(key="pagepad"):
        L.page_title("Account Settings", "Manage your display name and password securely.")
        account_panel(store, user)
        L.footer()


# ----------------------------------------------------------- certificates
def certificates_page(store) -> None:
    user = S.current_user()
    L.header()
    with st.container(key="pagepad"):
        L.page_title("My Certificates", "Internal training certificates earned in the lab.")
        L.note("", "These certificates are issued by the lab for training purposes. They are not official certificates "
                   "of Nasmo, Tuwaiq Academy or the Ministry of Education.")
        try:
            certs.sync_certificates(store, user, user.id)
            have = {c["cert_key"]: c for c in certs.list_certificates(store, user, user.id)}
            elig = certs.eligibility(store, user, user.id)
        except StoreError as e:
            L.note("bad", f"Could not load certificates: {e}")
            return
        earned = [e for e in elig if e["key"] in have]
        waiting = [e for e in elig if e["key"] not in have]
        stats = None
        try:
            gs = game_state(store, user, user.id)
            stats = {"rank": gs["rank"], "xp": gs["xp"], "stars": gs["stars"]}
        except StoreError:
            pass
        design = certgallery.selected_design()
        st.markdown('<div class="nl-root"><h2 class="nl-h2">Certificate designs</h2></div>', unsafe_allow_html=True)
        st.caption("Look at the four designs and choose the one you like. Your certificate is issued only after you "
                   "complete every mission of a stage; then it appears below in the design you chose "
                   "(you can change it at any time).")
        certgallery.gallery(user.display_name, selectable=True, stats=stats)
        st.markdown('<div class="nl-root"><h2 class="nl-h2">Your certificates</h2></div>', unsafe_allow_html=True)
        if not earned:
            L.note("", "No certificates yet. Complete all missions of a stage to earn its certificate.")
        for e in earned:
            c = have[e["key"]]
            revoked = bool(c.get("revoked"))
            with st.expander(f"{c['title']} · {c['serial']}" + (" · revoked" if revoked else ""), expanded=not revoked and len(earned) == 1):
                if revoked:
                    L.note("warn", "Your teacher revoked this certificate.")
                    continue
                html = certificate_html(c, user.display_name, design, stats)
                components.html(html, height=640, scrolling=True)
                st.download_button("Download certificate (HTML)", data=html.encode("utf-8"),
                                   file_name=f"certificate-{c['serial']}-{design}.html", mime="text/html",
                                   key=f"dlc_{c['id']}")
                st.caption("To get a PDF: open the downloaded file, press Print and choose Save as PDF.")
        if waiting:
            st.markdown('<div class="nl-root"><h2 class="nl-h2">Still to earn</h2></div>', unsafe_allow_html=True)
            st.markdown(C.table_html(["Certificate", "Your progress"], [[w["title"], w["progress"]] for w in waiting]),
                        unsafe_allow_html=True)
        L.footer()


# ---------------------------------------------------------------- account
def account_panel(store, user) -> None:
    # Show settings immediately on the Account Settings page (no nested expander).
    st.caption(f"Username: {user.username}")
    with st.form(f"name_form_{user.id}"):
        new_name = st.text_input("Display name", value=user.display_name)
        ok = st.form_submit_button("Save name")
    if ok:
        try:
            st.session_state["user"] = auth.update_display_name(store, user, new_name)
            st.success("Name updated.")
        except (auth.AuthError, StoreError) as e:
            st.error(str(e))
    with st.form(f"pw_form_{user.id}"):
        old = st.text_input("Current password", type="password")
        new = st.text_input("New password", type="password")
        if user.is_student:
            st.caption(f"At least {config.STUDENT_MIN_PASSWORD} characters, with English letters and at least one symbol. "
                       f"Allowed symbols: {'  '.join(auth.PASSWORD_SYMBOLS)}")
        new2 = st.text_input("Repeat new password", type="password")
        ok2 = st.form_submit_button("Change password")
    if ok2:
        if new != new2:
            st.error("The two new passwords do not match.")
        else:
            try:
                auth.change_password(store, user, old, new)
                st.success("Password changed.")
            except (auth.AuthError, StoreError) as e:
                st.error(str(e))
