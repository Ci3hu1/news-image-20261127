#!/usr/bin/env python3
"""Entrypoint for the make.fun news-image-20261127 v1 poster.

Standard library only. Copies the bundled poster image (entry.png,
drawn by render_poster.py: "Friday Night Edition" — one full-width hero
panel for the Kuwait drone strike, four large panels for the next four
leads, twelve small picture tiles for the remaining leads, a UTC
timeline, a DATE CHECK box and a sources footer; 36 stories verified
from Reuters / AP / AFP and named outlets, across 8 regions) to the
grader's output location.

No network access, no clock reads, no randomness: the output bytes are
identical on every run. The output file is left world-readable (0644);
the output directory itself is never chmodded.
"""

import os
import shutil
import sys


def _output_dir():
    """Pick the grader's output directory.

    The kit sets MAKEFUN_OUTPUT_DIR (preferred) or MAKEFUN_OUTPUT.
    Otherwise use /output, and fall back to a local ./output if /output
    cannot be created (for example a read-only root in a sandbox).
    """
    here = os.path.dirname(os.path.abspath(__file__))
    for key in ("MAKEFUN_OUTPUT_DIR", "MAKEFUN_OUTPUT"):
        value = os.environ.get(key)
        if value:
            return value
    try:
        os.makedirs("/output", exist_ok=True)
        return "/output"
    except OSError:
        fallback = os.path.join(here, "output")
        os.makedirs(fallback, exist_ok=True)
        return fallback


def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    if not os.path.isfile(source):
        print(f"error: bundled poster missing: {source}", file=sys.stderr)
        return 1
    target_dir = _output_dir()
    os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, "entry.png")
    shutil.copyfile(source, target)
    os.chmod(target, 0o644)
    return 0


if __name__ == "__main__":
    sys.exit(main())
