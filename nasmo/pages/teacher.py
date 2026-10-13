"""Teacher pages. Every data call also enforces the teacher role in the
service layer, so these pages are not the only line of defence."""
from __future__ import annotations

from ..ui.sx import st
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import BarChart, Reference
from datetime import datetime

from .. import admin, auth, config
from .. import certificates as certs
from .. import resources as res
from ..content.missions import TYPE_LABELS
from ..content.stages import STAGE_BY_ID, STAGES
from ..progress import all_missions, summarize
from ..store import StoreError
from ..ui import components as C
from ..ui import layout as L
from ..ui import session as S
from .student import _fmt_time, account_panel, md_escape

STAGE_OPTS = {s["id"]: (s["title"] if s["id"] == "f" else f'{s["title"]} - {s["subtitle"]}') for s in STAGES}


def _report_data(store, user, include_demo: bool):
    """Build the three datasets used by the complete analysis exports."""
    overview = admin.student_overview(store, user, include_demo=include_demo)
    student_ids = {row["id"] for row in overview}
    missions = all_missions(store)
    progress_rows = [r for r in store.select("mission_progress") if r.get("user_id") in student_ids]
    by_mission = {}
    for row in progress_rows:
        by_mission.setdefault(row.get("mission_id"), []).append(row)
    mission_report = []
    for mission in missions:
        rows = by_mission.get(mission["id"], [])
        completed = [r for r in rows if r.get("status") == "completed"]
        mission_report.append({
            "stage": STAGE_BY_ID[mission["stage"]]["title"],
            "mission": mission["title"],
            "started": len(rows),
            "completed": len(completed),
            "average_score": round(sum(float(r.get("score") or 0) for r in completed) / len(completed)) if completed else None,
        })
    attempts = [a for a in store.select("attempts") if a.get("user_id") in student_ids]
    attempts_report = []
    names = {row["id"]: row["display_name"] for row in overview}
    mission_names = {m["id"]: m["title"] for m in missions}
    for a in attempts:
        attempts_report.append({
            "student": names.get(a.get("user_id"), "Unknown"),
            "mission": mission_names.get(a.get("mission_id"), a.get("mission_id", "")),
            "step": a.get("step_id", ""),
            "result": "Correct" if a.get("correct") else "Incorrect",
            "date": a.get("created_at", ""),
        })
    return overview, mission_report, attempts_report


def _pdf_text(value) -> str:
    """Names and titles typed by people go into PDF paragraphs, which read <tags>: escape them."""
    from xml.sax.saxutils import escape
    return escape(str(value))


