"""Arabic / English switch.

The app is written in English. When the language is Arabic, every visible text goes through `tr()`:
it is looked up in the dictionary (nasmo/i18n_ar.py), then in a few patterns for texts with numbers.
Text that has no translation (mission questions, code, names) stays as it is, so nothing breaks.
Used automatically by nasmo/ui/sx.py, so pages keep calling the normal Streamlit functions."""
from __future__ import annotations

import html as _html
import re

LANGS = {"en": "English", "ar": "العربية"}
MISSES: set[str] = set()          # texts that had no translation (used by the tests)
_ARROWS = {"←": "→", "→": "←", "▶": "◀", "↗": "↖", "◀": "▶"}
_LATIN = re.compile(r"[A-Za-z]")
_DECOR = re.compile(r"^([^A-Za-z0-9؀-ۿ]*)(.*?)([^A-Za-z0-9؀-ۿ.!?)\]%]*)$", re.S)


_FORCED: list[str] = []


class force:
    """`with i18n.force("ar"):` renders texts in that language whatever the session says
    (used for the stand-alone report download)."""
    def __init__(self, lang: str):
        self.lang = lang

    def __enter__(self):
        _FORCED.append(self.lang)

    def __exit__(self, *a):
        _FORCED.pop()


def current_lang() -> str:
    if _FORCED:
        return _FORCED[-1]
    try:
        import streamlit as st
        lang = st.session_state.get("lang", "en")
    except Exception:       # outside Streamlit
        return "en"
    return lang if lang in LANGS else "en"


def is_rtl() -> bool:
    return current_lang() == "ar"


def _flip(s: str) -> str:
    return "".join(_ARROWS.get(c, c) for c in s)


def _keep(key: str) -> bool:
    """Texts that stay as they are (numbers, links, code, names that come from the data)."""
    from .i18n_ar import KEEP, KEEP_RX
    return key in KEEP() or any(rx.search(key) for rx in KEEP_RX)


def _core(key: str):
    from .i18n_ar import AR, PATTERNS
    if key in AR:
        return AR[key]
    for rx, fn in PATTERNS:
        m = rx.fullmatch(key)
        if m:
            return fn(m)
    return None


_SPLIT = re.compile(r"( · | — | - )")


def _resolve(key: str):
    """Translation of `key`, or None. Understands: exact text, patterns, decoration around a text
    (emoji, arrows, ** **), and composites such as 'Stage 2 · Binary Search' (every part must be
    translatable or kept as it is)."""
    out = _core(key)
    if out is not None:
        return out
    m = _DECOR.match(key)
    if m and (m.group(1) or m.group(3)) and m.group(2):
        inner = _resolve(m.group(2))
        if inner is not None:
            return _flip(m.group(1)) + inner + _flip(m.group(3))
    if "\n" in key:
        bits = re.split(r"(\s*\n\s*)", key)
        res, ok, changed = [], True, False
        for i, b in enumerate(bits):
            if i % 2 or not b.strip():
                res.append(b)
                continue
            r = _resolve(b.strip())
            if r is None and not _keep(b.strip()):
                ok = False
                break
            changed = changed or r is not None
            res.append(r if r is not None else b)
        if ok and changed:
            return "".join(res)
    parts = _SPLIT.split(key)
    if len(parts) > 1:
        res, ok, changed = [], True, False
        for i, part in enumerate(parts):
            if i % 2:
                res.append(part)
                continue
            r = _resolve(part.strip()) if part.strip() else part
            if r is None:
                dm = _DECOR.match(part.strip())
                if _keep(part.strip()) or (dm and dm.group(2) and _keep(dm.group(2))):
                    r = part.strip()
                else:
                    ok = False
                    break
            else:
                changed = True
            res.append(r)
        if ok and changed:
            return "".join(res)
    return None


def tr(text, **fmt):
    """Translate one text. `fmt` fills {placeholders} after translating (optional)."""
    if not isinstance(text, str) or not text.strip():
        return text
    if current_lang() != "ar":
        return text.format(**fmt) if fmt else text
    lead = text[: len(text) - len(text.lstrip())]
    trail = text[len(text.rstrip()):]
    key = text.strip()
    out = _resolve(key)
    pre = post = ""
    if out is None:
        if _LATIN.search(key) and not _keep(key):
            MISSES.add(key)
        return text.format(**fmt) if fmt else text
    res = lead + pre + out + post + trail
    return res.format(**fmt) if fmt else res


_NODE = re.compile(r">([^<>]+)<")


def tr_html(markup: str) -> str:
    """Translate the text nodes of an HTML snippet (tags, attributes, CSS and SVG are left alone)."""
    if current_lang() != "ar" or not isinstance(markup, str):
        return markup
    if "<style" in markup or "<script" in markup or 'class="imp' in markup or 'data-notr' in markup:   # the impact report is written in the right language already
        return markup
    if "<" not in markup:
        return tr(markup)

    def one(m):
        raw = m.group(1)
        if not raw.strip():
            return m.group(0)
        plain = _html.unescape(raw)
        new = tr(plain)
        if new == plain:
            return m.group(0)
        return ">" + _html.escape(new, quote=False) + "<"

    return _NODE.sub(one, markup)
