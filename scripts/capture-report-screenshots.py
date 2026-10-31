#!/usr/bin/env python3
"""Capture realistic desktop-sized screenshots for the project report."""

from pathlib import Path
from playwright.sync_api import sync_playwright

ASSETS = Path(__file__).resolve().parents[1] / "docs" / "report-assets"
BASE = "http://127.0.0.1:3456"
VIEW = {"width": 1366, "height": 768}


def shot(page, url: str, outfile: Path) -> None:
    page.goto(url, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(500)
    page.screenshot(path=str(outfile), full_page=False)
    print(f"saved {outfile.name}")


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport=VIEW, device_scale_factor=1)
        shots = [
            (f"{BASE}/demo-suite.html", ASSETS / "fig-demo-console.png"),
            (f"{BASE}/ss-page-create.html", ASSETS / "fig-create-json.png"),
            (f"{BASE}/ss-page-redirect.html", ASSETS / "fig-redirect-headers.png"),
            (f"{BASE}/ss-page-404.html", ASSETS / "fig-404.png"),
            (f"{BASE}/ss-page-terminal.html", ASSETS / "fig-terminal.png"),
            ("http://127.0.0.1:3000/health", ASSETS / "fig-health-browser.png"),
            ("https://github.com/Akshith7707/URL-shortner", ASSETS / "fig-github.png"),
        ]
        for url, out in shots:
            try:
                shot(page, url, out)
            except Exception as exc:
                print(f"FAILED {url}: {exc}")
        browser.close()


if __name__ == "__main__":
    main()
