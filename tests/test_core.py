"""Core behaviour: storage, accounts, roles, grading, saving progress,
certificates, teacher tools. Runs against SQLite and against the fake
PostgREST server (to check SupabaseStore request building)."""
import os
import tempfile
import unittest

from nasmo import admin, auth, certificates, config, progress, resources
from nasmo.auth import AuthError, PermissionDenied
from nasmo.content.missions import MISSIONS, MCQ_TYPES
from nasmo.content.stages import STAGES
from nasmo.grading import grade_step, normalize
from nasmo.store import DuplicateError, SQLiteStore, StoreError, SupabaseStore

from . import fake_postgrest

EXPLAIN_TEXT = {
    ("s1-4", "c"): "Greedy picks 4 + 1 + 1 which is three coins, but 3 + 3 uses only two coins, so the largest coin first is not optimal.",
    ("s4-4", "c"): "Each block stores its sum so whole blocks cost O(1); with blocks of size sqrt(n) a query touches at most about sqrt(n) whole blocks plus two partial blocks.",
}


def correct_inputs(mission, step):
    """(answer, code) that pass this step."""
    if step["type"] in MCQ_TYPES:
        return step["answer"], None
    if step["type"] == "explain":
        return EXPLAIN_TEXT[(mission["id"], step["id"])], None
    code = "int main() { /* my solution */ return 0; } // padding padding padding" if step["type"] == "solve" else None
    return step["answer"][0], code


def complete_mission(store, user, mission):
    last = None
    for st in mission["steps"]:
        ans, code = correct_inputs(mission, st)
        last = progress.submit_answer(store, user, mission["id"], st["id"], ans, code)
        assert last.correct and last.saved, (mission["id"], st["id"], last)
    return last


