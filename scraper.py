"""
Fetches raw text content from each source page.
Static pages: requests + BeautifulSoup is enough.
JS-heavy pages (allevents.in, 10times.com often render listings via JS):
  swap this out for Playwright if requests returns near-empty content.
"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def fetch_page_text(url: str, timeout: int = 15) -> str:
    """Fetch a page and return cleaned visible text (script/style stripped)."""
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def fetch_page_html_with_playwright(url: str) -> str:
    """
    Fallback for JS-rendered sites. Requires: pip install playwright
    then: playwright install chromium
    Only call this if fetch_page_text() comes back too short/empty.
    """
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, timeout=30000)
        page.wait_for_timeout(3000)  # let JS listings render
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def fetch_source(source: dict) -> dict:
    """Try static fetch first; flag for JS fallback if content looks too thin."""
    try:
        text = fetch_page_text(source["url"])
        if len(text) < 300:  # likely JS-rendered, static fetch got almost nothing
            return {"name": source["name"], "url": source["url"], "text": text, "needs_js": True}
        return {"name": source["name"], "url": source["url"], "text": text, "needs_js": False}
    except Exception as e:
        return {"name": source["name"], "url": source["url"], "text": "", "error": str(e)}
