"""Shared page chrome: CSS, header, sidebar, clickable cards."""
from __future__ import annotations

from .sx import st
import streamlit.components.v1 as components

from .. import auth, config
from ..content.stages import STAGES
from . import components as C
from . import session as S
from . import style
from .art import icon

NAV_ACTIVE = {  # page -> sidebar item that should look selected
    "stage": "stages", "mission": "stages", "account": "progress",
}


def inject_css() -> None:
    theme = st.session_state.get("theme", "light")
    st.markdown(style.build_css(theme, bool(st.session_state.get("anim", True)), st.session_state.get("lang", "en")),
                unsafe_allow_html=True)


def fit_sidebar() -> None:
    """Align the sidebar with the hero box (see ui/fit.py)."""
    from .fit import FIT_JS
    from .menu import MENU_JS
    components.html(f"<script>{FIT_JS}</script><script>{MENU_JS}</script>", height=0)


def sound_enabled() -> bool:
    return bool(st.session_state.get("sound", True))


def play(*kinds: str, stars: int = 3) -> None:
    """Play short sound effects (only if the student left sound on)."""
    if not sound_enabled():
        return
    from .sound import sound_html
    components.html(sound_html(list(kinds), stars), height=0)


def header() -> None:
    st.markdown(C.header_html(), unsafe_allow_html=True)


def card_button(key: str, markup: str, page: str | None = None, *, label: str = "Open",
                callback=None, args: tuple = (), kwargs: dict | None = None, **params) -> None:
    """A styled HTML card with a transparent real button stretched over it."""
    with st.container(key=f"ov_{key}"):
        st.markdown(markup, unsafe_allow_html=True)
        if callback is not None:
            st.button(label, key=f"btn_{key}", on_click=callback, args=args, kwargs=kwargs or {})
        else:
            st.button(label, key=f"btn_{key}", on_click=S.go, args=(page,), kwargs=params)


def nav_button(key: str, label: str, icon_name: str, page: str, active_page: str, **params) -> None:
    active = (NAV_ACTIVE.get(active_page, active_page) == page)
    card_button(f"nav_{key}", C.nav_item_html(label, icon_name, active), page, label=label, **params)


def _logout(store) -> None:
    S.sign_out(store)


def _sidebar_action(key: str, label: str, page: str, *, icon_text: str = "") -> None:
    """Use a real, visible Streamlit button for sidebar navigation.

    The previous transparent-overlay pattern depended on absolute-position CSS.
    On some Streamlit/browser layouts the overlay receives no clicks, so sidebar
    navigation is deliberately implemented as native buttons instead.
    """
    text = f"{icon_text}  {label}" if icon_text else label
    st.button(text, key=f"side_{key}", on_click=S.go, args=(page,), use_container_width=True,
              type="primary" if st.session_state.get("page", "home") == page else "secondary")


def sidebar(store, mode: str) -> None:
    ss = st.session_state
    user = S.current_user()
    page = ss.get("page", "home")
    with st.sidebar:
        st.markdown(C.side_logo_html(), unsafe_allow_html=True)
        if user is None:
            _sidebar_action("login_student", "Student Login", "student_login", icon_text="🎓")
            _sidebar_action("login_teacher", "Teacher Login", "teacher_login", icon_text="👩‍🏫")
            _sidebar_action("home", "Home", "home", icon_text="⌂")
            _sidebar_action("resources", "Resources", "resources", icon_text="▤")
            _sidebar_action("about", "About", "about", icon_text="ⓘ")
        elif user.is_student:
            st.markdown(C.who_html(user), unsafe_allow_html=True)
            _sidebar_action("home", "Home", "home", icon_text="⌂")
            _sidebar_action("stages", "Adventure Map", "stages", icon_text="🗺️")
            _sidebar_action("trophies", "Trophy Room", "trophies", icon_text="🏆")
            _sidebar_action("progress", "My Progress", "progress", icon_text="📈")
            _sidebar_action("certificates", "My Certificates", "certificates", icon_text="▧")
            _sidebar_action("forum", "Discussion Board", "forum", icon_text="💬")
            _sidebar_action("resources", "Resources", "resources", icon_text="▤")
            _sidebar_action("about", "About", "about", icon_text="ⓘ")
            _sidebar_action("account", "Account Settings", "account", icon_text="⚙")
            st.button("Logout", key="btn_logout", on_click=_logout, args=(store,), use_container_width=True)
        else:
            st.markdown(C.who_html(user), unsafe_allow_html=True)
            _sidebar_action("t_dashboard", "Teacher Dashboard", "t_dashboard", icon_text="▦")
            _sidebar_action("t_students", "Students", "t_students", icon_text="♙")
            _sidebar_action("t_impact", "Impact Report", "t_impact", icon_text="◈")
            _sidebar_action("t_content", "Missions and Content", "t_content", icon_text="⌘")
            _sidebar_action("t_certs", "Certificates", "t_certs", icon_text="▧")
            _sidebar_action("forum", "Discussion Board", "forum", icon_text="💬")
            _sidebar_action("resources", "Resources", "resources", icon_text="▤")
            _sidebar_action("t_settings", "Settings", "t_settings", icon_text="⚙")
            st.button("Logout", key="btn_logout", on_click=_logout, args=(store,), use_container_width=True)
        dark = ss.get("theme") == "dark"
        anim = bool(ss.get("anim", True))
        c1, c2 = st.columns(2)
        c1.button("☀ Light" if dark else "☾ Dark", key="btn_theme", on_click=S.toggle_theme, use_container_width=True)
        c2.button("Motion: on" if anim else "Motion: off", key="btn_anim",
                  on_click=lambda: ss.__setitem__("anim", not bool(ss.get("anim", True))), use_container_width=True)
        snd = sound_enabled()
        st.button("🔊 Sound: on" if snd else "🔇 Sound: off", key="btn_sound", use_container_width=True,
                  on_click=lambda: ss.__setitem__("sound", not sound_enabled()))
        st.button("English" if ss.get("lang") == "ar" else "العربية", key="btn_lang", on_click=S.toggle_lang,
                  use_container_width=True)
        st.markdown(C.deco_card_html(), unsafe_allow_html=True)
        if mode == "local":
            st.caption("Local mode: data is saved on this computer only.")


