#!/usr/bin/env python3
"""Friday Night Edition entrypoint (news-image-20261127 v2).

The grader runs this program with a plain Python 3.13 standard library
and no network. All it does is put the poster that ships in this
repository (entry.png, drawn by render_poster.py) into the directory
the grader collects output from, under the name entry.png, readable by
every user. Run it twice and the bytes are identical: the file is
copied, never generated, and nothing here reads a clock or any
randomness.
"""

import os
import shutil
import sys
from pathlib import Path

POSTER = "entry.png"


def _where_to_write():
    """Return the directory the grader collects output from."""
    for name in ("MAKEFUN_OUTPUT_DIR", "MAKEFUN_OUTPUT"):
        given = os.environ.get(name)
        if given:
            return Path(given)
    try:
        Path("/output").mkdir(parents=True, exist_ok=True)
        return Path("/output")
    except OSError:
        local = Path(__file__).resolve().parent / "output"
        local.mkdir(parents=True, exist_ok=True)
        return local


def main():
    here = Path(__file__).resolve().parent
    poster = here / POSTER
    if not poster.is_file():
        print(f"bundled poster not found: {poster}", file=sys.stderr)
        sys.exit(1)
    out_dir = _where_to_write()
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / POSTER
    shutil.copyfile(poster, dest)
    dest.chmod(0o644)
    sys.exit(0)


if __name__ == "__main__":
    main()
