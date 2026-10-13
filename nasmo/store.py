"""Storage layer.

All application logic talks to the tiny `Store` interface (select / insert /
upsert / update / delete). Two backends implement it:

* SQLiteStore   - local file `data/nasmo.db` (single computer, zero setup)
* SupabaseStore - Supabase (PostgREST) so progress follows the student across
                  devices. Uses the *service* key, which must stay server-side.

The table definitions below are the single source of truth; the SQL file for
Supabase (`supabase_schema.sql`) is generated from them by
`python tools/make_schema.py`.
"""
from __future__ import annotations

import json
import re
import sqlite3
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

# --------------------------------------------------------------------------
# Schema (name, type, nullable/default-hint)
# types: TEXT, INT, BOOL, JSON, TS
# --------------------------------------------------------------------------
SCHEMA: dict[str, dict[str, Any]] = {
    "users": {
        "cols": [
            ("id", "TEXT"), ("username", "TEXT"), ("display_name", "TEXT"),
            ("role", "TEXT"), ("password_hash", "TEXT"), ("active", "BOOL"),
            ("is_demo", "BOOL"), ("created_at", "TS"), ("last_login", "TS"),
        ],
        "pk": ["id"],
        "unique": [["username"]],
    },
    "sessions": {
        "cols": [("token_hash", "TEXT"), ("user_id", "TEXT"),
                 ("created_at", "TS"), ("expires_at", "TS")],
        "pk": ["token_hash"],
    },
    "mission_progress": {
        "cols": [
            ("user_id", "TEXT"), ("mission_id", "TEXT"), ("stage_id", "TEXT"),
            ("status", "TEXT"), ("score", "INT"), ("step_results", "JSON"),
            ("started_at", "TS"), ("completed_at", "TS"), ("last_activity", "TS"),
        ],
        "pk": ["user_id", "mission_id"],
    },
    "attempts": {
        "cols": [
            ("id", "TEXT"), ("user_id", "TEXT"), ("mission_id", "TEXT"),
            ("step_id", "TEXT"), ("stage_id", "TEXT"), ("answer", "TEXT"),
            ("correct", "BOOL"), ("score", "INT"), ("created_at", "TS"),
        ],
        "pk": ["id"],
    },
    "certificates": {
        "cols": [
            ("id", "TEXT"), ("user_id", "TEXT"), ("cert_key", "TEXT"),
            ("title", "TEXT"), ("reason", "TEXT"), ("serial", "TEXT"),
            ("issued_at", "TS"), ("revoked", "BOOL"),
        ],
        "pk": ["id"],
        "unique": [["user_id", "cert_key"]],
    },
    "resources": {
        "cols": [
            ("id", "TEXT"), ("stage_id", "TEXT"), ("kind", "TEXT"),
            ("title", "TEXT"), ("url", "TEXT"), ("description", "TEXT"),
            ("source", "TEXT"), ("visible", "BOOL"), ("sort", "INT"),
            ("created_at", "TS"),
        ],
        "pk": ["id"],
    },
    "custom_missions": {
        "cols": [
            ("id", "TEXT"), ("stage_id", "TEXT"), ("title", "TEXT"),
            ("summary", "TEXT"), ("steps", "JSON"), ("active", "BOOL"),
            ("created_at", "TS"),
        ],
        "pk": ["id"],
    },
    "mission_overrides": {
        "cols": [("mission_id", "TEXT"), ("active", "BOOL")],
        "pk": ["mission_id"],
    },
    "forum_posts": {
        "cols": [
            ("id", "TEXT"), ("user_id", "TEXT"), ("parent_id", "TEXT"), ("title", "TEXT"),
            ("body", "TEXT"), ("pinned", "BOOL"), ("closed", "BOOL"), ("accepted", "BOOL"),
            ("created_at", "TS"),
        ],
        "pk": ["id"],
    },
    "forum_thanks": {
        "cols": [("post_id", "TEXT"), ("user_id", "TEXT"), ("created_at", "TS")],
        "pk": ["post_id", "user_id"],
    },
    "settings": {
        "cols": [("key", "TEXT"), ("value", "TEXT")],
        "pk": ["key"],
    },
}

