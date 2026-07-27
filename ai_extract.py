import os
import time
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

# Example usage inside your pipeline
def extract_events_from_text(text, source_name):
    data = {
        "contents": [{"parts": [{"text": text}]}]
    }
    try:
        result = safe_gemini_request(data)
        return result
    except Exception as e:
        print(f"Error extracting events for {source_name}: {e}")
        return None
