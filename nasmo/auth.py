"""Accounts, passwords, sessions and role checks.

Roles: "student" and "teacher". Every function that returns or changes data
that belongs to someone else takes an `actor` (the logged-in User) and checks
the role here - hiding a button in the UI is never the only protection.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import re
import secrets
import threading
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone

from . import config
from .store import DuplicateError, Store, StoreError, parse_ts, utcnow

PBKDF2_ITERATIONS = 240_000
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.\-]{3,32}$")
NAME_EN_RE = re.compile(r"^[A-Za-z][A-Za-z .'\-]{1,59}$")
PASSWORD_SYMBOLS = "@#$%&*_-.!?"      # the only symbols a student password may use


def check_student_password(pw: str) -> None:
    """New student passwords: 6+ characters, English letters, at least one symbol from PASSWORD_SYMBOLS."""
    pw = pw or ""
    if len(pw) < config.STUDENT_MIN_PASSWORD:
        raise AuthError(f"Password must be at least {config.STUDENT_MIN_PASSWORD} characters.")
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789" + PASSWORD_SYMBOLS)
    if any(c not in allowed for c in pw):
        raise AuthError("Password can only use English letters, digits and these symbols: "
                        + " ".join(PASSWORD_SYMBOLS))
    if not any(c.isalpha() for c in pw):
        raise AuthError("Password must contain English letters.")
    if not any(c in PASSWORD_SYMBOLS for c in pw):
        raise AuthError("Password must contain at least one symbol: " + " ".join(PASSWORD_SYMBOLS))
MAX_FAILS = 5
LOCK_SECONDS = 300


class AuthError(Exception):
    """Message is safe to show to the user."""


class PermissionDenied(Exception):
    pass


@dataclass(frozen=True)
class User:
    id: str
    username: str
    display_name: str
    role: str
    active: bool = True
    is_demo: bool = False

    @property
    def is_teacher(self) -> bool:
        return self.role == "teacher"

    @property
    def is_student(self) -> bool:
        return self.role == "student"

    def public(self) -> dict:
        return asdict(self)


def _user_from_row(row: dict) -> User:
    return User(id=row["id"], username=row["username"],
                display_name=row.get("display_name") or row["username"],
                role=row["role"], active=bool(row.get("active", True)),
                is_demo=bool(row.get("is_demo", False)))


def require_teacher(actor: User | None) -> User:
    if actor is None or not actor.is_teacher or not actor.active:
        raise PermissionDenied("Teacher permission required.")
    return actor


def require_self_or_teacher(actor: User | None, user_id: str) -> User:
    if actor is None or not actor.active:
        raise PermissionDenied("Please sign in.")
    if actor.is_teacher or actor.id == user_id:
        return actor
    raise PermissionDenied("You can only view your own data.")


# ---------------------------------------------------------------- passwords
def hash_password(password: str, iterations: int = PBKDF2_ITERATIONS) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return "pbkdf2_sha256${}${}${}".format(
        iterations, base64.b64encode(salt).decode(), base64.b64encode(dk).decode())


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, it, salt_b64, dk_b64 = stored.split("$")
        if scheme != "pbkdf2_sha256":
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(dk_b64)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(it))
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False


_DUMMY_HASH = hash_password("not-a-real-password", iterations=PBKDF2_ITERATIONS)


def _unusable_password() -> str:
    """Hash of a random secret nobody knows (used for demo accounts)."""
    return hash_password(secrets.token_urlsafe(24))


# ---------------------------------------------------------- brute-force guard
_fail_lock = threading.Lock()
_fails: dict[str, list[float]] = {}


def _check_locked(key: str) -> None:
    now = time.time()
    with _fail_lock:
        recent = [t for t in _fails.get(key, []) if now - t < LOCK_SECONDS]
        _fails[key] = recent
        if len(recent) >= MAX_FAILS:
            wait = int(LOCK_SECONDS - (now - recent[0]))
            raise AuthError(f"Too many failed attempts. Try again in {max(wait, 1)} seconds.")


def _record_fail(key: str) -> None:
    with _fail_lock:
        _fails.setdefault(key, []).append(time.time())


def _clear_fails(key: str) -> None:
    with _fail_lock:
        _fails.pop(key, None)


def reset_lockouts() -> None:  # used by tests
    with _fail_lock:
        _fails.clear()


# ------------------------------------------------------------------ settings
DEFAULT_SETTINGS = {
    "registration_open": "1",
    "cert_pass_score": "60",       # minimum average score to earn a certificate
    "inactive_days": "7",          # "needs follow-up" threshold
}


def get_setting(store: Store, key: str) -> str:
    row = store.get("settings", {"key": key})
    if row and row.get("value") is not None:
        return row["value"]
    return DEFAULT_SETTINGS.get(key, "")


def set_setting(store: Store, actor: User, key: str, value: str) -> None:
    require_teacher(actor)
    if key not in DEFAULT_SETTINGS:
        raise AuthError("Unknown setting.")
    store.upsert("settings", {"key": key, "value": str(value)})


# ----------------------------------------------------------------- accounts
def _validate_new_account(username: str, display_name: str, password: str, min_pw: int):
    username = (username or "").strip()
    display_name = (display_name or "").strip()
    if not USERNAME_RE.match(username):
        raise AuthError("Username must be 3-32 characters: English letters, digits, "
                        "dot, dash or underscore.")
    if len(display_name) < 2 or len(display_name) > 60:
        raise AuthError("Please enter your name (2-60 characters).")
    if len(password or "") < min_pw:
        raise AuthError(f"Password must be at least {min_pw} characters.")
    return username.lower(), display_name


def _create_user(store: Store, role: str, username: str, display_name: str,
                 password_hash: str, is_demo: bool = False) -> User:
    row = {
        "id": str(uuid.uuid4()), "username": username, "display_name": display_name,
        "role": role, "password_hash": password_hash, "active": True,
        "is_demo": is_demo, "created_at": utcnow(), "last_login": None,
    }
    try:
        store.insert("users", row)
    except DuplicateError:
        raise AuthError("This username is already taken.") from None
    return _user_from_row(row)


def register_student(store: Store, username: str, display_name: str, password: str) -> User:
    if get_setting(store, "registration_open") != "1":
        raise AuthError("Student registration is closed. Ask your teacher for an account.")
    if not NAME_EN_RE.match((display_name or "").strip()):
        raise AuthError("Please write your name in English letters (A-Z).")
    check_student_password(password)
    username, display_name = _validate_new_account(
        username, display_name, password, config.STUDENT_MIN_PASSWORD)
    if store.get("users", {"username": username}):
        raise AuthError("This username is already taken.")
    return _create_user(store, "student", username, display_name, hash_password(password))


def teacher_exists(store: Store) -> bool:
    return bool(store.select("users", {"role": "teacher"}, limit=1))


def create_first_teacher(store: Store, setup_code: str, username: str,
                         display_name: str, password: str) -> User:
    if teacher_exists(store):
        raise AuthError("A teacher account already exists. Please sign in.")
    if config.setup_code_required() and not hmac.compare_digest(
            (setup_code or "").strip().encode(), config.setup_code().encode()):
        raise AuthError("Wrong setup code.")
    display_name = (display_name or "").strip() or (username or "").strip()
    username, display_name = _validate_new_account(
        username, display_name, password, config.TEACHER_MIN_PASSWORD)
    return _create_user(store, "teacher", username, display_name, hash_password(password))


def create_teacher(store: Store, actor: User, username: str, display_name: str,
                   password: str) -> User:
    require_teacher(actor)
    username, display_name = _validate_new_account(
        username, display_name, password, config.TEACHER_MIN_PASSWORD)
    return _create_user(store, "teacher", username, display_name, hash_password(password))


def create_student_by_teacher(store: Store, actor: User, username: str,
                              display_name: str, password: str) -> User:
    require_teacher(actor)
    username, display_name = _validate_new_account(
        username, display_name, password, config.STUDENT_MIN_PASSWORD)
    return _create_user(store, "student", username, display_name, hash_password(password))


def create_demo_user(store: Store, actor: User, username: str, display_name: str) -> User:
    """Demo students can never sign in (random unknown password)."""
    require_teacher(actor)
    return _create_user(store, "student", username, display_name,
                        _unusable_password(), is_demo=True)


def login(store: Store, username: str, password: str, role: str) -> User:
    """Sign in. `role` is the login page used - a student cannot sign in on
    the teacher page and vice versa."""
    if role not in ("student", "teacher"):
        raise AuthError("Invalid login type.")
    username = (username or "").strip().lower()
    key = f"{role}:{username}"
    _check_locked(key)
    row = store.get("users", {"username": username}) if username else None
    stored = row["password_hash"] if row else _DUMMY_HASH
    ok = verify_password(password or "", stored)
    if not (row and ok and row["role"] == role and row.get("active", True)):
        _record_fail(key)
        raise AuthError("Wrong username or password.")
    _clear_fails(key)
    store.update("users", {"id": row["id"]}, {"last_login": utcnow()})
    return _user_from_row(row)


def change_password(store: Store, actor: User, old: str, new: str) -> None:
    row = store.get("users", {"id": actor.id})
    if not row or not verify_password(old or "", row["password_hash"]):
        raise AuthError("Current password is wrong.")
    if actor.is_teacher:
        if len(new or "") < config.TEACHER_MIN_PASSWORD:
            raise AuthError(f"New password must be at least {config.TEACHER_MIN_PASSWORD} characters.")
    else:
        check_student_password(new)
    store.update("users", {"id": actor.id}, {"password_hash": hash_password(new)})


def update_display_name(store: Store, actor: User, new_name: str) -> User:
    new_name = (new_name or "").strip()
    if len(new_name) < 2 or len(new_name) > 60:
        raise AuthError("Please enter your name (2-60 characters).")
    store.update("users", {"id": actor.id}, {"display_name": new_name})
    return User(**{**actor.public(), "display_name": new_name})


def reset_student_password(store: Store, actor: User, student_id: str) -> str:
    """Teacher sets a new temporary password; shown once to the teacher."""
    require_teacher(actor)
    row = store.get("users", {"id": student_id})
    if not row or row["role"] != "student":
        raise AuthError("Student not found.")
    temp = secrets.token_urlsafe(6)
    store.update("users", {"id": student_id}, {"password_hash": hash_password(temp)})
    store.delete("sessions", {"user_id": student_id})
    store.delete("settings", {"key": _REQ_PREFIX + student_id})      # the request is answered
    return temp


# ------------------------------------------------- forgotten passwords
_REQ_PREFIX = "pwreq:"


def request_password_reset(store: Store, username: str) -> None:
    """A student who forgot her password asks her teacher for a new temporary one.
    If the username does not exist she is told so (so she can correct a typo)."""
    username = (username or "").strip().lower()
    key = f"request:{username}"
    _check_locked(key)
    _record_fail(key)                 # every request counts, so one name cannot be hammered
    if not username:
        raise AuthError("Please enter your username.")
    row = store.get("users", {"username": username})
    if not row or row["role"] != "student" or row.get("is_demo"):
        raise AuthError("This username does not exist. Check it and try again.")
    if not row.get("active", True):
        raise AuthError("This account is disabled. Ask your teacher.")
    store.upsert("settings", {"key": _REQ_PREFIX + row["id"], "value": utcnow()})


def list_reset_requests(store: Store, actor: User) -> list[dict]:
    """Students waiting for a temporary password, oldest first."""
    require_teacher(actor)
    out = []
    for r in store.select("settings"):
        k = str(r.get("key", ""))
        if k.startswith(_REQ_PREFIX):
            u = store.get("users", {"id": k[len(_REQ_PREFIX):]})
            if u and u["role"] == "student" and u.get("active", True):
                out.append({"user_id": u["id"], "username": u["username"],
                            "display_name": u["display_name"], "requested_at": r.get("value")})
            else:
                store.delete("settings", {"key": k})
    return sorted(out, key=lambda x: str(x["requested_at"]))


def dismiss_reset_request(store: Store, actor: User, student_id: str) -> None:
    require_teacher(actor)
    store.delete("settings", {"key": _REQ_PREFIX + student_id})


def list_teachers(store: Store, actor: User) -> list[dict]:
    require_teacher(actor)
    return [{"id": r["id"], "username": r["username"], "display_name": r["display_name"],
             "active": r.get("active", True)} for r in store.select("users", {"role": "teacher"})]


def reset_teacher_password(store: Store, actor: User, teacher_id: str) -> str:
    """One teacher gives another teacher a new temporary password (shown once)."""
    require_teacher(actor)
    if teacher_id == actor.id:
        raise AuthError("Use Account Settings to change your own password.")
    row = store.get("users", {"id": teacher_id})
    if not row or row["role"] != "teacher":
        raise AuthError("Teacher not found.")
    temp = secrets.token_urlsafe(9)
    store.update("users", {"id": teacher_id}, {"password_hash": hash_password(temp)})
    store.delete("sessions", {"user_id": teacher_id})
    return temp


def only_one_teacher(store: Store) -> bool:
    return len(store.select("users", {"role": "teacher"})) == 1


def recover_only_teacher(store: Store, code: str, new_password: str) -> str:
    """The lab has ONE teacher account and she forgot her password (or username).
    The owner of the computer / the server proves it with the setup code (NASMO_SETUP_CODE or the
    file setup_code.txt). Sets a new password and returns the username so she can sign in."""
    key = "recover:teacher"
    _check_locked(key)
    teachers = store.select("users", {"role": "teacher"})
    if len(teachers) != 1:
        raise AuthError("Recovery with the setup code works only when the lab has exactly one teacher account. "
                        "Ask another teacher to reset your password from Settings.")
    if not hmac.compare_digest((code or "").strip().encode(), config.setup_code().encode()):
        _record_fail(key)
        raise AuthError("Wrong setup code.")
    if len(new_password or "") < config.TEACHER_MIN_PASSWORD:
        raise AuthError(f"Password must be at least {config.TEACHER_MIN_PASSWORD} characters.")
    t = teachers[0]
    store.update("users", {"id": t["id"]}, {"password_hash": hash_password(new_password), "active": True})
    store.delete("sessions", {"user_id": t["id"]})
    _clear_fails(key)
    return t["username"]


def set_student_active(store: Store, actor: User, student_id: str, active: bool) -> None:
    require_teacher(actor)
    row = store.get("users", {"id": student_id})
    if not row or row["role"] != "student":
        raise AuthError("Student not found.")
    store.update("users", {"id": student_id}, {"active": bool(active)})
    if not active:
        store.delete("sessions", {"user_id": student_id})


# ----------------------------------------------------------------- sessions
def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_session(store: Store, user: User) -> str:
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    store.insert("sessions", {
        "token_hash": _hash_token(token), "user_id": user.id,
        "created_at": now.isoformat(timespec="seconds"),
        "expires_at": (now + timedelta(hours=config.SESSION_HOURS)).isoformat(timespec="seconds"),
    })
    return token


def resume_session(store: Store, token: str | None) -> User | None:
    if not token or len(token) > 200:
        return None
    row = store.get("sessions", {"token_hash": _hash_token(token)})
    if not row:
        return None
    exp = parse_ts(row.get("expires_at"))
    if not exp or exp < datetime.now(timezone.utc):
        store.delete("sessions", {"token_hash": row["token_hash"]})
        return None
    urow = store.get("users", {"id": row["user_id"]})
    if not urow or not urow.get("active", True):
        return None
    return _user_from_row(urow)


def end_session(store: Store, token: str | None) -> None:
    if token:
        try:
            store.delete("sessions", {"token_hash": _hash_token(token)})
        except StoreError:
            pass


def purge_expired_sessions(store: Store) -> None:
    try:
        store.delete("sessions", {"expires_at": ("lt", utcnow())})
    except StoreError:
        pass
