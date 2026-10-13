"""HTML for the impact report: used on screen (inside the app theme) and as a stand-alone file
the teacher can open, print or save as PDF. Texts come as English / Arabic pairs, so the file
does not depend on the session language. Every name from the data goes through html.escape."""
from __future__ import annotations

import html

from .. import i18n, impact
from . import components as C

e = html.escape

CSS = """
.imp{--i-ink:var(--ink,#1d1550);--i-text:var(--text,#38366a);--i-muted:var(--muted,#6b6a92);--i-line:var(--line,#e6e0f8);
--i-panel:var(--panel,#fff);--i-lav:var(--lav,#efe9ff);--i-brand:#6a47e8;--i-good:#1f9d63;--i-watch:#d9822b;--i-note:#4a78d8;
color:var(--i-text);font-family:inherit;line-height:1.6}
.imp *{box-sizing:border-box}
.imp h2{font-size:20px;margin:26px 0 10px;color:var(--i-ink)}
.imp h1{font-size:26px;margin:0 0 4px;color:var(--i-ink)}
.imp .sub{color:var(--i-muted);margin:0 0 14px;font-size:14px}
.imp .kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.imp .kpi{background:var(--i-panel);border:1px solid var(--i-line);border-radius:14px;padding:12px 14px}
.imp .kpi b{display:block;font-size:26px;color:var(--i-ink);line-height:1.2}
.imp .kpi span{font-size:13px;color:var(--i-muted)}
.imp .ins{display:flex;flex-direction:column;gap:8px}
.imp .in{background:var(--i-panel);border:1px solid var(--i-line);border-inline-start:5px solid var(--i-note);border-radius:12px;padding:10px 14px;font-size:14.5px}
.imp .in.good{border-inline-start-color:var(--i-good)} .imp .in.watch{border-inline-start-color:var(--i-watch)}
.imp table{width:100%;border-collapse:collapse;background:var(--i-panel);border:1px solid var(--i-line);border-radius:12px;overflow:hidden;font-size:14px}
.imp th,.imp td{padding:8px 10px;border-bottom:1px solid var(--i-line);text-align:start;vertical-align:middle}
.imp th{background:var(--i-lav);color:var(--i-ink);font-weight:700}
.imp tr:last-child td{border-bottom:0}
.imp .bar{height:10px;border-radius:6px;background:var(--i-lav);overflow:hidden;min-width:70px}
.imp .bar i{display:block;height:100%;background:var(--i-brand);border-radius:6px}
.imp .cols{display:flex;align-items:flex-end;gap:8px;height:150px;background:var(--i-panel);border:1px solid var(--i-line);border-radius:12px;padding:12px 12px 6px}
.imp .col{flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;height:100%;font-size:12px;color:var(--i-muted)}
.imp .col i{display:block;width:100%;max-width:46px;background:var(--i-brand);border-radius:6px 6px 0 0;min-height:2px}
.imp .col b{color:var(--i-ink);font-size:12px}
.imp .two{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.imp .recs{margin:0;padding-inline-start:22px}
.imp .recs li{margin:5px 0}
.imp .limits{background:var(--i-lav);border-radius:12px;padding:12px 16px;font-size:13.5px;margin-top:22px}
.imp .up{color:var(--i-good);font-weight:700} .imp .down{color:#c0392b;font-weight:700}
.imp .empty{color:var(--i-muted);font-size:14px}
.imp bdi{unicode-bidi:isolate}
.imp.rtl{direction:rtl;text-align:right}
@media (max-width:760px){.imp .two{grid-template-columns:1fr}}
@media print{.imp .in,.imp .kpi,.imp table,.imp .cols{break-inside:avoid}.imp h2{break-after:avoid}}
"""

STANDALONE_CSS = """
@page{size:A4;margin:14mm}
body{margin:0;padding:18px;background:#fff;color:#38366a;font-family:'Segoe UI',Tahoma,Arial,sans-serif}
@media print{body{padding:0}}
"""


def screen_css() -> str:
    """The on-screen fragment needs this style block once (kept separate so the page can inject it first)."""
    return f"<style>{CSS}</style>"


def _fmt(v, suffix="") -> str:
    return "—" if v is None else f"{v}{suffix}"


