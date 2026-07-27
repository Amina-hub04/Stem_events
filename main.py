import requests
import os
import time
import json
from ai_extract import extract_events_from_text, safe_get

# Sources list
SOURCES = [
    {"name": "EventAlways - Pakistan IT & Tech", "url": "https://www.eventalways.com/pakistan/it-technology"},
    {"name": "EventAlways - ICSTM 2026", "url": "https://www.eventalways.com/international-conference-on-science-technology-and-management-icstm-226123"},
    {"name": "Pakistan Expo Centres", "url": "https://www.pakexcel.com"},
    {"name": "AllEvents - Lahore Technology", "url": "https://allevents.in/lahore/technology"},
]

def run_pipeline():
    all_events = []

    for source in SOURCES:
        print(f"Fetching: {source['name']}...")
        text = safe_get(source["url"])  # safe_get handles SSL + 403

        if text is None:
            print(f"⚠️ Skipped {source['name']} (no data)")
            continue

        print("Extracting events with AI...")
        events = extract_events_from_text(text, source["name"])

        if events is None:
            print(f"⚠️ No events extracted for {source['name']}, skipping...")
            continue

        if isinstance(events, list):
            print(f"✅ Found {len(events)} raw event(s).")
            all_events.extend(events)
        else:
            print(f"⚠️ Unexpected data format for {source['name']}, skipping...")

    # Always save results (even empty)
    with open("events_output.json", "w", encoding="utf-8") as f:
        if all_events:
            json.dump(all_events, f, indent=2, ensure_ascii=False)
            print("🎉 Events saved to events_output.json")
        else:
            json.dump([], f, indent=2, ensure_ascii=False)
            print("⚠️ No events found, saved empty events_output.json")

if __name__ == "__main__":
    run_pipeline()
