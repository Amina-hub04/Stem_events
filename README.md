# STEM Events Auto-Retrieval

Auto-fetches upcoming Science/Tech/Engineering/Maths events (Pakistan first,
worldwide as phase 2), filtered to the past 1 month + upcoming 2 months, and
writes them to `events_output.json`.

## How it works

1. **scraper.py** — pulls raw visible text off each source page (`requests`
   + BeautifulSoup). If a page looks JS-rendered (very little text comes
   back), it falls back to Playwright to load the page in a real browser.
2. **ai_extract.py** — sends that raw text to Gemini with one extraction
   prompt that works across every site's different layout, and gets back
   structured JSON: title, date, location, category, source.
   This is the part that replaces writing a custom HTML parser per site.
3. **filters.py** — keeps only STEM-tagged events whose date falls in the
   target window (today - 30 days to today + 60 days), and de-dupes.
4. **main.py** — runs all of the above end to end and saves the result.

## Setup

```bash
pip install -r requirements.txt
playwright install chromium   # only needed if a source needs the JS fallback

export GEMINI_API_KEY=your_key_here   # get one free at aistudio.google.com

python main.py
```

Output lands in `events_output.json`, e.g.:

```json
[
  {
    "title": "ICSTM 2026 - International Conference on Science, Technology and Management",
    "date": "May 2026",
    "location": "Rawalpindi, Pakistan",
    "category": "Science",
    "source_note": "Annual conference bringing together researchers",
    "source": "EventAlways - ICSTM 2026",
    "_date_parsed": true,
    "_date_value": "2026-05-01"
  }
]
```

## Making it "auto-populate"

**GitHub Actions is already set up** in `.github/workflows/run.yml` — it runs
`main.py` daily and commits the refreshed `events_output.json` straight back
to the repo. To activate it:

1. Push this project to a GitHub repo.
2. In the repo, go to **Settings → Secrets and variables → Actions → New
   repository secret**, add a secret named `GEMINI_API_KEY` with your key
   as the value. (Never commit the key itself to the repo.)
3. That's it — the workflow runs automatically every day at 06:00 UTC. You
   can also trigger it manually any time from the **Actions** tab (it has
   `workflow_dispatch` enabled).
4. Any frontend (a simple React page, or even a static HTML page) can then
   fetch `events_output.json` from the repo's raw GitHub URL — always
   showing the latest list with zero manual work.

Alternative if you're running this on your own machine/server instead of
GitHub Actions:
```
0 6 * * * cd /path/to/stem_events && python main.py
```
Runs daily at 6am and refreshes `events_output.json` locally.

## Extending to worldwide (Phase 2)

Just add more entries to `SOURCES` in `config.py` — e.g. 10times.com global
tech listings, Eventbrite's tech category, etc. Nothing else in the
pipeline needs to change, since the AI extraction step adapts to each
page's format automatically.

## Things to check when you actually run this

- Some sites (10times, allevents.in) may block simple scraping via
  robots.txt/anti-bot measures — check their terms before scraping, and
  Playwright with a real browser context usually gets through better than
  plain `requests`.
- The AI extraction quality depends on how much event info is actually
  visible as plain text on the page vs. loaded as images — verify a few
  sample outputs manually against the source page.
- Gemini free tier has rate limits — if you're hitting many sources, add
  a short `time.sleep()` between calls in `main.py`.