_IDENT = re.compile(r"^[a-z_][a-z0-9_]*$")


class StoreError(Exception):
    """Any storage failure. Message is safe to show to users (no secrets)."""


class DuplicateError(StoreError):
    """Unique constraint violated."""


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    v = str(value).strip().replace("Z", "+00:00").replace(" ", "T", 1)
    try:
        dt = datetime.fromisoformat(v)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _col_types(table: str) -> dict[str, str]:
    return {c: t for c, t in SCHEMA[table]["cols"]}


def _check_table(table: str) -> None:
    if table not in SCHEMA:
        raise StoreError(f"Unknown table {table!r}")


def _check_cols(table: str, cols: Iterable[str]) -> None:
    known = _col_types(table)
    for c in cols:
        if c not in known:
            raise StoreError(f"Unknown column {c!r} for table {table!r}")


# --------------------------------------------------------------------------
class Store(ABC):
    backend = "abstract"

    @abstractmethod
    def select(self, table: str, where: dict | None = None,
               order: list[tuple[str, str]] | None = None,
               limit: int | None = None) -> list[dict]: ...

    @abstractmethod
    def insert(self, table: str, row: dict) -> dict: ...

    @abstractmethod
    def upsert(self, table: str, row: dict) -> dict: ...

    @abstractmethod
    def update(self, table: str, where: dict, patch: dict) -> int: ...

    @abstractmethod
    def delete(self, table: str, where: dict) -> int: ...

    @abstractmethod
    def ping(self) -> None:
        """Raise StoreError if the database is not ready."""

    # convenience -----------------------------------------------------
    def get(self, table: str, where: dict) -> dict | None:
        rows = self.select(table, where, limit=1)
        return rows[0] if rows else None


