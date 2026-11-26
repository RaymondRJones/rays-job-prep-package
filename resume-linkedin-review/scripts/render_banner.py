#!/usr/bin/env python3
"""Render a LinkedIn banner HTML file to a 1584 x 396 PNG with headless Chrome.

  python3 render_banner.py banner.html                # writes banner.png next to it
  python3 render_banner.py banner.html -o out.png
  python3 render_banner.py banner.html --preview      # also writes banner-preview.png
                                                      # (photo position, plus phone size)

Needs Google Chrome, Chromium or Edge. Set CHROME=/path/to/chrome if it isn't found.
"""
import argparse
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

WIDTH, HEIGHT = 1584, 396

CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def find_chrome():
    for c in [os.environ.get("CHROME")] + CANDIDATES:
        if not c:
            continue
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c
        found = shutil.which(c)
        if found:
            return found
    sys.exit("Chrome not found. Install Google Chrome or set CHROME=/path/to/chrome.")


def shoot(chrome, url, out, width, height, scale=1):
    with tempfile.TemporaryDirectory() as profile:
        cmd = [
            chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
            f"--user-data-dir={profile}", f"--window-size={width},{height}",
            f"--force-device-scale-factor={scale}", f"--screenshot={out}", url,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    if not os.path.isfile(out):
        sys.exit(f"Chrome did not write {out}.\n{r.stderr[-800:]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("html")
    ap.add_argument("-o", "--out")
    ap.add_argument("--preview", action="store_true",
                    help="also write <name>-preview.png: the banner with the profile photo drawn in, "
                         "and the same thing at phone size")
    a = ap.parse_args()

    src = pathlib.Path(a.html).resolve()
    if not src.is_file():
        sys.exit(f"No such file: {src}")
    out = pathlib.Path(a.out).resolve() if a.out else src.with_suffix(".png")
    chrome = find_chrome()

    shoot(chrome, src.as_uri(), str(out), WIDTH, HEIGHT)
    print(f"Banner: {out} ({WIDTH} x {HEIGHT})")

    if a.preview:
        prev = out.with_name(out.stem + "-preview.png")
        # One page: full-size banner with the photo, then the phone-size version under it.
        page = f"""<!doctype html><meta charset="utf-8">
<body style="margin:0;background:#e9edf1;font:20px Helvetica,Arial,sans-serif;color:#333">
<div style="padding:12px 16px">Desktop, with the profile photo</div>
<iframe src="{src.as_uri()}?preview=1" style="border:0;display:block;width:{WIDTH}px;height:{HEIGHT + 120}px"></iframe>
<div style="padding:12px 16px">Phone size (390 px wide). Anything you can't read here, a recruiter can't either.</div>
<div style="width:390px;height:{(HEIGHT + 120) // 4 + 4}px;overflow:hidden;margin-left:16px">
<iframe src="{src.as_uri()}?preview=1" style="border:0;width:{WIDTH}px;height:{HEIGHT + 120}px;
 transform:scale({390 / WIDTH});transform-origin:0 0"></iframe></div></body>"""
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, dir=src.parent) as f:
            f.write(page)
            tmp = f.name
        try:
            shoot(chrome, pathlib.Path(tmp).as_uri(), str(prev), WIDTH, HEIGHT + 120 + 260)
        finally:
            os.unlink(tmp)
        print(f"Preview: {prev}")


if __name__ == "__main__":
    main()
