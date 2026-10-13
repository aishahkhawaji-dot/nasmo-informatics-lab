"""Arabic / English switch: every UI text has a translation, the switch works and English is untouched."""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

# texts that are data or content, not interface (names typed by the tests, mission content)
_DATA = {"sara", "sara (sara)", "teacher1", "my mission", "good", "bad", "t2"}


def _content_strings() -> set:
    from nasmo.content import missions, stages
    out: set = set()

    def walk(o):
        if isinstance(o, str):
            out.add(o.strip())
            out.update(l.strip() for l in o.split("\n"))
        elif isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, (list, tuple)):
            for v in o:
                walk(v)
    walk(missions.MISSIONS)
    walk(stages.STAGES)
    return out


class ArabicTests(unittest.TestCase):
    def test_01_translate_basics(self):
        from nasmo import i18n
        i18n.current_lang = lambda: "ar"
        try:
            self.assertEqual(i18n.tr("Logout"), "تسجيل الخروج")
            self.assertEqual(i18n.tr("🏆  Trophy Room"), "🏆  غرفة الكؤوس")
            self.assertEqual(i18n.tr("← Home"), "→ الرئيسية")
            self.assertEqual(i18n.tr("3/4 Missions"), "3/4 مهمات")
            self.assertEqual(i18n.tr("Stage 2 · Binary Search"), "المرحلة 2 · Binary Search")   # mission names stay English
            self.assertEqual(i18n.tr("Hello, C++!"), "Hello, C++!")
            self.assertEqual(i18n.tr("   "), "   ")
            self.assertIn("غرفة الكؤوس", i18n.tr_html('<div class="x">Trophy Room</div>'))
            self.assertIn('class="x"', i18n.tr_html('<div class="x">Trophy Room</div>'))
        finally:
            del i18n.current_lang       # back to the module's own function
            import importlib
            importlib.reload(i18n)

    def test_02_english_is_untouched(self):
        from nasmo import i18n
        self.assertEqual(i18n.tr("Logout"), "Logout")
        self.assertEqual(i18n.tr_html("<b>Logout</b>"), "<b>Logout</b>")

    @classmethod
    def _walk(cls):
        if not hasattr(cls, "_res"):          # a separate process keeps the other tests' fake Streamlit clean
            r = subprocess.run([sys.executable, str(ROOT / "tests" / "arabic_walk.py")], cwd=str(ROOT),
                               capture_output=True, text=True, timeout=600)
            line = [l for l in r.stdout.splitlines() if l.startswith("@@")]
            if not line:
                raise AssertionError("walk failed: " + (r.stderr or r.stdout)[-1500:])
            cls._res = json.loads(line[-1][2:])
        return cls._res

    def test_03_every_page_is_translated(self):
        misses = self._walk()["misses"]
        content = _content_strings()
        left = [m for m in misses if m not in content and m.lower() not in _DATA]
        self.assertEqual(left, [], "texts without Arabic translation: " + " | ".join(left[:20]))

    def test_04_switch_button_and_rtl(self):
        seen = self._walk()["switch"]
        self.assertEqual(seen, [True, "ar", "en", "ar"])      # button exists; it flips ar -> en -> ar
        from nasmo.ui import style
        self.assertIn("unicode-bidi:plaintext", style.build_css("light", True, "ar"))
        self.assertNotIn("unicode-bidi:plaintext", style.build_css("light", True, "en"))


if __name__ == "__main__":
    unittest.main()
