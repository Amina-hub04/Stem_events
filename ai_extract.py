import os
import time
import json
import requests
from bs4 import BeautifulSoup

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"


# Safe GET request for scraping sites - returns clean visible text, not raw HTML
def safe_get(url, max_retries=3):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=headers, timeout=15, verify=False)
            if resp.status_code == 403:
                print(f"Skipped (403 Forbidden for url: {url})")
                return None
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "noscript", "svg"]):
                tag.decompose()
            text = soup.get_text(separator="\n")
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            clean_text = "\n".join(lines)

            if len(clean_text) < 200:
                print(f"⚠️ Very little text found for {url} — page may need JavaScript to render.")

            return clean_text
        except requests.exceptions.SSLError:
            print(f"Skipped (SSL error for url: {url})")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(5)
    return None


# Safe request wrapper for Groq API (retries on rate limit)
def safe_groq_request(payload, max_retries=5, wait=10):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}",
    }
    for attempt in range(max_retries):
        resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
        if resp.status_code == 429:
            print(f"Rate limit hit, waiting {wait}s before retry...")
            time.sleep(wait)
            wait += 5
            continue
        if resp.status_code == 401:
            raise Exception("Groq API Unauthorized - check your GROQ_API_KEY.")
        resp.raise_for_status()
        return resp.json()
    raise Exception("Groq API failed after retries")


# AI extraction function (schema: name, date, location, topic)
def extract_events_from_text(text, source_name):
    if not GROQ_API_KEY:
        print("⚠️ GROQ_API_KEY not set.")
        return None

    prompt = f"""
    Extract upcoming STEM (Science, Technology, Engineering, Maths) events
    from the following text.

    Output must be a JSON array with fields:
    - name
    - date (YYYY-MM-DD format)
    - location
    - topic

    Skip events without a valid date. Return ONLY the JSON array, no other text,
    no markdown fences. If no events found, return [].

    Source: {source_name}
    Text: {text[:12000]}
    """

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }

    try:
        result = safe_groq_request(payload)

        raw_text = result["choices"][0]["message"]["content"].strip()

        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            raw_text = raw_text.replace("json", "", 1).strip()

        try:
            events = json.loads(raw_text)
            if isinstance(events, list):
                return events
            else:
                print("⚠️ AI did not return a list, skipping...")
                return None
        except Exception as e:
            print(f"⚠️ Error parsing JSON: {e}")
            print(f"   Raw AI response was: {raw_text[:300]}")
            return None

    except Exception as e:
        print(f"Error extracting events for {source_name}: {e}")
        return None