STEM Events Auto-Retrieval
Auto-fetches upcoming Science / Tech / Engineering / Maths (STEM) events.
Phase 1: Pakistan events.
Phase 2: Worldwide events.

Filters: past 30 days + upcoming 60 days.
Outputs: events_output.json, events_pakistan.json, events_global.json.

How it works
scraper.py — pulls raw text from each source page (requests + BeautifulSoup).
-If page looks JS-rendered (very little text), falls back to Playwright (Chromium).

ai_extract.py — sends raw text to Gemini with one extraction prompt.
-Returns structured JSON: title, date, location, category, source.

filters.py — keeps only STEM-tagged events in target window (today − 30 days → today + 60 days).
-Deduplicates overlapping events.

main.py — runs the pipeline end-to-end and saves results.

Setup:
-pip install -r requirements.txt
-playwright install chromium   # needed if JS fallback required
-export GEMINI_API_KEY=your_key_here   # get one free at aistudio.google.com
-python main.py

Outputs:
-events_output.json → consolidated list
-events_pakistan.json → Pakistan-only events
-events_global.json → worldwide events

Example Output:
json
[
  {
    "title": "ICSTM 2026 - International Conference on Science, Technology and Management",
    "date": "2026-05-01",
    "location": "Rawalpindi, Pakistan",
    "category": "Science",
    "source_note": "Annual conference bringing together researchers",
    "source": "EventAlways - ICSTM 2026",
    "_date_parsed": true
  }
]

Making it "auto-populate":
GitHub Actions is already set up in .github/workflows/run.yml — runs main.py daily and commits refreshed JSON outputs back to repo.

Steps:
-Push project to GitHub.
                  In repo → Settings → Secrets → Actions → New repository secret, add GEMINI_API_KEY.
Workflow runs daily at 06:00 UTC, or manually via Actions tab (workflow_dispatch enabled).
Alternative (local cron job):

Code:
  0 6 * * * cd /path/to/stem_events && python main.py

Extending to worldwide (Phase 2):
-Add more entries to SOURCES in config.py (e.g. 10times.com global tech, Eventbrite tech).
-No pipeline changes needed — AI extraction adapts automatically.

Things to check when you actually run this:
-Some sites (10times, allevents.in) may block scraping — check terms.
-Playwright with browser context works better than plain requests.
-Verify AI extraction quality against source pages.
-Gemini free tier has rate limits — add time.sleep() between calls if needed.
