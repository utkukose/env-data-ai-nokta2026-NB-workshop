"""Open every page of the site in Chrome and report script errors and overflow.

Needs Playwright for Python and a Chrome or Chromium browser:
    pip install playwright && python -m playwright install chromium
Run:
    python tools/check_site.py [--shots out_dir]
"""
import argparse
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["index", "part1", "part2", "part3", "part4", "part5", "lab"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", default="")
    ap.add_argument("--chrome", default="")
    ap.add_argument("--pages", default=",".join(PAGES))
    args = ap.parse_args()
    shots = Path(args.shots) if args.shots else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)
    failures = 0
    with sync_playwright() as p:
        launch = dict(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader",
                            "--ignore-gpu-blocklist", "--allow-file-access-from-files"])
        if args.chrome:
            launch["executable_path"] = args.chrome
        browser = p.chromium.launch(**launch)
        for lang in ("en", "tr"):
            for page_name in args.pages.split(","):
                path = ROOT / "docs" / (f"{page_name}.html" if lang == "en" else f"tr/{page_name}.html")
                for width in (1400, 375):
                    ctx = browser.new_context(viewport={"width": width, "height": 900})
                    page = ctx.new_page()
                    errors = []
                    page.on("pageerror", lambda e, errors=errors: errors.append(str(e)))
                    page.on("console", lambda m, errors=errors: errors.append(m.text)
                            if m.type == "error" and "fonts.g" not in m.text
                            and "ERR_" not in m.text else None)
                    page.goto(path.as_uri())
                    page.wait_for_timeout(2500)
                    overflow = page.evaluate(
                        "document.documentElement.scrollWidth - document.documentElement.clientWidth")
                    ok = not errors and overflow <= 1
                    failures += 0 if ok else 1
                    print(f"{'OK ' if ok else 'ERR'} {lang} {page_name:6s} {width:4d}px"
                          f" overflow={overflow} errors={errors[:3]}")
                    if shots and width == 1400:
                        page.screenshot(path=str(shots / f"{lang}_{page_name}.png"))
                    ctx.close()
        browser.close()
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
