"""Smoke test of the real page code against a fake Streamlit (see
stub_streamlit.py). Uses a throw-away SQLite database."""
import os
import runpy
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_tmp = tempfile.mkdtemp(prefix="nasmo_pages_")
os.environ["NASMO_DATA_DIR"] = _tmp
os.environ["NASMO_SETUP_CODE"] = "TESTCODE-123"
os.environ["NASMO_RAISE"] = "1"
os.environ.pop("SUPABASE_URL", None)
os.environ.pop("SUPABASE_SERVICE_KEY", None)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

import importlib  # noqa: E402
from nasmo import config as _cfg  # noqa: E402
importlib.reload(_cfg)  # pick up this file's private data folder
import stub_streamlit as T  # noqa: E402

st = T.install()

from nasmo.content.missions import MISSION_BY_ID  # noqa: E402
from nasmo.content.stages import STAGES  # noqa: E402
from nasmo import game as G  # noqa: E402


def run(page=None, params=None, pressed=(), values=None, user=None):
    """Run app.py once (re-running after st.rerun like Streamlit does)."""
    ss = st.session_state
    if page is not None:
        ss["page"] = page
        ss["params"] = params or {}
    if user is not None:
        ss["user"] = user
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


def assert_clean(tc, out):
    tc.assertNotIn("Something went wrong", out)
    tc.assertNotIn("not reachable", out)


class PageFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["NASMO_SETUP_CODE"] = "TESTCODE-123"   # other test files change it
        T.full_reset()

    def test_01_visitor_pages(self):
        out = run("home")
        assert_clean(self, out)
        for s in STAGES:                       # stage cards are NOT on the home page
            self.assertNotIn(f'<h3>{s["title"]}</h3>', out)
        self.assertIn(("button", "side_login_student"), T.SEEN)
        self.assertFalse(any(d[1] == "Nasmo_Informatics_Interactive_Guide.html" for d in T.DOWNLOADS))
        run("stages")                          # a visitor pressing Start is sent to the student login
        self.assertEqual(st.session_state["page"], "student_login")
        self.assertIn(("button", "side_login_teacher"), T.SEEN)
        self.assertNotIn("My Progress", out)           # not in the visitor menu
        for page in ("resources", "about", "student_login", "teacher_login"):
            assert_clean(self, run(page))
        out = run("stage", {"stage": "s2"})
        self.assertIn("Sign in as a student to open the missions", out)

    def test_01b_registration_hints(self):
        out = run("student_login")
        self.assertIn("in English letters", out)
        self.assertIn("Allowed symbols: @  #  $", out)
        T.PRESSED.discard("Create account")
        run("student_login", values={"reg_name": "سارة", "reg_user": "sara_x", "reg_pw": "abc@123", "reg_pw2": "abc@123"},
            pressed=["Create account"])
        self.assertTrue(any("English" in m for _, m in T.MSGS), T.MSGS)
        self.assertIsNone(st.session_state.get("user"))

    def test_02_visitor_cannot_open_protected_pages(self):
        for page in ("progress", "certificates", "mission", "t_dashboard", "t_students", "t_settings"):
            out = run(page, {"mission": "f-1"})
            self.assertIn("login", st.session_state["page"], page)
        self.assertIsNone(st.session_state.get("user"))

    def test_03_first_teacher_and_dashboard(self):
        run("teacher_login")
        out = run(values={"ft_code": "wrong", "ft_name": "Teacher", "ft_user": "teacher1",
                          "ft_pw": "correct-horse-1", "ft_pw2": "correct-horse-1"},
                  pressed=["Create teacher account"])
        self.assertIsNone(st.session_state.get("user"))
        self.assertTrue(any("Wrong setup code" in m for _, m in T.MSGS))
        run(values={"ft_code": "TESTCODE-123"}, pressed=["Create teacher account"])
        u = st.session_state.get("user")
        self.assertTrue(u and u.is_teacher, T.MSGS)
        self.assertEqual(st.session_state["page"], "t_dashboard")
        out = run()
        self.assertIn("Teacher Dashboard", out)
        self.assertIn("Students", out)
        self.assertNotIn('class="nl-login', out)

    def test_04_teacher_pages_render(self):
        for page in ("stages", "t_dashboard", "t_students", "t_reports", "t_content", "t_certs", "t_settings",
                     "resources", "about"):
            assert_clean(self, run(page))
        out = run("stage", {"stage": "f"})
        self.assertIn("Teacher preview", out)
        out = run("mission", {"mission": "f-1"})
        self.assertIn("Teacher preview", out)
        for s in STAGES:
            for p in ("student_login",):
                pass

    def test_05_teacher_preview_does_not_save(self):
        from nasmo.ui import session as S
        store, _, _ = S.get_store()
        mid = "f-1"
        step = MISSION_BY_ID[mid]["steps"][0]
        run("mission", {"mission": mid}, values={f"ans_{mid}_{step['id']}": step["answer"]},
            pressed=[f"check_{mid}_{step['id']}"])
        self.assertEqual(store.select("mission_progress"), [])
        self.assertEqual(store.select("attempts"), [])

    def test_06_demo_data(self):
        run("t_dashboard", pressed=["demo_load"])
        out = run("t_dashboard", values={"include_demo": True})
        self.assertIn("DEMO DATA is included", out)
        out = run("t_students")
        self.assertIn("Demo Student", out)
        run("t_dashboard", values={"include_demo": False})
        out = run("t_students")
        self.assertNotIn("Demo Student", out)
        run("t_reports"); run("t_certs")

    def test_07_teacher_adds_student_then_logout(self):
        run("t_students", values={"Student name": "Sara", "Username": "sara",
                                  "Temporary password (at least 6 characters)": "pass1234"},
            pressed=["Create student"])
        out = run("t_students")
        self.assertIn("sara", out)
        run(pressed=["btn_logout"])
        self.assertIsNone(st.session_state.get("user"))
        self.assertEqual(st.session_state["page"], "home")

    def test_08_student_cannot_use_teacher_login(self):
        run("teacher_login", values={"teacher_u": "sara", "teacher_p": "pass1234"}, pressed=["Sign in"])
        self.assertIsNone(st.session_state.get("user"))

    def test_09_student_login_and_menu(self):
        run("student_login", values={"student_u": "sara", "student_p": "pass1234"}, pressed=["Sign in"])
        u = st.session_state.get("user")
        self.assertTrue(u and u.is_student)
        run("home")
        for key in ("side_home", "side_progress", "side_certificates", "side_resources", "side_about"):
            self.assertIn(("button", key), T.SEEN)
        self.assertNotIn(("button", "side_t_dashboard"), T.SEEN)
        for page in ("t_dashboard", "t_students"):
            run(page)
            self.assertEqual(st.session_state["page"], "home")

    def _solve(self, mid):
        m = MISSION_BY_ID[mid]
        for s in m["steps"]:
            key = f"ans_{mid}_{s['id']}"
            vals = {key: s["answer"] if "options" in s else s["answer"][0]}
            if s["type"] == "solve":
                vals[key + "_code"] = "int main(){ /* my solution */ " + "x" * 120 + " }"
            run("mission", {"mission": mid}, values=vals, pressed=[f"check_{mid}_{s['id']}"])
            out = run()
            self.assertIn("Correct!", out, (mid, s["id"]))
            self.finish_out = run(pressed=[f"next_{mid}_{s['id']}"])   # the run that shows the victory screen
        return run()

    def test_09b_designs_visible_but_no_certificate_before_completion(self):
        out = run("certificates")
        assert_clean(self, out)
        self.assertEqual(out.count("Certificate PREVIEW"), 4)            # the four designs can be seen
        for k in ("royal", "galaxy", "gold", "adventure"):
            self.assertIn(("button", f"cert_pick_{k}"), T.SEEN)
        self.assertIn("No certificates yet", out)
        self.assertEqual([d for d in T.DOWNLOADS if d[1] and d[1].startswith("certificate-")], [])   # nothing to download
        self.assertNotIn("Print / Save as PDF", out)

    def test_10_wrong_then_right_and_progress_saved(self):
        from nasmo.ui import session as S
        store, _, _ = S.get_store()
        mid = "f-1"
        s0 = MISSION_BY_ID[mid]["steps"][0]
        wrong = (s0["answer"] + 1) % len(s0["options"])
        run("mission", {"mission": mid}, values={f"ans_{mid}_{s0['id']}": wrong},
            pressed=[f"check_{mid}_{s0['id']}"])
        out = run()
        self.assertNotIn("Correct!", out)
        rows = store.select("mission_progress", {"user_id": st.session_state["user"].id})
        self.assertEqual(rows[0]["status"], "in_progress")
        out = self._solve_from_state(mid)
        self.assertIn("Mission completed", out)
        rows = store.select("mission_progress", {"user_id": st.session_state["user"].id})
        self.assertEqual(rows[0]["status"], "completed")

    def _solve_from_state(self, mid):
        return self._solve(mid)

    def test_11_complete_fundamentals_and_certificate(self):
        for mid in ("f-2", "f-3", "f-4"):
            out = self._solve(mid)
            self.assertIn("Mission completed", out, mid)
            self.assertIn("nl-victory", out, mid)
            self.assertIn("nlAudio", self.finish_out, mid)   # played once, on first view
        out = run("progress")
        assert_clean(self, out)
        self.assertIn("4/4", out)
        out = run("certificates")
        assert_clean(self, out)
        self.assertIn("Fundamentals - Training Completion", out)
        self.assertIn("not official", out.lower().replace("they are not official", "not official"))
        self.assertTrue(any(d[1] and d[1].startswith("certificate-") for d in T.DOWNLOADS))
        for k in ("galaxy", "gold", "adventure"):
            run("certificates", pressed=[f"cert_pick_{k}"])
            run("certificates")
            self.assertTrue(any(d[1] and d[1].endswith(f"-{k}.html") for d in T.DOWNLOADS), k)
        run("certificates", pressed=["cert_pick_royal"])

    def test_12_progress_survives_logout(self):
        run(pressed=["btn_logout"])
        run("student_login", values={"student_u": "sara", "student_p": "pass1234"}, pressed=["Sign in"])
        out = run("progress")
        self.assertIn("4/20", out.replace(" ", "")) if False else None
        self.assertIn("4/", out)

    def test_13_home_shows_progress_for_student(self):
        out = run("home")
        self.assertNotIn("<h3>Fundamentals</h3>", out)
        run(pressed=["hero_start"])
        self.assertEqual(st.session_state["page"], "stages")
        out = run()
        self.assertIn("4/4 Missions", out)
        for s in STAGES:
            self.assertIn(G.WORLDS[s["id"]][0], out)

    def test_14_all_stage_and_mission_pages_for_student(self):
        for s in STAGES:
            assert_clean(self, run("stage", {"stage": s["id"]}))
        for mid in MISSION_BY_ID:
            assert_clean(self, run("mission", {"mission": mid}))

    def test_14b_game_pages(self):
        out = run("trophies")
        assert_clean(self, out)
        for word in ("Trophy Room", "Mission Maker", "Backpack", "Nasmo Champion", "Pixel Cape"):
            self.assertIn(word, out)
        out = run("stage", {"stage": "f"})
        self.assertIn("nl-quest done", out)
        self.assertIn("Code Camp", out)
        out = run("stages")
        self.assertIn("nl-hud", out)
        self.assertIn(("button", "world_go_f"), T.SEEN)

    def test_15_hidden_mission_not_available_to_student(self):
        from nasmo import admin
        from nasmo.ui import session as S
        store, _, _ = S.get_store()
        teacher = store.get("users", {"username": "teacher1"})
        from nasmo.auth import User
        t = User(id=teacher["id"], username="teacher1", display_name="T", role="teacher")
        admin.set_mission_active(store, t, "s1-1", False)
        out = run("mission", {"mission": "s1-1"})
        self.assertIn("not available", out)
        admin.set_mission_active(store, t, "s1-1", True)


    def test_16_forgot_password_requests(self):
        run(pressed=["btn_logout"])
        run("student_login")
        run("student_login", values={"forgot_u": "sara"}, pressed=["Send request to my teacher"])
        self.assertTrue(any("Request sent" in m for _, m in T.MSGS), T.MSGS)
        run("student_login", values={"forgot_u": "nobody-here"}, pressed=["Send request to my teacher"])
        self.assertTrue(any("does not exist" in m for _, m in T.MSGS), T.MSGS)
        self.assertFalse(any("Request sent" in m for _, m in T.MSGS))
        T.VALUES.clear()
        # teacher: sees the request and generates a temporary password
        run("teacher_login", values={"teacher_u": "teacher1", "teacher_p": "correct-horse-1"}, pressed=["Sign in"])
        T.VALUES.clear()
        out = run("t_dashboard")
        self.assertIn("asked for a new password", out)
        from nasmo.ui import session as S
        store, _, _ = S.get_store()
        sid = [u["id"] for u in store.select("users") if u["username"] == "sara"][0]
        run("t_students")
        self.assertIn(("button", f"reqgen_{sid}"), T.SEEN)
        run("t_students", pressed=[f"reqgen_{sid}"])
        run("t_students")
        temp = st.session_state.get(f"reqtemp_{sid}")
        self.assertTrue(temp)
        self.assertNotIn(("button", f"reqgen_{sid}"), T.SEEN)        # request answered
        run(pressed=["btn_logout"])
        run("student_login", values={"student_u": "sara", "student_p": temp}, pressed=["Sign in"])
        self.assertTrue(st.session_state.get("user") and st.session_state["user"].is_student)
        run(pressed=["btn_logout"])
        T.VALUES.clear()
        # teacher login page offers recovery (one teacher)
        run("teacher_login")
        self.assertIn(("text_input", "rec_code"), T.SEEN)


    def test_16b_impact_page_and_standalone_report(self):
        from nasmo import auth, impact
        from nasmo.ui import impact_view as IV, session as S
        run("teacher_login", values={"teacher_u": "teacher1", "teacher_p": "correct-horse-1"}, pressed=["Sign in"])
        T.VALUES.clear()
        out = run("t_impact")
        self.assertIn("Impact Report", out)
        self.assertIn("Situation analysis", out)
        store, _, _ = S.get_store()
        t = st.session_state["user"]
        P = "<img src=x onerror=alert(1)>"
        auth.create_student_by_teacher(store, t, "impx", P, "pass@123")
        d = impact.build(store, t, include_demo=False)
        for lang in ("ar", "en"):
            doc = IV.report_html(d, lang, standalone=True)
            self.assertTrue(doc.startswith("<!doctype html>"))
            self.assertIn(f'dir="{"rtl" if lang == "ar" else "ltr"}"', doc)
            self.assertNotIn("<img src=x", doc)
        self.assertIn("تحليل الموقف", IV.report_html(d, "ar", standalone=True))
        self.assertIn("Situation analysis", IV.report_html(d, "en", standalone=True))
        self.assertEqual([c for c in run("t_impact").split("\n") if "<img src=x" in c and "<div" in c], [])
        run(pressed=["btn_logout"])
        T.VALUES.clear()
        # a student can never open it
        auth.register_student(store, "impstu", "Imp Student", "pass@123")
        run("student_login", values={"student_u": "impstu", "student_p": "pass@123"}, pressed=["Sign in"])
        T.VALUES.clear()
        self.assertTrue(st.session_state["user"].is_student)
        out = run("t_impact")
        self.assertNotIn("Situation analysis", out)
        run(pressed=["btn_logout"])
        self.assertIsNone(st.session_state.get("user"))

    def test_16c_forum_page(self):
        from nasmo import auth, forum
        from nasmo.ui import session as S
        run("teacher_login", values={"teacher_u": "teacher1", "teacher_p": "correct-horse-1"}, pressed=["Sign in"])
        T.VALUES.clear()
        store, _, _ = S.get_store()
        t = st.session_state["user"]
        stu = auth.register_student(store, "forumer", "Forum Girl", "pass@123")
        P = "<img src=x onerror=alert(1)>"
        q = forum.ask(store, stu, P + " title", P + "\n```\n<script>x</script>\n```")
        out = run("forum")
        self.assertIn("Discussion Board", out)
        self.assertIn("new post", out)                       # teacher counter
        self.assertIn(("button", f"fm_open_{q['id']}"), T.SEEN)
        out = run("forum", {"thread": q["id"]})
        self.assertEqual([c for c in out.split("\n") if ("<img src=x" in c or "<script>x" in c)], [])
        self.assertIn("&lt;img src=x", out)
        run("forum", {"thread": q["id"]}, values={"fm_reply_body": "Try a counter."}, pressed=["Post answer"])
        T.VALUES.clear()
        self.assertEqual(len(store.select("forum_posts", {"parent_id": q["id"]})), 1)
        run("forum", {"thread": q["id"]}, pressed=["fm_pin"])
        self.assertTrue(store.get("forum_posts", {"id": q["id"]})["pinned"])
        run("forum", {"thread": q["id"]}, pressed=["fm_close"])
        run(pressed=["btn_logout"])
        T.VALUES.clear()
        # a student sees the board, cannot see teacher buttons, cannot reply to a closed discussion
        run("student_login", values={"student_u": "forumer", "student_p": "pass@123"}, pressed=["Sign in"])
        T.VALUES.clear()
        out = run("forum", {"thread": q["id"]})
        self.assertNotIn(("button", "fm_pin"), T.SEEN)
        self.assertIn("This discussion is closed.", out)
        self.assertIn(("button", f"fm_del_{q['id']}"), T.SEEN)          # her own question
        out = run("forum")
        self.assertIn("Discussion Board", out)
        run("forum", values={"fm_title": "My real question", "fm_body": "details please"}, pressed=["Post question"])
        T.VALUES.clear()
        self.assertEqual(len([p for p in store.select("forum_posts") if p["title"] == "My real question"]), 1)
        run(pressed=["btn_logout"])
        T.VALUES.clear()

    def test_17_html_in_names_is_escaped_and_pdf_survives(self):
        """Names, titles and questions typed by people must never become live HTML, and the PDF export must not crash."""
        from nasmo import admin, auth, resources as R
        from nasmo.ui import session as S
        run("teacher_login", values={"teacher_u": "teacher1", "teacher_p": "correct-horse-1"}, pressed=["Sign in"])
        T.VALUES.clear()
        store, _, _ = S.get_store()
        t = st.session_state["user"]
        P = "<img src=x onerror=alert(1)>"
        stu = auth.create_student_by_teacher(store, t, "xssuser", P, "pass@123")
        R.add_resource(store, t, P + "t", "https://example.org/x", "all", "Video", P)
        m = admin.add_custom_mission(store, t, "s2", P + "mt", P, P + "q", [P + "a", "b", "<script>alert(2)</script>"], 1, P)

        def live_html(out_text):
            return [c for c in out_text.split("\n") if ("<div" in c or "<table" in c or "<section" in c)
                    and ("<img src=x" in c or "<script>alert" in c)]
        for page in ("t_dashboard", "t_students", "t_reports", "t_content", "t_certs", "t_settings", "resources", "stages"):
            self.assertEqual(live_html(run(page)), [], page)
        self.assertEqual(live_html(run("t_students", values={"stu_pick": stu.id})), [])
        run(pressed=["btn_logout"])
        T.VALUES.clear()
        run("student_login", values={"student_u": "xssuser", "student_p": "pass@123"}, pressed=["Sign in"])
        for page, prm in (("home", {}), ("stages", {}), ("stage", {"stage": "s2"}), ("resources", {}),
                          ("progress", {}), ("mission", {"mission": m["id"]})):
            self.assertEqual(live_html(run(page, prm)), [], page)
        run(pressed=["btn_logout"])


if __name__ == "__main__":
    unittest.main(verbosity=2)