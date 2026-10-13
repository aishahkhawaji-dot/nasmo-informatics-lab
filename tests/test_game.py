import unittest
from pathlib import Path
from datetime import date

from nasmo import game as G
from nasmo.content.missions import MISSIONS


def row(mission, wrong=0, passed=True, status="completed", code=False):
    res = {}
    for s in mission["steps"]:
        res[s["id"]] = {"passed": passed, "wrong": wrong, "attempts": wrong + 1, "score": 100}
        if code:
            res[s["id"]]["code"] = "int main(){}"
    return {"status": status, "step_results": res, "score": 100}


class GameLogic(unittest.TestCase):
    def test_empty_state(self):
        st = G.compute(MISSIONS, {}, [])
        self.assertEqual((st["xp"], st["level"], st["stars"]), (0, 1, 0))
        self.assertEqual(st["rank"], "Code Rookie")
        self.assertEqual(st["trophies_unlocked"], 0)
        self.assertEqual(st["loot_collected"], 0)

    def test_stars_by_wrong_answers(self):
        m = MISSIONS[0]
        self.assertEqual(G.mission_stars(m, row(m, 0)), 3)
        self.assertEqual(G.mission_stars(m, row(m, 1)), 2)   # one wrong per step, >=2 steps in total -> check below
        self.assertEqual(G.mission_stars(m, row(m, 3)), 1)
        self.assertEqual(G.mission_stars(m, row(m, 0, status="in_progress")), 0)
        self.assertEqual(G.mission_stars(m, None), 0)

    def test_xp_formula(self):
        m = MISSIONS[0]
        n = len(m["steps"])
        st = G.compute(MISSIONS, {m["id"]: row(m, 0)}, [])
        self.assertEqual(st["xp"], n * (G.XP_STEP + G.XP_STEP_FIRST_TRY) + G.XP_MISSION + 3 * G.XP_PER_STAR)
        self.assertEqual(G.mission_xp(m, row(m, 0)), st["xp"])
        self.assertEqual(st["stars"], 3)
        self.assertEqual(st["loot_collected"], 1)

    def test_max_xp_reaches_top_rank(self):
        rows = {m["id"]: row(m, 0) for m in MISSIONS}
        st = G.compute(MISSIONS, rows, [])
        self.assertEqual(st["rank"], "Nasmo Champion")
        self.assertEqual(st["level_pct"], 100)
        self.assertTrue(all(t["unlocked"] for t in st["trophies"] if t["id"] not in ("streak_3", "streak_7", "comeback", "coder")))
        self.assertTrue(all(st["worlds_done"].values()))

    def test_levels_monotonic(self):
        last, got = 0, []
        rows = {}
        for m in MISSIONS:
            rows[m["id"]] = row(m, 0)
            lv = G.compute(MISSIONS, rows, [])["level"]
            self.assertGreaterEqual(lv, last)
            last = lv
            got.append(lv)
        self.assertEqual(got[0], 1 if G.compute(MISSIONS, {MISSIONS[0]["id"]: row(MISSIONS[0])}, [])["xp"] < 200 else got[0])
        self.assertEqual(got[-1], len(G.RANKS))

    def test_streak(self):
        today = date(2026, 10, 9)
        self.assertEqual(G.streak_days([], today), 0)
        self.assertEqual(G.streak_days(["2026-10-09T10:00"], today), 1)
        self.assertEqual(G.streak_days(["2026-10-08T10:00", "2026-10-07T01:00"], today), 2)   # yesterday still counts
        self.assertEqual(G.streak_days(["2026-10-09", "2026-10-08", "2026-10-06"], today), 2)  # gap breaks it
        self.assertEqual(G.streak_days(["2026-10-01"], today), 0)
        self.assertEqual(G.streak_days(["garbage"], today), 0)

    def test_trophy_unlock_and_diff(self):
        m = MISSIONS[0]
        before = G.snapshot(G.compute(MISSIONS, {}, []))
        st = G.compute(MISSIONS, {m["id"]: row(m, 0, code=True)}, [])
        gain = G.new_since(before, G.snapshot(st), st)
        ids = {t["id"] for t in gain["trophies"]}
        self.assertTrue({"first_step", "mission_1", "perfect_1", "coder"} <= ids)
        self.assertEqual(len(gain["loot"]), 1)
        self.assertEqual(gain["xp"], st["xp"])
        again = G.new_since(G.snapshot(st), G.snapshot(st), st)
        self.assertEqual((again["trophies"], again["loot"], again["xp"]), ([], [], 0))

    def test_comeback_trophy(self):
        m = MISSIONS[0]
        r = row(m, 2)
        st = G.compute(MISSIONS, {m["id"]: r}, [])
        self.assertTrue(next(t for t in st["trophies"] if t["id"] == "comeback")["unlocked"])

    def test_loot_unique_for_builtin_missions(self):
        names = {G.loot_for(m, i)[0] for i, m in enumerate(MISSIONS)}
        self.assertEqual(len(names), len(MISSIONS))
        self.assertEqual(G.loot_for({"id": "custom-x", "custom": True}, 99), G.loot_for({"id": "custom-x", "custom": True}, 3))

    def test_game_ui_renders(self):
        from nasmo.ui import game_ui as GU
        rows = {m["id"]: row(m, 0) for m in MISSIONS[:6]}
        st = G.compute(MISSIONS, rows, ["2026-10-09"])
        for html in (GU.hud_html(st, "Sara <b>"), GU.rank_ladder_html(st), GU.mascot("cheer", 90, 8),
                     GU.victory_html(MISSIONS[0], 3, 100, {"xp": 50, "trophies": st["trophies"][:1], "level_up": True, "worlds": ["f"]},
                                     st, st["loot"][0], ""),
                     GU.correct_banner(15, True, 3, 3, "Correct!")):
            self.assertTrue(html)
        self.assertNotIn("Sara <b>", GU.hud_html(st, "Sara <b>"))   # escaped

    def test_sound_script(self):
        from nasmo.ui.sound import sound_html
        a, b = sound_html(["correct"]), sound_html(["victory", "trophy"], 2)
        self.assertNotEqual(a, sound_html(["correct"]))        # nonce -> fresh iframe each time
        self.assertIn('["victory", "trophy"]', b)
        self.assertNotIn("%KINDS%", b)




