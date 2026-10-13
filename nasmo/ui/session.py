"""Streamlit session helpers: store, signed-in user, navigation, theme."""
from __future__ import annotations

from .sx import st

from .. import auth, config
from ..resources import seed_resources
from ..store import SQLiteStore, Store, StoreError, SupabaseStore

STUDENT_PAGES = {"home", "trophies", "progress", "certificates", "resources", "about", "stage", "stages", "mission", "account", "forum"}
TEACHER_PAGES = {"home", "stages", "t_dashboard", "t_students", "t_reports", "t_impact", "t_content", "t_certs",
                 "resources", "t_settings", "about", "stage", "stages", "mission", "account", "forum"}
PUBLIC_PAGES = {"home", "student_login", "teacher_login", "resources", "about", "stage"}


# ------------------------------------------------------------------ store
@st.cache_resource(show_spinner=False)
def _open_store() -> tuple[Store | None, str, str]:
    """Returns (store, mode, error). Never falls back silently from Supabase
    to the local file - that would split the data in two places."""
    sb = config.supabase_settings()
    try:
        if sb:
            store: Store = SupabaseStore(*sb)
            mode = "supabase"
        else:
            config.DATA_DIR.mkdir(parents=True, exist_ok=True)
            print(f"[Nasmo] Data folder: {config.DATA_DIR}", flush=True)
            store = SQLiteStore(config.DATA_DIR / "nasmo.db")
            mode = "local"
        store.ping()
        seed_resources(store)
        auth.purge_expired_sessions(store)
        return store, mode, ""
    except StoreError as e:
        hint = ""
        if sb:
            hint = ("Check SUPABASE_URL and SUPABASE_SERVICE_KEY, and that supabase_schema.sql "
                    "was run in the Supabase SQL editor.")
        return None, "supabase" if sb else "local", f"{e} {hint}".strip()
    except Exception as e:  # pragma: no cover - defensive
        return None, "local", f"Could not open the database ({type(e).__name__})."


def get_store() -> tuple[Store | None, str, str]:
    return _open_store()


def retry_store() -> None:
    _open_store.clear()


# ------------------------------------------------------------------- user
def current_user() -> auth.User | None:
    return st.session_state.get("user")


def init_state() -> None:
    ss = st.session_state
    ss.setdefault("page", "home")
    ss.setdefault("params", {})
    ss.setdefault("theme", "dark")
    ss.setdefault("user", None)
    ss.setdefault("token", None)
    if "lang" not in ss:
        try:
            q = st.query_params.get("l")
        except Exception:
            q = None
        ss["lang"] = q if q in ("ar", "en") else "en"


def resume_from_url(store: Store) -> None:
    """Restore the sign-in after a browser refresh (token kept in the URL)."""
    ss = st.session_state
    if ss.get("user") is not None:
        return
    token = st.query_params.get("s")
    if token:
        user = auth.resume_session(store, token)
        if user:
            ss["user"], ss["token"] = user, token
        else:
            _drop_query("s")
    t = st.query_params.get("t")
    if t in ("light", "dark") and "theme_set" not in ss:
        ss["theme"] = t


def _drop_query(key: str) -> None:
    try:
        if key in st.query_params:
            del st.query_params[key]
    except Exception:
        pass


def sign_in(store: Store, user: auth.User) -> None:
    ss = st.session_state
    token = auth.create_session(store, user)
    ss["user"], ss["token"] = user, token
    st.query_params["s"] = token
    ss["page"] = "t_dashboard" if user.is_teacher else "home"
    ss["params"] = {}


def sign_out(store: Store | None) -> None:
    ss = st.session_state
    if store is not None:
        auth.end_session(store, ss.get("token"))
    for k in [k for k in ss.keys() if k.startswith(("m_", "res_", "ans_"))]:
        del ss[k]
    ss["user"], ss["token"] = None, None
    ss["page"], ss["params"] = "home", {}
    _drop_query("s")


# -------------------------------------------------------------- navigation
def go(page: str, **params) -> None:
    st.session_state["page"] = page
    st.session_state["params"] = params


def toggle_theme() -> None:
    ss = st.session_state
    ss["theme"] = "dark" if ss.get("theme") != "dark" else "light"
    ss["theme_set"] = True
    st.query_params["t"] = ss["theme"]


def toggle_lang() -> None:
    ss = st.session_state
    ss["lang"] = "en" if ss.get("lang") == "ar" else "ar"
    try:
        st.query_params["l"] = ss["lang"]
    except Exception:
        pass


def allowed(page: str, user: auth.User | None) -> bool:
    if user is None:
        return page in PUBLIC_PAGES
    return page in (TEACHER_PAGES if user.is_teacher else STUDENT_PAGES)
