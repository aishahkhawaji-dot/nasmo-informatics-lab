"""Compile and run every C++ example in the missions and check the stored
answers. Skipped automatically when no C++ compiler (g++) is installed."""
import os
import shutil
import subprocess
import tempfile
import unittest

from nasmo.content.missions import MISSIONS, MCQ_TYPES, TEXT_TYPES
from nasmo.content.stages import STAGE_BY_ID, STAGES

GPP = shutil.which("g++") or shutil.which("clang++")


def norm(s: str) -> str:
    return " ".join(s.split())


def run_cpp(source: str, stdin: str = "") -> str:
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "a.cpp")
        exe = os.path.join(d, "a.out")
        with open(src, "w", encoding="utf-8") as f:
            f.write(source)
        c = subprocess.run([GPP, "-std=c++17", "-O0", "-o", exe, src],
                           capture_output=True, text=True, timeout=60)
        if c.returncode != 0:
            raise AssertionError("compile error:\n" + c.stderr[:800])
        r = subprocess.run([exe], input=stdin, capture_output=True, text=True, timeout=10)
        return r.stdout


class ContentStructure(unittest.TestCase):
    def test_stage_and_mission_counts(self):
        self.assertEqual([s["id"] for s in STAGES], ["f", "s1", "s2", "s3", "s4"])
        for s in STAGES:
            ms = [m for m in MISSIONS if m["stage"] == s["id"]]
            self.assertEqual(len(ms), 4, s["id"])

    def test_unique_ids(self):
        ids = [m["id"] for m in MISSIONS]
        self.assertEqual(len(ids), len(set(ids)))
        for m in MISSIONS:
            sids = [st["id"] for st in m["steps"]]
            self.assertEqual(len(sids), len(set(sids)), m["id"])

    def test_step_shapes(self):
        types = set()
        for m in MISSIONS:
            self.assertIn(m["stage"], STAGE_BY_ID)
            self.assertGreaterEqual(len(m["steps"]), 2)
            for st in m["steps"]:
                types.add(st["type"])
                self.assertTrue(st["prompt"] and st["explain_en"] and st["explain_ar"], (m["id"], st["id"]))
                if st["type"] in MCQ_TYPES:
                    self.assertGreaterEqual(len(st["options"]), 2)
                    self.assertTrue(0 <= st["answer"] < len(st["options"]))
                elif st["type"] in TEXT_TYPES:
                    self.assertTrue(st["answer"])
                else:
                    self.assertEqual(st["type"], "explain")
                    self.assertIn("groups", st["rubric"])
        self.assertEqual(types, {"understand", "predict", "bug", "complete", "solve", "choice", "explain"})

    def test_official_links_only_nsmo(self):
        for s in STAGES:
            for title, desc, url in s["topics"]:
                if url:
                    self.assertTrue(url.startswith("https://nsmobooklets.mawhiba.sa/en/learn/"), url)
                    self.assertTrue(url.endswith(".html"))


@unittest.skipUnless(GPP, "no C++ compiler installed")
class CppAnswers(unittest.TestCase):
    def test_all_examples(self):
        checked = 0
        for m in MISSIONS:
            for st in m["steps"]:
                v = st.get("verify")
                if v:
                    out = run_cpp(v["source"], v.get("stdin", ""))
                    self.assertEqual(norm(out), norm(v["expect"]), f"{m['id']}:{st['id']} verify")
                    checked += 1
                    if st["type"] in ("solve", "complete"):
                        self.assertIn(norm(v["expect"]), [norm(a) for a in st["answer"]] +
                                      ([norm(v["expect"])] if st["type"] == "complete" else []),
                                      f"{m['id']}:{st['id']} answer vs verify")
                if st["type"] == "predict":
                    out = run_cpp(st["code"])
                    self.assertIn(norm(out), [norm(a) for a in st["answer"]], f"{m['id']}:{st['id']} predict")
                    checked += 1
        self.assertGreaterEqual(checked, 25)


if __name__ == "__main__":
    unittest.main()
