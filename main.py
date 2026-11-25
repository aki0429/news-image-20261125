#!/usr/bin/env python3
"""make.fun entry — "Sum up 25 November's world news in one image".

The repository ships entry.png: a one-image front page of the world news of
Wednesday 25 November 2026, drawn by tools/render_poster.py from the verified
stories in news.json (see SOURCES.md). This program writes that image to the
output directory, byte for byte, so both grading runs produce the same file.

Python 3.13, standard library only. No network, no clocks, no randomness.
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")


def main() -> None:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    with open(SOURCE, "rb") as f:
        data = f.read()
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
