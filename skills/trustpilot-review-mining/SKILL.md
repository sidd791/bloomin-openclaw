---
name: trustpilot-review-mining
description: Daily competitor Trustpilot review mining for Bloomin. Scrapes 1-2★ reviews from competitors in the bloomin Postgres DB, stores pain points, generates a PDF report, and posts a Block Kit summary + file upload to Slack. Use for the trustpilot-review-mining cron job.
---

# Trustpilot Review Mining — Daily Report

## What This Does
Pulls all qualifying competitors from Postgres, scrapes their Trustpilot 1-2★ reviews, tags each with pain point categories, maps them to Bloomin advantages, stores everything in Postgres, generates a PDF, and posts to Slack.

## Step 1 — Run the Script
```bash
python3 /Users/teambloomin/.openclaw/workspace/scripts/competitor-review-scraper.py
```

## How Scraping Works (for debugging)

### Competitor Source
```sql
SELECT id, name, url, trustpilot_url, category, threat_level 
FROM competitors WHERE qualifies = true ORDER BY threat_level DESC
```
Only competitors with a `trustpilot_url` get scraped. Others are noted as "no Trustpilot" in the report.

### Scraping Method
- Direct HTTP request to `{trustpilot_url}?stars=1` and `?stars=2&sort=recency`
- Extracts: review text, publish date, author, star rating from JSON embedded in HTML
- Partial data only (Trustpilot is JS-rendered — we get what we can)
- 1 second sleep between star pages, 1 second between competitors

## Step 2 — Pain Point Tagging

Each review is tagged with one or more:
| Tag | Trigger Keywords |
|-----|-----------------|
| `slow_results` | weeks, months, didn't work, no results, no difference |
| `taste` | taste, flavor, smell, gross, disgusting |
| `price` | expensive, pricey, cost, overpriced, not worth |
| `shipping` | shipping, delivery, arrived, late, never received |
| `scam` | scam, fraud, fake, counterfeit |
| `side_effects` | side effect, headache, nausea, stomach, sick |
| `no_libido_change` | libido, desire, sex drive, no change, same as before |
| `customer_service` | customer service, support, refund, return |

## Step 3 — Bloomin Advantage Mapping
Each pain point maps to a Bloomin counter-position:
- `slow_results` → "Most users feel results within a week"
- `scam` → Direct ships from warehouse, subscription = verified fulfillment
- `no_libido_change` → Addresses root cause (cortisol blocker) not symptoms
- `price` → 90-day guarantee — value positioned clearly
- `taste` → Strawberry honey — designed to be enjoyable
- `side_effects` → Natural Ayurvedic formula, third-party tested

## Step 4 — Data Storage
```sql
INSERT INTO competitor_reviews 
(competitor_id, platform, rating, review_text, review_date, author, verified, sentiment, pain_point_tags, bloomin_advantage)
VALUES (id, 'trustpilot', 1|2, text, date, author, false, 'negative', '{tag1,tag2}'::text[], advantage_text)
```

Scrape run logged in `scrape_runs` table: `pipeline='competitor_reviews'`, status `running` → `completed`.

## Step 5 — Report

### Report File
Saved to `/Users/teambloomin/.openclaw/workspace/reports/competitor-review-report-{YYYY-MM-DD}.pdf`
Generated with weasyprint (HTML → PDF). Falls back to `.html` if weasyprint unavailable.

### 🆕 New Competitors Section
Compare `competitor_reviews` for current week vs previous week. Any competitor with reviews this week but not last week = new. Always show this section at the top of the report.

## Step 6 — Slack Report Format (Block Kit)

Use `message` tool with `action=send`, `channel=slack`, `target=C0AM45T4XT8`. Send as multiple messages. All use the `blocks` parameter (JSON array).

---

**Message 1 — Header**
```json
[
  {"type":"header","text":{"type":"plain_text","text":"🔴 Competitor Review Intelligence Report","emoji":true}},
  {"type":"context","elements":[{"type":"mrkdwn","text":"📅 {date}  |  📊 {N} negative reviews analyzed  |  🏢 {M} competitors covered  |  Daily scrape · Trustpilot 1-2★ focus"}]},
  {"type":"divider"}
]
```

---

**Message 2 — Competitor overview**
```json
[
  {"type":"section","text":{"type":"mrkdwn","text":"*Competitor Overview*\n\n• *{Competitor}* — {Direct/Adjacent} | {High/Medium/Low} threat | {N} reviews\n• *{Competitor}* — {Direct/Adjacent} | {High/Medium/Low} threat | {N} reviews\n• _(others: no Trustpilot URL or 404)_"}},
  {"type":"divider"}
]
```

---

**Message 3 — Pain points**
```json
[
  {"type":"section","text":{"type":"mrkdwn","text":"*🔍 Top Customer Pain Points*\n\n• *Customer Service* — {N}x across competitors\n• *Shipping* — {N}x across competitors\n• *Slow Results* — {N}x across competitors\n• *Taste* — {N}x across competitors\n• *Price* — {N}x across competitors\n• *No Libido Change* — {N}x across competitors\n• *Side Effects* — {N}x across competitors"}},
  {"type":"divider"}
]
```

---

**Message 4 — Bloomin advantages + footer**
```json
[
  {"type":"section","text":{"type":"mrkdwn","text":"*🎯 Bloomin Advantages (from competitor failures)*\n\n1. *Customer service gap* — {description}\n2. *Speed beats slow* — {description}\n3. *Own the mechanism* — {description}\n4. *Taste* — {description}\n5. *Direct ship / safety* — {description}"}},
  {"type":"divider"},
  {"type":"context","elements":[{"type":"mrkdwn","text":"🌸 BloomBrain · {date} · PDF: `reports/competitor-review-report-{date}.pdf` · Next scrape: tomorrow 09:00 AM GMT+1"}]}
]
```

**File upload** — After sending blocks, upload the PDF/HTML report to Slack channel `C0AM45T4XT8` using the `message` tool with `action=send` and `filePath`. If upload fails, post the local path as a fallback message.

## Step 7 — Verification
- Exit code 0 + "🌸 Done!" in stdout = success
- If Trustpilot scraping yields 0 reviews for all competitors: check if Trustpilot changed their HTML structure. Post a notice.
- If PDF generation fails: HTML report is the fallback — still upload it.

## Output Channels
- **Production + Testing**: `C0AM45T4XT8` + `C0AM45T4XT8`
- **DB**: `competitor_reviews` + `scrape_runs` tables in `bloomin` Postgres
- **Files**: `/Users/teambloomin/.openclaw/workspace/reports/`
