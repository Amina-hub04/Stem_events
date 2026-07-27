"""
Filters extracted events down to the target date window (past 1 month,
upcoming 2 months) and de-duplicates near-identical entries.
"""

from datetime import datetime
from dateutil import parser as dateparser  # pip install python-dateutil

from config import WINDOW_START, WINDOW_END, STEM_KEYWORDS


def parse_event_date(date_str: str):
    """Best-effort parse of loosely-formatted date strings like 'May 2026'."""
    if not date_str:
        return None
    try:
        # fuzzy=True lets it pull a date out of messy strings
        return dateparser.parse(date_str, fuzzy=True, default=datetime(2026, 1, 1)).date()
    except (ValueError, OverflowError):
        return None


def in_date_window(event: dict) -> bool:
    parsed = parse_event_date(event.get("date", ""))
    if parsed is None:
        # keep undated events out of the auto-filtered list, but don't lose them
        event["_date_parsed"] = False
        return False
    event["_date_parsed"] = True
    event["_date_value"] = parsed.isoformat()
    return WINDOW_START <= parsed <= WINDOW_END


def is_stem_related(event: dict) -> bool:
    haystack = f"{event.get('title','')} {event.get('category','')} {event.get('source_note','')}".lower()
    return any(kw.lower() in haystack for kw in STEM_KEYWORDS)


def dedupe(events: list) -> list:
    seen = set()
    unique = []
    for e in events:
        key = e.get("title", "").strip().lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(e)
    return unique


def apply_filters(events: list) -> list:
    stem_only = [e for e in events if is_stem_related(e)]
    dated = [e for e in stem_only if in_date_window(e)]
    return dedupe(dated)
