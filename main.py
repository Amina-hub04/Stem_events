import requests
import os
import time
import json
from datetime import datetime, timedelta
from ai_extract import extract_events_from_text, safe_get

# 👇 Timeline filter function
def is_in_timeline(event_date_str):
    try:
        event_date = datetime.strptime(event_date_str, "%Y-%m-%d")
        today = datetime.today()
        past_limit = today - timedelta(days=30)
        future_limit = today + timedelta(days=60)
        return past_limit <= event_date <= future_limit
    except Exception:
        return False

# 👇 Pakistan event sources (expanded)
SOURCES = [
    {"name": "EventAlways - Pakistan IT & Tech", "url": "https://www.eventalways.com/pakistan/it-technology"},
    {"name": "EventAlways - ICSTM 2026", "url": "https://www.eventalways.com/international-conference-on-science-technology-and-management-icstm-226123"},
    {"name": "Pakistan Expo Centres", "url": "https://www.pakexcel.com"},
    {"name": "AllEvents - Lahore Technology", "url": "https://allevents.in/lahore/technology"},
    {"name": "TechDestination Events", "url": "https://techdestination.com/events"},
    {"name": "Pakistani IT Expo", "url": "https://example.com/pakistan-it-expo"},
    {"name": "University STEM Conferences", "url": "https://example.com/university-stem-events"}
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

        # 👇 Timeline filter applied here
        filtered_events = []
        for ev in events:
            if "date" in ev and is_in_timeline(ev["date"]):
                filtered_events.append(ev)

        if filtered_events:
            print(f"✅ {len(filtered_events)} events kept for timeline.")
            all_events.extend(filtered_events)
        else:
            print(f"⚠️ No events in timeline for {source['name']}.")

        # 👇 Add delay between API calls
        time.sleep(2)

    # 👇 Always save results (even empty)
    with open("events_output.json", "w", encoding="utf-8") as f:
        if all_events:
            json.dump(all_events, f, indent=2, ensure_ascii=False)
            print("🎉 Events saved to events_output.json")
        else:
            json.dump([], f, indent=2, ensure_ascii=False)
            print("⚠️ No events found, saved empty events_output.json")

if __name__ == "__main__":
    run_pipeline()
