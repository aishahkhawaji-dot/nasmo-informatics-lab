"""Grading of mission steps. Pure functions - no database, no Streamlit.

Completion rules (what makes a step count as passed):
  understand / bug / choice : the chosen option is the correct one
  predict / complete        : the typed answer matches an accepted answer
                              (extra spaces ignored; Arabic digits accepted)
  solve                     : the final answer is correct AND the student wrote
                              some code (it is saved for the teacher)
  explain                   : at least `min_words` words and enough key ideas
                              from the rubric (automatic check - the teacher can
                              read the text in the student's report)
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .content.missions import MCQ_TYPES

_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
_PUNCT = str.maketrans({"،": ",", "؛": ";", "٫": ".", "‑": "-", "–": "-", "−": "-"})

MAX_TEXT = 4000


@dataclass
class GradeResult:
    correct: bool
    feedback: str = ""        # short reason shown to the student (English)
    feedback_ar: str = ""
    needs_code: bool = False  # solve: right answer but no code written
    incomplete: bool = False  # nothing chosen / too short: not counted as an attempt


def _clean(s: str) -> str:
    return (s or "").translate(_DIGITS).translate(_PUNCT)


def normalize(s: str, mode: str = "words") -> str:
    s = _clean(s).strip().lower()
    if mode == "nospace":
        s = re.sub(r"\s+", "", s).rstrip(";")
        return s
    return " ".join(s.split())


def score_for(wrong_attempts: int) -> int:
    """100 points for a first-try pass, minus 20 per wrong attempt (min 40)."""
    return max(40, 100 - 20 * max(0, wrong_attempts))


def grade_step(step: dict, answer, code: str | None = None) -> GradeResult:
    t = step["type"]
    if t in MCQ_TYPES:
        if answer is None or answer == "":
            return GradeResult(False, "Choose one option first.", "اختاري إجابة أولًا.", incomplete=True)
        try:
            idx = int(answer)
        except (TypeError, ValueError):
            return GradeResult(False, "Invalid choice.", "اختيار غير صالح.", incomplete=True)
        ok = idx == step["answer"]
        return GradeResult(ok)

    text = (answer or "")
    if len(text) > MAX_TEXT:
        return GradeResult(False, "Answer is too long.", "الإجابة طويلة جدًا.", incomplete=True)

    if t in ("predict", "complete", "solve"):
        mode = step.get("match", "words")
        got = normalize(text, mode)
        if not got:
            return GradeResult(False, "Type your answer first.", "اكتبي إجابتك أولًا.", incomplete=True)
        accepted = {normalize(a, mode) for a in step["answer"]}
        ok = got in accepted
        if ok and t == "solve":
            need = int(step.get("min_code_chars", 0))
            if len((code or "").strip()) < need:
                return GradeResult(
                    False,
                    f"Your answer is right, but please also write your C++ solution "
                    f"in the code box (at least {need} characters) - then submit again.",
                    "إجابتك صحيحة، لكن اكتبي أيضًا حلّك بلغة C++ في مربع الكود ثم أرسلي مرة أخرى.",
                    needs_code=True)
        return GradeResult(ok)

    if t == "explain":
        rub = step["rubric"]
        words = len(_clean(text).split())
        if words < rub.get("min_words", 8):
            return GradeResult(
                False, f"Write a little more - at least {rub.get('min_words', 8)} words.",
                "اكتبي شرحًا أطول قليلًا.", incomplete=True)
        hits = 0
        for group in rub["groups"]:
            if any(re.search(p, _clean(text), re.I) for p in group):
                hits += 1
        if hits >= rub["need"]:
            return GradeResult(True)
        return GradeResult(False, "Your explanation is missing some key ideas - read the hint and try again.",
                           "شرحك ينقصه بعض الأفكار الأساسية؛ اقرئي التلميح وحاولي مرة أخرى.")

    return GradeResult(False, "Unknown step type.")
