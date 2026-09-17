#!/usr/bin/env python3
"""Record demo output as an animated GIF for README/docs (CM-607)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO = REPO_ROOT / "examples" / "demo" / "run_demo.py"
OUT = REPO_ROOT / "assets" / "demo.gif"


def _capture_lines() -> list[str]:
    proc = subprocess.run(
        [sys.executable, str(DEMO)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout.splitlines()


def _write_gif(lines: list[str], path: Path) -> None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise SystemExit("Install Pillow to record demo GIF: pip install pillow") from exc

    path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 900, 520
    frames: list[Image.Image] = []
    chunk_size = 18
    for i in range(0, len(lines), chunk_size):
        chunk = lines[i : i + chunk_size]
        img = Image.new("RGB", (width, height), color=(15, 23, 42))
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        y = 20
        for line in chunk:
            draw.text((20, y), line[:100], fill=(226, 232, 240), font=font)
            y += 16
        frames.append(img)
    if not frames:
        frames = [Image.new("RGB", (width, height), color=(15, 23, 42))]
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=1200,
        loop=0,
        optimize=True,
    )


def main() -> int:
    lines = _capture_lines()
    _write_gif(lines, OUT)
    print(f"Wrote {OUT} ({len(lines)} lines, animated)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