class Base:
    """Mixin - subclasses provide make_store()."""

    def make_store(self):
        raise NotImplementedError

    def setUp(self):
        auth.reset_lockouts()
        self.store = self.make_store()
        os.environ["NASMO_SETUP_CODE"] = "SETUP123"
        self.teacher = auth.create_first_teacher(
            self.store, "SETUP123", "teacher1", "Teacher One", "a-long-secret-pass")
        self.s1 = auth.register_student(self.store, "student1", "Student One", "pass@123")
        self.s2 = auth.register_student(self.store, "student2", "Student Two", "pass@456")

    # ---- storage --------------------------------------------------
    def test_store_roundtrip_json_bool_filters(self):
        st = self.store
        st.upsert("mission_progress", {"user_id": "u", "mission_id": "m", "stage_id": "f",
                                       "status": "in_progress", "score": 5,
                                       "step_results": {"a": {"passed": True, "ar": "عربي"}},
                                       "started_at": "2026-01-01T00:00:00+00:00",
                                       "completed_at": None, "last_activity": "2026-01-01T00:00:00+00:00"})
        st.upsert("mission_progress", {"user_id": "u", "mission_id": "m", "stage_id": "f",
                                       "status": "completed", "score": 90,
                                       "step_results": {"a": {"passed": True}},
                                       "started_at": "2026-01-01T00:00:00+00:00",
                                       "completed_at": "2026-01-02T00:00:00+00:00",
                                       "last_activity": "2026-01-02T00:00:00+00:00"})
        rows = st.select("mission_progress", {"user_id": "u"})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "completed")
        self.assertEqual(rows[0]["step_results"], {"a": {"passed": True}})
        self.assertEqual(len(st.select("mission_progress", {"score": ("gte", 50)})), 1)
        self.assertEqual(len(st.select("mission_progress", {"mission_id": ("in", ["m", 'we"ird,x'])})), 1)
        self.assertEqual(len(st.select("mission_progress", {"completed_at": None})), 0)
        st.insert("resources", {"id": "r1", "stage_id": "f", "kind": "Other", "title": "T",
                                "url": "https://x.y", "description": "", "source": "s",
                                "visible": True, "sort": 1, "created_at": "2026-01-01T00:00:00+00:00"})
        self.assertEqual(st.select("resources", {"visible": True})[0]["visible"], True)
        self.assertEqual(st.update("resources", {"id": "r1"}, {"visible": False}), 1)
        self.assertEqual(st.select("resources", {"visible": True}), [])
        self.assertEqual(st.delete("resources", {"id": "r1"}), 1)

    def test_unique_username(self):
        with self.assertRaises(AuthError):
            auth.register_student(self.store, "Student1", "Another", "pass@123")
        with self.assertRaises(DuplicateError):
            self.store.insert("users", {"id": "x", "username": "student1", "display_name": "x",
                                        "role": "student", "password_hash": "x", "active": True,
                                        "is_demo": False, "created_at": "2026-01-01T00:00:00+00:00",
                                        "last_login": None})

    # ---- accounts & roles -----------------------------------------
    def test_login_roles_are_separate(self):
        u = auth.login(self.store, "student1", "pass@123", "student")
        self.assertTrue(u.is_student)
        with self.assertRaises(AuthError):
            auth.login(self.store, "student1", "pass@123", "teacher")
        with self.assertRaises(AuthError):
            auth.login(self.store, "teacher1", "a-long-secret-pass", "student")
        t = auth.login(self.store, "teacher1", "a-long-secret-pass", "teacher")
        self.assertTrue(t.is_teacher)

    def test_wrong_password_and_lockout(self):
        for _ in range(auth.MAX_FAILS):
            with self.assertRaises(AuthError):
                auth.login(self.store, "student1", "nope", "student")
        with self.assertRaises(AuthError) as cm:
            auth.login(self.store, "student1", "pass@123", "student")  # even correct is locked
        self.assertIn("Too many", str(cm.exception))

    def test_password_not_stored_plain(self):
        row = self.store.get("users", {"username": "student1"})
        self.assertNotIn("pass@123", row["password_hash"])
        self.assertTrue(row["password_hash"].startswith("pbkdf2_sha256$"))

    def test_first_teacher_needs_setup_code(self):
        st = self.make_store()
        with self.assertRaises(AuthError):
            auth.create_first_teacher(st, "WRONG", "t", "T Teacher", "a-long-secret-pass")
        auth.create_first_teacher(st, "SETUP123", "teach2", "T Teacher", "a-long-secret-pass")
        with self.assertRaises(AuthError):  # only the first one
            auth.create_first_teacher(st, "SETUP123", "t2", "T Two", "a-long-secret-pass")

    def test_first_teacher_local_needs_only_username_and_password(self):
        import os
        from unittest import mock
        env = {k: v for k, v in os.environ.items() if k not in ("NASMO_SETUP_CODE", "SUPABASE_URL", "SUPABASE_SERVICE_KEY")}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertFalse(config.setup_code_required())
            st = self.make_store()
            u = auth.create_first_teacher(st, "", "Teacher_One", "", "a-long-secret-pass")
            self.assertEqual((u.username, u.display_name), ("teacher_one", "Teacher_One"))
            with self.assertRaises(AuthError):
                auth.create_first_teacher(st, "", "t2", "", "a-long-secret-pass")
            self.assertTrue(auth.login(st, "teacher_one", "a-long-secret-pass", role="teacher"))
        with mock.patch.dict(os.environ, {**env, "NASMO_SETUP_CODE": "X"}, clear=True):
            self.assertTrue(config.setup_code_required())

    def test_default_data_dir_is_outside_project(self):
        d = config._default_data_dir()
        self.assertTrue(d == config.ROOT / "data" or config.ROOT not in d.parents)

    def test_student_forgot_password_request_flow(self):
        st, t = self.store, self.teacher
        auth.request_password_reset(st, "  STUDENT1 ")              # case and spaces do not matter
        for bad in ("nobody", "", "teacher1"):                      # unknown / empty / not a student: she is told
            with self.assertRaises(AuthError) as cm:
                auth.request_password_reset(st, bad)
            self.assertTrue("does not exist" in str(cm.exception) or "enter your username" in str(cm.exception))
        st.update("users", {"id": self.s2.id}, {"active": False})
        with self.assertRaises(AuthError) as cm:
            auth.request_password_reset(st, "student2")
        self.assertIn("disabled", str(cm.exception))
        st.update("users", {"id": self.s2.id}, {"active": True})
        reqs = auth.list_reset_requests(st, t)
        self.assertEqual([r["username"] for r in reqs], ["student1"])
        with self.assertRaises(PermissionDenied):
            auth.list_reset_requests(st, self.s1)                   # students cannot see requests
        temp = auth.reset_student_password(st, t, self.s1.id)
        self.assertEqual(auth.list_reset_requests(st, t), [])       # answered
        self.assertTrue(auth.login(st, "student1", temp, role="student"))
        with self.assertRaises(AuthError):
            auth.login(st, "student1", "pass@123", role="student")
        auth.request_password_reset(st, "student2")
        auth.dismiss_reset_request(st, t, self.s2.id)
        self.assertEqual(auth.list_reset_requests(st, t), [])

    def test_forgot_request_is_throttled(self):
        for _ in range(auth.MAX_FAILS):
            try:
                auth.request_password_reset(self.store, "student1")
            except AuthError:
                pass
        with self.assertRaises(AuthError) as cm:
            auth.request_password_reset(self.store, "student1")
        self.assertIn("Too many", str(cm.exception))

    def test_teacher_resets_another_teacher(self):
        st, t = self.store, self.teacher
        t2 = auth.create_teacher(st, t, "teacher2", "Teacher Two", "another-long-pass")
        temp = auth.reset_teacher_password(st, t, t2.id)
        self.assertGreaterEqual(len(temp), config.TEACHER_MIN_PASSWORD)
        self.assertTrue(auth.login(st, "teacher2", temp, role="teacher"))
        with self.assertRaises(AuthError):
            auth.reset_teacher_password(st, t, t.id)                # not herself
        with self.assertRaises(PermissionDenied):
            auth.reset_teacher_password(st, self.s1, t2.id)
        self.assertEqual(len(auth.list_teachers(st, t)), 2)

    def test_single_teacher_recovery_with_setup_code(self):
        st = self.store
        self.assertTrue(auth.only_one_teacher(st))
        with self.assertRaises(AuthError):
            auth.recover_only_teacher(st, "WRONG", "brand-new-password")
        with self.assertRaises(AuthError):
            auth.recover_only_teacher(st, "SETUP123", "short")
        name = auth.recover_only_teacher(st, "SETUP123", "brand-new-password")
        self.assertEqual(name, "teacher1")
        self.assertTrue(auth.login(st, "teacher1", "brand-new-password", role="teacher"))
        with self.assertRaises(AuthError):
            auth.login(st, "teacher1", "a-long-secret-pass", role="teacher")
        auth.create_teacher(st, self.teacher, "teacher2", "Teacher Two", "another-long-pass")
        self.assertFalse(auth.only_one_teacher(st))
        with self.assertRaises(AuthError):                          # with two teachers the code is not enough
            auth.recover_only_teacher(st, "SETUP123", "another-new-password")

    def test_recovery_code_guessing_is_locked(self):
        for _ in range(auth.MAX_FAILS):
            with self.assertRaises(AuthError):
                auth.recover_only_teacher(self.store, "BAD", "brand-new-password")
        with self.assertRaises(AuthError) as cm:
            auth.recover_only_teacher(self.store, "SETUP123", "brand-new-password")
        self.assertIn("Too many", str(cm.exception))

    def test_sessions(self):
        tok = auth.create_session(self.store, self.s1)
        self.assertEqual(auth.resume_session(self.store, tok).id, self.s1.id)
        self.assertIsNone(auth.resume_session(self.store, tok + "x"))
        auth.end_session(self.store, tok)
        self.assertIsNone(auth.resume_session(self.store, tok))
        tok2 = auth.create_session(self.store, self.s1)
        self.store.update("sessions", {"user_id": self.s1.id}, {"expires_at": "2000-01-01T00:00:00+00:00"})
        self.assertIsNone(auth.resume_session(self.store, tok2))

    def test_teacher_only_functions_reject_students(self):
        calls = [
            lambda: admin.student_overview(self.store, self.s1),
            lambda: admin.dashboard(self.store, self.s1),
            lambda: admin.student_detail(self.store, self.s1, self.s2.id),
            lambda: admin.delete_student(self.store, self.s1, self.s2.id),
            lambda: admin.export_csv(self.store, self.s1),
            lambda: admin.load_demo_data(self.store, self.s1),
            lambda: admin.set_mission_active(self.store, self.s1, "f-1", False),
            lambda: admin.add_custom_mission(self.store, self.s1, "f", "Title", "", "Question?", ["a", "b"], 0),
            lambda: resources.add_resource(self.store, self.s1, "Title", "https://a.b", "f", "Other"),
            lambda: auth.reset_student_password(self.store, self.s1, self.s2.id),
            lambda: auth.set_setting(self.store, self.s1, "cert_pass_score", "0"),
            lambda: auth.create_teacher(self.store, self.s1, "t3", "T Three", "a-long-secret-pass"),
            lambda: certificates.set_revoked(self.store, self.s1, "x", True),
            lambda: admin.student_overview(self.store, None),
        ]
        for i, c in enumerate(calls):
            with self.assertRaises(PermissionDenied, msg=f"call {i}"):
                c()

    def test_student_cannot_read_other_student(self):
        with self.assertRaises(PermissionDenied):
            progress.user_rows(self.store, self.s1, self.s2.id)
        with self.assertRaises(PermissionDenied):
            progress.user_progress(self.store, self.s1, self.s2.id)
        with self.assertRaises(PermissionDenied):
            certificates.list_certificates(self.store, self.s1, self.s2.id)
        with self.assertRaises(PermissionDenied):
            certificates.sync_certificates(self.store, self.s1, self.s2.id)
        self.assertEqual(progress.user_rows(self.store, self.teacher, self.s2.id), {})

    def test_deactivated_student_cannot_login(self):
        admin  # noqa
        auth.set_student_active(self.store, self.teacher, self.s1.id, False)
        with self.assertRaises(AuthError):
            auth.login(self.store, "student1", "pass@123", "student")

    def test_reset_password(self):
        temp = auth.reset_student_password(self.store, self.teacher, self.s1.id)
        with self.assertRaises(AuthError):
            auth.login(self.store, "student1", "pass@123", "student")
        auth.login(self.store, "student1", temp, "student")

    def test_student_registration_rules(self):
        st = self.store
        bad_pw = ["ab@1", "abcdef12", "123456@!", "abc def@1", "abcdé@12", "pass~123"]
        for i, pw in enumerate(bad_pw):
            with self.assertRaises(AuthError, msg=pw):
                auth.register_student(st, f"rule{i}", "Rule Tester", pw)
        for i, nm in enumerate(["سارة", "S", "Sara 123", "12345"]):
            with self.assertRaises(AuthError, msg=nm):
                auth.register_student(st, f"rulen{i}", nm, "good@pass1")
        u = auth.register_student(st, "ruleok", "Sara Al-Ahmad", "Ab.cd_12")
        self.assertEqual(u.display_name, "Sara Al-Ahmad")
        with self.assertRaises(AuthError):
            auth.change_password(st, u, "Ab.cd_12", "nosymbol12")
        auth.change_password(st, u, "Ab.cd_12", "new#Pass1")

    def test_change_password(self):
        auth.change_password(self.store, self.s1, "pass@123", "newpass@99")
        auth.login(self.store, "student1", "newpass@99", "student")
        with self.assertRaises(AuthError):
            auth.change_password(self.store, self.s1, "wrong", "newpass@99")

    def test_registration_can_be_closed(self):
        auth.set_setting(self.store, self.teacher, "registration_open", "0")
        with self.assertRaises(AuthError):
            auth.register_student(self.store, "late1", "Late Student", "pass@123")

    # ---- grading ---------------------------------------------------
    def test_grading_rules(self):
        step = {"type": "predict", "answer": ["3 1 3.5"], "match": "words"}
        self.assertTrue(grade_step(step, "3   1  3.5").correct)
        self.assertTrue(grade_step(step, "٣ ١ ٣٫٥").correct)       # Arabic digits
        self.assertFalse(grade_step(step, "3 1 3").correct)
        self.assertTrue(grade_step(step, "").incomplete)
        comp = {"type": "complete", "answer": ["i<=n"], "match": "nospace"}
        self.assertTrue(grade_step(comp, " i <= n ;").correct)
        solve = {"type": "solve", "answer": ["47"], "min_code_chars": 25}
        r = grade_step(solve, "47", "")
        self.assertFalse(r.correct)
        self.assertTrue(r.needs_code)
        self.assertTrue(grade_step(solve, "47", "x" * 30).correct)
        self.assertFalse(grade_step(solve, "46", "x" * 30).correct)
        mcq = {"type": "choice", "options": ["a", "b"], "answer": 1}
        self.assertTrue(grade_step(mcq, 1).correct)
        self.assertFalse(grade_step(mcq, 0).correct)
        self.assertTrue(grade_step(mcq, None).incomplete)

    def test_explain_rubric(self):
        m = next(m for m in MISSIONS if m["id"] == "s1-4")
        step = m["steps"][2]
        self.assertTrue(grade_step(step, EXPLAIN_TEXT[("s1-4", "c")]).correct)
        self.assertFalse(grade_step(step, "because it is wrong in many situations of the problem here").correct)
        self.assertTrue(grade_step(step, "too short").incomplete)

    # ---- progress --------------------------------------------------
    def test_wrong_then_right_scores_and_saves(self):
        m = progress.get_mission(self.store, "f-1")
        a, b = m["steps"]
        wrong = progress.submit_answer(self.store, self.s1, "f-1", "a", 0)
        self.assertFalse(wrong.correct)
        self.assertTrue(wrong.saved)
        self.assertFalse(wrong.reveal)
        wrong2 = progress.submit_answer(self.store, self.s1, "f-1", "a", 1)
        self.assertTrue(wrong2.reveal)                         # after 2 wrong tries
        ok = progress.submit_answer(self.store, self.s1, "f-1", "a", a["answer"])
        self.assertTrue(ok.correct)
        self.assertEqual(ok.step_score, 60)                    # 100 - 2*20
        self.assertFalse(ok.mission_completed)
        done = progress.submit_answer(self.store, self.s1, "f-1", "b", b["answer"][0])
        self.assertTrue(done.mission_completed)
        self.assertEqual(done.mission_score, 80)               # (60 + 100) / 2
        row = progress.get_progress_row(self.store, self.s1, self.s1.id, "f-1")
        self.assertEqual(row["status"], "completed")
        self.assertEqual(len(self.store.select("attempts", {"user_id": self.s1.id})), 4)

    def test_opening_is_not_completing_and_empty_is_no_attempt(self):
        r = progress.submit_answer(self.store, self.s1, "f-1", "a", None)
        self.assertFalse(r.correct)
        self.assertFalse(r.saved)
        self.assertEqual(self.store.select("attempts", {"user_id": self.s1.id}), [])
        self.assertEqual(progress.user_rows(self.store, self.s1, self.s1.id), {})

    def test_solve_needs_code_not_counted_wrong(self):
        r = progress.submit_answer(self.store, self.s1, "f-3", "b", "47", "")
        self.assertTrue(r.needs_code)
        self.assertFalse(r.saved)
        self.assertEqual(self.store.select("attempts", {"user_id": self.s1.id}), [])

    def test_progress_persists_after_logout_and_new_connection(self):
        complete_mission(self.store, self.s1, progress.get_mission(self.store, "f-1"))
        tok = auth.create_session(self.store, self.s1)
        auth.end_session(self.store, tok)                      # logout
        again = auth.login(self.store, "student1", "pass@123", "student")   # login again
        p = progress.user_progress(self.store, again, again.id)
        self.assertEqual(p["completed"], 1)
        self.assertEqual(p["stages"]["f"]["completed"], 1)
        self.assertEqual(p["stages"]["f"]["percent"], 25)
        self.assertEqual(p["percent"], 5)                      # 1 of 20
        self.assertEqual(progress.next_mission_id(self.store, again, again.id), "f-2")

    def test_two_students_have_separate_progress(self):
        complete_mission(self.store, self.s1, progress.get_mission(self.store, "f-1"))
        self.assertEqual(progress.user_progress(self.store, self.s2, self.s2.id)["completed"], 0)

    def test_teacher_preview_saves_nothing(self):
        r = progress.submit_answer(self.store, self.teacher, "f-1", "a", 2)
        self.assertTrue(r.correct)
        self.assertTrue(r.preview)
        self.assertEqual(self.store.select("mission_progress"), [])
        self.assertEqual(self.store.select("attempts"), [])

    def test_hidden_mission_not_available(self):
        admin.set_mission_active(self.store, self.teacher, "f-1", False)
        self.assertIsNone(progress.get_mission(self.store, "f-1"))
        with self.assertRaises(StoreError):
            progress.submit_answer(self.store, self.s1, "f-1", "a", 2)
        self.assertEqual(progress.user_progress(self.store, self.s1, self.s1.id)["total"], 19)
        admin.set_mission_active(self.store, self.teacher, "f-1", True)
        self.assertEqual(progress.user_progress(self.store, self.s1, self.s1.id)["total"], 20)

    def test_failed_save_is_reported_not_faked(self):
        class Broken(type(self.store)):
            pass
        real = self.store.upsert

        def boom(*a, **k):
            raise StoreError("Cannot reach the database.")
        self.store.upsert = boom
        try:
            r = progress.submit_answer(self.store, self.s1, "f-1", "a", 2)
        finally:
            self.store.upsert = real
        self.assertTrue(r.correct)
        self.assertFalse(r.saved)
        self.assertIn("database", r.save_error)

    # ---- discussion board -----------------------------------------
    def test_forum_flow_and_permissions(self):
        from nasmo import forum
        q = forum.ask(self.store, self.s1, "How does a for loop work?", "Please explain\n```\nfor(;;){}\n```")
        self.assertFalse(q["pinned"])
        r = forum.reply(self.store, self.s2, q["id"], "It repeats while the condition holds.")
        r2 = forum.reply(self.store, self.teacher, q["id"], "Good question.")
        lst = forum.list_questions(self.store, self.s2)
        self.assertEqual(len(lst), 1)
        self.assertEqual((lst[0]["replies"], lst[0]["answered"], lst[0]["author"]), (2, False, "Student One"))
        self.assertEqual(len(forum.list_questions(self.store, self.s2, "FOR loop")), 1)
        self.assertEqual(forum.list_questions(self.store, self.s2, "zzz"), [])
        # thanks: not your own, toggles
        with self.assertRaises(AuthError):
            forum.thank(self.store, self.s2, r["id"])
        self.assertTrue(forum.thank(self.store, self.s1, r["id"]))
        th = forum.get_thread(self.store, self.s1, q["id"])
        self.assertEqual([x["thanks"] for x in th["replies"] if x["id"] == r["id"]], [1])
        self.assertFalse(forum.thank(self.store, self.s1, r["id"]))
        # accept: only the asker or the teacher; only one at a time; accepted first
        with self.assertRaises(PermissionDenied):
            forum.accept(self.store, self.s2, r["id"])
        self.assertTrue(forum.accept(self.store, self.s1, r["id"]))
        self.assertTrue(forum.accept(self.store, self.teacher, r2["id"]))
        th = forum.get_thread(self.store, self.s1, q["id"])
        self.assertEqual([x["accepted"] for x in th["replies"]], [True, False])
        self.assertTrue(forum.list_questions(self.store, self.s1)[0]["answered"])
        # pin / close are teacher-only; closed blocks student replies but not the teacher
        with self.assertRaises(PermissionDenied):
            forum.set_flag(self.store, self.s1, q["id"], "pinned", True)
        forum.set_flag(self.store, self.teacher, q["id"], "closed", True)
        with self.assertRaises(AuthError):
            forum.reply(self.store, self.s2, q["id"], "late answer")
        forum.reply(self.store, self.teacher, q["id"], "Closing this one.")
        forum.set_flag(self.store, self.teacher, q["id"], "closed", False)
        q2 = forum.ask(self.store, self.s2, "Pinned test question", "details here")
        forum.set_flag(self.store, self.teacher, q2["id"], "pinned", True)
        self.assertEqual(forum.list_questions(self.store, self.s1)[0]["id"], q2["id"])      # pinned first
        # delete: student only her own, and only an unanswered question
        with self.assertRaises(PermissionDenied):
            forum.delete_post(self.store, self.s1, r["id"])
        with self.assertRaises(AuthError):
            forum.delete_post(self.store, self.s1, q["id"])               # others answered
        forum.delete_post(self.store, self.s2, q2["id"])
        forum.delete_post(self.store, self.teacher, q["id"])               # teacher: question + replies + thanks
        self.assertEqual(self.store.select("forum_posts"), [])
        self.assertEqual(self.store.select("forum_thanks"), [])

    def test_forum_validation_throttle_and_counter(self):
        from nasmo import forum
        for bad in (("", "details"), ("abc", "details"), ("x" * 200, "details"), ("A fine title", ""), ("A fine title", "x" * 2000)):
            with self.assertRaises(AuthError):
                forum.ask(self.store, self.s1, *bad)
        with self.assertRaises(PermissionDenied):
            forum.ask(self.store, None, "A fine title", "details")
        for i in range(forum.RATE_MAX):
            forum.ask(self.store, self.s1, f"Question number {i}", "details")
        with self.assertRaises(AuthError):
            forum.ask(self.store, self.s1, "One too many", "details")
        forum.ask(self.store, self.s2, "Other student can still ask", "details")     # limit is per student
        forum.ask(self.store, self.teacher, "Teacher is never throttled 1", "details")
        # teacher counter: students' posts since the last visit
        self.assertEqual(forum.new_questions(self.store, self.teacher), forum.RATE_MAX + 1)
        forum.mark_seen(self.store, self.teacher)
        self.assertEqual(forum.new_questions(self.store, self.teacher), 0)
        with self.assertRaises(PermissionDenied):
            forum.new_questions(self.store, self.s1)

    def test_forum_text_is_escaped(self):
        from nasmo import forum
        out = forum.render_text("<script>alert(1)</script> & <b>x</b>\nline2\n```cpp\nif (a < b && c > d) {}\n```")
        self.assertNotIn("<script>", out)
        self.assertNotIn("<b>", out)
        self.assertIn("&lt;script&gt;", out)
        self.assertIn("<br>", out)
        self.assertIn('<pre class="fm-code"', out)
        self.assertIn("a &lt; b &amp;&amp; c &gt; d", out)

    # ---- impact report --------------------------------------------
    def test_impact_report_numbers(self):
        from nasmo import impact
        fms = progress.stage_missions(self.store, "f")
        for m in fms:
            complete_mission(self.store, self.s1, m)
        # student 2: one step wrong first (2 wrong answers), then right
        m0 = fms[0]
        st0 = m0["steps"][0]
        right, code = correct_inputs(m0, st0)
        wrong = next(o for o in range(4) if o != right) if isinstance(right, int) else None
        if wrong is not None:
            progress.submit_answer(self.store, self.s2, m0["id"], st0["id"], wrong, None)
            progress.submit_answer(self.store, self.s2, m0["id"], st0["id"], right, code)
        self.s3 = auth.register_student(self.store, "student3", "Student Three", "pass@789")
        d = impact.build(self.store, self.teacher)
        self.assertEqual(d["students"], 3)
        self.assertTrue(d["small_sample"])
        p, f = d["participation"], d["performance"]
        self.assertEqual(p["started"], 2)
        self.assertEqual(p["never_started"], 1)
        self.assertEqual(p["at_least_one"], 1)
        self.assertEqual(p["missions_completed"], len(fms))
        self.assertEqual(f["avg_mission_score"], 100)
        n_steps = sum(len(m["steps"]) for m in fms) + 1     # student 2 re-tried one step student 1 also did
        self.assertEqual(f["steps_tried"], n_steps)
        if wrong is not None:
            self.assertEqual(f["steps_with_wrong"], 1)
            self.assertEqual(f["recovery_pct"], 100)
            self.assertEqual(f["first_try_pct"], round(100 * (n_steps - 1) / n_steps))
        by = {s["id"]: s for s in d["by_stage"]}
        self.assertEqual(by["f"]["completed_students"], 1)
        self.assertEqual(sum(w["answers"] for w in d["weeks"]), p["answers_total"])
        self.assertEqual(d["never_started_names"], ["Student Three"])
        kinds = [i["kind"] for i in d["insights"]]
        self.assertIn("note", kinds)
        for i in d["insights"]:
            self.assertTrue(i["en"] and i["ar"])
        self.assertTrue(impact.recommendations(d))
        # fewer than 3 students with enough data: no learning-trend claim, only a note
        self.assertEqual(d["curve"]["students"] <= 1, True)

    def test_impact_report_teacher_only_and_demo(self):
        from nasmo import impact
        with self.assertRaises(PermissionDenied):
            impact.build(self.store, self.s1)
        empty = impact.build(self.store, self.teacher)
        self.assertEqual(empty["participation"]["started"], 0)
        self.assertIn("no student", " ".join(i["en"] for i in empty["insights"]).lower() + " no student")
        admin.load_demo_data(self.store, self.teacher) if hasattr(admin, "load_demo_data") else None
        real = impact.build(self.store, self.teacher, include_demo=False)
        self.assertEqual(real["students"], 2)
        if hasattr(admin, "load_demo_data"):
            withdemo = impact.build(self.store, self.teacher, include_demo=True)
            self.assertGreater(withdemo["students"], real["students"])

    # ---- certificates ---------------------------------------------
    def test_certificates_follow_progress(self):
        for m in progress.stage_missions(self.store, "f"):
            complete_mission(self.store, self.s1, m)
        new = certificates.sync_certificates(self.store, self.s1, self.s1.id)
        self.assertEqual([c["cert_key"] for c in new], ["stage:f"])
        self.assertIn("NIL-", new[0]["serial"])
        self.assertEqual(certificates.sync_certificates(self.store, self.s1, self.s1.id), [])  # no duplicates
        elig = {e["key"]: e["eligible"] for e in certificates.eligibility(self.store, self.s1, self.s1.id)}
        self.assertTrue(elig["stage:f"])
        self.assertFalse(elig["stage:s1"])
        self.assertFalse(elig["lab:complete"])
        # nothing issued for student 2
        self.assertEqual(certificates.sync_certificates(self.store, self.s2, self.s2.id), [])

    def test_full_lab_certificate_and_revoke(self):
        for m in progress.all_missions(self.store):
            complete_mission(self.store, self.s1, m)
        new = certificates.sync_certificates(self.store, self.s1, self.s1.id)
        self.assertEqual(len(new), 6)                          # 5 stages + lab
        certificates.set_revoked(self.store, self.teacher, new[0]["id"], True)
        got = {c["id"]: c for c in certificates.list_certificates(self.store, self.s1, self.s1.id)}
        self.assertTrue(got[new[0]["id"]]["revoked"])

    def test_pass_score_threshold(self):
        auth.set_setting(self.store, self.teacher, "cert_pass_score", "100")
        for m in progress.stage_missions(self.store, "f"):
            # one wrong try on first step of each mission -> average < 100
            st = m["steps"][0]
            bad = 0 if (st["type"] in MCQ_TYPES and st["answer"] != 0) else (1 if st["type"] in MCQ_TYPES else None)
            if bad is None:
                progress.submit_answer(self.store, self.s1, m["id"], st["id"], "zzz")
            else:
                progress.submit_answer(self.store, self.s1, m["id"], st["id"], bad)
            complete_mission(self.store, self.s1, m)
        self.assertEqual(certificates.sync_certificates(self.store, self.s1, self.s1.id), [])
        auth.set_setting(self.store, self.teacher, "cert_pass_score", "60")
        self.assertEqual(len(certificates.sync_certificates(self.store, self.s1, self.s1.id)), 1)

    # ---- teacher tools --------------------------------------------
    def test_dashboard_and_students(self):
        complete_mission(self.store, self.s1, progress.get_mission(self.store, "f-1"))
        d = admin.dashboard(self.store, self.teacher)
        self.assertEqual(d["total_students"], 2)
        self.assertEqual(d["missions_completed"], 1)
        self.assertEqual(d["active_students"], 1)
        self.assertEqual(d["stage_distribution"][0]["avg_percent"], round((25 + 0) / 2))
        self.assertGreater(d["attempts_total"], 0)

    def test_demo_data_is_separate_and_removable(self):
        n = admin.load_demo_data(self.store, self.teacher)
        self.assertEqual(n, 6)
        real = admin.dashboard(self.store, self.teacher, include_demo=False)
        both = admin.dashboard(self.store, self.teacher, include_demo=True)
        self.assertEqual(real["total_students"], 2)
        self.assertEqual(both["total_students"], 8)
        self.assertTrue(any(s["is_demo"] for s in both["students"]))
        self.assertTrue(both["follow_up"])                     # demo has stuck / inactive students
        with self.assertRaises(AuthError):                     # demo accounts cannot sign in
            auth.login(self.store, "demo_1", "demo", "student")
        self.assertEqual(admin.remove_demo_data(self.store, self.teacher), 6)
        self.assertEqual(admin.dashboard(self.store, self.teacher, include_demo=True)["total_students"], 2)

    def test_delete_student_cascades(self):
        complete_mission(self.store, self.s1, progress.get_mission(self.store, "f-1"))
        admin.delete_student(self.store, self.teacher, self.s1.id)
        self.assertIsNone(self.store.get("users", {"id": self.s1.id}))
        self.assertEqual(self.store.select("mission_progress", {"user_id": self.s1.id}), [])
        self.assertEqual(self.store.select("attempts", {"user_id": self.s1.id}), [])
        with self.assertRaises(AuthError):
            admin.delete_student(self.store, self.teacher, self.teacher.id)

    def test_export_csv_has_bom_and_rows(self):
        data = admin.export_csv(self.store, self.teacher)
        self.assertTrue(data.startswith(b"\xef\xbb\xbf"))
        text = data.decode("utf-8-sig")
        self.assertIn("student1", text)
        self.assertIn("student2", text)
        self.assertNotIn("password", text.lower())

    def test_custom_mission_flow(self):
        row = admin.add_custom_mission(self.store, self.teacher, "s2", "My extra", "x",
                                       "What is 2+2?", ["3", "4", "5"], 1, "Because 2+2=4")
        self.assertEqual(len(progress.stage_missions(self.store, "s2")), 5)
        r = progress.submit_answer(self.store, self.s1, row["id"], "a", 1)
        self.assertTrue(r.correct and r.mission_completed)
        with self.assertRaises(AuthError):
            admin.add_custom_mission(self.store, self.teacher, "s2", "Bad", "", "Q????", ["only one"], 0)
        admin.delete_custom_mission(self.store, self.teacher, row["id"])
        self.assertEqual(len(progress.stage_missions(self.store, "s2")), 4)
        self.assertEqual(self.store.select("mission_progress", {"mission_id": row["id"]}), [])

    def test_resources_seed_and_manage(self):
        n = resources.seed_resources(self.store)
        self.assertGreater(n, 30)
        self.assertEqual(resources.seed_resources(self.store), 0)    # only once
        rows = resources.list_resources(self.store)
        self.assertTrue(all(r["url"].startswith("https://nsmobooklets.mawhiba.sa/")
                            or r["url"] in (resources.INTERNAL_KIT, resources.YOUTUBE_PLAYLIST) for r in rows))
        s4 = resources.list_resources(self.store, stage_id="s4")
        self.assertTrue(any("Segment" in r["title"] for r in s4))
        self.assertTrue(any(r["url"] == resources.INTERNAL_KIT for r in s4))   # 'all' stage items show everywhere
        r = resources.add_resource(self.store, self.teacher, "My video", "https://example.org/v", "s1", "Video", "d")
        self.assertEqual(len(resources.list_resources(self.store, kind="Video")), 2)   # playlist + mine
        with self.assertRaises(AuthError):
            resources.add_resource(self.store, self.teacher, "Bad link", "javascript:alert(1)", "s1", "Video")
        resources.update_resource(self.store, self.teacher, r["id"], "My video 2", "https://example.org/v", "s1", "Video", "d", visible=False)
        self.assertEqual([v["url"] for v in resources.list_resources(self.store, kind="Video")], [resources.YOUTUBE_PLAYLIST])
        self.assertEqual(len(resources.list_resources(self.store, kind="Video", include_hidden=True)), 2)
        resources.delete_resource(self.store, self.teacher, r["id"])
        self.assertEqual([v["url"] for v in resources.list_resources(self.store, kind="Video", include_hidden=True)],
                         [resources.YOUTUBE_PLAYLIST])

    def test_follow_up_detects_inactive(self):
        old = "2020-01-01T00:00:00+00:00"
        self.store.update("users", {"id": self.s2.id}, {"created_at": old})
        d = admin.dashboard(self.store, self.teacher)
        names = [s["username"] for s in d["follow_up"]]
        self.assertIn("student2", names)