# --------------------------------------------------------------------------
# SQLite
# --------------------------------------------------------------------------
class SQLiteStore(Store):
    backend = "sqlite"

    def __init__(self, path: str | Path):
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._mem: sqlite3.Connection | None = None
        if self.path == ":memory:":
            self._mem = sqlite3.connect(":memory:", check_same_thread=False)
            self._mem.row_factory = sqlite3.Row
        self._init_schema()

    # -- connection ---------------------------------------------------
    def _connect(self) -> sqlite3.Connection:
        if self._mem is not None:
            return self._mem
        conn = sqlite3.connect(self.path, timeout=15, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _release(self, conn: sqlite3.Connection) -> None:
        if conn is not self._mem:
            conn.close()

    def _init_schema(self) -> None:
        sqlt = {"TEXT": "TEXT", "INT": "INTEGER", "BOOL": "INTEGER",
                "JSON": "TEXT", "TS": "TEXT"}
        with self._lock:
            conn = self._connect()
            try:
                if self._mem is None:
                    conn.execute("PRAGMA journal_mode=WAL")
                for table, spec in SCHEMA.items():
                    cols = ", ".join(f"{c} {sqlt[t]}" for c, t in spec["cols"])
                    pk = ", ".join(spec["pk"])
                    extra = "".join(
                        f", UNIQUE ({', '.join(u)})" for u in spec.get("unique", []))
                    conn.execute(
                        f"CREATE TABLE IF NOT EXISTS {table} "
                        f"({cols}, PRIMARY KEY ({pk}){extra})")
                conn.execute("CREATE INDEX IF NOT EXISTS ix_attempts_user "
                             "ON attempts(user_id, created_at)")
                conn.commit()
            finally:
                self._release(conn)

    # -- value conversion --------------------------------------------
    @staticmethod
    def _to_db(ctype: str, value: Any) -> Any:
        if value is None:
            return None
        if ctype == "BOOL":
            return 1 if value else 0
        if ctype == "JSON":
            return json.dumps(value, ensure_ascii=False)
        return value

    @staticmethod
    def _from_db(ctype: str, value: Any) -> Any:
        if value is None:
            return None
        if ctype == "BOOL":
            return bool(value)
        if ctype == "JSON":
            try:
                return json.loads(value)
            except (TypeError, ValueError):
                return None
        return value

    def _row_out(self, table: str, row: sqlite3.Row) -> dict:
        types = _col_types(table)
        return {k: self._from_db(types[k], row[k]) for k in row.keys()}

    def _where(self, table: str, where: dict | None) -> tuple[str, list]:
        if not where:
            return "", []
        _check_cols(table, where.keys())
        types = _col_types(table)
        parts: list[str] = []
        params: list[Any] = []
        ops = {"gte": ">=", "lte": "<=", "gt": ">", "lt": "<", "neq": "<>"}
        for col, cond in where.items():
            t = types[col]
            if isinstance(cond, tuple):
                op, val = cond
                if op == "in":
                    vals = list(val)
                    if not vals:
                        parts.append("1=0")
                        continue
                    parts.append(f"{col} IN ({','.join('?' * len(vals))})")
                    params.extend(self._to_db(t, v) for v in vals)
                elif op in ops:
                    parts.append(f"{col} {ops[op]} ?")
                    params.append(self._to_db(t, val))
                else:
                    raise StoreError(f"Unsupported operator {op!r}")
            elif cond is None:
                parts.append(f"{col} IS NULL")
            else:
                parts.append(f"{col} = ?")
                params.append(self._to_db(t, cond))
        return " WHERE " + " AND ".join(parts), params

    # -- API -----------------------------------------------------------
    def select(self, table, where=None, order=None, limit=None):
        _check_table(table)
        w, params = self._where(table, where)
        sql = f"SELECT * FROM {table}{w}"
        if order:
            _check_cols(table, [c for c, _ in order])
            sql += " ORDER BY " + ", ".join(
                f"{c} {'DESC' if d.lower() == 'desc' else 'ASC'}" for c, d in order)
        if limit:
            sql += f" LIMIT {int(limit)}"
        with self._lock:
            conn = self._connect()
            try:
                return [self._row_out(table, r)
                        for r in conn.execute(sql, params).fetchall()]
            except sqlite3.Error as e:
                raise StoreError(f"Database read failed ({type(e).__name__})") from e
            finally:
                self._release(conn)

    def _write(self, sql: str, params: list) -> int:
        with self._lock:
            conn = self._connect()
            try:
                cur = conn.execute(sql, params)
                conn.commit()
                return cur.rowcount
            except sqlite3.IntegrityError as e:
                conn.rollback()
                raise DuplicateError("Record already exists") from e
            except sqlite3.Error as e:
                conn.rollback()
                raise StoreError(f"Database write failed ({type(e).__name__})") from e
            finally:
                self._release(conn)

    def _prepare_row(self, table: str, row: dict) -> tuple[list[str], list]:
        _check_cols(table, row.keys())
        types = _col_types(table)
        cols = list(row.keys())
        return cols, [self._to_db(types[c], row[c]) for c in cols]

    def insert(self, table, row):
        _check_table(table)
        cols, vals = self._prepare_row(table, row)
        self._write(
            f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
            vals)
        return dict(row)

    def upsert(self, table, row):
        _check_table(table)
        cols, vals = self._prepare_row(table, row)
        pk = SCHEMA[table]["pk"]
        upd = [c for c in cols if c not in pk]
        action = ("DO UPDATE SET " + ", ".join(f"{c}=excluded.{c}" for c in upd)
                  if upd else "DO NOTHING")
        self._write(
            f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join('?' * len(cols))}) "
            f"ON CONFLICT({','.join(pk)}) {action}", vals)
        return dict(row)

    def update(self, table, where, patch):
        _check_table(table)
        if not where:
            raise StoreError("update() requires a filter")
        cols, vals = self._prepare_row(table, patch)
        w, params = self._where(table, where)
        return self._write(
            f"UPDATE {table} SET {', '.join(c + '=?' for c in cols)}{w}", vals + params)

    def delete(self, table, where):
        _check_table(table)
        if not where:
            raise StoreError("delete() requires a filter")
        w, params = self._where(table, where)
        return self._write(f"DELETE FROM {table}{w}", params)

    def ping(self):
        self.select("settings", limit=1)


