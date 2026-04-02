---
name: youtube-founder-intel
description: Weekly YouTube founder intelligence for Bloomin. Scrapes YouTube for D2C supplement brand founder content, downloads subtitles via yt-dlp, analyzes transcripts for tactical takeaways applicable to Bloomin's stage (~$35K/day, ~8K subscribers). Posts structured report to Slack and updates memory. Use for the youtube-founder-intel cron job.
---

# YouTube Founder Intelligence — Weekly Report

## What This Does
Finds 5 most relevant YouTube videos from the past 30 days about women's supplement or D2C wellness brand building. Downloads their subtitles. Analyzes transcripts for tactics applicable to Bloomin. Posts a per-video breakdown + cross-video synthesis to Slack.

## Step 1 — Scrape via Apify
```bash
apify call streamers/youtube-scraper
```
Input:
```json
{
  "searchQueries": [
    "women supplement brand founder",
    "female wellness ecommerce scaling",
    "D2C supplement brand growth",
    "hormonal health supplement brand",
    "supplement subscription brand scaling"
  ],
  "maxResultsPerQuery": 10,
  "dateFilter": "month"
}
```
Pick top 5 most relevant videos overall. Relevance = closest match to Bloomin's context (D2C supplement, women's health, brand building).

## Step 2 — Download Subtitles
For each video URL:
```bash
yt-dlp --write-auto-sub --skip-download --sub-format vtt \
  -o /tmp/yt-%(id)s.%(ext)s "{video_url}"
```
Convert VTT to plain text (strip timestamps). If subtitles unavailable: use video title + description only (note limitation in report).

## Step 3 — Transcript Analysis Framework

### What to Extract Per Video
- **Tactical takeaways** (specific, actionable things they did)
- **Revenue/growth levers** (what moved the needle)
- **Creative strategy** (what ad angles, hooks, formats worked)
- **Retention plays** (subscription, LTV, churn reduction)
- **Offer structure** (bundles, guarantees, pricing)
- **Anything specific to ~$35K/day stage or ~8K subscriber scale** — flag these prominently

### Relevance Filter
Skip or deprioritize content about:
- Men's supplements
- Enterprise/corporate wellness
- Brick-and-mortar retail
- Pure dropshipping (not brand-owned)

## Step 4 — Data to Save

### DB Storage (Primary) — `youtube_videos` table in `bloomin` Postgres
For each video analyzed, insert:
```sql
INSERT INTO youtube_videos (video_url, title, channel, search_query, transcript_summary, key_takeaways, bloomin_relevance, has_transcript, week_of)
VALUES ('{url}', '{title}', '{channel}', '{query}', '{summary}', ARRAY['{takeaway1}','{takeaway2}'], '{relevance_text}', {true|false}, '{YYYY-MM-DD}')
```
Also log the run in `scrape_runs`:
```sql
INSERT INTO scrape_runs (pipeline, status, records_scraped, completed_at)
VALUES ('youtube_founder_intel', 'completed', {N}, now())
```

### Memory File (`~/.openclaw/workspace/memory/youtube-intel.md`) — Summary Only
Append a dated section (condensed, not raw rows):
```markdown
## Week of {YYYY-MM-DD}
### Videos Analyzed
1. [{Title}]({URL}) — {Channel}
   Key takeaways: [bullet points]

### Cross-Video Synthesis
- [Pattern appearing in multiple videos]
- [Pattern appearing in multiple videos]

### Bloomin Applicability
- [Specific tactic + why it applies to Bloomin's current stage]

- DB: {N} videos stored in youtube_videos
```

## Step 5 — Slack Report Format (Block Kit)

Use the `message` tool with `action=send`, `channel=slack`, `target=C0AM45T4XT8`. Build the report as **multiple messages** — one per video plus a header and synthesis — to avoid hitting block limits.

All messages use the `blocks` parameter (JSON array).

---

**Message 1 — Header**
```json
[
  {
    "type": "header",
    "text": { "type": "plain_text", "text": "🎬 YouTube Founder Intelligence — Week of {date}", "emoji": true }
  },
  {
    "type": "context",
    "elements": [
      { "type": "mrkdwn", "text": "📅 {date}  |  5 videos analyzed  |  Focus: D2C supplement brand scaling" }
    ]
  },
  { "type": "divider" }
]
```

---

**Messages 2–6 — One per video**
```json
[
  {
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": "*🎥 <{video_url}|{Video Title}>*\n_{Channel}_"
    }
  },
  {
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": "• *Tactic 1 — {label}:* {description}\n• *Tactic 2 — {label}:* {description}\n• *Tactic 3 — {label}:* {description}\n• *Tactic 4 — {label}:* {description}\n• *Tactic 5 — {label}:* {description}"
    }
  },
  {
    "type": "context",
    "elements": [
      { "type": "mrkdwn", "text": "⭐ *Bloomin relevance:* {why this matters for Bloomin right now}" }
    ]
  },
  { "type": "divider" }
]
```

---

**Final message — Synthesis**
```json
[
  {
    "type": "header",
    "text": { "type": "plain_text", "text": "🧠 Cross-Video Synthesis — Top 3 Insights This Week", "emoji": true }
  },
  {
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": "*1. {Insight title}*\n{Explanation + recommended action}\n\n*2. {Insight title}*\n{Explanation + recommended action}\n\n*3. {Insight title}*\n{Explanation + recommended action}"
    }
  },
  { "type": "divider" },
  {
    "type": "context",
    "elements": [
      { "type": "mrkdwn", "text": "🌸 BloomBrain · {date} · YouTube via Apify + yt-dlp · Next run: next week" }
    ]
  }
]
```

## Step 6 — Error Handling
- Apify fails → try YouTube search via `web_fetch` on `youtube.com/results?search_query=...` as fallback
- yt-dlp subtitle download fails for a video → use title + description only, note `[no transcript]` in report
- 0 relevant videos found → post notice to `C0AM45T4XT8`, skip memory update

## Output Channel
- **Slack**: `C0AM45T4XT8`
- **Memory**: `~/.openclaw/workspace/memory/youtube-intel.md` (append, never overwrite)
