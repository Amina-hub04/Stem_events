"""
Main pipeline: run this on a schedule (cron / GitHub Actions) to keep
the events list auto-populated.

Usage:
    export GEMINI_API_KEY=your_key_here
    python main.py
"""

import json

from config import SOURCES, OUTPUT_JSON
from scraper import fetch_source, fetch_page_html_with_playwright
from ai_extract import extract_events_from_text
from filters import apply_filters


def run_pipeline():
    all_events = []

    for source in SOURCES:
        print(f"Fetching: {source['name']}...")
        result = fetch_source(source)

        if result.get("error"):
            print(f"  Skipped ({result['error']})")
            continue

        text = result["text"]
        if result.get("needs_js"):
            print("  Static fetch too thin, retrying with Playwright...")
            try:
                text = fetch_page_html_with_playwright(source["url"])
            except Exception as e:
                print(f"  Playwright fallback failed: {e}")
                continue

        if not text:
            print("  No content extracted, skipping.")
            continue

        print("  Extracting events with AI...")
        events = extract_events_from_text(text, source["name"])
        print(f"  Found {len(events)} raw event(s).")
        all_events.extend(events)

    print(f"\nTotal raw events collected: {len(all_events)}")
    final_events = apply_filters(all_events)
    print(f"Events in STEM + date window: {len(final_events)}")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(final_events, f, indent=2, ensure_ascii=False)

    print(f"Saved to {OUTPUT_JSON}")
    return final_events


if __name__ == "__main__":
    run_pipeline()
