import os
import time
import json
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# Safe request wrapper for Gemini API
def safe_gemini_request(data, max_retries=5, wait=10):
    headers = {"Content-Type": "application/json"}
    for attempt in range(max_retries):
        resp = requests.post(GEMINI_URL, headers=headers, json=data)
        if resp.status_code == 429:  # Too Many Requests
            print("Rate limit hit, waiting before retry...")
            time.sleep(wait)
            continue
        if resp.status_code == 401:  # Unauthorized
            raise Exception("Gemini API Unauthorized – check your API key.")
        resp.raise_for_status()
        return resp.json()
    raise Exception("Gemini API failed after retries")

# Safe GET request for scraping sites
def safe_get(url, max_retries=3):
    headers = {"User-Agent": "Mozilla/5.0"}
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=headers, timeout=15, verify=False)
            if resp.status_code == 403:
                print(f"Skipped (403 Forbidden for url: {url})")
                return None
            resp.raise_for_status()
            return resp.text
        except requests.exceptions.SSLError:
            print(f"Skipped (SSL error for url: {url})")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(5)
    return None

# Refined AI extraction function
def extract_events_from_text(text, source_name):
    prompt = f"""
    Extract upcoming STEM (Science, Technology, Engineering, Maths) events 
    from the following text.

    Output must be a JSON array with fields:
    - name
    - date (YYYY-MM-DD format)
    - location
    - topic

    Skip events without a valid date.
    Source: {source_name}
    Text: {text}
    """

    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        result = safe_gemini_request(data)

        # Gemini response parsing
        if "candidates" in result and len(result["candidates"]) > 0:
            raw_text = result["candidates"][0]["content"]["parts"][0]["text"]
            try:
                events = json.loads(raw_text)
                if isinstance(events, list):
                    return events
                else:
                    print("⚠️ AI did not return a list, skipping...")
                    return None
            except Exception as e:
                print(f"⚠️ Error parsing JSON: {e}")
                return None
        else:
            print("⚠️ No candidates returned from Gemini.")
            return None

    except Exception as e:
        print(f"Error extracting events for {source_name}: {e}")
        return None