def _build_analysis_xlsx(overview, mission_report, attempts_report) -> bytes:
    """Create a workbook containing student, mission, and answer analysis."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Students"
    headers = ["Student", "Username", "Progress %", "Missions completed", "Total missions", "Average score %", "Certificates", "Last activity"]
    ws.append(headers)
    for s in overview:
        ws.append([s.get("display_name", ""), s.get("username", ""), s.get("percent", 0), s.get("completed", 0), s.get("total", 0), s.get("avg_score", 0), s.get("certificates", 0), s.get("last_activity", "")])
    ws2 = wb.create_sheet("Missions")
    ws2.append(["Stage", "Mission", "Started", "Completed", "Average score %"])
    for m in mission_report:
        ws2.append([m["stage"], m["mission"], m["started"], m["completed"], m["average_score"]])
    ws3 = wb.create_sheet("Attempts")
    ws3.append(["Student", "Mission", "Step", "Result", "Date"])
    for a in attempts_report:
        ws3.append([a["student"], a["mission"], a["step"], a["result"], a["date"]])
    for sheet in wb.worksheets:
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        for cell in sheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="39217C")
            cell.alignment = Alignment(wrap_text=True)
        for column in sheet.columns:
            letter = column[0].column_letter
            width = min(max(max(len(str(c.value or "")) for c in column) + 2, 12), 42)
            sheet.column_dimensions[letter].width = width
    out = BytesIO()
    wb.save(out)
    return out.getvalue()


def _build_analysis_pdf(overview, mission_report, attempts_report) -> bytes:
    """Create a real multi-section PDF; return bytes suitable for st.download_button."""
    out = BytesIO()
    doc = SimpleDocTemplate(out, pagesize=A4, rightMargin=32, leftMargin=32, topMargin=34, bottomMargin=34)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="NasmoTitle", parent=styles["Title"], textColor=colors.HexColor("#39217c"), spaceAfter=8))
    styles.add(ParagraphStyle(name="NasmoSection", parent=styles["Heading2"], textColor=colors.HexColor("#6b46c1"), spaceBefore=12, spaceAfter=6))
    styles.add(ParagraphStyle(name="NasmoSmall", parent=styles["BodyText"], fontSize=7, leading=9, wordWrap="CJK"))
    story = [Paragraph("Nasmo Informatics Lab", styles["NasmoTitle"]), Paragraph("Complete Student Progress Analysis", styles["Heading2"]), Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["BodyText"]), Spacer(1, 10)]
    avg_progress = round(sum(int(s.get("percent", 0) or 0) for s in overview) / len(overview)) if overview else 0
    story += [Paragraph("Overview", styles["NasmoSection"]), Paragraph(f"Students: {len(overview)} &nbsp;&nbsp; Average progress: {avg_progress}% &nbsp;&nbsp; Mission records: {len(mission_report)} &nbsp;&nbsp; Answer attempts: {len(attempts_report)}", styles["BodyText"])]
    story.append(Paragraph("Student Summary", styles["NasmoSection"]))
    student_data = [["Student", "Username", "Progress", "Completed", "Avg. score", "Certificates"]]
    student_data += [[str(s.get("display_name", "")), str(s.get("username", "")), f"{s.get('percent', 0)}%", f"{s.get('completed', 0)}/{s.get('total', 0)}", f"{s.get('avg_score', 0)}%", str(s.get("certificates", 0))] for s in overview]
    t = Table([[Paragraph(_pdf_text(c), styles["NasmoSmall"]) for c in row] for row in student_data], repeatRows=1, colWidths=[120, 75, 48, 58, 55, 55])
    t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#39217c")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#ddd6ee")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f7f4fc")]), ("PADDING", (0,0), (-1,-1), 5)]))
    story.append(t)
    story.append(Paragraph("Mission Analysis", styles["NasmoSection"]))
    mission_data = [["Stage", "Mission", "Started", "Completed", "Avg. score"]] + [[m["stage"], m["mission"], str(m["started"]), str(m["completed"]), (f"{m['average_score']}%" if m["average_score"] is not None else "—")] for m in mission_report]
    mt = Table([[Paragraph(_pdf_text(c), styles["NasmoSmall"]) for c in row] for row in mission_data], repeatRows=1, colWidths=[75, 210, 45, 50, 55])
    mt.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#39217c")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#ddd6ee")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f7f4fc")]), ("PADDING", (0,0), (-1,-1), 4)]))
    story.append(mt)
    story.append(Paragraph("Answer Attempts (latest records)", styles["NasmoSection"]))
    attempt_data = [["Student", "Mission", "Step", "Result", "Date"]] + [[a["student"], a["mission"], a["step"], a["result"], str(a["date"])[:16]] for a in attempts_report[:250]]
    at = Table([[Paragraph(_pdf_text(c), styles["NasmoSmall"]) for c in row] for row in attempt_data], repeatRows=1, colWidths=[95, 145, 45, 55, 95])
    at.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#39217c")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#ddd6ee")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f7f4fc")]), ("PADDING", (0,0), (-1,-1), 4)]))
    story.append(at)
    doc.build(story)
    return out.getvalue()


def _guard(fn):
    """Show data-layer errors as messages instead of a crashed page."""
    def wrapper(store):
        try:
            fn(store)
        except (StoreError, auth.AuthError, auth.PermissionDenied) as e:
            L.note("bad", str(e))
    wrapper.__name__ = fn.__name__
    return wrapper


def _reset_requests(store, user) -> None:
    """Students who pressed 'Forgot your password?'. The teacher generates a temporary password."""
    ss = st.session_state
    reqs = auth.list_reset_requests(store, user)
    shown_temp = [(k[len("reqtemp_"):], v) for k, v in list(ss.items()) if k.startswith("reqtemp_")]
    if not reqs and not shown_temp:
        return
    st.markdown('<div class="nl-root"><h2 class="nl-h2">Password requests</h2></div>', unsafe_allow_html=True)
    for sid, temp in shown_temp:
        who = store.get("users", {"id": sid}) or {}
        st.success(f"Temporary password for {who.get('display_name', '')} ({who.get('username', '')}) - shown only now. "
                   "Give it to her; she should change it from Account Settings:")
        st.code(temp)
        if st.button("Done", key=f"reqdone_{sid}"):
            del ss[f"reqtemp_{sid}"]
            st.rerun()
    for r in reqs:
        c1, c2, c3 = st.columns([3, 2, 2])
        c1.markdown(f"**{r['display_name']}** ({r['username']})")
        if c2.button("Generate temporary password", key=f"reqgen_{r['user_id']}"):
            ss[f"reqtemp_{r['user_id']}"] = auth.reset_student_password(store, user, r["user_id"])
            st.rerun()
        if c3.button("Dismiss request", key=f"reqno_{r['user_id']}"):
            auth.dismiss_reset_request(store, user, r["user_id"])
            st.rerun()


def _demo_flag() -> bool:
    return bool(st.session_state.get("include_demo", False))


def _demo_toggle() -> bool:
    st.toggle("Include demo data in the numbers", key="include_demo")
    return _demo_flag()


def _demo_banner(on: bool) -> None:
    if on:
        L.note("warn", "DEMO DATA is included in these numbers. Turn it off to see real students only.")


# -------------------------------------------------------------- impact report
@_guard
def impact_page(store) -> None:
    from .. import impact as IM
    from ..ui import impact_view as IV
    user = S.current_user()
    L.header()
    with st.container(key="pagepad"):
        L.page_title("Impact Report", "How the lab is affecting your students: participation, scores, progress and a full analysis.")
        demo = _demo_toggle()
        _demo_banner(demo)
        d = IM.build(store, user, include_demo=demo)
        stamp = datetime.now().strftime("%Y%m%d")
        c1, c2 = st.columns(2)
        c1.download_button("Download report (Arabic)", IV.report_html(d, "ar", standalone=True).encode("utf-8"),
                           file_name=f"impact_report_ar_{stamp}.html", mime="text/html", key="imp_dl_ar", use_container_width=True)
        c2.download_button("Download report (English)", IV.report_html(d, "en", standalone=True).encode("utf-8"),
                           file_name=f"impact_report_en_{stamp}.html", mime="text/html", key="imp_dl_en", use_container_width=True)
        st.caption("Open the downloaded file in your browser and choose Print, then Save as PDF.")
        st.markdown(IV.screen_css(), unsafe_allow_html=True)
        st.markdown(IV.report_html(d, st.session_state.get("lang", "en")), unsafe_allow_html=True)


# -------------------------------------------------------------- dashboard
@_guard
def dashboard(store) -> None:
    user = S.current_user()
    L.header()
    with st.container(key="pagepad"):
        L.page_title("Teacher Dashboard", "Real numbers from your students' saved progress.")
        demo = _demo_toggle()
        _demo_banner(demo)
        d = admin.dashboard(store, user, include_demo=demo)
        n_req = len(auth.list_reset_requests(store, user))
        if n_req:
            L.note("warn", f"{n_req} student(s) asked for a new password. Open Students to give each one a temporary password.")
        from .. import forum
        n_new = forum.new_questions(store, user)
        if n_new:
            L.note("warn", f"{n_new} new post(s) on the Discussion Board. Open it to read them.")
        if d["total_students"] == 0:
            L.note("", "No students yet. Students can create their own account from Student Login, "
                       "or you can add them in Students. You can also load demo data to see how the dashboard looks.")
        st.markdown(C.kpis_html([
            ("Students", str(d["total_students"])),
            (f"Active ({auth.get_setting(store, 'inactive_days')} days)", str(d["active_students"])),
            ("Missions completed", str(d["missions_completed"])),
            ("Average progress", f"{d['avg_progress']}%"),
            ("Average score", f"{d['avg_score']}%" if d["avg_score"] else "—"),
            ("Answer accuracy", f"{d['accuracy']}%" if d["attempts_total"] else "—"),
            ("Certificates", str(d["certificates"])),
        ]), unsafe_allow_html=True)
        st.markdown('<div class="nl-root"><h2 class="nl-h2">Progress by stage</h2></div>', unsafe_allow_html=True)
        st.markdown(C.table_html(
            ["Stage", "Average progress", "Students started", "Students finished"],
            [[x["stage"]["title"] if x["stage"]["id"] == "f" else f'{x["stage"]["title"]} - {x["stage"]["subtitle"]}',
              C.progress_bar_html(x["avg_percent"]), str(x["students_started"]), str(x["students_done"])]
             for x in d["stage_distribution"]], raw_cols={1}), unsafe_allow_html=True)
        st.markdown('<div class="nl-root"><h2 class="nl-h2">Students who need follow-up</h2></div>', unsafe_allow_html=True)
        if d["follow_up"]:
            st.markdown(C.table_html(["Student", "Progress", "Why"],
                                     [[s["display_name"], f'{s["completed"]}/{s["total"]}', "; ".join(s["reasons"])]
                                      for s in d["follow_up"]]), unsafe_allow_html=True)
        else:
            L.note("ok", "Nobody needs follow-up right now.")
        st.markdown('<div class="nl-root"><h2 class="nl-h2">Recent answers</h2></div>', unsafe_allow_html=True)
        if d["recent"]:
            st.markdown(C.table_html(["When", "Student", "Mission", "Step", "Result"],
                                     [[_fmt_time(r["at"]), r["name"], r["mission"], r["step"],
                                       "Correct" if r["correct"] else "Not yet"] for r in d["recent"]]),
                        unsafe_allow_html=True)
        else:
            L.note("", "No answers yet.")

        with st.expander("Demo data"):
            st.caption("Demo students are clearly named 'Demo Student …', cannot sign in, and are never mixed into "
                       "the numbers unless you switch the option above on.")
            c1, c2 = st.columns(2)
            if c1.button("Load demo data", key="demo_load"):
                n = admin.load_demo_data(store, user)
                st.success(f"Created {n} demo students." if n else "Demo students already exist.")
            if c2.button("Remove demo data", key="demo_remove"):
                n = admin.remove_demo_data(store, user)
                st.success(f"Removed {n} demo students.")
        L.footer()


# ---------------------------------------------------------------- students
@_guard
def students(store) -> None:
    user = S.current_user()
    ss = st.session_state
    L.header()
    with st.container(key="pagepad"):
        L.page_title("Students", "Search, review, manage and export.")
        demo = _demo_toggle()
        _demo_banner(demo)
        ov = admin.student_overview(store, user, include_demo=demo)

        _reset_requests(store, user)

        with st.expander("Add a student account"):
            with st.form("add_student", clear_on_submit=True):
                nm = st.text_input("Student name", placeholder="Example: Sara Ahmed")
                un = st.text_input("Username", placeholder="Enter a username", autocomplete="off")
                pw = st.text_input(f"Temporary password (at least {config.STUDENT_MIN_PASSWORD} characters)", type="password",
                                   placeholder="Enter a temporary password", autocomplete="new-password")
                ok = st.form_submit_button("Create student")
            if ok:
                try:
                    auth.create_student_by_teacher(store, user, un, nm, pw)
                    st.success("Student created. Give them the username and the temporary password.")
                    st.rerun()
                except auth.AuthError as e:
                    st.error(str(e))

        q = st.text_input("Search by name or username", key="stu_q").strip().lower()
        shown = [s for s in ov if q in s["display_name"].lower() or q in s["username"].lower()] if q else ov
        if not ov:
            L.note("", "No students yet.")
            return
        st.markdown(C.table_html(
            ["Name", "Username", "Progress", "Average score", "Last activity", "Certificates", "Status"],
            [[s["display_name"] + (" (DEMO)" if s["is_demo"] else ""), s["username"],
              C.progress_bar_html(s["percent"], f'{s["completed"]}/{s["total"]}'),
              f'{s["avg_score"]}%' if s["completed"] else "—", _fmt_time(s["last_activity"]),
              str(s["certificates"]), "Active" if s["active"] else "Disabled"] for s in shown],
            raw_cols={2}), unsafe_allow_html=True)
        if not shown:
            L.note("", "No student matches your search.")

        c1, c2 = st.columns(2)
        c1.download_button("Export students (CSV)", admin.export_csv(store, user, demo),
                           file_name="nasmo_students.csv", mime="text/csv", key="dl_students")
        c2.download_button("Export all answers (CSV)", admin.export_attempts_csv(store, user, demo),
                           file_name="nasmo_answers.csv", mime="text/csv", key="dl_attempts")

        if not shown:
            return
        st.markdown('<div class="nl-root"><h2 class="nl-h2">Student details</h2></div>', unsafe_allow_html=True)
        by_id = {s["id"]: s for s in shown}
        sid = st.selectbox("Choose a student", list(by_id), format_func=lambda i: f'{by_id[i]["display_name"]} ({by_id[i]["username"]})',
                           key="stu_pick")
        det = admin.student_detail(store, user, sid)
        u, summ = det["user"], det["summary"]
        st.markdown(C.kpis_html([
            ("Missions completed", f'{summ["completed"]}/{summ["total"]}'),
            ("Average score", f'{summ["avg_score"]}%' if summ["completed"] else "—"),
            ("Last activity", _fmt_time(summ["last_activity"])),
            ("Last sign-in", _fmt_time(u["last_login"])),
        ]), unsafe_allow_html=True)
        # Individual PDF report: summary + stage progress chart, no spreadsheet export.
        pdf_buffer = BytesIO()
        font_path = config.ASSETS_DIR / "DejaVuSans.ttf"
        if font_path.exists() and "NasmoUnicode" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("NasmoUnicode", str(font_path)))
        pdf_font = "NasmoUnicode" if "NasmoUnicode" in pdfmetrics.getRegisteredFontNames() else "Helvetica"
        pdf = canvas.Canvas(pdf_buffer, pagesize=A4)
        page_w, page_h = A4
        pdf.setTitle(f"Student Progress - {u['display_name']}")
        pdf.setFillColor(colors.HexColor("#39217c"))
        pdf.setFont(pdf_font, 20)
        pdf.drawString(48, page_h - 58, "Nasmo Informatics Lab")
        pdf.setFont(pdf_font, 15)
        pdf.setFillColor(colors.HexColor("#29213f"))
        pdf.drawString(48, page_h - 88, "Student Progress Report")
        pdf.setFont(pdf_font, 11)
        pdf.drawString(48, page_h - 116, f"Student: {u['display_name']}")
        pdf.drawString(48, page_h - 134, f"Username: {u['username']}")
        pdf.drawString(48, page_h - 152, f"Missions completed: {summ['completed']} / {summ['total']}")
        pdf.drawString(48, page_h - 170, f"Overall progress: {summ['percent']}%")
        pdf.drawString(48, page_h - 188, f"Average score: {summ['avg_score']}%" if summ['completed'] else "Average score: No completed missions yet")
        pdf.drawString(48, page_h - 206, f"Last activity: {_fmt_time(summ['last_activity'])}")
        pdf.setFont(pdf_font, 12)
        pdf.drawString(48, page_h - 246, "Progress by stage")
        y = page_h - 278
        for stage in STAGES:
            v = summ['stages'].get(stage['id'], {})
            label = stage['title'] if stage['id'] == 'f' else f"{stage['title']} - {stage['subtitle']}"
            pct = max(0, min(100, int(v.get('percent', 0))))
            pdf.setFillColor(colors.HexColor("#302064")); pdf.setFont(pdf_font, 10)
            pdf.drawString(48, y, label[:54])
            pdf.setFillColor(colors.HexColor("#e8e2f4")); pdf.roundRect(250, y - 3, 220, 12, 5, fill=1, stroke=0)
            if pct:
                pdf.setFillColor(colors.HexColor("#6b46c1")); pdf.roundRect(250, y - 3, 220 * pct / 100, 12, 5, fill=1, stroke=0)
            pdf.setFillColor(colors.HexColor("#302064")); pdf.drawRightString(520, y, f"{pct}%")
            y -= 34
        pdf.setFillColor(colors.HexColor("#777184")); pdf.setFont("Helvetica-Oblique", 8)
        pdf.drawString(48, 38, "Generated from saved training progress. Internal training report, not an official competition certificate.")
        pdf.save()
        st.download_button("Download Student Progress PDF", data=pdf_buffer.getvalue(),
                           file_name=f"student-progress-{u['username']}.pdf", mime="application/pdf",
                           key=f"student_pdf_{sid}")
        trs = []
        for m in det["missions"]:
            r = det["rows"].get(m["id"])
            status = {"completed": "Completed", "in_progress": "In progress"}.get((r or {}).get("status"), "Not started")
            tries = sum(int(x.get("attempts", 0)) for x in ((r or {}).get("step_results") or {}).values())
            wrong = sum(int(x.get("wrong", 0)) for x in ((r or {}).get("step_results") or {}).values())
            trs.append([STAGE_BY_ID[m["stage"]]["title"], m["title"], status,
                        f'{r["score"]}%' if r and r["status"] == "completed" else "—", str(tries) if r else "—", str(wrong) if r else "—"])
        st.markdown(C.table_html(["Stage", "Mission", "Status", "Score", "Attempts", "Wrong"], trs), unsafe_allow_html=True)

        codes = [(m, r["step_results"][s["id"]]["code"]) for m in det["missions"]
                 for r in [det["rows"].get(m["id"])] if r
                 for s in m["steps"] if s["id"] in (r.get("step_results") or {}) and r["step_results"][s["id"]].get("code")]
        if codes:
            with st.expander("Code the student wrote (Solve the Problem steps)"):
                for m, code in codes:
                    st.markdown(f"**{md_escape(m['title'])}**")
                    st.code(code, language="cpp")

        if det["attempts"]:
            with st.expander("Latest answers"):
                st.markdown(C.table_html(["When", "Mission", "Step", "Result"],
                                         [[_fmt_time(a["created_at"]), a["mission_id"], a["step_id"],
                                           "Correct" if a["correct"] else "Not yet"] for a in det["attempts"][:30]]),
                            unsafe_allow_html=True)
        if det["certificates"]:
            with st.expander("Certificates"):
                st.markdown(C.table_html(["Certificate", "Serial", "Issued", "Status"],
                                         [[c["title"], c["serial"], str(c["issued_at"])[:10],
                                           "Revoked" if c["revoked"] else "Valid"] for c in det["certificates"]]),
                            unsafe_allow_html=True)

        if u["is_demo"]:
            L.note("warn", "Demo student: no account actions (it cannot sign in). Remove all demo data from the Dashboard.")
            return
        st.markdown('<div class="nl-root"><h2 class="nl-h2">Account actions</h2></div>', unsafe_allow_html=True)
        a1, a2 = st.columns(2)
        if a1.button("Reset password", key=f"rp_{sid}"):
            temp = auth.reset_student_password(store, user, sid)
            ss[f"temp_{sid}"] = temp
        if ss.get(f"temp_{sid}"):
            st.success("New temporary password (shown only now - give it to the student):")
            st.code(ss[f"temp_{sid}"])
        if u["active"]:
            if a2.button("Disable account", key=f"dis_{sid}"):
                auth.set_student_active(store, user, sid, False)
                st.rerun()
        else:
            if a2.button("Enable account", key=f"en_{sid}"):
                auth.set_student_active(store, user, sid, True)
                st.rerun()
        with st.expander("Delete this student"):
            st.warning("This permanently deletes the account, progress, answers and certificates. It cannot be undone.")
            typed = st.text_input(f"Type the username ({u['username']}) to confirm", key=f"del_t_{sid}")
            if st.button("Delete permanently", key=f"del_{sid}"):
                if typed.strip().lower() == u["username"]:
                    admin.delete_student(store, user, sid)
                    st.success("Student deleted.")
                    st.rerun()
                else:
                    st.error("The username does not match.")
        L.footer()


# ----------------------------------------------------------------- reports
@_guard
def reports(store) -> None:
    user = S.current_user()
    L.header()
    with st.container(key="pagepad"):
        L.page_title("Progress Reports", "How the class is doing, stage by stage and mission by mission.")
        demo = _demo_toggle()
        _demo_banner(demo)
        ov = admin.student_overview(store, user, include_demo=demo)
        ids = {s["id"] for s in ov}
        if not ov:
            L.note("", "No students yet, so there is nothing to report.")
            return
        missions = all_missions(store)
        rows = [r for r in store.select("mission_progress") if r["user_id"] in ids]
        by_m: dict[str, list[dict]] = {}
        for r in rows:
            by_m.setdefault(r["mission_id"], []).append(r)
        attempts = [a for a in store.select("attempts") if a["user_id"] in ids]
        wrong_by_m: dict[str, int] = {}
        for a in attempts:
            if not a["correct"]:
                wrong_by_m[a["mission_id"]] = wrong_by_m.get(a["mission_id"], 0) + 1
        trs = []
        for m in missions:
            rs = by_m.get(m["id"], [])
            done = [r for r in rs if r["status"] == "completed"]
            avg = round(sum(r["score"] for r in done) / len(done)) if done else None
            trs.append([STAGE_BY_ID[m["stage"]]["title"], m["title"], f"{len(rs)}/{len(ov)}",
                        f"{len(done)}/{len(ov)}", f"{avg}%" if avg is not None else "—", str(wrong_by_m.get(m["id"], 0))])
        st.markdown('<div class="nl-root"><h2 class="nl-h2">Missions</h2></div>', unsafe_allow_html=True)
        st.markdown(C.table_html(["Stage", "Mission", "Started", "Completed", "Average score", "Wrong answers"], trs),
                    unsafe_allow_html=True)
        hardest = sorted(((wrong_by_m.get(m["id"], 0), m["title"]) for m in missions), reverse=True)[:3]
        if hardest and hardest[0][0]:
            L.note("", "Most wrong answers: " + "; ".join(f"{t} ({n})" for n, t in hardest if n))
        ov_report, mission_report, attempts_report = _report_data(store, user, demo)
        xlsx_data = _build_analysis_xlsx(ov_report, mission_report, attempts_report)
        pdf_data = _build_analysis_pdf(ov_report, mission_report, attempts_report)
        c1, c2 = st.columns(2)
        c1.download_button("Download Complete Analysis (Excel)", xlsx_data,
                           file_name="nasmo_complete_analysis.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           key="rep_dl_excel")
        c2.download_button("Download Complete Analysis (PDF)", pdf_data,
                           file_name="nasmo_complete_analysis.pdf", mime="application/pdf",
                           key="rep_dl_pdf")
        L.footer()


# ----------------------------------------------------------------- content
@_guard
def content(store) -> None:
    user = S.current_user()
    L.header()
    with st.container(key="pagepad"):
        L.page_title("Missions and Content", "Show or hide missions, add your own, and manage resources.")
        t1, t2, t3, t4 = st.tabs(["Missions", "Review questions", "Add a mission", "Resources"])
        missions = all_missions(store, include_inactive=True)
        with t1:
            for m in missions:
                c1, c2 = st.columns([4, 1])
                tag = " · teacher-made" if m["custom"] else ""
                c1.markdown(f"**{md_escape(m['title'])}** — {STAGE_BY_ID[m['stage']]['title']}{tag}"
                            + ("" if m["active"] else "  \n:orange[Hidden from students]"))
                if c2.button("Show" if not m["active"] else "Hide", key=f"vis_{m['id']}"):
                    admin.set_mission_active(store, user, m["id"], not m["active"])
                    st.rerun()
                if m["custom"] and c2.button("Delete", key=f"delm_{m['id']}"):
                    admin.delete_custom_mission(store, user, m["id"])
                    st.rerun()
        with t2:
            by_id = {m["id"]: m for m in missions}
            mid = st.selectbox("Mission", list(by_id), format_func=lambda i: f'{STAGE_BY_ID[by_id[i]["stage"]]["title"]} · {by_id[i]["title"]}',
                               key="rev_pick")
            m = by_id[mid]
            for i, s in enumerate(m["steps"], 1):
                st.markdown(f"**Step {i} · {TYPE_LABELS.get(s['type'], s['type'])}**")
                st.write(s["prompt"])
                if s.get("code"):
                    st.code(s["code"], language="cpp")
                if "options" in s:
                    for j, o in enumerate(s["options"]):
                        st.markdown(("✅ " if j == s["answer"] else "◻ ") + md_escape(o))
                elif "answer" in s:
                    st.markdown("Accepted answer(s): " + ", ".join(f"`{a}`" for a in s["answer"]))
                else:
                    st.caption("Free-text explanation, checked against key ideas.")
                st.caption(s["explain_en"])
                st.divider()
        with t3:
            st.caption("A teacher-made mission has one multiple-choice question.")
            with st.form("add_mission", clear_on_submit=True):
                stg = st.selectbox("Stage", list(STAGE_OPTS), format_func=STAGE_OPTS.get, key="am_stage")
                title = st.text_input("Mission title")
                summ = st.text_input("Short description")
                q = st.text_area("Question")
                code = st.text_area("Code to show (optional)", height=120)
                opts = [st.text_input(f"Option {i + 1}") for i in range(4)]
                correct = st.selectbox("Correct option", [1, 2, 3, 4])
                ex_en = st.text_area("Explanation (English)")
                ex_ar = st.text_area("Explanation (Arabic)")
                ok = st.form_submit_button("Add mission", type="primary")
            if ok:
                try:
                    given = [o for o in opts if o.strip()]
                    idx = [i for i, o in enumerate(opts) if o.strip()].index(correct - 1) if opts[correct - 1].strip() else -1
                    admin.add_custom_mission(store, user, stg, title, summ, q, given, idx, ex_en, ex_ar, code)
                    st.success("Mission added. Students see it in its stage.")
                except (auth.AuthError, ValueError):
                    st.error("Please fill in the title, the question, at least two options, and make sure the correct option is not empty.")
        with t4:
            _resources_admin(store, user)
        L.footer()


def _resources_admin(store, user) -> None:
    rows = res.list_resources(store, include_hidden=True)
    with st.expander("Add a resource"):
        with st.form("add_res", clear_on_submit=True):
            title = st.text_input("Title")
            url = st.text_input("Link (https://…)")
            stage = st.selectbox("Stage", ["all", *STAGE_OPTS], format_func=lambda i: "All stages" if i == "all" else STAGE_OPTS[i], key="ar_stage")
            kind = st.selectbox("Type", res.KINDS, key="ar_kind")
            desc = st.text_input("Description (optional)")
            ok = st.form_submit_button("Add resource", type="primary")
        if ok:
            try:
                res.add_resource(store, user, title, url, stage, kind, desc)
                st.success("Resource added.")
                st.rerun()
            except auth.AuthError as e:
                st.error(str(e))
    for r in rows:
        with st.expander(f"{r['title']}" + ("" if r["visible"] else "  (hidden)")):
            st.caption(f"{r['kind']} · {r['url']}")
            c1, c2 = st.columns(2)
            if c1.button("Show" if not r["visible"] else "Hide", key=f"rv_{r['id']}"):
                res.update_resource(store, user, r["id"], r["title"], r["url"], r["stage_id"], r["kind"],
                                    r.get("description") or "", not r["visible"])
                st.rerun()
            if c2.button("Delete", key=f"rd_{r['id']}"):
                res.delete_resource(store, user, r["id"])
                st.rerun()


# ------------------------------------------------------------ certificates
@_guard
def certificates(store) -> None:
    user = S.current_user()
    L.header()
    with st.container(key="pagepad"):
        L.page_title("Certificates", "Internal training certificates issued to students.")
        demo = _demo_toggle()
        names = {s["id"]: s["display_name"] for s in admin.student_overview(store, user, include_demo=demo)}
        rows = [c for c in store.select("certificates", order=[("issued_at", "desc")]) if c["user_id"] in names]
        L.note("", f"A certificate is issued automatically when a student completes every mission of a stage with an "
                   f"average score of at least {auth.get_setting(store, 'cert_pass_score')}% (change it in Settings).")
        with st.expander("Certificate designs students can choose from"):
            from . import certgallery
            certgallery.gallery("Student Name", selectable=False)
        if not rows:
            L.note("", "No certificates have been earned yet.")
            return
        st.markdown(C.table_html(["Student", "Certificate", "Serial", "Issued", "Status"],
                                 [[names[c["user_id"]], c["title"], c["serial"], str(c["issued_at"])[:10],
                                   "Revoked" if c["revoked"] else "Valid"] for c in rows]), unsafe_allow_html=True)
        by = {c["id"]: c for c in rows}
        cid = st.selectbox("Certificate", list(by), format_func=lambda i: f'{names[by[i]["user_id"]]} · {by[i]["title"]}', key="cert_pick")
        c = by[cid]
        if c["revoked"]:
            if st.button("Restore certificate", key="cert_restore"):
                certs.set_revoked(store, user, cid, False); st.rerun()
        else:
            if st.button("Revoke certificate", key="cert_revoke"):
                certs.set_revoked(store, user, cid, True); st.rerun()
        L.footer()


# ---------------------------------------------------------------- settings
@_guard
def settings(store) -> None:
    user = S.current_user()
    ss = st.session_state
    L.header()
    with st.container(key="pagepad"):
        L.page_title("Settings", "Lab rules and your account.")
        with st.form("lab_settings"):
            reg = st.toggle("Students can create their own accounts", value=auth.get_setting(store, "registration_open") == "1")
            score = st.number_input("Minimum average score for a certificate (%)", 0, 100,
                                    int(auth.get_setting(store, "cert_pass_score") or 60))
            days = st.number_input("Days without activity before a student needs follow-up", 1, 90,
                                   int(auth.get_setting(store, "inactive_days") or 7))
            ok = st.form_submit_button("Save settings", type="primary")
        if ok:
            auth.set_setting(store, user, "registration_open", "1" if reg else "0")
            auth.set_setting(store, user, "cert_pass_score", str(int(score)))
            auth.set_setting(store, user, "inactive_days", str(int(days)))
            st.success("Settings saved.")
        with st.expander("Teachers"):
            for t in auth.list_teachers(store, user):
                c1, c2 = st.columns([3, 2])
                c1.markdown(f"**{t['display_name']}** ({t['username']})" + ("  - you" if t["id"] == user.id else ""))
                if t["id"] != user.id and c2.button("Reset password", key=f"trp_{t['id']}"):
                    ss[f"ttemp_{t['id']}"] = auth.reset_teacher_password(store, user, t["id"])
                if ss.get(f"ttemp_{t['id']}"):
                    st.success("New temporary password (shown only now - give it to the teacher; she changes it in Account Settings):")
                    st.code(ss[f"ttemp_{t['id']}"])
        with st.expander("Add another teacher"):
            with st.form("add_teacher", clear_on_submit=True):
                nm = st.text_input("Name", placeholder="Teacher name")
                un = st.text_input("Username", placeholder="Enter a username", autocomplete="off")
                pw = st.text_input(f"Password (at least {config.TEACHER_MIN_PASSWORD} characters)", type="password",
                                   placeholder="Enter a password", autocomplete="new-password")
                ok2 = st.form_submit_button("Create teacher account")
            if ok2:
                try:
                    auth.create_teacher(store, user, un, nm, pw)
                    st.success("Teacher account created.")
                except auth.AuthError as e:
                    st.error(str(e))
        account_panel(store, user)
        L.footer()