def report_html(d: dict, lang: str = "en", standalone: bool = False) -> str:
    """The whole report. lang: 'en' or 'ar'. standalone=True returns a complete HTML document."""
    ar = lang == "ar"

    def T(en: str, arb: str) -> str:
        return arb if ar else en

    with i18n.force(lang):
        def stage_name(s) -> str:
            t, sub = i18n.tr(s["title"]), i18n.tr(s["subtitle"])
            return f"{t} · {sub}" if s["id"] != "f" else f"{t} · {sub}"
        stage_rows = [(stage_name(s), s) for s in d["by_stage"]]

    p, f, c = d["participation"], d["performance"], d["curve"]
    n = d["students"]
    out: list[str] = []

    def h2(en, arb):
        out.append(f"<h2>{e(T(en, arb))}</h2>")

    def bar(pct) -> str:
        w = max(0, min(100, pct or 0))
        return f'<div class="bar"><i style="width:{w}%"></i></div>'

    out.append(f'<h1>{e(T("Impact report: what the lab did for the students", "تقرير الأثر: ماذا قدّم المعمل للطالبات"))}</h1>')
    period = ""
    if d["period"]["from"]:
        period = T(f" · Activity from {d['period']['from']} to {d['period']['to']}",
                   f" · النشاط من {d['period']['from']} إلى {d['period']['to']}")
    demo = T(" · INCLUDES DEMO DATA", " · يتضمن بيانات تجريبية") if d.get("include_demo") else ""
    out.append(f'<p class="sub">{e(T("Created", "أُعدّ في"))} {e(d["generated_at"])}{e(period)}{e(demo)}</p>')

    kp = [
        (T("Students", "الطالبات"), str(n)),
        (T("Started practising", "بدأن التدرّب"), f"{p['started']} ({_fmt(p['started_pct'], '%')})"),
        (T("Average progress", "متوسط التقدّم"), f"{p['avg_progress']}%"),
        (T("Average score", "متوسط الدرجات"), _fmt(f["avg_mission_score"], "%")),
        (T("Right on first try", "صحيح من المحاولة الأولى"), _fmt(f["first_try_pct"], "%")),
        (T("Missions completed", "مهمات مكتملة"), str(p["missions_completed"])),
        (T("Answers submitted", "إجابات مُرسلة"), str(p["answers_total"])),
        (T("Certificates", "الشهادات"), str(p["certificates"])),
    ]
    out.append('<div class="kpis">' + "".join(f'<div class="kpi"><b><bdi dir="ltr">{e(v)}</bdi></b><span>{e(k)}</span></div>' for k, v in kp) + "</div>")

    h2("Situation analysis", "تحليل الموقف")
    out.append('<div class="ins">' + "".join(f'<div class="in {e(i["kind"])}">{e(i[lang])}</div>' for i in d["insights"]) + "</div>")

    if p["started"]:
        h2("Participation", "المشاركة")
        total = max(n, 1)
        rows = [(T("Registered students", "الطالبات المسجّلات"), n),
                (T("Answered at least one question", "أجبن عن سؤال واحد على الأقل"), p["started"]),
                (T(f"Active in the last {d['inactive_days']} days", f"نشطن خلال آخر {d['inactive_days']} أيام"), p["active_recent"]),
                (T("Completed at least one mission", "أكملن مهمة واحدة على الأقل"), p["at_least_one"]),
                (T("Finished all missions", "أنهين كل المهمات"), p["finished_all"])]
        out.append(f'<table><tr><th>{e(T("Step","المرحلة"))}</th><th>{e(T("Students","الطالبات"))}</th><th></th></tr>' +
                   "".join(f"<tr><td>{e(k)}</td><td><bdi dir=ltr>{v} ({round(100 * v / total)}%)</bdi></td><td>{bar(100 * v / total)}</td></tr>"
                           for k, v in rows) + "</table>")

        h2("Scores and progress", "الدرجات والتقدّم")
        mx = max([b["count"] for b in f["bands"]] + [b["count"] for b in f["progress_buckets"]] + [1])

        def cols(items, unit):
            return '<div class="cols">' + "".join(
                f'<div class="col"><b>{x["count"]}</b><i style="height:{round(100 * x["count"] / mx)}%"></i><span>{e(x["label"])}{unit}</span></div>'
                for x in items) + "</div>"
        out.append('<div class="two"><div>'
                   f'<p class="sub">{e(T("Students by average mission score (%)", "الطالبات حسب متوسط درجات المهمات (%)"))}</p>{cols(f["bands"], "")}</div><div>'
                   f'<p class="sub">{e(T("Students by progress (% of missions completed)", "الطالبات حسب التقدّم (% من المهمات المكتملة)"))}</p>{cols(f["progress_buckets"], "")}</div></div>')
        out.append(f'<p class="sub" style="margin-top:8px">{e(T("Average wrong answers per step", "متوسط الإجابات الخاطئة لكل خطوة"))}: '
                   f'{_fmt(f["avg_wrong_per_step"])} · {e(T("Steps solved in the end", "خطوات حُلّت في النهاية"))}: {_fmt(f["steps_passed_pct"], "%")}</p>')

        h2("By stage", "حسب المرحلة")
        out.append("<table><tr>" + "".join(f"<th>{e(x)}</th>" for x in (
            T("Stage", "المرحلة"), T("Started", "بدأن"), T("Finished", "أنهين"), T("Average score", "متوسط الدرجة"),
            T("First-try %", "% من المحاولة الأولى"))) + "</tr>" +
                   "".join(f"<tr><td><bdi>{e(name)}</bdi></td><td><bdi dir=ltr>{s['started_students']} ({_fmt(s['started_pct'], '%')})</bdi></td>"
                           f"<td><bdi dir=ltr>{s['completed_students']} ({_fmt(s['completed_pct'], '%')})</bdi></td><td>{_fmt(s['avg_score'], '%')}</td>"
                           f"<td>{_fmt(s['first_try_pct'], '%')}</td></tr>" for name, s in stage_rows) + "</table>")

        h2("Skills (by question type)", "المهارات (حسب نوع السؤال)")
        out.append("<table><tr>" + "".join(f"<th>{e(x)}</th>" for x in (
            T("Skill", "المهارة"), T("Steps tried", "خطوات جُرّبت"), T("First-try %", "% من المحاولة الأولى"),
            T("Avg wrong", "متوسط الخطأ"))) + "</tr>" +
                   "".join(f"<tr><td>{e(impact.TYPE_AR[t['type']] if ar else t['type'])}</td><td>{t['steps_tried']}</td>"
                           f"<td>{_fmt(t['first_try_pct'], '%')}</td><td>{_fmt(t['avg_wrong'])}</td></tr>" for t in d["by_type"]) + "</table>")

        h2("Hardest steps", "أصعب الخطوات")
        if d["hardest"]:
            out.append("<table><tr>" + "".join(f"<th>{e(x)}</th>" for x in (
                T("Mission", "المهمة"), T("Step", "الخطوة"), T("Skill", "المهارة"), T("Students", "الطالبات"),
                T("First-try %", "% من المحاولة الأولى"))) + "</tr>" +
                       "".join(f"<tr><td><bdi>{e(h['mission'])}</bdi></td><td><bdi>{e(h['step'])}</bdi></td>"
                               f"<td>{e(impact.TYPE_AR[h['type']] if ar else h['type'])}</td><td>{h['students']}</td>"
                               f"<td>{h['first_try_pct']}%</td></tr>" for h in d["hardest"]) + "</table>")
        else:
            out.append(f'<p class="empty">{e(T("Needs a step tried by at least 3 students.", "يلزم أن تجرّب الخطوة 3 طالبات على الأقل."))}</p>')

        h2("Weekly activity (last 8 weeks)", "النشاط الأسبوعي (آخر 8 أسابيع)")
        wm = max([w["answers"] for w in d["weeks"]] + [1])
        out.append('<div class="cols">' + "".join(
            f'<div class="col"><b>{w["answers"]}</b><i style="height:{round(100 * w["answers"] / wm)}%"></i>'
            f'<span>{e(w["start"][5:])}</span></div>' for w in d["weeks"]) + "</div>")
        out.append(f'<p class="sub">{e(T("Bars = answers submitted; the label is the Sunday that starts the week.", "الأعمدة = الإجابات المُرسلة؛ التاريخ هو يوم الأحد الذي يبدأ به الأسبوع."))}</p>')

        h2("Learning trend", "اتجاه التعلّم")
        if c["students"] >= 1:
            def arrow(v):
                cls = "up" if v >= 5 else "down" if v <= -5 else ""
                return f'<span class="{cls}"><bdi dir=ltr>{v:+d}</bdi></span>'
            out.append(f'<p>{e(T("Compares each student\'s first-try accuracy in her first third of steps with her last third.", "تقارن دقة المحاولة الأولى لكل طالبة في ثلث خطواتها الأول بثلثها الأخير."))}</p>')
            out.append("<table><tr>" + "".join(f"<th>{e(x)}</th>" for x in (
                T("Student", "الطالبة"), T("First third", "الثلث الأول"), T("Last third", "الثلث الأخير"), T("Change", "التغيّر"))) +
                       "</tr>" + "".join(f"<tr><td><bdi>{e(r['name'])}</bdi></td><td>{r['early']}%</td><td>{r['late']}%</td><td>{arrow(r['change'])}</td></tr>"
                                         for r in c["rows"]) + "</table>")
        else:
            out.append(f'<p class="empty">{e(T(f"Not measurable yet: a student needs {impact.MIN_CURVE_STEPS}+ answered steps.", f"غير قابل للقياس بعد: تحتاج الطالبة إلى {impact.MIN_CURVE_STEPS} خطوات مجاب عنها فأكثر."))}</p>')

        h2("Students", "الطالبات")
        out.append("<table><tr>" + "".join(f"<th>{e(x)}</th>" for x in (
            T("Student", "الطالبة"), T("Missions", "المهمات"), T("Progress", "التقدّم"), T("Avg score", "متوسط الدرجة"),
            T("Answers", "الإجابات"), T("Active days", "أيام النشاط"), T("Last activity", "آخر نشاط"))) + "</tr>" +
                   "".join(f"<tr><td><bdi>{e(r['name'])}</bdi></td><td><bdi dir=ltr>{r['completed']}/{d['missions_total']}</bdi></td>"
                           f"<td>{bar(r['percent'])}</td><td>{_fmt(r['avg_score'], '%')}</td><td>{r['answers']}</td><td>{r['active_days']}</td>"
                           f"<td>{e(r['last_at'].astimezone(impact.RIYADH).date().isoformat()) if r['last_at'] else '—'}</td></tr>"
                           for r in d["students_table"]) + "</table>")

    h2("Students who need follow-up", "طالبات يحتجن إلى متابعة")
    if d["needs_follow_up"] or d["never_started_names"]:
        items = [f"<tr><td><bdi>{e(x['name'])}</bdi></td><td>{T('Started, then stopped', 'بدأت ثم توقفت')} "
                 f"({x['completed']} {T('missions done', 'مهمات مكتملة')}, {T('last activity', 'آخر نشاط')} {e(x['last_at'] or '—')})</td></tr>"
                 for x in d["needs_follow_up"]]
        items += [f"<tr><td><bdi>{e(nm)}</bdi></td><td>{T('Has not started yet', 'لم تبدأ بعد')}</td></tr>" for nm in d["never_started_names"]]
        out.append("<table>" + "".join(items) + "</table>")
    else:
        out.append(f'<p class="empty">{e(T("Nobody needs follow-up right now.", "لا أحد يحتاج إلى متابعة الآن."))}</p>')

    h2("Recommendations", "التوصيات")
    out.append('<ul class="recs">' + "".join(f"<li>{e(r[lang])}</li>" for r in impact.recommendations(d)) + "</ul>")

    out.append(f'<div class="limits"><b>{e(T("What this report can and cannot tell you", "ما الذي يستطيع هذا التقرير قوله وما لا يستطيعه"))}</b><br>' +
               e(T("It measures learning and engagement inside the lab, from the answers students actually submitted: how much they practise, "
                   "how accurately they answer and whether they improve while practising. It does not see school marks, so it cannot prove an "
                   "effect on them by itself. For that, give the same students a short test before and after a stage and compare. "
                   "Scores follow the lab rule: 100 for a right answer on the first try, 20 less for each wrong answer, never below 40.",
                   "يقيس التقرير التعلّم والمشاركة داخل المعمل من الإجابات التي أرسلتها الطالبات فعلًا: كم تدرّبن، ومدى دقة إجاباتهن، وهل "
                   "يتحسّنّ أثناء التدرّب. لكنه لا يرى درجات المدرسة، فلا يثبت وحده أثرًا عليها. ولإثبات ذلك أعطي الطالبات أنفسهن اختبارًا قصيرًا "
                   "قبل المرحلة وبعدها وقارني النتيجتين. تتبع الدرجات قاعدة المعمل: 100 للإجابة الصحيحة من المحاولة الأولى، وتنقص 20 عن كل إجابة خاطئة، ولا تقل عن 40.")) +
               "</div>")

    body = f'<div class="imp{" rtl" if ar else ""}" dir="{"rtl" if ar else "ltr"}">' + "".join(out) + "</div>"
    if not standalone:
        return C.compact(body)
    return (f'<!doctype html><html lang="{lang}" dir="{"rtl" if ar else "ltr"}"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(T("Impact report", "تقرير الأثر"))}</title>'
            f"<style>{CSS}{STANDALONE_CSS}</style></head><body>{body}</body></html>")