# --------------------------------------------------------- page scaffolding
def page_title(title: str, subtitle: str = "", chips: list[str] | None = None) -> None:
    chip_html = "".join(f'<span class="nl-chip">{C.esc(c)}</span> ' for c in (chips or []))
    sub = f'<p class="nl-sub">{C.esc(subtitle)}</p>' if subtitle else ""
    st.markdown(f'<div class="nl-root"><div class="nl-pad" style="padding-bottom:0"><h1 class="nl-h1">{C.esc(title)}</h1>{sub}{chip_html}</div></div>',
                unsafe_allow_html=True)


def back_button(label: str, page: str, key: str, **params) -> None:
    st.button(f"← {label}", key=key, on_click=S.go, args=(page,), kwargs=params)


def note(kind: str, text: str) -> None:
    st.markdown(f'<div class="nl-root"><div class="nl-note {kind}">{C.esc(text)}</div></div>', unsafe_allow_html=True)


def footer() -> None:
    """No credits row: the name is already in the header."""
    return


def stage_cards(user, summary: dict | None, store, state: dict | None = None) -> None:
    """The adventure world map: five worlds, each with a native Enter button."""
    from ..progress import all_missions
    from . import game_ui as GU
    missions = all_missions(store)
    current = None
    if summary is not None:
        current = next((s["id"] for s in STAGES if summary["stages"][s["id"]]["total"]
                        and summary["stages"][s["id"]]["completed"] < summary["stages"][s["id"]]["total"]), None)
    with st.container(key="worldmap"):
        cols = st.columns(len(STAGES))
        for i, (stg, col) in enumerate(zip(STAGES, cols)):
            total = sum(1 for m in missions if m["stage"] == stg["id"])
            done = summary["stages"][stg["id"]]["completed"] if summary is not None else None
            stars = 0
            if state is not None:
                stars = sum(state["stars_by"].get(m["id"], 0) for m in missions if m["stage"] == stg["id"])
            with col:
                st.markdown(GU.world_card_html(stg, i, total, done, stars, stg["id"] == current), unsafe_allow_html=True)
                st.button("Enter ▶", key=f"world_go_{stg['id']}", use_container_width=True, type="primary",
                          on_click=S.go, args=("stage",), kwargs={"stage": stg["id"]},
                          help=f"Enter {stg['title']}")


def tabbar(user, store) -> None:
    """Phone bottom bar; hidden on wide screens by CSS."""
    page = st.session_state.get("page", "home")
    if user is None:
        tabs = [("Home", "home", "home"), ("Resources", "book", "resources"), None,
                ("About", "info", "about"), ("Login", "cap", "student_login")]
        plus_page = "student_login"
    elif user.is_student:
        tabs = [("Home", "home", "home"), ("Progress", "trophy", "progress"), None,
                ("Trophies", "trophy", "trophies"), ("Certificates", "cert", "certificates")]
        plus_page = None
    else:
        tabs = [("Dashboard", "chart", "t_dashboard"), ("Students", "users", "t_students"), None,
                ("Content", "code", "t_content"), ("Settings", "settings", "t_settings")]
        plus_page = "t_dashboard"
    with st.container(key="tabbar"):
        cols = st.columns(5)
        for t, col in zip(tabs, cols):
            with col:
                if t is None:
                    if plus_page:
                        card_button("tab_plus", C.tab_html("Start", "play", False, plus=True), plus_page, label="Start")
                    else:
                        card_button("tab_plus", C.tab_html("Continue", "play", False, plus=True),
                                    callback=_continue, args=(store,), label="Continue learning")
                else:
                    label, ic, pg = t
                    card_button(f"tab_{pg}", C.tab_html(label, ic, NAV_ACTIVE.get(page, page) == pg), pg, label=label)


def _continue(store) -> None:
    from ..progress import next_mission_id
    user = S.current_user()
    mid = next_mission_id(store, user, user.id) if user else None
    S.go("mission", mission=mid) if mid else S.go("progress")
