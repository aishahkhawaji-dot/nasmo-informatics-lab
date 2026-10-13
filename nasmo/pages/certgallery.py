"""Certificate design gallery: previews of the four designs (never printable) + the choice button."""
from __future__ import annotations

import streamlit.components.v1 as components

from ..ui.sx import st
from ..ui.certificate import DEFAULT_DESIGN, DESIGNS, certificate_html

_SAMPLE = {"serial": "PREVIEW", "title": "Your certificate title", "issued_at": "",
           "reason": "This is a preview. A real certificate is issued after you complete every mission of a stage."}


def selected_design() -> str:
    d = st.session_state.get("cert_design", DEFAULT_DESIGN)
    return d if d in DESIGNS else DEFAULT_DESIGN


def _pick(key: str) -> None:
    st.session_state["cert_design"] = key


def gallery(name: str, selectable: bool = True, stats: dict | None = None) -> None:
    """Shows the four designs two by two. Students pick one; a teacher only looks."""
    current = selected_design()
    cols = st.columns(2)
    for i, (key, (title, desc)) in enumerate(DESIGNS.items()):
        with cols[i % 2]:
            components.html(certificate_html(_SAMPLE, name or "Student Name", key, stats, preview=True), height=230)
            st.markdown(f"**{title}** - {desc}")
            if selectable:
                if key == current:
                    st.button("✓ Selected", key=f"cert_pick_{key}", disabled=True, use_container_width=True)
                else:
                    st.button("Use this design", key=f"cert_pick_{key}", on_click=_pick, args=(key,),
                              use_container_width=True)
