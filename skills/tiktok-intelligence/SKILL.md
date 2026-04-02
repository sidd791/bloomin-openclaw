---
name: tiktok-intelligence
description: Daily TikTok intelligence scrape for Bloomin. Runs Apify tiktok-scraper across hormonal health hashtags, analyzes hooks and ingredient signals for the women's libido/cortisol niche, posts a Block Kit report to Slack, and updates memory. Use for the tiktok-daily-report cron job.
---

# TikTok Intelligence — Daily Report

## What This Does
Scrapes TikTok via Apify for 5 hashtags, filters for Bloomin-relevant content (hormonal health, cortisol, desire, ingredient mentions), analyzes hooks and patterns, posts a structured Block Kit report, and appends to memory.

## Step 1 — Write Input File
```bash
cat > /tmp/tiktok-daily-input.json << 'EOF'
{
  "hashtags": ["hormonehealth", "lowlibido", "womenshealth", "cortisol", "shatavari"],
  "resultsPerPage": 50,
  "shouldDownloadVideos": false
}
EOF
```

## Step 2 — Run Apify Scraper
```bash
apify call clockworks/tiktok-scraper --input-file /tmp/tiktok-daily-input.json --output-dataset
```
Extract `run_id` from stdout. Poll until SUCCEEDED (same pattern as competitor-discovery.py's Google scraper).

## Step 3 — Fetch + Analyze Results
Fetch dataset items via Apify API. For each video, analyze:

### Filter Criteria (Bloomin-relevant)
- Women's hormonal health: cortisol, estrogen, progesterone, perimenopause, menopause, hormones
- Desire/libido: low libido, sex drive, intimacy, desire
- Ingredients: shilajit, shatavari, saffron, ashwagandha, maca
- General: supplements for women, wellness, stress

### Extract Per Video
- Hook (first line of caption, or video title)
- View count + engagement rate
- Hashtags used
- Ingredient mentions
- Hook pattern type (question / pain agitate / transformation / stat / social proof)

## Step 4 — Data to Capture

### DB Storage (Primary) — `tiktok_videos` table in `bloomin` Postgres
For each Bloomin-relevant video, insert:
```sql
INSERT INTO tiktok_videos (hashtag, hook, caption, view_count, like_count, comment_count, share_count, engagement_rate, author, video_url, ingredient_mentions, hook_pattern, bloomin_relevant, run_date)
VALUES ('{hashtag}', '{hook}', '{caption}', {views}, {likes}, {comments}, {shares}, {engagement_rate}, '{author}', '{url}', ARRAY['{ingredient1}','{ingredient2}'], '{pattern}', true, '{YYYY-MM-DD}')
```
Also log the run in `scrape_runs`:
```sql
INSERT INTO scrape_runs (pipeline, status, records_scraped, completed_at)
VALUES ('tiktok_intelligence', 'completed', {N}, now())
```

### Memory File (`~/.openclaw/workspace/memory/tiktok-insights.md`) — Summary Only
Append a dated section (condensed summary, not raw rows):
```markdown
## {YYYY-MM-DD}
- Top hashtags this run: ...
- Trending hooks: ...
- Ingredient mentions: shilajit (N), shatavari (N), saffron (N)
- Hook patterns working: ...
- Content gaps (questions asked but not answered): ...
- DB: {N} videos stored in tiktok_videos
```

## Step 5 — Slack Report Format (Block Kit)

Use `message` tool with `action=send`, `channel=slack`, `target=C0AM45T4XT8`. Send as multiple messages to stay within Slack's block limit. All use the `blocks` parameter (JSON array).

---

**Message 1 — Header**
```json
[
  {"type":"header","text":{"type":"plain_text","text":"📱 TikTok Intelligence Report","emoji":true}},
  {"type":"context","elements":[{"type":"mrkdwn","text":"📅 {date}  |  #hormonehealth #lowlibido #womenshealth #cortisol #shatavari  |  {N} videos analyzed ({M} relevant)"}]},
  {"type":"divider"}
]
```

---

**Message 2 — Top hooks** (sort by views desc, max 6 rows)
```json
[
  {"type":"section","text":{"type":"mrkdwn","text":"*🎣 Top Performing Hooks*"}},
  {"type":"section","fields":[
    {"type":"mrkdwn","text":"*Views*"},{"type":"mrkdwn","text":"*Hook / Caption*"},
    {"type":"mrkdwn","text":"{views}"},{"type":"mrkdwn","text":"{hook truncated to 80 chars}"},
    {"type":"mrkdwn","text":"{views}"},{"type":"mrkdwn","text":"{hook}"}
  ]},
  {"type":"divider"}
]
```
> Note: Slack `fields` renders as 2-column. Alternate views / hook pairs. Max 10 fields per section block (5 rows). Use a second section block if needed.

---

**Message 3 — Hook patterns**
```json
[
  {"type":"section","text":{"type":"mrkdwn","text":"*🧩 Hook Pattern Breakdown*\n\n*Pattern* | *Count* | *Best Example*\n• *Pain agitate* — {N} | \"{best example}\"\n• *Question opener* — {N} | \"{best example}\"\n• *Transformation* — {N} | \"{best example}\"\n• *Stat / number* — {N} | \"{best example}\"\n• *Social proof* — {N} | \"{best example}\""}},
  {"type":"divider"}
]
```

---

**Message 4 — Ingredient mentions**
```json
[
  {"type":"section","text":{"type":"mrkdwn","text":"*💊 Ingredient Mentions This Run*\n\n• *Shatavari* — {N} mentions | Sentiment: {pos/neg/neutral} | Trending: {✅/🔶/❌}\n• *Saffron* — {N} mentions | {context}\n• *Shilajit* — {N} mentions | {context}\n• *Maca* — {N} mentions | {context}\n• *Ashwagandha* — {N} mentions | {context}"}},
  {"type":"divider"}
]
```

---

**Message 5 — Cross-platform signals + opportunities**
```json
[
  {"type":"section","text":{"type":"mrkdwn","text":"*🔀 Cross-Platform Signals*\n\n• *TikTok:* {signal} → *Meta relevance:* {relevance} → *Action:* {action}\n• *TikTok:* {signal} → *Meta relevance:* {relevance} → *Action:* {action}\n• *TikTok:* {signal} → *Meta relevance:* {relevance} → *Action:* {action}"}},
  {"type":"divider"},
  {"type":"section","text":{"type":"mrkdwn","text":"*💡 3 Content Opportunities for Bloomin*\n\n*1. {Opportunity title}*\n{Description}\n\n*2. {Opportunity title}*\n{Description}\n\n*3. {Opportunity title}*\n{Description}"}},
  {"type":"divider"},
  {"type":"context","elements":[{"type":"mrkdwn","text":"🌸 BloomBrain · {date} · TikTok via Apify · Next run: tomorrow 09:00 AM GMT+1"}]}
]
```

**Rule**: Max 1 logical section per Slack message. Never nest tables — use mrkdwn bullet lists instead.

## Step 6 — Error Handling
- Apify fails → post failure notice to `C0AM45T4XT8`, log error, exit cleanly
- Empty dataset → post "no content found" notice, still update memory with the date + note
- Memory file write fails → post report to Slack anyway, note memory write failure in message

## Output Channel
- **Slack**: `C0AM45T4XT8`
- **Memory**: `~/.openclaw/workspace/memory/tiktok-insights.md` (append, never overwrite)
