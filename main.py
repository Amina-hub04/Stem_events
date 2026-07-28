import requests
import os
import time
import json
import urllib3
from datetime import datetime, timedelta
from ai_extract import extract_events_from_text, safe_get

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Timeline filter function
def is_in_timeline(event_date_str):
    try:
        event_date = datetime.strptime(event_date_str, "%Y-%m-%d")
        today = datetime.today()
        past_limit = today - timedelta(days=30)
        future_limit = today + timedelta(days=60)
        return past_limit <= event_date <= future_limit
    except Exception:
        return False

# Pakistan + Global event sources (Phase 1 + Phase 2)
SOURCES = [
    {"name": "EventAlways - Pakistan IT & Tech", "url": "https://www.eventalways.com/pakistan/it-technology"},
    {"name": "AllEvents - Lahore Technology", "url": "https://allevents.in/lahore/technology"},
    {"name": "TechDestination Events", "url": "https://techdestination.com/events-and-delegations/"},
    {"name": "Pakistan Expo Centres", "url": "https://www.pakexcel.com/"},
    {"name": "10Times - Pakistan Technology", "url": "https://10times.com/pakistan/technology"},
    {"name": "10Times - Global Technology", "url": "https://10times.com/technology"},
    {"name": "10Times - Global Science & Research", "url": "https://10times.com/research"},
    {"name": "10Times - Global Engineering", "url": "https://10times.com/engineering"},
]

# Save events separately (Pakistan vs Global)
def save_events(events, source_name):
    if "Pakistan" in source_name:
        filename = "events_pakistan.json"
    else:
        filename = "events_global.json"

    # Add source field to each event
    for ev in events:
        ev["source"] = source_name

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(events)} events to {filename}")

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

        print(f"🔍 Raw events found: {len(events)}")
        for ev in events[:5]:
            print(f"   {ev}")

        # Timeline filter applied here
        filtered_events = []
        for ev in events:
            if "date" in ev and is_in_timeline(ev["date"]):
                ev["source"] = source["name"]  # enrich with source field
                filtered_events.append(ev)

        if filtered_events:
            print(f"✅ {len(filtered_events)} events kept for timeline.")
            all_events.extend(filtered_events)
            save_events(filtered_events, source["name"])
        else:
            print(f"⚠️ No events in timeline for {source['name']}.")

        # Delay between API calls to respect rate limits
        time.sleep(10)

    # Always save consolidated results too
    with open("events_output.json", "w", encoding="utf-8") as f:
        if all_events:
            json.dump(all_events, f, indent=2, ensure_ascii=False)
            print("🎉 Consolidated events saved to events_output.json")
        else:
            json.dump([], f, indent=2, ensure_ascii=False)
            print("⚠️ No events found, saved empty events_output.json")

if __name__ == "__main__":
    run_pipeline()