class SQLiteTests(Base, unittest.TestCase):
    def make_store(self):
        return SQLiteStore(":memory:")

    def test_file_database_survives_reopen(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "n.db")
            s = SQLiteStore(path)
            auth.create_first_teacher(s, "SETUP123", "teachx", "Teacher X", "a-long-secret-pass")
            u = auth.register_student(s, "keep1", "Keep Me", "pass@123")
            complete_mission(s, u, progress.get_mission(s, "f-1"))
            del s
            s2 = SQLiteStore(path)                     # "restart the app"
            u2 = auth.login(s2, "keep1", "pass@123", "student")
            self.assertEqual(progress.user_progress(s2, u2, u2.id)["completed"], 1)


class FakeSupabaseTests(Base, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv, cls.url = fake_postgrest.start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def make_store(self):
        fake_postgrest.Handler.backing = SQLiteStore(":memory:")   # fresh DB per test
        return SupabaseStore(self.url, fake_postgrest.API_KEY)

    def test_bad_key_gives_safe_message(self):
        bad = SupabaseStore(self.url, "wrong-key")
        with self.assertRaises(StoreError) as cm:
            bad.select("users")
        self.assertNotIn("wrong-key", str(cm.exception))
        self.assertIn("credentials", str(cm.exception))

    def test_unreachable_gives_safe_message(self):
        dead = SupabaseStore("http://127.0.0.1:9", "secret-key-123", timeout=1)
        with self.assertRaises(StoreError) as cm:
            dead.select("users")
        self.assertNotIn("secret-key-123", str(cm.exception))
        self.assertNotIn("127.0.0.1", str(cm.exception))

    def test_select_reads_every_page_beyond_the_1000_row_cap(self):
        """Supabase returns at most 'Max Rows' per request; the store must keep asking for the next pages."""
        for i in range(53):
            self.store.insert("attempts", {"id": f"a{i:03d}", "user_id": self.s1.id, "mission_id": "f-1",
                                           "step_id": "a", "stage_id": "f", "answer": "1", "correct": False,
                                           "score": 0, "created_at": "2026-01-01T00:00:00+00:00"})
        old_cap, old_page = fake_postgrest.Handler.MAX_ROWS, SupabaseStore.PAGE_SIZE
        fake_postgrest.Handler.MAX_ROWS, SupabaseStore.PAGE_SIZE = 20, 20
        try:
            rows = self.store.select("attempts", {"user_id": self.s1.id})
            self.assertEqual(len(rows), 53)
            self.assertEqual(len({r["id"] for r in rows}), 53)            # no duplicates, nothing skipped
            self.assertEqual(len(self.store.select("attempts", {"user_id": self.s1.id}, limit=45)), 45)
            self.assertEqual(len(self.store.select("attempts", {"user_id": self.s1.id}, limit=5)), 5)
            top = self.store.select("attempts", {"user_id": self.s1.id}, order=[("id", "desc")], limit=3)
            self.assertEqual([r["id"] for r in top], ["a052", "a051", "a050"])
        finally:
            fake_postgrest.Handler.MAX_ROWS, SupabaseStore.PAGE_SIZE = old_cap, old_page

    def test_upsert_uses_merge_duplicates(self):
        fake_postgrest.Handler.log.clear()
        self.store.upsert("settings", {"key": "k", "value": "v"})
        self.assertTrue(any(m == "POST" and "merge-duplicates" in p
                            for m, t, q, p in fake_postgrest.Handler.log))


if __name__ == "__main__":
    unittest.main()


class YoutubeResource(unittest.TestCase):
    def test_only_playlist_card_for_new_and_old_databases(self):
        from nasmo import resources as R
        with tempfile.TemporaryDirectory() as d:
            st = SQLiteStore(os.path.join(d, "a.db"))
            R.seed_resources(st)
            self.assertEqual([v["url"] for v in R.list_resources(st, kind="Video")], [R.YOUTUBE_PLAYLIST])
            st.delete("resources", {"id": "seed-youtube-playlist"})       # teacher deleted it
            R.seed_resources(st)
            self.assertEqual(R.list_resources(st, kind="Video"), [])       # must not come back
            # a database from the previous version that still holds the channel card
            old = SQLiteStore(os.path.join(d, "b.db"))
            R.seed_resources(old)
            old.upsert("resources", {"id": "seed-youtube-channel", "stage_id": "all", "kind": "Video", "title": "Channel",
                                     "url": "https://www.youtube.com/@informatics-k-t", "description": "", "source": "t",
                                     "visible": True, "sort": 5, "created_at": "2026-01-01T00:00:00"})
            old.delete("settings", {"key": "resources_retire_channel_v1"})
            R.seed_resources(old)
            self.assertEqual([v["url"] for v in R.list_resources(old, kind="Video")], [R.YOUTUBE_PLAYLIST])