# --------------------------------------------------------------------------
# Supabase / PostgREST
# --------------------------------------------------------------------------
class SupabaseStore(Store):
    backend = "supabase"

    def __init__(self, url: str, service_key: str, timeout: float = 15.0):
        import requests  # imported lazily so local mode needs nothing extra

        self._requests = requests
        self.base = url.rstrip("/") + "/rest/v1"
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
        })

    # -- helpers -------------------------------------------------------
    @staticmethod
    def _lit(val: Any) -> str:
        if isinstance(val, bool):
            return "true" if val else "false"
        return str(val)

    @staticmethod
    def _quote(val: Any) -> str:
        s = SupabaseStore._lit(val).replace("\\", "\\\\").replace('"', '\\"')
        return f'"{s}"'

    def _filters(self, table: str, where: dict | None) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        if not where:
            return out
        _check_cols(table, where.keys())
        for col, cond in where.items():
            if isinstance(cond, tuple):
                op, val = cond
                if op == "in":
                    out.append((col, "in.(" + ",".join(self._quote(v) for v in val) + ")"))
                elif op in ("gte", "lte", "gt", "lt", "neq"):
                    out.append((col, f"{op}.{self._lit(val)}"))
                else:
                    raise StoreError(f"Unsupported operator {op!r}")
            elif cond is None:
                out.append((col, "is.null"))
            else:
                out.append((col, f"eq.{self._lit(cond)}"))
        return out

    def _request(self, method: str, table: str, params=None, body=None,
                 prefer: str | None = None, retry: bool = False):
        _check_table(table)
        headers = {}
        if prefer:
            headers["Prefer"] = prefer
        url = f"{self.base}/{table}"
        attempts = 2 if retry else 1
        last_exc: Exception | None = None
        for _ in range(attempts):
            try:
                resp = self._session.request(
                    method, url, params=params, headers=headers,
                    data=None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8"),
                    timeout=self.timeout)
                break
            except self._requests.RequestException as e:
                last_exc = e
        else:
            raise StoreError("Cannot reach the database. Check your internet "
                             "connection and Supabase settings.") from last_exc
        if resp.status_code >= 400:
            code = ""
            try:
                code = str(resp.json().get("code", ""))
            except Exception:
                pass
            if code == "23505" or resp.status_code == 409:
                raise DuplicateError("Record already exists")
            if resp.status_code in (401, 403):
                raise StoreError("The database rejected the credentials "
                                 "(check SUPABASE_SERVICE_KEY).")
            if resp.status_code == 404 or code in ("42P01", "PGRST205"):
                raise StoreError("Database tables are missing. Run "
                                 "supabase_schema.sql in the Supabase SQL editor.")
            raise StoreError(f"Database request failed (HTTP {resp.status_code}).")
        if resp.status_code == 204 or not resp.content:
            return []
        try:
            return resp.json()
        except ValueError:
            return []

    # -- API -----------------------------------------------------------
    PAGE_SIZE = 1000      # Supabase returns at most 1000 rows per request (its default "Max Rows")

    def select(self, table, where=None, order=None, limit=None):
        """All matching rows. Supabase caps every request, so the rows are fetched page by page
        (in a fixed order, otherwise pages could overlap or skip rows)."""
        _check_table(table)
        base: list[tuple[str, str]] = [("select", "*")]
        base += self._filters(table, where)
        if order:
            _check_cols(table, [c for c, _ in order])
        keys = list(order or []) + [(c, "asc") for c in SCHEMA[table]["pk"] if c not in {c for c, _ in (order or [])}]
        base.append(("order", ",".join(f"{c}.{'desc' if d.lower() == 'desc' else 'asc'}" for c, d in keys)))
        want = int(limit) if limit else None
        out: list = []
        offset = 0
        while True:
            n = self.PAGE_SIZE if want is None else min(self.PAGE_SIZE, want - len(out))
            if n <= 0:
                break
            page = self._request("GET", table, params=base + [("limit", str(n)), ("offset", str(offset))], retry=True)
            out.extend(page)
            if len(page) < n:
                break
            offset += n
        return out

    def insert(self, table, row):
        _check_table(table)
        _check_cols(table, row.keys())
        res = self._request("POST", table, body=row, prefer="return=representation")
        return res[0] if res else dict(row)

    def upsert(self, table, row):
        _check_table(table)
        _check_cols(table, row.keys())
        pk = SCHEMA[table]["pk"]
        res = self._request(
            "POST", table, params=[("on_conflict", ",".join(pk))], body=row,
            prefer="resolution=merge-duplicates,return=representation")
        return res[0] if res else dict(row)

    def update(self, table, where, patch):
        _check_table(table)
        if not where:
            raise StoreError("update() requires a filter")
        _check_cols(table, patch.keys())
        res = self._request("PATCH", table, params=self._filters(table, where),
                            body=patch, prefer="return=representation")
        return len(res)

    def delete(self, table, where):
        _check_table(table)
        if not where:
            raise StoreError("delete() requires a filter")
        res = self._request("DELETE", table, params=self._filters(table, where),
                            prefer="return=representation")
        return len(res)

    def ping(self):
        self.select("settings", limit=1)


