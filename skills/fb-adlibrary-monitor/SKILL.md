---
name: fb-adlibrary-monitor
description: Daily Facebook/Meta Ad Library competitor monitor for Bloomin. Uses Playwright + Chrome cookies to scrape active ads without a Meta API token. Stores advertisers in Postgres, flags brand-new advertisers, and posts a Block Kit report per search query to Slack. Use for the fb-adlibrary-monitor cron job.
---

# Facebook Ad Library Monitor — Daily Report

## What This Does
Scrapes the Meta Ad Library for 6 keyword queries, extracts active advertisers and ad hooks, deduplicates, stores in Postgres, identifies brand-new advertisers vs yesterday, and posts a per-query breakdown to Slack.

## Step 1 — Run the Script
```bash
python3 /Users/teambloomin/.openclaw/workspace/scripts/fb-ads-scraper.py
```

## How Scraping Works (for debugging)

### Search Queries
1. libido supplement women
2. shilajit honey sticks
3. female desire supplement
4. shatavari women supplement
5. women desire restore supplement
6. cortisol women libido supplement

### Method
- Playwright + persistent Chrome context from `~/Library/Application Support/Google/Chrome`
- Chrome profile copied to `/tmp/chrome-profile-fb` before each run (fresh cookies)
- Headless mode, `--disable-blink-features=AutomationControlled`
- URL template: `https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&q={query}&search_type=keyword_unordered&media_type=all`
- Scrolls 3x to load more results
- Parses `body` text: advertiser = line before "Sponsored", ad text = next 5 lines, start date from "Started running on" lines

### Failure Modes
- **"Log in to Facebook"** in body → Chrome cookies expired → need to log back into Facebook in Chrome manually
- **403/timeout** → Meta blocking — wait and retry next day
- If all queries fail: post failure notice to `C0AM45T4XT8` with specific error

## Step 2 — Deduplication
Within the run: deduplicate by `advertiser.lower()` — one entry per brand.

Across days: compare against `competitor_mentions` table where `platform='facebook_ads'` and `scraped_at < NOW() - 12h` to identify truly new advertisers today.

## Step 3 — Data Storage
```sql
INSERT INTO competitor_mentions (competitor_name, platform, post_title, post_text, score, subreddit, url, sentiment)
VALUES (advertiser, 'facebook_ads', query, ad_text[:300], 0, 'meta_ad_library', 'https://www.facebook.com/ads/library/', 'neutral')
ON CONFLICT DO NOTHING
```

## Step 4 — New Advertiser Detection
Two levels:
1. **Not in `competitors` table** → unknown brand advertising in our niche
2. **Not in `competitor_mentions` from last 12h** → brand new today (flag as 🆕)

## Step 5 — Slack Report Format (Block Kit)

Use `message` tool with `action=send`, `channel=slack`, `target=C0AM45T4XT8`. Send as multiple messages. All use the `blocks` parameter (JSON array).

---

**Message 1 — Header**
```json
[
  {"type":"header","text":{"type":"plain_text","text":"📢 Facebook Ad Library Report","emoji":true}},
  {"type":"context","elements":[{"type":"mrkdwn","text":"📅 {date}  |  🔍 6 keyword searches  |  👤 {N} unique advertisers  |  🆕 {M} brand new since yesterday  |  Scraped via Playwright + Chrome"}]},
  {"type":"divider"}
]
```

---

**Messages 2–7 — One per query** (only if ads found for that query; max 6 rows per message)
```json
[
  {"type":"section","text":{"type":"mrkdwn","text":"*🔎 \"{query}\"*"}},
  {"type":"section","text":{"type":"mrkdwn","text":"• 🆕 *{Advertiser}* — since {date} — _{ad hook truncated to 80 chars}_\n• *{Advertiser}* — since {date} — _{ad hook}_\n• *{Advertiser}* — since {date} — _{ad hook}_"}},
  {"type":"divider"}
]
```
> Prefix 🆕 on advertisers that are brand-new today. Use plain bullets — no tables.

---

**Final message — New advertisers summary** (if any new today)
```json
[
  {"type":"section","text":{"type":"mrkdwn","text":"*🆕 {N} Brand New Advertisers Today*\n\n• *{Brand}* — found via \"{query}\" — _{ad hook}_\n• *{Brand}* — found via \"{query}\" — _{ad hook}_"}},
  {"type":"divider"},
  {"type":"context","elements":[{"type":"mrkdwn","text":"🌸 BloomBrain · {date} · FB Ad Library via Playwright + Chrome · Next run: tomorrow 09:00 AM GMT+1"}]}
]
```

**Or if no new advertisers:**
```json
[
  {"type":"divider"},
  {"type":"context","elements":[{"type":"mrkdwn","text":"🌸 BloomBrain · {date} · No new advertisers since yesterday · {N} total tracked · Next run: tomorrow 09:00 AM GMT+1"}]}
]
```

## Step 5b — Log Run in scrape_runs
After every run (success or failure), insert a record:
```sql
INSERT INTO scrape_runs (pipeline, status, records_scraped, completed_at)
VALUES ('fb_adlibrary', 'completed', {N_unique_advertisers}, now())
```
On failure:
```sql
INSERT INTO scrape_runs (pipeline, status, error_message, completed_at)
VALUES ('fb_adlibrary', 'failed', '{error}', now())
```

## Step 6 — Verification
- Exit code 0 + "✅ FB Ad Library report posted to both channels" = success
- If Chrome profile is locked (another process using it): script will fail — note this, it's a known issue if running manually at same time as cron
- After any Meta login session expiry: manually open Chrome, log into facebook.com, then re-run

## Output Channels
- **Production + Testing**: `C0AM45T4XT8` + `C0AM45T4XT8`
- **DB**: `competitor_mentions` table in `bloomin` Postgres
- **Chrome profile**: `/tmp/chrome-profile-fb` (rebuilt each run from `~/Library/Application Support/Google/Chrome`)
