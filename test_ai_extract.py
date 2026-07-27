from ai_extract import safe_get, extract_events_from_text

# 👇 Test ek real Pakistan source se
url = "https://allevents.in/lahore/technology"
text = safe_get(url)

if text:
    events = extract_events_from_text(text, "AllEvents - Lahore Technology")
    print("Extracted events:", events)
else:
    print("⚠️ Could not fetch source")
