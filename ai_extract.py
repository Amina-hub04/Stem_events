"""
Uses Gemini to extract structured event data from a page's raw text.
This is the "AI" part of the pipeline: one prompt handles every site's
different HTML layout instead of writing a custom parser per source.
"""

import json
import re
import requests

from config import GEMINI_API_KEY

def safe_request(url, headers, data):
    for attempt in range(5):
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code == 429:  # Too Many Requests
            print("Rate limit hit, waiting...")
            time.sleep(10)  # wait before retry
            continue
        resp.raise_for_status()
        return resp
    raise Exception("Gemini API failed after retries") 

headers = {"User-Agent": "Mozilla/5.0"}
resp = requests.get(url, headers=headers)

resp = requests.get(url, headers=headers, verify=False)

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent?key={key}"
)

EXTRACTION_PROMPT = """You are extracting event listings from a webpage's text content.

From the text below, find every distinct event related to Science, Technology,
Engineering, or Maths (conferences, expos, workshops, hackathons, symposiums, etc).

For each event, return a JSON object with these fields:
- "title": event name
- "date": event date as written on the page (keep original format, e.g. "May 2026" or "12 Aug 2026")
- "location": city/venue if mentioned, else ""
- "category": one of ["Science", "Technology", "Engineering", "Maths", "General STEM"]
- "source_note": one short phrase from the page giving context (not a full sentence copy)

Return ONLY a JSON array, no other text, no markdown fences. If no events found, return [].

PAGE TEXT:
---
{page_text}
---
"""


def extract_events_from_text(page_text: str, source_name: str) -> list:
    if not GEMINI_API_KEY:
        raise RuntimeError("Set GEMINI_API_KEY environment variable before running AI extraction.")

    # Trim very long pages to keep prompt reasonable
    trimmed = page_text[:12000]

    payload = {
        "contents": [
            {"parts": [{"text": EXTRACTION_PROMPT.format(page_text=trimmed)}]}
        ]
    }

    resp = requests.post(
        GEMINI_URL.format(key=GEMINI_API_KEY),
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    try:
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return []

    # Strip accidental markdown fences if the model adds them
    cleaned = re.sub(r"^```json|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()

    try:
        events = json.loads(cleaned)
    except json.JSONDecodeError:
        return []

    for e in events:
        e["source"] = source_name

    return events
