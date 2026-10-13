"""A thin proxy around `streamlit` used by every page: it behaves exactly like `st`, but translates
visible texts (labels, captions, messages, HTML text nodes) when the language is Arabic."""
from __future__ import annotations

import streamlit as _st

from ..i18n import tr, tr_html

_TEXT_FIRST = {"caption", "success", "error", "warning", "info", "write", "toast", "subheader", "header", "title"}
_LABEL_FIRST = {"button", "text_input", "text_area", "number_input", "selectbox", "radio", "toggle", "checkbox",
                "download_button", "form_submit_button", "expander", "multiselect", "slider", "select_slider"}
_PICKERS = {"selectbox", "radio", "multiselect", "select_slider"}
_KW = ("placeholder", "help")


def _wrap_fn(name: str, fn):
    def call(*args, **kwargs):
        args = list(args)
        if name == "markdown":
            if args and isinstance(args[0], str):
                args[0] = tr_html(args[0])
        elif name in _TEXT_FIRST or name in _LABEL_FIRST:
            if args and isinstance(args[0], str):
                args[0] = tr(args[0])
            if name in _PICKERS:
                ff = kwargs.get("format_func") or str
                kwargs["format_func"] = lambda o, _f=ff: tr(str(_f(o)))
        elif name == "tabs" and args:
            args[0] = [tr(x) if isinstance(x, str) else x for x in args[0]]
        for k in _KW:
            if isinstance(kwargs.get(k), str):
                kwargs[k] = tr(kwargs[k])
        try:
            res = fn(*args, **kwargs)
        except TypeError:
            # Newer Streamlit versions removed use_container_width (replaced by width="stretch"):
            # retry once in the new form, so one library update cannot break every button.
            if "use_container_width" not in kwargs:
                raise
            kw = dict(kwargs)
            if kw.pop("use_container_width"):
                kw["width"] = "stretch"
            res = fn(*args, **kw)
        if name in ("columns", "tabs"):
            return [Proxy(r) for r in res]
        return res
    return call


_WRAP = {"markdown"} | _TEXT_FIRST | _LABEL_FIRST | {"tabs", "columns"}


class Proxy:
    """`with proxy:` and `proxy.method(...)` work like the real object; texts are translated."""

    def __init__(self, target):
        object.__setattr__(self, "_t", target)

    def __getattr__(self, name):
        attr = getattr(self._t, name)
        if name in _WRAP and callable(attr):
            return _wrap_fn(name, attr)
        if name == "sidebar":
            return Proxy(attr)
        return attr

    def __setattr__(self, name, value):
        setattr(self._t, name, value)

    def __enter__(self):
        self._t.__enter__()
        return self

    def __exit__(self, *a):
        return self._t.__exit__(*a)

    def __iter__(self):
        return iter(self._t)


st = Proxy(_st)
