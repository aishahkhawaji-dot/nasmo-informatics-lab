"""Central configuration. Secrets come from environment variables or
.streamlit/secrets.toml - never from source code."""
from __future__ import annotations

import os
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _default_data_dir() -> Path:
    """Keep the local database OUTSIDE the project folder, so unzipping a new version of the app
    never starts from an empty database (that made the teacher register again every time).
    An older data\\nasmo.db inside the project folder is still used if it exists."""
    legacy = ROOT / "data"
    if (legacy / "nasmo.db").exists():
        return legacy
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(base) / "NasmoLab"


DATA_DIR = Path(os.environ.get("NASMO_DATA_DIR") or _default_data_dir())
ASSETS_DIR = ROOT / "assets"
KIT_FILE = ROOT / "interactive_kit" / "Nasmo_Informatics_Interactive_Guide.html"

APP_NAME = "Nasmo Informatics Lab"
APP_NAME_AR = "نسمو معلوماتيًا"
TAGLINE_AR = "نفكّر .. نبرمج .. ننافس"
TEACHER_CREDIT_AR = "عائشة علي خواجي"
SCHOOL_AR = "ثانوية الموهوبات التقنية - بنات"

SESSION_HOURS = 8
STUDENT_MIN_PASSWORD = 6
TEACHER_MIN_PASSWORD = 10


def get_setting(name: str, default: str | None = None) -> str | None:
    """Environment variable first, then Streamlit secrets (optional)."""
    val = os.environ.get(name)
    if val:
        return val
    try:  # st.secrets raises if no secrets file exists
        import streamlit as st  # type: ignore

        if name in st.secrets:
            v = st.secrets[name]
            return str(v) if v else default
    except Exception:
        pass
    return default


def supabase_settings() -> tuple[str, str] | None:
    url = get_setting("SUPABASE_URL")
    key = get_setting("SUPABASE_SERVICE_KEY")
    if url and key:
        return url.rstrip("/"), key
    return None


def setup_code_required() -> bool:
    """A setup code protects the very first teacher account only when the app may be reachable by
    others (Supabase / hosted) or when the owner set NASMO_SETUP_CODE. On a private local computer
    the first teacher just chooses a username and password."""
    return bool(supabase_settings() or get_setting("NASMO_SETUP_CODE"))


def setup_code() -> str:
    """Code the first teacher must type to create the teacher account.

    Taken from NASMO_SETUP_CODE if set; otherwise generated once and saved in
    data/setup_code.txt (also printed in the console window)."""
    env = get_setting("NASMO_SETUP_CODE")
    if env:
        return env
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    f = DATA_DIR / "setup_code.txt"
    if f.exists():
        code = f.read_text(encoding="utf-8").strip()
        if code:
            return code
    code = secrets.token_hex(4).upper()
    f.write_text(code + "\n", encoding="utf-8")
    return code
