"""Walks through every page (visitor, teacher, student) in Arabic mode, including error paths,
and returns the English texts that have no Arabic translation (i18n.MISSES)."""
import os
import runpy
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))


def walk(lang="ar"):
    os.environ["NASMO_DATA_DIR"] = tempfile.mkdtemp(prefix="nasmo_ar_")
    os.environ["NASMO_SETUP_CODE"] = "TESTCODE-123"
    os.environ["NASMO_RAISE"] = "1"
    os.environ.pop("SUPABASE_URL", None)
    os.environ.pop("SUPABASE_SERVICE_KEY", None)
    import importlib
    from nasmo import config
    importlib.reload(config)
    import stub_streamlit as T
    st = T.install()
    from nasmo import i18n
    from nasmo.content.missions import MISSION_BY_ID
    from nasmo.content.stages import STAGES
    tr = i18n.tr
    T.full_reset()
    st.session_state["lang"] = lang
    i18n.MISSES.clear()
    errors = []

    def run(page=None, params=None, pressed=(), values=None, user=None):
        ss = st.session_state
        if page is not None:
            ss["page"] = page
            ss["params"] = params or {}
        T.VALUES.update(values or {})
        T.PRESSED.update(pressed)
        for _ in range(6):
            T.reset_run()
            try:
                runpy.run_path(str(ROOT / "app.py"), run_name="__main__")
                break
            except T.RerunException:
                continue
        return "\n".join(T.OUT)

    def setv(**kw):
        T.VALUES.update(kw)

    # ---- visitor
    for p in ("home", "stages", "resources", "about", "student_login", "teacher_login"):
        run(p)
    for s in STAGES:
        run("stage", {"stage": s["id"]})
    run("resources", values={"res_q": "zzzzqq"})
    T.VALUES.clear()
    # student registration errors
    run("student_login")
    for vals in ({"reg_name": "", "reg_user": "", "reg_pw": "", "reg_pw2": ""},
                 {"reg_name": "سارة", "reg_user": "sara1", "reg_pw": "abc@12", "reg_pw2": "abc@12"},
                 {"reg_name": "Sara Ahmed", "reg_user": "s", "reg_pw": "abc@12", "reg_pw2": "abc@12"},
                 {"reg_name": "Sara Ahmed", "reg_user": "sara1", "reg_pw": "abcdef", "reg_pw2": "abcdef"},
                 {"reg_name": "Sara Ahmed", "reg_user": "sara1", "reg_pw": "abc@12", "reg_pw2": "abc@13"},
                 {"reg_name": "Sara Ahmed", "reg_user": "sara1", "reg_pw": "ab@1", "reg_pw2": "ab@1"}):
        run("student_login", values=vals, pressed=[tr("Create account")])
    T.VALUES.clear()
    run("student_login", values={"student_u": "nobody", "student_p": "wrong"}, pressed=[tr("Sign in")])
    run("teacher_login", values={"teacher_u": "nobody", "teacher_p": "wrong"}, pressed=[tr("Sign in")])
    T.VALUES.clear()
    # ---- first teacher
    run("teacher_login")
    for vals in ({"ft_code": "wrong", "ft_user": "teacher1", "ft_pw": "correct-horse-1"},
                 {"ft_code": "TESTCODE-123", "ft_user": "t", "ft_pw": "x"},
                 {"ft_code": "TESTCODE-123", "ft_user": "teacher1", "ft_pw": "abc"}):
        run("teacher_login", values=vals, pressed=[tr("Create teacher account")])
    run(values={"ft_code": "TESTCODE-123", "ft_user": "teacher1", "ft_pw": "correct-horse-1"},
        pressed=[tr("Create teacher account")])
    T.VALUES.clear()
    for _ in range(3):
        for p in ("t_dashboard", "stages", "t_students", "t_reports", "t_impact", "t_content", "t_certs", "t_settings",
                  "resources", "about", "account"):
            run(p)
        if _ == 0:
            run("t_dashboard", pressed=["demo_load"])
            run("t_dashboard", values={"include_demo": True})
            for p in ("t_dashboard", "t_students", "t_reports", "t_impact", "t_content", "t_certs", "t_settings"):
                run(p)
            run("t_dashboard", values={"include_demo": False})
        break
    run("stage", {"stage": "f"})
    run("mission", {"mission": "f-1"})
    # teacher adds student, errors
    for vals in ({"Student name": "", "Username": "", "Temporary password (at least 6 characters)": ""},
                 {"Student name": "Sara", "Username": "sara", "Temporary password (at least 6 characters)": "123"},
                 {"Student name": "Sara", "Username": "sara", "Temporary password (at least 6 characters)": "pass1234"},
                 {"Student name": "Sara", "Username": "sara", "Temporary password (at least 6 characters)": "pass1234"}):
        run("t_students", values={tr(k): v for k, v in vals.items()}, pressed=[tr("Create student")])
    run("t_students")
    T.VALUES.clear()
    from nasmo.ui import session as S
    store, _, _ = S.get_store()
    sid = [u["id"] for u in store.select("users") if u["username"] == "sara"][0]
    run("t_students", values={"stu_pick": sid}, pressed=[f"rp_{sid}"])
    run("t_students", pressed=[f"dis_{sid}"])
    run("t_students", values={"stu_pick": sid})
    run("t_students", pressed=[f"en_{sid}"])
    run("t_students", values={f"del_t_{sid}": "wrong"}, pressed=[f"del_{sid}"])
    T.VALUES.clear()
    run("t_reports")
    run("t_content", pressed=["vis_f-1"])
    run("t_content", pressed=["vis_f-1"])
    run("t_content", values={tr("Mission title"): "", }, pressed=[tr("Add mission")])
    run("t_content", values={tr("Mission title"): "My mission", tr("Question"): "Q?", tr("Option 1"): "a",
                              tr("Option 2"): "b", "Correct option": 1}, pressed=[tr("Add mission")])
    run("t_content", values={tr("Title"): "Bad", tr("Link (https://…)"): "javascript:x"}, pressed=[tr("Add resource")])
    run("t_content", values={tr("Title"): "Good", tr("Link (https://…)"): "https://example.com"}, pressed=[tr("Add resource")])
    run("t_content")
    T.VALUES.clear()
    run("t_settings", values={"Minimum average score for a certificate (%)": 70}, pressed=[tr("Save settings")])
    run("t_settings", values={tr("Name"): "T2", tr("Username"): "t2", tr("Password (at least 10 characters)"): "x"},
        pressed=[tr("Create teacher account")])
    run("t_settings", values={tr("Name"): "T2", tr("Username"): "t2", tr("Password (at least 10 characters)"): "long-password-1"},
        pressed=[tr("Create teacher account")])
    T.VALUES.clear()
    run("t_certs")
    # ---- discussion board (teacher side, then student side)
    from nasmo import forum, auth as _auth
    tch = st.session_state["user"]
    sara = _auth._user_from_row([u for u in store.select("users") if u["username"] == "sara"][0])
    run("forum")
    q1 = forum.ask(store, sara, "Why does my loop never stop?", "My code:\n```\nwhile(true){}\n```\nhelp")
    r1 = forum.reply(store, tch, q1["id"], "Check your condition.")
    run("forum")
    run("forum", values={"fm_search": "zzzz"})
    T.VALUES.clear()
    run("forum", {"thread": q1["id"]})
    run("forum", {"thread": q1["id"]}, pressed=[f"fm_pin"])
    run("forum", {"thread": q1["id"]}, pressed=[f"fm_close"])
    run("forum", {"thread": q1["id"]}, pressed=[f"fm_acc_{r1['id']}"])
    run("forum", {"thread": q1["id"]}, values={"fm_reply_body": "x"}, pressed=[tr("Post answer")])
    run("forum", values={"fm_title": "", "fm_body": ""}, pressed=[tr("Post question")])
    run("forum", {"thread": "nope"})
    T.VALUES.clear()
    run("t_dashboard")
    run(pressed=["btn_logout"])
    # ---- student
    run("teacher_login", values={"teacher_u": "sara", "teacher_p": "pass1234"}, pressed=[tr("Sign in")])
    T.VALUES.clear()
    run("student_login", values={"student_u": "sara", "student_p": "pass1234"}, pressed=[tr("Sign in")])
    T.VALUES.clear()
    for p in ("home", "stages", "trophies", "progress", "certificates", "resources", "about", "account"):
        run(p)
    for p in ("t_dashboard", "t_students"):
        run(p)
    run("forum")
    run("forum", {"thread": q1["id"]})
    run("forum", {"thread": q1["id"]}, pressed=[f"fm_thx_{r1['id']}"])
    run("forum", {"thread": q1["id"]}, pressed=[f"fm_acc_{r1['id']}"])
    run("forum", {"thread": q1["id"]}, values={"fm_reply_body": "Thanks!"}, pressed=[tr("Post answer")])
    run("forum", values={"fm_title": "Hi", "fm_body": "x"}, pressed=[tr("Post question")])
    run("forum", values={"fm_title": "A real new question here", "fm_body": "Some details"}, pressed=[tr("Post question")])
    T.VALUES.clear()
    run("forum")
    for s in STAGES:
        run("stage", {"stage": s["id"]})
    for mid in MISSION_BY_ID:
        run("mission", {"mission": mid})
    # wrong then right on a mission, finish it
    mid = "f-1"
    m = MISSION_BY_ID[mid]
    s0 = m["steps"][0]
    wrong = (s0["answer"] + 1) % len(s0["options"])
    run("mission", {"mission": mid}, values={f"ans_{mid}_{s0['id']}": wrong}, pressed=[f"check_{mid}_{s0['id']}"])
    run()
    T.VALUES.clear()
    for mid in ("f-1", "f-2", "f-3", "f-4"):
        for s in MISSION_BY_ID[mid]["steps"]:
            key = f"ans_{mid}_{s['id']}"
            vals = {key: s["answer"] if "options" in s else s["answer"][0]}
            if s["type"] == "solve":
                vals[key + "_code"] = "int main(){ " + "x" * 130 + " }"
            else:
                pass
            if s["type"] != "solve" and "options" not in s:
                vals[key] = s["answer"][0]
            run("mission", {"mission": mid}, values=vals, pressed=[f"check_{mid}_{s['id']}"])
            run()
            run(pressed=[f"next_{mid}_{s['id']}"])
    for p in ("certificates", "trophies", "progress", "stages", "home"):
        run(p)
    for k in ("galaxy", "gold", "adventure", "royal"):
        run("certificates", pressed=[f"cert_pick_{k}"])
    # account errors
    run("account")
    for k in list(T.SEEN):
        pass
    run("account", values={"cur_pw": "bad", "new_pw": "abc", "new_pw2": "abc"}, pressed=[tr("Change password")])
    run("account", values={"cur_pw": "pass1234", "new_pw": "abcdef", "new_pw2": "abcdef"}, pressed=[tr("Change password")])
    run("account", values={"cur_pw": "pass1234", "new_pw": "abc@12", "new_pw2": "abc@13"}, pressed=[tr("Change password")])
    run("account", values={"Your name": "Sara A"}, pressed=[tr("Save name")])
    run(pressed=["btn_logout"])
    # ---- forgotten passwords
    run("student_login")
    run("student_login", values={"forgot_u": "nobody-here"}, pressed=[tr("Send request to my teacher")])
    run("student_login", values={"forgot_u": ""}, pressed=[tr("Send request to my teacher")])
    run("student_login", values={"forgot_u": "sara"}, pressed=[tr("Send request to my teacher")])
    T.VALUES.clear()
    run("teacher_login")                                    # two teachers: "ask another teacher"
    store.delete("users", {"username": "t2"})
    run("teacher_login")
    for vals in ({"rec_code": "WRONG", "rec_pw": "brand-new-password", "rec_pw2": "brand-new-password"},
                 {"rec_code": "TESTCODE-123", "rec_pw": "brand-new-password", "rec_pw2": "different-password"},
                 {"rec_code": "TESTCODE-123", "rec_pw": "short", "rec_pw2": "short"},
                 {"rec_code": "TESTCODE-123", "rec_pw": "brand-new-password", "rec_pw2": "brand-new-password"}):
        run("teacher_login", values=vals, pressed=[tr("Recover my account")])
    T.VALUES.clear()
    run("teacher_login", values={"teacher_u": "teacher1", "teacher_p": "brand-new-password"}, pressed=[tr("Sign in")])
    T.VALUES.clear()
    run("t_dashboard")
    run("t_students")
    sid = [u["id"] for u in store.select("users") if u["username"] == "sara"][0]
    run("t_students", pressed=[f"reqgen_{sid}"])
    run("t_students")
    run("t_students", pressed=[f"reqdone_{sid}"])
    run("t_settings")
    run(pressed=["btn_logout"])
    return sorted(i18n.MISSES), T


def switch_check(T):
    """Press the language button on the home page; returns the languages seen."""
    import runpy
    from nasmo import i18n
    st = T.install()

    def run(pressed=()):
        T.PRESSED.update(pressed)
        for _ in range(5):
            T.reset_run()
            try:
                runpy.run_path(str(ROOT / "app.py"), run_name="__main__")
                break
            except T.RerunException:
                continue
    st.session_state["page"] = "home"
    run()
    seen = [("button", "btn_lang") in T.SEEN, st.session_state["lang"]]
    run(["btn_lang"])
    seen.append(st.session_state["lang"])
    run(["btn_lang"])
    seen.append(st.session_state["lang"])
    return seen


if __name__ == "__main__":
    import json
    miss, T = walk()
    print("@@" + json.dumps({"misses": miss, "switch": switch_check(T)}))
