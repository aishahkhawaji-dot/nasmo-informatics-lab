"""Renders real page HTML (captured through the fake Streamlit) into static files for a visual check.
Usage: python tools/render_pages.py OUTDIR"""
import os, sys, tempfile, runpy
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
os.environ["NASMO_DATA_DIR"] = tempfile.mkdtemp(prefix="nasmo_render_")
os.environ["NASMO_SETUP_CODE"] = "X-render-code"
os.environ["NASMO_RAISE"] = "1"
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import stub_streamlit as T
st = T.install()
from nasmo.ui import style
from nasmo.content.missions import MISSION_BY_ID

def run(page=None, params=None, pressed=(), values=None):
    if page: st.session_state["page"], st.session_state["params"] = page, params or {}
    T.VALUES.update(values or {}); T.PRESSED.update(pressed)
    for _ in range(6):
        T.reset_run()
        try: runpy.run_path(str(ROOT / "app.py"), run_name="__main__"); break
        except T.RerunException: continue
    return list(T.OUT)

def save(name, chunks, out, theme):
    body = "\n".join(c for c in chunks if not c.startswith(("[component", "[expander")))
    html = f'<!doctype html><html data-nl="{theme}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{style.build_css_static(theme)}</head><body><div style="max-width:1100px;margin:0 auto;padding:0 16px">{body}</div></body></html>'
    (out / f"{name}_{theme}.html").write_text(html, encoding="utf-8")

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
run("teacher_login", values={"ft_code": "X-render-code", "ft_name": "Teacher", "ft_user": "teach1", "ft_pw": "correct-horse-1", "ft_pw2": "correct-horse-1"}, pressed=["Create teacher account"])
run("t_dashboard", pressed=["demo_load"])
run("t_dashboard", values={"include_demo": True})
dash = run("t_dashboard")
for th in ("light", "dark"):
    save("dashboard", dash, out, th)
run("t_students", values={"Student name": "Sara", "Username": "sara", "Temporary password (at least 6 characters)": "pass1234"}, pressed=["Create student"])
run(pressed=["btn_logout"])
run("student_login", values={"student_u": "sara", "student_p": "pass1234"}, pressed=["Sign in"])
m = MISSION_BY_ID["f-1"]; s0 = m["steps"][0]
run("mission", {"mission": "f-1"}, values={f"ans_f-1_{s0['id']}": (s0["answer"] + 1) % len(s0["options"])}, pressed=[f"check_f-1_{s0['id']}"])
mission = run()
for th in ("light", "dark"):
    save("mission", mission, out, th)
save("progress", run("progress"), out, "light")
print("ok")

# home as a visitor (sidebar chunks come first in the capture; the real layout puts them left)
run(pressed=["btn_logout"])
home = run("home")
side = [c for c in home if 'nl-login' in c or 'nl-nav' in c or 'nl-deco' in c]
for th in ("dark", "light"):
    st.session_state["theme"] = th
    h = run("home")
    keep = [c for c in h if not any(k in c for k in ('class="nl-nav', 'class="nl-login', 'class="nl-deco', 'nl-tab'))]
    save("home", keep, out, th)
