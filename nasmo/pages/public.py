"""Pages visible before sign-in (and shared pages): home, logins, about,
resources, interactive kit."""
from __future__ import annotations

from ..ui.sx import st

from .. import auth, config
from ..content.stages import OFFICIAL_OVERVIEW, STAGE_BY_ID, STAGES
from .. import game as G
from ..progress import all_missions, game_state, get_mission, next_mission_id, summarize, user_rows
from ..resources import INTERNAL_KIT, KINDS, list_resources
from ..store import StoreError
from ..ui import components as C
from ..ui import game_ui as GU
from ..ui import layout as L
from ..ui import session as S


# ------------------------------------------------------------------- home
def _start_journey(store) -> None:
    user = S.current_user()
    if user is None:
        S.go("student_login")
    else:
        S.go("stages")


def home(store) -> None:
    user = S.current_user()
    L.header()
    with st.container(key="hero"):
        st.markdown(C.hero_html(), unsafe_allow_html=True)
        st.button("Start Your Journey →", key="hero_start", on_click=_start_journey, args=(store,), type="primary")
    with st.container(key="pagepad"):
        if user is None:
            L.note("", "Sign in as a student, then press Start Your Journey to open your stages.")
        L.footer()


def stages_page(store) -> None:
    """The adventure map - shown only after sign-in, when Start Your Journey is pressed."""
    user = S.current_user()
    L.header()
    summary, state = None, None
    with st.container(key="pagepad"):
        if user and user.is_student:
            try:
                missions = all_missions(store)
                rows = user_rows(store, user, user.id)
                summary = summarize(missions, rows)
                state = game_state(store, user, user.id, missions, rows)
                nxt = next_mission_id(store, user, user.id)
            except StoreError as e:
                L.note("bad", f"Could not load your progress: {e}")
                return
            st.markdown(GU.hud_html(state, user.display_name), unsafe_allow_html=True)
            if nxt:
                m = get_mission(store, nxt)
                st.markdown(GU.speech(f"Your next quest is waiting: {m['title']}. Ready?", "happy", state["level"]),
                            unsafe_allow_html=True)
                st.button("Continue your quest ▶", key="stages_continue", type="primary",
                          on_click=S.go, args=("mission",), kwargs={"mission": nxt})
            else:
                st.markdown(GU.speech("You cleared every world. You are a Nasmo Legend!", "cheer", state["level"]),
                            unsafe_allow_html=True)
        else:
            L.page_title("Adventure Map", "Teacher preview: open any world and quest; nothing is saved.")
        st.markdown('<div class="nl-root"><h2 class="nl-h2">Choose your world</h2></div>', unsafe_allow_html=True)
        L.stage_cards(user, summary, store, state)
        L.footer()


# ------------------------------------------------------------------ stage
def stage_page(store) -> None:
    user = S.current_user()
    sid = st.session_state["params"].get("stage", "f")
    stg = STAGE_BY_ID.get(sid)
    if not stg:
        S.go("home"); st.rerun()
    L.header()
    with st.container(key="pagepad"):
        L.back_button("Adventure Map" if user else "Home", "stages" if user else "home", "back_home")
        wname, wemoji, wline = G.WORLDS[sid]
        L.page_title(f"{wemoji} {wname}", f'{stg["title"]} · {stg["subtitle"]} — {stg["desc"]}')
        ms = [m for m in all_missions(store) if m["stage"] == sid]
        if user is None:
            L.note("warn", "Sign in as a student to open the missions and save your progress.")
            st.button("Student Login", key="stage_login", on_click=S.go, args=("student_login",), type="primary")
            return
        rows, state = {}, None
        if user.is_student:
            try:
                rows = user_rows(store, user, user.id)
                state = game_state(store, user, user.id, all_missions(store), rows)
            except StoreError as e:
                L.note("bad", f"Could not load your progress: {e}")
                return
            done = sum(1 for m in ms if rows.get(m["id"], {}).get("status") == "completed")
            stars = sum(state["stars_by"].get(m["id"], 0) for m in ms)
            st.markdown(C.kpis_html([("Quests cleared", f"{done}/{len(ms)}"), ("Stars here", f"{stars}/{3 * len(ms)}"),
                                     ("Your rank", state["rank"])]), unsafe_allow_html=True)
        else:
            L.note("", "Teacher preview: you can open every quest and check answers, but nothing is saved.")
        if not ms:
            L.note("", "No active quests in this world yet.")
        cur = next((m["id"] for m in ms if rows.get(m["id"], {}).get("status") != "completed"), None)
        all_missions_list = all_missions(store)
        index_of = {m["id"]: i for i, m in enumerate(all_missions_list)}
        for i, m in enumerate(ms):
            status = rows.get(m["id"], {}).get("status", "new") if rows else "new"
            stars = state["stars_by"].get(m["id"], 0) if state else 0
            loot = G.loot_for(m, index_of.get(m["id"], i))
            with st.container(key=f"qrow{'odd' if i % 2 else 'even'}_{i}"):
                c1, c2 = st.columns([5, 1.25])
                with c1:
                    st.markdown(GU.quest_node_html(i, m, status, stars, m["id"] == cur and bool(rows or user.is_student), loot),
                                unsafe_allow_html=True)
                with c2:
                    label = "Replay ↺" if status == "completed" else ("Continue ▶" if status == "in_progress" else "Play ▶")
                    st.button(label, key=f"start_mission_{m['id']}", type="primary", use_container_width=True,
                              on_click=S.go, args=("mission",), kwargs={"mission": m["id"]})
        cleared = bool(ms) and bool(state) and all(rows.get(m["id"], {}).get("status") == "completed" for m in ms)
        st.markdown(GU.world_end_html(cleared, wname, wemoji), unsafe_allow_html=True)
        L.footer()


