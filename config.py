"""
Config for the STEM Events Auto-Retrieval project.
Add/remove sources here as you extend from Pakistan -> worldwide.
"""

from datetime import date, timedelta
import os

# ---- Phase 1: Pakistan sources ----
SOURCES = [
    {
        "name": "EventAlways - Pakistan IT & Tech",
        "url": "https://www.eventalways.com/pakistan/it-technology",
    },
    {
        "name": "EventAlways - ICSTM 2026",
        "url": "https://www.eventalways.com/international-conference-on-science-technology-and-management-icstm-226123",
    },
    {
        "name": "Pakistan Expo Centres",
        "url": "https://www.pakexcel.com/",
    },
    {
        "name": "AllEvents - Lahore Technology",
        "url": "https://allevents.in/lahore/technology",
    },
    {
        "name": "TechDestination - Events & Delegations",
        "url": "https://techdestination.com/events-and-delegations/",
    },
    {
        "name": "10Times - Pakistan Technology",
        "url": "https://10times.com/pakistan/technology",
    },
]

# ---- Phase 2: Worldwide sources ----
SOURCES += [
    {
        "name": "10Times - Global Technology",
        "url": "https://10times.com/technology",
    },
    {
        "name": "10Times - Global Science & Research",
        "url": "https://10times.com/research",
    },
    {
        "name": "10Times - Global Engineering",
        "url": "https://10times.com/engineering",
    },
]

# STEM keyword filter (used as a backstop check on top of AI classification)
STEM_KEYWORDS = [
    "science", "technology", "tech", "engineering", "math", "maths",
    "ai", "artificial intelligence", "robotics", "data", "software",
    "innovation", "research", "computing", "electronics", "biotech",
    "IT", "conference", "expo", "hackathon", "workshop", "symposium",
]

# Date window: past 1 month -> upcoming 2 months
TODAY = date.today()
WINDOW_START = TODAY - timedelta(days=30)
WINDOW_END = TODAY + timedelta(days=60)

# Output storage
OUTPUT_JSON = "events_output.json"

# API key (set as environment variable, don't hardcode)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
