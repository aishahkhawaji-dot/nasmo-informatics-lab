"""A small fake `streamlit` used ONLY to smoke-test the page functions in an
environment where Streamlit cannot be installed. It runs our page code, catches
NameErrors / wrong arguments / duplicate widget keys, and lets tests "press
buttons" and "type values" by widget key. It does NOT prove the real Streamlit
renders the pages correctly - that still needs a real run (START_NASMO.bat)."""
from __future__ import annotations

import sys
import types
from contextlib import contextmanager


class RerunException(Exception):
    pass


class _State(dict):
    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError as e:
            raise AttributeError(k) from e

    def __setattr__(self, k, v):
        self[k] = v


class _Ctx:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def __getattr__(self, name):          # allow `col.button(...)`, `c1.markdown(...)`
        fn = getattr(_mod, name, None)
        if fn is None:
            raise AttributeError(name)
        return fn


_mod = types.ModuleType("streamlit")
_mod.session_state = _State()
_mod.query_params = {}
_mod.secrets = {}
SEEN: set = set()
OUT: list[str] = []          # every markdown/html chunk rendered
MSGS: list[tuple[str, str]] = []   # (kind, text) for success/error/warning/info
VALUES: dict = {}            # widget key -> value the "user" typed/selected
PRESSED: set = set()         # button keys pressed in the next run
DOWNLOADS: list = []


def reset_run() -> None:
    SEEN.clear()
    OUT.clear()
    MSGS.clear()
    DOWNLOADS.clear()


def full_reset() -> None:
    reset_run()
    _mod.session_state.clear()
    _mod.query_params.clear()
    VALUES.clear()
    PRESSED.clear()


def _register(kind, key, label):
    ident = (kind, key if key else ("label", label))
    if ident in SEEN:
        raise RuntimeError(f"DuplicateWidgetID: {kind} {key or label!r}")
    SEEN.add(ident)


def _w(kind):
    def deco(fn):
        _mod.__dict__[kind] = fn
        return fn
    return deco


@_w("markdown")
def markdown(body="", unsafe_allow_html=False, **k):
    import re
    body = str(body)
    if body.startswith("<style>"):
        return
    OUT.append(re.sub(r"data:[a-z/+]+;base64,[A-Za-z0-9+/=]+", "data:...", body))


for _n in ("write", "caption", "code", "text", "html", "divider", "json", "image"):
    _mod.__dict__[_n] = (lambda n: (lambda *a, **k: OUT.append(" ".join(str(x) for x in a))))(_n)
_mod.__dict__["exception"] = lambda e, **k: OUT.append(repr(e))
for _n in ("success", "error", "warning", "info"):
    _mod.__dict__[_n] = (lambda n: (lambda text="", **k: MSGS.append((n, str(text)))))(_n)


@_w("set_page_config")
def set_page_config(**k):
    pass


@_w("container")
def container(*a, key=None, **k):
    if key:
        _register("container", key, "")
    return _Ctx()


@_w("columns")
def columns(spec, **k):
    n = spec if isinstance(spec, int) else len(spec)
    return [_Ctx() for _ in range(n)]


@_w("tabs")
def tabs(labels, **k):
    return [_Ctx() for _ in labels]


@_w("expander")
def expander(label, **k):
    OUT.append("[expander] " + str(label))
    return _Ctx()


@_w("form")
def form(key, **k):
    _register("form", key, "")
    return _Ctx()


@_w("button")
def button(label, key=None, on_click=None, args=(), kwargs=None, **k):
    _register("button", key, label)
    if key in PRESSED:
        PRESSED.discard(key)
        if on_click:               # Streamlit runs callbacks first, then reruns the script
            on_click(*args, **(kwargs or {}))
            raise RerunException()
        return True
    return False


_mod.__dict__["form_submit_button"] = lambda label="Submit", **k: (
    (PRESSED.discard(label) or True) if label in PRESSED else False)


@_w("download_button")
def download_button(label, data=None, file_name=None, key=None, **k):
    _register("download_button", key, label)
    DOWNLOADS.append((label, file_name, data))
    return False


def _input(kind, default):
    def fn(label, *a, key=None, value=None, **k):
        _register(kind, key, label)
        kk = key or label
        if kk in VALUES:
            return VALUES[kk]
        return value if value is not None else default
    return fn


for _k in ("text_input", "text_area"):
    _mod.__dict__[_k] = _input(_k, "")
_mod.__dict__["number_input"] = lambda label, min_value=0, max_value=100, value=None, key=None, **k: (
    _register("number_input", key, label) or VALUES.get(key or label, value if value is not None else min_value))


@_w("toggle")
def toggle(label, value=False, key=None, **k):
    _register("toggle", key, label)
    if key and key in VALUES:
        _mod.session_state[key] = VALUES[key]
    return _mod.session_state.get(key, value) if key else value


@_w("radio")
def radio(label, options, index=0, key=None, format_func=str, **k):
    _register("radio", key, label)
    for o in options:      # format_func must work for every option
        format_func(o)
    return VALUES.get(key, None if index is None else options[index])


@_w("selectbox")
def selectbox(label, options, index=0, key=None, format_func=str, **k):
    _register("selectbox", key, label)
    options = list(options)
    for o in options:
        format_func(o)
    return VALUES.get(key, options[index] if options else None)


@_w("balloons")
def balloons():
    OUT.append("[balloons]")


@_w("toast")
def toast(msg="", **k):
    OUT.append("[toast]" + str(msg))


@_w("rerun")
def rerun():
    raise RerunException()


def _cache_resource(*a, **k):
    def deco(fn):
        cache = {}

        def wrapper(*aa, **kk):
            if "v" not in cache:
                cache["v"] = fn(*aa, **kk)
            return cache["v"]
        wrapper.clear = cache.clear
        return wrapper
    return deco(a[0]) if a and callable(a[0]) else deco


_mod.cache_resource = _cache_resource


class _Sidebar(_Ctx):
    pass


_mod.sidebar = _Sidebar()

# streamlit.components.v1
_comp = types.ModuleType("streamlit.components")
_v1 = types.ModuleType("streamlit.components.v1")
_v1.html = lambda body, **k: OUT.append("[component-html]" + str(body)[:700])
_comp.v1 = _v1
_mod.components = _comp


def install() -> types.ModuleType:
    sys.modules["streamlit"] = _mod
    sys.modules["streamlit.components"] = _comp
    sys.modules["streamlit.components.v1"] = _v1
    return _mod
