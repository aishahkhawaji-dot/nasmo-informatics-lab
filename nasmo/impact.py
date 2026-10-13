"""Impact report: what the lab did for the students, from the real saved data only.

Everything is computed from rows that already exist (mission_progress.step_results and attempts),
nothing is invented and nothing needs a new table.

IMPORTANT honesty rule: these are learning and engagement indicators measured INSIDE the lab.
They show how much students practised, how well they answer and whether they improve while
practising. They cannot prove an effect on school marks (that needs a test before and after, or
a comparison group) and the report says so.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from . import auth
from .auth import User, require_teacher
from .content.stages import STAGES, STAGE_BY_ID
from .progress import all_missions
from .store import Store, parse_ts

RIYADH = timezone(timedelta(hours=3))
MIN_CLASS = 5            # fewer students than this: numbers are shown but flagged "small sample"
MIN_CURVE_STEPS = 9      # a student needs 9 answered steps to compare her first and last third
STEP_TYPES = ["understand", "predict", "choice", "bug", "complete", "solve", "explain"]
BANDS = [("90-100", 90, 101), ("75-89", 75, 90), ("60-74", 60, 75), ("<60", 0, 60)]
PROGRESS_BUCKETS = [("0", 0, 0), ("1-25", 1, 25), ("26-50", 26, 50), ("51-75", 51, 75), ("76-100", 76, 100)]


def _pct(a: float, b: float) -> int | None:
    return round(100 * a / b) if b else None


def _avg(vals: list[float]) -> float | None:
    return sum(vals) / len(vals) if vals else None


def _day(ts: datetime | None):
    return ts.astimezone(RIYADH).date() if ts else None


def _week_start(d):
    """Saudi weeks start on Sunday."""
    return d - timedelta(days=(d.weekday() + 1) % 7)


def build(store: Store, actor: User, include_demo: bool = False, now: datetime | None = None) -> dict:
    require_teacher(actor)
    now = now or datetime.now(timezone.utc)
    students = store.select("users", {"role": "student"}, order=[("created_at", "asc")])
    if not include_demo:
        students = [s for s in students if not s.get("is_demo")]
    ids = {s["id"] for s in students}
    missions = all_missions(store)
    mission_by_id = {m["id"]: m for m in missions}
    step_info: dict[tuple[str, str], dict] = {}
    for m in missions:
        for s in m["steps"]:
            step_info[(m["id"], s["id"])] = {"type": s["type"], "stage": m["stage"], "mission": m["title"],
                                            "mission_id": m["id"], "step": s["id"]}
    try:
        inactive_days = int(auth.get_setting(store, "inactive_days") or 7)
    except ValueError:
        inactive_days = 7
    pass_score = auth.get_setting(store, "cert_pass_score") or "60"

    progress = [r for r in store.select("mission_progress") if r.get("user_id") in ids]
    attempts = [a for a in store.select("attempts") if a.get("user_id") in ids]
    certs = [c for c in store.select("certificates", {"revoked": False}) if c.get("user_id") in ids]

    rows_by_user: dict[str, list[dict]] = defaultdict(list)
    for r in progress:
        rows_by_user[r["user_id"]].append(r)
    att_by_user: dict[str, list[dict]] = defaultdict(list)
    for a in attempts:
        att_by_user[a["user_id"]].append(a)
    certs_by_user: dict[str, int] = defaultdict(int)
    for c in certs:
        certs_by_user[c["user_id"]] += 1

    total_missions = len(missions)
    per_student: list[dict] = []
    all_steps: list[dict] = []               # one record per (student, step) that was tried
    for u in students:
        rows = rows_by_user.get(u["id"], [])
        steps = []
        for r in rows:
            for sid, sr in (r.get("step_results") or {}).items():
                info = step_info.get((r["mission_id"], sid))
                if not info or int(sr.get("attempts", 0)) <= 0:
                    continue
                passed = bool(sr.get("passed"))
                wrong = int(sr.get("wrong", 0))
                ts = parse_ts(sr.get("passed_at") or sr.get("last_at"))
                steps.append({**info, "user_id": u["id"], "passed": passed, "wrong": wrong,
                              "attempts": int(sr.get("attempts", 0)), "first_try": passed and wrong == 0, "ts": ts})
        steps.sort(key=lambda x: (x["ts"] is None, x["ts"] or now))
        all_steps.extend(steps)
        completed = [r for r in rows if r.get("status") == "completed" and r["mission_id"] in mission_by_id]
        scores = [float(r.get("score") or 0) for r in completed]
        att = att_by_user.get(u["id"], [])
        att_ts = [parse_ts(a.get("created_at")) for a in att]
        att_ts = [t for t in att_ts if t]
        last = max(att_ts) if att_ts else None
        first = min(att_ts) if att_ts else None
        curve = None
        timed = [s for s in steps if s["ts"]]
        if len(timed) >= MIN_CURVE_STEPS:
            k = len(timed) // 3
            early = 100 * sum(1 for s in timed[:k] if s["first_try"]) / k
            late = 100 * sum(1 for s in timed[-k:] if s["first_try"]) / k
            curve = {"early": round(early), "late": round(late), "change": round(late - early)}
        per_student.append({
            "id": u["id"], "name": u["display_name"], "username": u["username"], "active": bool(u.get("active", True)),
            "steps_tried": len(steps), "steps_passed": sum(1 for s in steps if s["passed"]),
            "first_try": sum(1 for s in steps if s["first_try"]),
            "wrong": sum(s["wrong"] for s in steps),
            "completed": len(completed), "percent": _pct(len(completed), total_missions) or 0,
            "avg_score": round(_avg(scores)) if scores else None,
            "answers": len(att), "active_days": len({_day(t) for t in att_ts}),
            "first_at": first, "last_at": last, "certificates": certs_by_user.get(u["id"], 0),
            "curve": curve,
        })

    n = len(students)
    started = [p for p in per_student if p["steps_tried"] > 0]
    limit = now - timedelta(days=inactive_days)
    active_recent = [p for p in per_student if p["last_at"] and p["last_at"] >= limit]
    finished_all = [p for p in per_student if total_missions and p["completed"] == total_missions]
    at_least_one = [p for p in per_student if p["completed"] >= 1]
    stalled = [p for p in started if p["active"] and p["completed"] < total_missions
               and (not p["last_at"] or p["last_at"] < limit)]
    never = [p for p in per_student if p["steps_tried"] == 0 and p["active"]]

    tried = len(all_steps)
    first_try_n = sum(1 for s in all_steps if s["first_try"])
    passed_n = sum(1 for s in all_steps if s["passed"])
    had_wrong = [s for s in all_steps if s["wrong"] > 0]
    recovered = [s for s in had_wrong if s["passed"]]

    completed_rows = [r for r in progress if r.get("status") == "completed" and r["mission_id"] in mission_by_id]
    mission_scores = [float(r.get("score") or 0) for r in completed_rows]
    student_avgs = [p["avg_score"] for p in per_student if p["avg_score"] is not None]
    bands = []
    for label, lo, hi in BANDS:
        bands.append({"label": label, "count": sum(1 for v in student_avgs if lo <= v < hi)})
    buckets = []
    for label, lo, hi in PROGRESS_BUCKETS:
        buckets.append({"label": label, "count": sum(1 for p in per_student if lo <= p["percent"] <= hi)})

    by_stage = []
    for st in STAGES:
        ms = [m for m in missions if m["stage"] == st["id"]]
        mids = {m["id"] for m in ms}
        srows = [r for r in progress if r["mission_id"] in mids]
        done_rows = [r for r in srows if r.get("status") == "completed"]
        st_students_started = {r["user_id"] for r in srows}
        st_students_done = [p["id"] for p in per_student
                            if ms and sum(1 for r in rows_by_user.get(p["id"], [])
                                          if r["mission_id"] in mids and r.get("status") == "completed") == len(ms)]
        st_steps = [s for s in all_steps if s["stage"] == st["id"]]
        by_stage.append({
            "id": st["id"], "title": st["title"], "subtitle": st["subtitle"], "missions": len(ms),
            "started_students": len(st_students_started), "completed_students": len(st_students_done),
            "started_pct": _pct(len(st_students_started), n), "completed_pct": _pct(len(st_students_done), n),
            "avg_score": round(_avg([float(r.get("score") or 0) for r in done_rows])) if done_rows else None,
            "first_try_pct": _pct(sum(1 for s in st_steps if s["first_try"]), len(st_steps)),
            "steps_tried": len(st_steps),
        })

    by_type = []
    for t in STEP_TYPES:
        ts_ = [s for s in all_steps if s["type"] == t]
        by_type.append({"type": t, "steps_tried": len(ts_),
                        "first_try_pct": _pct(sum(1 for s in ts_ if s["first_try"]), len(ts_)),
                        "avg_wrong": round(sum(s["wrong"] for s in ts_) / len(ts_), 1) if ts_ else None})

    per_step: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for s in all_steps:
        per_step[(s["mission_id"], s["step"])].append(s)
    hardest = []
    for (mid, sid), lst in per_step.items():
        if len(lst) >= 3:
            hardest.append({"mission": mission_by_id[mid]["title"], "mission_id": mid, "step": sid,
                            "type": lst[0]["type"], "students": len(lst),
                            "first_try_pct": _pct(sum(1 for x in lst if x["first_try"]), len(lst)),
                            "avg_wrong": round(sum(x["wrong"] for x in lst) / len(lst), 1)})
    hardest.sort(key=lambda h: (h["first_try_pct"], -h["avg_wrong"]))
    hardest = hardest[:5]

    # activity: the last 8 weeks (Sunday to Saturday), answers and distinct students
    this_week = _week_start(now.astimezone(RIYADH).date())
    weeks = []
    for i in range(7, -1, -1):
        w0 = this_week - timedelta(days=7 * i)
        w1 = w0 + timedelta(days=7)
        in_w = [(a, parse_ts(a.get("created_at"))) for a in attempts]
        in_w = [(a, t) for a, t in in_w if t and w0 <= _day(t) < w1]
        weeks.append({"start": w0.isoformat(), "answers": len(in_w), "students": len({a["user_id"] for a, _ in in_w})})

    curve_students = [p for p in per_student if p["curve"]]
    changes = [p["curve"]["change"] for p in curve_students]
    curve = {
        "students": len(curve_students),
        "early": round(_avg([p["curve"]["early"] for p in curve_students])) if curve_students else None,
        "late": round(_avg([p["curve"]["late"] for p in curve_students])) if curve_students else None,
        "change": round(_avg(changes)) if changes else None,
        "improved": sum(1 for c in changes if c >= 5),
        "same": sum(1 for c in changes if -5 < c < 5),
        "declined": sum(1 for c in changes if c <= -5),
        "rows": sorted(({"name": p["name"], **p["curve"]} for p in curve_students), key=lambda r: -r["change"]),
    }

    first_use = min((p["first_at"] for p in per_student if p["first_at"]), default=None)
    last_use = max((p["last_at"] for p in per_student if p["last_at"]), default=None)
    data = {
        "generated_at": now.astimezone(RIYADH).strftime("%Y-%m-%d %H:%M"),
        "include_demo": include_demo,
        "period": {"from": first_use.astimezone(RIYADH).date().isoformat() if first_use else None,
                   "to": last_use.astimezone(RIYADH).date().isoformat() if last_use else None},
        "students": n, "small_sample": n < MIN_CLASS, "missions_total": total_missions,
        "inactive_days": inactive_days, "pass_score": pass_score,
        "participation": {
            "started": len(started), "started_pct": _pct(len(started), n),
            "active_recent": len(active_recent), "active_recent_pct": _pct(len(active_recent), n),
            "at_least_one": len(at_least_one), "at_least_one_pct": _pct(len(at_least_one), n),
            "finished_all": len(finished_all), "never_started": len(never), "stalled": len(stalled),
            "avg_progress": round(_avg([p["percent"] for p in per_student])) if per_student else 0,
            "avg_active_days": round(_avg([p["active_days"] for p in started]), 1) if started else 0,
            "avg_answers": round(_avg([p["answers"] for p in started])) if started else 0,
            "certificates": len(certs), "students_with_certificate": sum(1 for p in per_student if p["certificates"]),
            "missions_completed": len(completed_rows), "answers_total": len(attempts),
        },
        "performance": {
            "avg_mission_score": round(_avg(mission_scores)) if mission_scores else None,
            "avg_student_score": round(_avg(student_avgs)) if student_avgs else None,
            "first_try_pct": _pct(first_try_n, tried), "steps_tried": tried,
            "steps_passed_pct": _pct(passed_n, tried),
            "avg_wrong_per_step": round(sum(s["wrong"] for s in all_steps) / tried, 2) if tried else None,
            "recovery_pct": _pct(len(recovered), len(had_wrong)), "steps_with_wrong": len(had_wrong),
            "bands": bands, "progress_buckets": buckets,
        },
        "by_stage": by_stage, "by_type": by_type, "hardest": hardest, "weeks": weeks, "curve": curve,
        "students_table": sorted(per_student, key=lambda p: (-p["percent"], p["name"])),
        "needs_follow_up": [{"name": p["name"], "username": p["username"], "completed": p["completed"],
                             "last_at": p["last_at"].astimezone(RIYADH).date().isoformat() if p["last_at"] else None}
                            for p in stalled],
        "never_started_names": [p["name"] for p in never],
    }
    data["insights"] = insights(data)
    return data


# ---------------------------------------------------------------------------- analysis text
def _ar_stage(st: dict) -> str:
    from . import i18n
    with i18n.force("ar"):
        return i18n.tr(st["title"])


def insights(d: dict) -> list[dict]:
    """The 'situation analysis': plain sentences (English and Arabic) with a kind: good / watch / note.
    Every sentence is conditional on enough data, so a small class never gets a confident claim."""
    out: list[dict] = []
    n = d["students"]
    p, f = d["participation"], d["performance"]

    def add(kind, en, ar):
        out.append({"kind": kind, "en": en, "ar": ar})

    if n == 0:
        add("note", "There are no students yet, so there is nothing to analyse.", "لا توجد طالبات بعد، فلا يوجد ما يُحلَّل.")
        return out
    if d["small_sample"]:
        add("note", f"Only {n} student(s) are included. With so few students the numbers describe them individually; "
                    "they should not be generalised to a whole class.",
            f"عدد الطالبات المشمولات {n} فقط. مع هذا العدد الصغير تصف الأرقام كل طالبة على حدة، ولا يصح تعميمها على فصل كامل.")
    if p["started"] == 0:
        add("watch", "No student has answered a question yet. The report fills in as soon as students start practising.",
            "لم تجب أي طالبة عن سؤال بعد. سيمتلئ التقرير بمجرد أن تبدأ الطالبات التدرّب.")
        return out

    s_pct = p["started_pct"]
    add("good" if s_pct >= 70 else "watch" if s_pct < 40 else "note",
        f"Participation: {p['started']} of {n} students ({s_pct}%) started practising and {p['active_recent']} "
        f"({p['active_recent_pct']}%) were active in the last {d['inactive_days']} days.",
        f"المشاركة: بدأت {p['started']} من {n} طالبة ({s_pct}%) التدرّب، ونشطت {p['active_recent']} "
        f"({p['active_recent_pct']}%) خلال آخر {d['inactive_days']} أيام.")
    add("note", f"On average a student completed {p['avg_progress']}% of the {d['missions_total']} missions; "
                f"{p['at_least_one']} students completed at least one mission and {p['finished_all']} finished all of them.",
        f"في المتوسط أكملت الطالبة {p['avg_progress']}% من {d['missions_total']} مهمة؛ أكملت {p['at_least_one']} طالبة مهمة واحدة "
        f"على الأقل، وأنهت {p['finished_all']} المهمات كلها.")
    if p["certificates"]:
        add("good", f"{p['certificates']} internal certificate(s) were issued to {p['students_with_certificate']} student(s).",
            f"صدرت {p['certificates']} شهادة داخلية لعدد {p['students_with_certificate']} طالبة.")

    if f["avg_mission_score"] is not None:
        sc = f["avg_mission_score"]
        add("good" if sc >= 80 else "watch" if sc < 60 else "note",
            f"Performance: the average score of completed missions is {sc}% (100 = every step right on the first try).",
            f"الأداء: متوسط درجات المهمات المكتملة {sc}% (100 تعني صحة كل خطوة من المحاولة الأولى).")
    if f["first_try_pct"] is not None and f["steps_tried"] >= 10:
        ft = f["first_try_pct"]
        add("good" if ft >= 65 else "watch" if ft < 40 else "note",
            f"{ft}% of the steps students tried were solved on the first attempt, and "
            f"{f['recovery_pct'] if f['recovery_pct'] is not None else 0}% of the steps that were first answered wrongly were "
            "later solved - a sign of persistence.",
            f"{ft}% من الخطوات التي جرّبتها الطالبات حُلّت من المحاولة الأولى، و"
            f"{f['recovery_pct'] if f['recovery_pct'] is not None else 0}% من الخطوات التي أُخطئ فيها أولًا حُلّت لاحقًا، وهذا مؤشر "
            "على المثابرة.")

    c = d["curve"]
    if c["students"] >= 3 and c["change"] is not None:
        verb_en = "improved" if c["change"] >= 5 else "declined" if c["change"] <= -5 else "stayed about the same"
        verb_ar = "تحسّنت" if c["change"] >= 5 else "تراجعت" if c["change"] <= -5 else "بقيت قريبة من مستواها"
        add("good" if c["change"] >= 5 else "watch" if c["change"] <= -5 else "note",
            f"Learning trend: for the {c['students']} students with enough answers, first-attempt accuracy {verb_en} "
            f"from {c['early']}% (their first third of steps) to {c['late']}% (their last third), a change of {c['change']:+d} points. "
            f"{c['improved']} improved, {c['same']} stayed about the same, {c['declined']} declined. "
            "Later missions are harder, so a rise here is a strong sign.",
            f"اتجاه التعلّم: عند {c['students']} طالبة لديهن إجابات كافية {verb_ar} دقة المحاولة الأولى من {c['early']}% "
            f"(في ثلث خطواتهن الأول) إلى {c['late']}% (في ثلثهن الأخير)، بتغيّر قدره \u2066{c['change']:+d}\u2069 نقطة. "
            f"تحسّنت {c['improved']}، وبقيت {c['same']} قريبة من مستواها، وتراجعت {c['declined']}. "
            "المهمات اللاحقة أصعب، فالارتفاع هنا مؤشر قوي.")
    elif c["students"] < 3:
        add("note", f"There is not enough data to measure a learning trend yet (it needs at least 3 students with {MIN_CURVE_STEPS}+ answered steps).",
            f"لا توجد بيانات كافية لقياس اتجاه التعلّم بعد (يلزم 3 طالبات على الأقل أجبن عن {MIN_CURVE_STEPS} خطوات فأكثر).")

    typed = [t for t in d["by_type"] if t["steps_tried"] >= 5 and t["first_try_pct"] is not None]
    if len(typed) >= 2:
        weak = min(typed, key=lambda t: t["first_try_pct"])
        strong = max(typed, key=lambda t: t["first_try_pct"])
        if weak["type"] != strong["type"]:
            add("note", f"Skills: strongest on '{strong['type']}' steps ({strong['first_try_pct']}% first try), "
                        f"weakest on '{weak['type']}' steps ({weak['first_try_pct']}%).",
                f"المهارات: الأقوى في خطوات «{TYPE_AR.get(strong['type'], strong['type'])}» ({strong['first_try_pct']}% من المحاولة الأولى)، "
                f"والأضعف في خطوات «{TYPE_AR.get(weak['type'], weak['type'])}» ({weak['first_try_pct']}%).")
    if d["hardest"]:
        h = d["hardest"][0]
        add("watch", f"The hardest step so far is {h['mission']} / step {h['step']} ({h['type']}): only {h['first_try_pct']}% of "
                     f"{h['students']} students got it right on the first try.",
            f"أصعب خطوة حتى الآن: {h['mission']} / الخطوة {h['step']} ({TYPE_AR.get(h['type'], h['type'])}): "
            f"{h['first_try_pct']}% فقط من {h['students']} طالبة أصبن من المحاولة الأولى.")

    # drop-off between stages
    st = [s for s in d["by_stage"] if s["started_pct"] is not None]
    for a, b in zip(st, st[1:]):
        if a["started_students"] >= 3 and a["started_students"] - b["started_students"] >= max(2, a["started_students"] // 2):
            add("watch", f"Many students stop before the next stage: {a['started_students']} started {a['title']} but only "
                         f"{b['started_students']} started {b['title']}.",
                f"تتوقف طالبات كثيرات قبل المرحلة التالية: بدأت {a['started_students']} المرحلة «{_ar_stage(a)}» ولم تبدأ التالية إلا {b['started_students']}.")
            break

    if p["stalled"]:
        add("watch", f"{p['stalled']} student(s) started but have had no activity for {d['inactive_days']}+ days.",
            f"{p['stalled']} طالبة بدأن لكن لا نشاط لهن منذ {d['inactive_days']} أيام أو أكثر.")
    if p["never_started"]:
        add("watch", f"{p['never_started']} active account(s) have not answered any question yet.",
            f"{p['never_started']} حساب نشط لم يُجب عن أي سؤال بعد.")
    return out


def recommendations(d: dict) -> list[dict]:
    out: list[dict] = []
    p = d["participation"]
    if d["students"] == 0 or p["started"] == 0:
        out.append({"en": "Invite the students to sign in and start the first mission, then come back to this report.",
                    "ar": "ادعي الطالبات إلى تسجيل الدخول وبدء المهمة الأولى، ثم عودي إلى هذا التقرير."})
        return out
    if p["stalled"] or p["never_started"]:
        out.append({"en": "Follow up personally with the students listed under 'Students who need follow-up'.",
                    "ar": "تابعي شخصيًا الطالبات المذكورات تحت «طالبات يحتجن إلى متابعة»."})
    if d["hardest"]:
        out.append({"en": "Review the hardest steps in class (table below) before the next practice session.",
                    "ar": "راجعي أصعب الخطوات في الحصة (الجدول أدناه) قبل جلسة التدريب القادمة."})
    weak = [t for t in d["by_type"] if t["steps_tried"] >= 5 and t["first_try_pct"] is not None and t["first_try_pct"] < 50]
    if weak:
        names_en = ", ".join(t["type"] for t in weak)
        names_ar = "، ".join(TYPE_AR.get(t["type"], t["type"]) for t in weak)
        out.append({"en": f"Give extra practice on: {names_en} questions (under 50% first-try accuracy).",
                    "ar": f"أعطي تدريبًا إضافيًا على أسئلة: {names_ar} (دقة المحاولة الأولى أقل من 50%)."})
    if p["started_pct"] is not None and p["started_pct"] < 70:
        out.append({"en": "Set a short weekly lab time so more students start and keep a routine.",
                    "ar": "حدّدي وقتًا أسبوعيًا قصيرًا للمعمل ليبدأ عدد أكبر من الطالبات ويلتزمن بروتينًا."})
    out.append({"en": "To measure the effect on real school results, give a short test before and after a stage and compare "
                      "the same students (this report cannot see school marks).",
                "ar": "لقياس الأثر على نتائج المدرسة الفعلية، أعطي اختبارًا قصيرًا قبل المرحلة وبعدها وقارني الطالبات أنفسهن "
                      "(هذا التقرير لا يرى درجات المدرسة)."})
    return out


TYPE_AR = {"understand": "فهم الكود", "predict": "توقّع المخرجات", "choice": "اختيار الإجابة", "bug": "إيجاد الخطأ",
           "complete": "إكمال الكود", "solve": "حل المسألة", "explain": "الشرح"}