class StreamlitCompat(unittest.TestCase):
    def test_use_container_width_falls_back_to_width_stretch(self):
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import stub_streamlit as T
        T.install()
        from nasmo.ui import sx
        calls = []

        def new_button(label, key=None, width=None):          # a "future" Streamlit: no use_container_width
            calls.append((label, width))
            return False
        wrapped = sx._wrap_fn("button", new_button)
        wrapped("Go", key="k", use_container_width=True)
        wrapped("Go2", key="k2", use_container_width=False)
        self.assertEqual(calls, [("Go", "stretch"), ("Go2", None)])


if __name__ == "__main__":
    unittest.main()


class CertificateDesigns(unittest.TestCase):
    def test_all_designs_render_with_same_text(self):
        from nasmo.ui.certificate import DESIGNS, certificate_html
        cert = {"serial": "NL-1", "title": "Fundamentals - Training Completion", "reason": "Done <b>x</b>", "issued_at": "2026-10-10T10:00:00"}
        self.assertEqual(len(DESIGNS), 4)
        for k in DESIGNS:
            h = certificate_html(cert, "Sara <i>", k, {"rank": "Logic Knight", "xp": 5, "stars": 2})
            for needle in ("Fundamentals - Training Completion", "NL-1", "not an official certificate", "Logic Knight"):
                self.assertIn(needle, h, (k, needle))
            self.assertNotIn("Sara <i>", h)             # escaped
            self.assertNotIn("Done <b>x</b>", h)
        pv = certificate_html(cert, "Sara", "galaxy", None, preview=True)
        self.assertIn("PREVIEW", pv)
        self.assertNotIn("window.print", pv)                     # a preview cannot be printed
        self.assertIn("window.print", certificate_html(cert, "Sara", "galaxy"))
        self.assertIn("royal", DESIGNS)
        self.assertEqual(certificate_html(cert, "A B", "nope"), certificate_html(cert, "A B", "royal"))