# --------------------------------------------------------------------------
def postgres_ddl() -> str:
    pg = {"TEXT": "text", "INT": "integer", "BOOL": "boolean",
          "JSON": "jsonb", "TS": "timestamptz"}
    out = [
        "-- NASMO INFORMATICS LAB - Supabase schema",
        "-- Generated by tools/make_schema.py from nasmo/store.py. Do not edit by hand.",
        "-- Run once in: Supabase dashboard > SQL Editor > New query > Run.",
        "-- Safe to run again (uses IF NOT EXISTS).",
        "",
    ]
    for table, spec in SCHEMA.items():
        lines = []
        for c, t in spec["cols"]:
            line = f"  {c} {pg[t]}"
            if c in spec["pk"] and len(spec["pk"]) == 1:
                line += " primary key"
            if c == "active" or c == "visible":
                line += " default true"
            if c in ("revoked", "is_demo"):
                line += " default false"
            if c == "created_at":
                line += " default now()"
            if c == "step_results" or c == "steps":
                line += " default '{}'::jsonb" if c == "step_results" else " default '[]'::jsonb"
            lines.append(line)
        if len(spec["pk"]) > 1:
            lines.append(f"  primary key ({', '.join(spec['pk'])})")
        for u in spec.get("unique", []):
            lines.append(f"  unique ({', '.join(u)})")
        out.append(f"create table if not exists public.{table} (")
        out.append(",\n".join(lines))
        out.append(");")
        out.append(f"alter table public.{table} enable row level security;")
        out.append("")
    out += [
        "create index if not exists ix_attempts_user on public.attempts (user_id, created_at);",
        "",
        "-- Row Level Security is ON and no public policies are created.",
        "-- That means the public 'anon' key can read or write NOTHING.",
        "-- The app talks to the database only from the server with the SERVICE",
        "-- key (keep it secret: .streamlit/secrets.toml or an environment variable;",
        "-- never put it in a web page or a public repository).",
    ]
    return "\n".join(out) + "\n"