# ------------------------------------------------------------------ login
def _login_form(store, role: str) -> None:
    with st.form(f"login_{role}", clear_on_submit=False):
        u = st.text_input("Username", key=f"{role}_u", autocomplete="off", placeholder="Enter your username")
        p = st.text_input("Password", type="password", key=f"{role}_p", autocomplete="new-password", placeholder="Enter your password")
        ok = st.form_submit_button("Sign in", type="primary")
    if ok:
        try:
            user = auth.login(store, u, p, role)
            S.sign_in(store, user)
            st.rerun()
        except auth.AuthError as e:
            st.error(str(e))
        except StoreError as e:
            st.error(f"Could not reach the database: {e}")


def _forgot_student(store) -> None:
    """She asks her teacher for a new temporary password (the teacher sees the request in Students)."""
    with st.expander("Forgot your password?"):
        st.caption("Write your username and send a request. Your teacher will give you a temporary password.")
        with st.form("forgot_student", clear_on_submit=True):
            u = st.text_input("Your username", key="forgot_u", autocomplete="off", placeholder="Enter your username")
            ok = st.form_submit_button("Send request to my teacher")
        if ok:
            try:
                auth.request_password_reset(store, u)
                st.success("Request sent. When your teacher gives you a temporary password, sign in with it "
                           "and change it from Account Settings.")
            except auth.AuthError as e:
                st.error(str(e))
            except StoreError as e:
                st.error(f"Could not reach the database: {e}")


def _forgot_teacher(store) -> None:
    with st.expander("Forgot your password or username?"):
        try:
            single = auth.only_one_teacher(store)
        except StoreError as e:
            st.error(f"Could not reach the database: {e}")
            return
        if not single:
            st.caption("Ask another teacher to reset your password: Settings, then Teachers, then Reset password.")
            return
        st.caption("There is one teacher account, so you can recover it with the setup code. The code is in the file "
                   "setup_code.txt inside the data folder of this computer, or it is the NASMO_SETUP_CODE value if you set one. "
                   "After recovery the page shows your username.")
        try:
            config.setup_code()                 # makes sure the file exists
        except OSError:
            pass
        with st.form("recover_teacher", clear_on_submit=True):
            code = st.text_input("Setup code", type="password", key="rec_code")
            pw = st.text_input(f"New password (at least {config.TEACHER_MIN_PASSWORD} characters)", type="password",
                               key="rec_pw", autocomplete="new-password", placeholder="Choose a password")
            pw2 = st.text_input("Repeat new password", type="password", key="rec_pw2", placeholder="Repeat your password")
            ok = st.form_submit_button("Recover my account")
        if ok:
            if pw != pw2:
                st.error("The two passwords do not match.")
                return
            try:
                uname = auth.recover_only_teacher(store, code, pw)
                st.success(f"Done. Your username is: {uname}. Sign in with your new password.")
            except auth.AuthError as e:
                st.error(str(e))
            except StoreError as e:
                st.error(f"Could not reach the database: {e}")


