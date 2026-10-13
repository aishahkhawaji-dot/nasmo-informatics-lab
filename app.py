"""Nasmo Informatics Lab - Streamlit entry point.  Run:  streamlit run app.py"""
from __future__ import annotations

from nasmo.ui.sx import st

from nasmo import config

st.set_page_config(page_title=config.APP_NAME, page_icon=str(config.ASSETS_DIR / "nasmo_logo_420.png"),
                   layout="wide", initial_sidebar_state="auto")

from nasmo.pages import forum_page, public, student, teacher  # noqa: E402
from nasmo.ui import layout as L  # noqa: E402
from nasmo.ui import session as S  # noqa: E402

ROUTES = {
    "home": public.home, "stages": public.stages_page, "stage": public.stage_page, "student_login": public.student_login,
    "teacher_login": public.teacher_login, "about": public.about, "resources": public.resources,
    "mission": student.mission_page, "progress": student.progress_page, "trophies": student.trophies_page,
    "certificates": student.certificates_page, "account": student.account_page, "forum": forum_page.page,
    "t_dashboard": teacher.dashboard, "t_students": teacher.students, "t_reports": teacher.reports,
    "t_impact": teacher.impact_page, "t_content": teacher.content, "t_certs": teacher.certificates, "t_settings": teacher.settings,
}


def main() -> None:
    S.init_state()
    L.inject_css()
    store, mode, error = S.get_store()
    if store is None:
        L.header()
        with st.container(key="pagepad"):
            L.page_title("The database is not reachable")
            L.note("bad", error)
            st.button("Try again", key="retry_db", on_click=S.retry_store, type="primary")
        return
    S.resume_from_url(store)
    user = S.current_user()
    ss = st.session_state
    page = ss.get("page", "home")
    if not S.allowed(page, user):
        if user is None and page in ("stages", "mission", "progress", "certificates", "account"):
            page = "student_login"
        elif user is None and page.startswith("t_"):
            page = "teacher_login"
        else:
            page = "t_dashboard" if (user and user.is_teacher) else "home"
        ss["page"] = page
    L.sidebar(store, mode)
    # (no bottom tab bar: the sidebar - opened with the round menu button on phones - is the only navigation)
    try:
        ROUTES.get(page, public.home)(store)
    except Exception as e:  # last resort: never show a raw traceback to students
        if type(e).__name__ in ("RerunException", "StopException", "RerunData"):
            raise
        if config.get_setting("NASMO_RAISE") == "1":   # used by the smoke tests
            raise
        L.header()
        with st.container(key="errpad"):
            L.note("bad", f"Something went wrong on this page ({type(e).__name__}). "
                          "Go back to Home and try again; if it repeats, tell your teacher.")
            st.button("Home", key="err_home", on_click=S.go, args=("home",))
        if config.get_setting("NASMO_DEBUG") == "1":
            st.exception(e)

    L.fit_sidebar()


main()
