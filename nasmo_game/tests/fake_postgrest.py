"""A tiny PostgREST look-alike backed by SQLite, used ONLY by the tests to
check that SupabaseStore builds correct requests (filters, upsert headers,
JSON columns, error codes). It is not Supabase and does not prove Supabase
itself works - see README for how to test against a real project."""
from __future__ import annotations

import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qsl, urlparse

from nasmo.store import SCHEMA, DuplicateError, SQLiteStore, StoreError

API_KEY = "test-service-key"


def _coerce(table: str, col: str, text: str):
    t = dict(SCHEMA[table]["cols"])[col]
    if t == "BOOL":
        return text == "true"
    if t == "INT":
        return int(text)
    return text


def _parse_filters(table: str, pairs):
    where = {}
    for col, expr in pairs:
        if col in ("select", "order", "limit", "offset", "on_conflict"):
            continue
        op, _, val = expr.partition(".")
        if op == "eq":
            where[col] = _coerce(table, col, val)
        elif op == "is" and val == "null":
            where[col] = None
        elif op in ("gte", "lte", "gt", "lt", "neq"):
            where[col] = (op, _coerce(table, col, val))
        elif op == "in":
            inner = val[1:-1]
            items = re.findall(r'"((?:[^"\\]|\\.)*)"|([^,]+)', inner)
            vals = [(a.replace('\\"', '"').replace("\\\\", "\\") if a != "" else b) for a, b in items]
            where[col] = ("in", [_coerce(table, col, v) for v in vals])
        else:
            raise ValueError(f"bad filter {col}={expr}")
    return where


class Handler(BaseHTTPRequestHandler):
    backing: SQLiteStore = None  # set by start()
    MAX_ROWS = 1000             # Supabase's default 'Max Rows' per request
    log: list = []

    def log_message(self, *a):  # silence
        pass

    def _send(self, code, payload=None):
        body = b"" if payload is None else json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle(self, method):
        if self.headers.get("apikey") != API_KEY or \
                self.headers.get("Authorization") != f"Bearer {API_KEY}":
            return self._send(401, {"message": "Invalid API key"})
        u = urlparse(self.path)
        m = re.match(r"^/rest/v1/([a-z_]+)$", u.path)
        if not m:
            return self._send(404, {"message": "not found"})
        table = m.group(1)
        if table not in SCHEMA:
            return self._send(404, {"code": "42P01", "message": "relation does not exist"})
        pairs = parse_qsl(u.query, keep_blank_values=True)
        q = dict(pairs)
        n = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(n)) if n else None
        prefer = self.headers.get("Prefer", "")
        Handler.log.append((method, table, dict(pairs), prefer))
        b = Handler.backing
        try:
            where = _parse_filters(table, pairs)
            if method == "GET":
                order = None
                if "order" in q:
                    order = [(c.split(".")[0], c.split(".")[1]) for c in q["order"].split(",")]
                rows = b.select(table, where or None, order, None)
                # like Supabase: at most MAX_ROWS rows per request, whatever limit was asked for
                off = int(q.get("offset", 0))
                lim = min(int(q["limit"]), Handler.MAX_ROWS) if "limit" in q else Handler.MAX_ROWS
                return self._send(200, rows[off:off + lim])
            if method == "POST":
                if "resolution=merge-duplicates" in prefer:
                    if q.get("on_conflict") != ",".join(SCHEMA[table]["pk"]):
                        return self._send(400, {"message": "bad on_conflict"})
                    b.upsert(table, body)
                else:
                    b.insert(table, body)
                return self._send(201, [body])
            if method == "PATCH":
                if not where:
                    return self._send(400, {"message": "filter required"})
                n_upd = b.update(table, where, body)
                rows = b.select(table, None)  # not used; return n copies
                return self._send(200, [{}] * n_upd)
            if method == "DELETE":
                if not where:
                    return self._send(400, {"message": "filter required"})
                n_del = b.delete(table, where)
                return self._send(200, [{}] * n_del)
        except DuplicateError:
            return self._send(409, {"code": "23505", "message": "duplicate key"})
        except (StoreError, ValueError) as e:
            return self._send(400, {"message": str(e)})
        return self._send(405, {"message": "method"})

    def do_GET(self): self._handle("GET")
    def do_POST(self): self._handle("POST")
    def do_PATCH(self): self._handle("PATCH")
    def do_DELETE(self): self._handle("DELETE")


def start() -> tuple[ThreadingHTTPServer, str]:
    Handler.backing = SQLiteStore(":memory:")
    Handler.log = []
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"
