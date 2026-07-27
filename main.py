import requests
import os
import time
from ai_extract import extract_events_from_text, safe_get

# Sources list (example)
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

        print(f"✅ Found {len(events)} raw event(s).")
        all_events.extend(events)

    # Save results
    if all_events:
        with open("events_output.json", "w", encoding="utf-8") as f:
            import json
            json.dump(all_events, f, indent=2, ensure_ascii=False)
        print("🎉 Events saved to events_output.json")
    else:
        print("⚠️ No events found at all.")

if __name__ == "__main__":
    run_pipeline()