def student_login(store) -> None:
    L.header()
    with st.container(key="pagepad"):
        L.page_title("Student Login", "Sign in to continue your training. Your progress is saved to your account.")
        tabs = ["Sign in", "Create account"]
        t1, t2 = st.tabs(tabs)
        with t1:
            _login_form(store, "student")
            _forgot_student(store)
        with t2:
            if auth.get_setting(store, "registration_open") != "1":
                L.note("warn", "Account creation is closed. Ask your teacher to create an account for you.")
            else:
                with st.form("register", clear_on_submit=False):
                    name = st.text_input("Your name (in English)", key="reg_name", placeholder="Example: Sara Ahmed")
                    st.caption("Please write your name in English letters (A-Z), as it will appear on your certificate.")
                    uname = st.text_input("Username", key="reg_user", placeholder="Example: sara_2026", autocomplete="off")
                    st.caption("3-32 characters: English letters, digits, _ . -")
                    pw = st.text_input("Password", type="password", key="reg_pw", placeholder="Choose a password", autocomplete="new-password")
                    st.caption(f"At least {config.STUDENT_MIN_PASSWORD} characters, with English letters and at least one symbol. "
                               f"Allowed symbols: {'  '.join(auth.PASSWORD_SYMBOLS)}")
                    pw2 = st.text_input("Repeat password", type="password", key="reg_pw2", placeholder="Repeat your password")
                    ok = st.form_submit_button("Create account", type="primary")
                if ok:
                    if pw != pw2:
                        st.error("The two passwords do not match.")
                    else:
                        try:
                            user = auth.register_student(store, uname, name, pw)
                            S.sign_in(store, user)
                            st.rerun()
                        except auth.AuthError as e:
                            st.error(str(e))
                        except StoreError as e:
                            st.error(f"Could not reach the database: {e}")
        L.footer()


def teacher_login(store) -> None:
    L.header()
    with st.container(key="pagepad"):
        L.page_title("Teacher Login", "Access the dashboard and manage students.")
        try:
            exists = auth.teacher_exists(store)
        except StoreError as e:
            st.error(f"Could not reach the database: {e}")
            return
        if exists:
            _login_form(store, "teacher")
            _forgot_teacher(store)
        else:
            need_code = config.setup_code_required()
            if need_code:
                try:
                    code_now = config.setup_code()      # creates data/setup_code.txt on first use
                    if not st.session_state.get("_code_printed"):
                        print(f"[Nasmo] Teacher setup code: {code_now}", flush=True)
                        st.session_state["_code_printed"] = True
                except OSError:
                    pass
                L.note("warn", "No teacher account exists yet. Create the first one with the setup code "
                               "(the NASMO_SETUP_CODE setting, or data/setup_code.txt, also printed in the console).")
            else:
                L.note("warn", "First time on this computer: choose a username and password for the teacher account. "
                               "You do this once; afterwards you only sign in.")
            with st.form("first_teacher"):
                code = st.text_input("Setup code", type="password", key="ft_code") if need_code else ""
                uname = st.text_input("Username", key="ft_user", placeholder="Choose a username", autocomplete="off")
                pw = st.text_input(f"Password (at least {config.TEACHER_MIN_PASSWORD} characters)", type="password", key="ft_pw", placeholder="Choose a password", autocomplete="new-password")
                ok = st.form_submit_button("Create teacher account", type="primary")
            if ok:
                try:
                    user = auth.create_first_teacher(store, code, uname, uname, pw)
                    S.sign_in(store, user)
                    st.rerun()
                except auth.AuthError as e:
                    st.error(str(e))
                except StoreError as e:
                    st.error(f"Could not reach the database: {e}")
        L.footer()


