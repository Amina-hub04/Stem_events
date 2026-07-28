import os
import requests
import json

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"

payload = {"contents": [{"parts": [{"text": "Say hello in one word."}]}]}

resp = requests.post(GEMINI_URL, headers={"Content-Type": "application/json"}, json=payload)

print("Status code:", resp.status_code)
print("Response body:")
print(json.dumps(resp.json(), indent=2))
