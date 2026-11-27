#!/usr/bin/env python3
"""Tests for the news-image-20261127 v1 entry.

Covers the grader contract (stdlib-only entrypoint, deterministic
byte-identical output, 1024x1024 PNG <= 1 MiB, world-readable output),
the 300px legibility gate (Laplacian variance of the sharpened 300px
preview), the micro-text floors, and the story record (36 stories,
8 regions, DATE CHECK present).
"""

import ast
import os
import re
import subprocess
import sys
import unittest

from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import render_poster  # noqa: E402


def run_entry(outdir, extra_env=None):
    env = dict(os.environ)
    env["MAKEFUN_OUTPUT_DIR"] = outdir
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, "-S", os.path.join(ROOT, "main.py")],
        env=env, capture_output=True, text=True, timeout=60)


def laplacian_var(gray):
    """Variance of the Laplacian (3x3 kernel), pure Python + Pillow."""
    w, h = gray.size
    px = gray.load()
    vals = []
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            lap = (4 * px[x, y] - px[x - 1, y] - px[x + 1, y]
                   - px[x, y - 1] - px[x, y + 1])
            vals.append(lap)
    n = len(vals)
    mean = sum(vals) / n
    return sum((v - mean) ** 2 for v in vals) / n


class EntryTest(unittest.TestCase):
    def test_main_writes_valid_png(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            proc = run_entry(tmp)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = os.path.join(tmp, "entry.png")
            self.assertTrue(os.path.isfile(out))
            self.assertEqual(os.stat(out).st_mode & 0o777, 0o644)
            self.assertLessEqual(os.path.getsize(out), 1024 * 1024)
            with Image.open(out) as im:
                self.assertEqual(im.size, (1024, 1024))
                self.assertEqual(im.format, "PNG")

    def test_main_deterministic(self):
        import tempfile
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            self.assertEqual(run_entry(a).returncode, 0)
            self.assertEqual(run_entry(b).returncode, 0)
            with open(os.path.join(a, "entry.png"), "rb") as f:
                ba = f.read()
            with open(os.path.join(b, "entry.png"), "rb") as f:
                bb = f.read()
            self.assertEqual(ba, bb)

    def test_main_stdlib_only_and_no_network_or_clock(self):
        with open(os.path.join(ROOT, "main.py")) as f:
            src = f.read()
        tree = ast.parse(src)
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertTrue(imported <= set(sys.stdlib_module_names),
                        f"non-stdlib imports: {imported}")
        for banned in ("socket", "urllib", "requests", "http", "time",
                       "datetime", "random", "subprocess"):
            self.assertNotIn(banned, imported, f"main.py imports {banned}")

    def test_main_never_chmods_the_output_dir(self):
        with open(os.path.join(ROOT, "main.py")) as f:
            src = f.read()
        # Only the output FILE may be chmodded (dest.chmod); the output
        # directory itself must never be chmodded (Thankful R1 lesson).
        self.assertNotIn("os.chmod(", src)
        self.assertNotIn("out_dir.chmod(", src)
        self.assertIn("dest.chmod(0o644)", src)

    def test_render_rebuilds_entry(self):
        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, "render_poster.py")],
            capture_output=True, text=True, timeout=180)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        entry = os.path.join(ROOT, "entry.png")
        prev = os.path.join(ROOT, "preview-300.png")
        self.assertTrue(os.path.isfile(entry))
        self.assertTrue(os.path.isfile(prev))
        self.assertLessEqual(os.path.getsize(entry), 1024 * 1024)
        with Image.open(entry) as im:
            self.assertEqual(im.size, (1024, 1024))

    def test_preview_300_sharpness(self):
        prev = os.path.join(ROOT, "preview-300.png")
        self.assertTrue(os.path.isfile(prev), "run render_poster.py first")
        with Image.open(prev) as im:
            self.assertEqual(im.size, (300, 300))
            gray = im.convert("L")
        var = laplacian_var(gray)
        self.assertGreaterEqual(var, 1200,
                                f"300px preview too soft: lap var {var:.0f}")

    def test_text_floors(self):
        sizes = render_poster.TEXT_SIZES
        floors = {"hero_headline": 24, "headline": 24, "deck": 20,
                  "stat": 36, "timeline": 20, "tile_label": 18,
                  "datecheck": 18, "footer": 16, "region": 18,
                  "source": 18, "chip": 18, "number": 24, "kicker": 20,
                  "title": 24}
        for role, floor in floors.items():
            self.assertGreaterEqual(sizes[role], floor,
                                    f"{role} {sizes[role]}px < floor {floor}")
        for role, size in sizes.items():
            self.assertGreaterEqual(size, 16, f"{role} {size}px < 16")

    def test_story_record(self):
        with open(os.path.join(ROOT, "STORIES.md")) as f:
            text = f.read()
        headers = re.findall(r"^### \d+\. .*? \u2014 ([A-Z][A-Z \.\-]+?) \u2014 ",
                             text, re.M)
        self.assertEqual(len(headers), 36, f"{len(headers)} stories, want 36")
        regions = {}
        for r in headers:
            regions[r] = regions.get(r, 0) + 1
        self.assertEqual(len(regions), 8, f"regions: {regions}")
        self.assertEqual(sum(regions.values()), 36)
        self.assertIn("DATE CHECK", text)
        self.assertIn("26 DECEMBER 2025", text)
        self.assertIn("3 NOVEMBER 2026", text)


if __name__ == "__main__":
    unittest.main()