# ------------------------------------------------------------------ about
def about(store) -> None:
    L.header()
    with st.container(key="pagepad"):
        st.markdown(f'''<div class="nl-root"><section style="padding:28px;border-radius:24px;background:linear-gradient(135deg,#f2edff,#fff8e8);border:1px solid #e4dafa;margin-bottom:18px;text-align:center">
<div style="font-size:13px;letter-spacing:3px;font-weight:800;color:#6d4bd1">THINK · CODE · COMPETE</div>
<h1 style="color:#302064;font-size:29px;line-height:1.15;margin:5px 0 4px;display:flex;align-items:center;justify-content:center;gap:12px;flex-wrap:wrap"><span style="display:inline-block;animation:nasmoFloat 2.8s ease-in-out infinite">⌘</span><span>Nasmo Live Informatics Lab</span><span style="display:inline-block;animation:nasmoPulse 2s ease-in-out infinite">✦</span></h1>
<style>@keyframes nasmoFloat{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-4px)}}}}@keyframes nasmoPulse{{0%,100%{{opacity:.65;transform:scale(.94)}}50%{{opacity:1;transform:scale(1.08)}}}}</style>
<div style="font-size:23px;font-weight:800;color:#5a35b5">{C.esc(config.APP_NAME_AR)}</div>
<div style="font-size:16px;color:#554c6b;margin-top:8px">{C.esc(config.TAGLINE_AR)}</div></section></div>''', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("### About the Lab")
            st.write("Nasmo Informatics Lab is an interactive training space designed to help students prepare for the Nasmo Informatics 2 competition in the C++ track. The learning journey is organized into Fundamentals and Stages 1–4, with short practical missions.")
        a, b = st.columns(2)
        with a:
            with st.container(border=True):
                st.markdown("### Learn by doing")
                st.write("Students practise reading code, predicting output, debugging, completing code, solving problems, and explaining their reasoning.")
        with b:
            with st.container(border=True):
                st.markdown("### Track your progress")
                st.write("Answers and scores are saved to the student account, allowing students to leave and continue their training later.")
        with st.container(border=True):
            st.markdown("### About the learning materials")
            st.write("Missions and certificates are internal training resources created for this lab. They are not official materials or certificates of the Nasmo competition, Tuwaiq Academy, or the Ministry of Education. Links to the official Nasmo booklet are provided for reference.")
        st.markdown(f'''<div class="nl-root"><div style="padding:22px;border-radius:18px;background:var(--panel);border:1px solid var(--line);text-align:center;margin-top:14px">
<div style="font-size:12px;letter-spacing:1.5px;color:var(--muted);font-weight:700">DESIGN & EDUCATIONAL SUPERVISION</div>
<div style="font-size:24px;font-weight:850;color:var(--primary);margin:8px 0">{C.esc(config.TEACHER_CREDIT_AR)}</div>
<div style="font-size:14px;color:var(--text)">{C.esc(config.SCHOOL_AR)}</div></div></div>''', unsafe_allow_html=True)
        st.markdown(f"[Official Nasmo booklet – introduction]({OFFICIAL_OVERVIEW})")
        L.footer()

# -------------------------------------------------------------- resources
def resources(store) -> None:
    user = S.current_user()
    L.header()
    with st.container(key="pagepad"):
        L.page_title("Resources", "Official Nasmo topics and the materials your teacher added.")
        c1, c2, c3 = st.columns([2, 1, 1])
        q = c1.text_input("Search", key="res_q", placeholder="Search by title or description")
        stage_opts = {"all": "All stages", **{s["id"]: (s["title"] if s["id"] == "f" else f'{s["title"]} - {s["subtitle"]}') for s in STAGES}}
        sid = c2.selectbox("Stage", list(stage_opts), format_func=stage_opts.get, key="res_stage")
        kind_labels = {"Official Nismo Topics": "Official Nasmo topic", "Videos": "Video"}
        kind_label = c3.selectbox("Type", list(kind_labels), key="res_kind")
        kind = kind_labels[kind_label]
        try:
            rows = list_resources(store, sid, kind, q)
        except StoreError as e:
            st.error(f"Could not load resources: {e}")
            return
        if not rows:
            L.note("", "No resources match. Try clearing the filters." if (q or sid != "all" or kind != "All")
                   else "No resources yet.")
        with st.container(key="grid3_resources"):
            cols = st.columns(3)
            for i, r in enumerate(rows):
                stg = STAGE_BY_ID.get(r["stage_id"])
                where = stg["title"] if stg else "All stages"
                internal = r["url"] == INTERNAL_KIT
                link = ("" if internal else f'<em style="font-style:normal;font-size:12.5px;font-weight:600;color:var(--primary)">Open link ↗</em>')
                if internal:
                    continue
                body = C.compact(f'''<div class="nl-root"><div class="nl-mcard">
<div class="row"><span class="nl-chip">{C.esc(r["kind"])}</span><span class="nl-chip">{C.esc(where)}</span></div>
<h4>{C.esc(r["title"])}</h4><p>{C.esc(r.get("description") or "")}</p>{link}</div></div>''')
                with cols[i % 3]:
                    st.markdown(f'<a href="{C.esc(r["url"])}" target="_blank" rel="noopener noreferrer" style="text-decoration:none">{body}</a>',
                                unsafe_allow_html=True)
        L.footer()


# --------------------------------------------------------- interactive guide
def _kit_download(key: str, label: str) -> None:
    """The guide is download-only (the teacher's file, unchanged)."""
    f = config.KIT_FILE
    if not f.exists():
        st.caption(f"The guide file is missing: interactive_kit/{f.name}")
        return
    st.download_button(label, data=f.read_bytes(), file_name=f.name, mime="text/html", key=key)
