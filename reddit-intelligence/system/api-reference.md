# BloomBrain Reddit Intelligence — Full API Reference
_Saved 2026-03-21. Source: Saad's Complete API Call System doc._
_Base URL: http://187.127.96.93/api_
_Auth header: X-API-Key: see `REDDIT_INTEL_API_KEY` in .env_

---

## SYSTEM

### GET /
No auth. Returns service ID.

### GET /health
No auth. Full system health — DB stats, last/next scrape, Apify + Claude connectivity.
Key fields: `status`, `last_scrape.completed_at`, `last_scrape.posts_stored`, `database.analyzed_posts`, `errors`

---

## ICP PROFILES — /icps
⭐ PRIMARY endpoints for BloomBrain intelligence.

### GET /icps
All ICP profiles. Filter by subreddit: `?subreddit=beyondthebump`
Returns: `profiles[]` with `name`, `description`, `pain_points`, `emotional_state`, `desire_triggers`, `objections`, `language_patterns`, `post_count`, `confidence_score`

### GET /icps/ranked?limit=50
All ICP profiles sorted by `confidence_score` desc. Max 200.

### GET /icps/export
Full export: all profiles flat + grouped by subreddit with aggregated insights per subreddit.
Returns: `total_profiles`, `total_subreddits`, `profiles[]`, `by_subreddit{}`

### GET /icps/subreddit/{name}
Full ICP data for one subreddit: all profiles + aggregated pain/desire/objections/language + weekly score history.

### GET /icps/subreddit/{name}/scores
Weekly score history only for one subreddit (chronological).

---

## ICP INSIGHTS (Analyzed Posts) — /insights

### GET /insights
Latest global ICP summary — aggregated cross-subreddit intelligence.
Key fields: `icp_summary_paragraph`, `top_pain_points`, `top_language_patterns`, `top_desire_triggers`, `top_objections`, `emerging_topics`, `best_performing_subreddits`, `posts_analyzed`

### GET /insights/raw
Raw individual analyzed post insights from `icp_insights` table.
Params: `topic` (optional, see valid tags), `limit` (default 20, max 200), `days` (default 30, max 365)
Valid topic tags: `low_libido`, `stress`, `postpartum`, `menopause`, `perimenopause`, `pcos`, `fatigue`, `mood`, `anxiety`, `relationship`, `supplements`, `ayurveda`, `natural_remedies`, `body_image`, `hormones`, `cortisol`, `intimacy`, `marriage`, `self_care`, `confidence`

### GET /insights/pain-points
Just `top_pain_points` array from latest summary.

### GET /insights/objections
Just `top_objections` with `counter_message` from latest summary.

### GET /insights/language
Just `top_language_patterns` — verbatim phrases for ad copy.

### GET /insights/trending
Compares last 2 summaries. Topics classified as `rising`, `stable`, or `falling`.

### GET /insights/by-subreddit/{name}
All raw analyzed insights from one subreddit. Param: `limit` (default 50, max 500)

---

## SUBREDDITS — /subreddits

### GET /subreddits
All approved subreddits by total_score.

### GET /subreddits/all
All subreddits (approved + review + rejected) with full score breakdown.

### GET /subreddits/{name}
Full validation details for one subreddit.

### POST /subreddits/add
Add subreddits manually as approved (bypasses scoring).
Body: `{"names": ["subredditname"]}`

### POST /subreddits/evaluate/{name}
Trigger Claude re-evaluation of a subreddit.

### PATCH /subreddits/{name}/status
Manual status override. Body: `{"status": "approved|review|rejected", "reason": "..."}`

---

## SCRAPER — /scrape
⚠️ Only trigger when explicitly directed.

### POST /scrape
Full scrape across ALL approved subreddits. Params: `limit`, `generate_report`
Returns: `scrape_run_id`, `subreddits_queued`, `phase1_count`, `phase2_count`, `status`

### POST /scrape/{subreddit}
Scrape one subreddit. Auto-detects Phase 1 or 2.

### POST /scrape/phase1/{subreddit}
Force Phase 1 on a subreddit.

### POST /scrape/topic/search
Body: `{"keyword": "..."}` — scrapes subreddits matching keyword.

### POST /scrape/from-dataset
Ingest existing Apify dataset without consuming credits.
Body: `{"dataset_id": "...", "subreddit": "...", "generate_report": false}`

### GET /scrape/status/{run_id}
Poll status. Fields: `status`, `posts_found`, `posts_stored`, `posts_filtered`, `posts_duplicated`

### GET /scrape/logs/recent
Last 20 scrape runs.

---

## CONFIGURATION — /config

### GET /config
Returns full scrape config.

### PATCH /config
Update config fields. Key fields: `max_posts_per_subreddit`, `max_posts_to_analyze`, `scrape_interval_hours`, `min_relevance_score`

### GET /config/keywords
Current keyword list.

### POST /config/keywords/add
Body: `{"keywords": ["..."]}` — adds to existing list.

### POST /config/keywords/remove
Body: `{"keywords": ["..."]}` — removes from list.

### POST /config/keywords/reset
Restore defaults.

### GET /config/env
Returns masked credential status + report schedule.

---

## REPORTS — /reports

### POST /reports/generate
Generate PDF report from latest data and upload to Slack.

---

## CHAT — /chat (AI assistant with live ICP data)

### POST /chat/sessions
Create new chat session. Body: `{"first_message": "..."}`

### GET /chat/sessions
List all sessions.

### POST /chat/sessions/{session_id}/messages
Send message. Body: `{"content": "..."}`

### GET /chat/sessions/{session_id}/messages
Get all messages in a session.

### DELETE /chat/sessions/{session_id}
Delete session permanently.

---

## Quick Reference

| Method | Endpoint | Use |
|--------|----------|-----|
| GET | /health | System health check |
| GET | /icps/export | Full ICP export |
| GET | /icps/ranked | ICPs by confidence |
| GET | /icps/subreddit/{name} | Deep dive one subreddit |
| GET | /insights | Latest global summary |
| GET | /insights/pain-points | Top pain points |
| GET | /insights/language | Verbatim copy language |
| GET | /insights/trending | Rising/falling topics |
| GET | /insights/raw | Raw post-level insights |
| POST | /scrape | Trigger full scrape |
| GET | /scrape/status/{id} | Poll scrape progress |
| PATCH | /config | Update config |
| POST | /reports/generate | Generate + send report |
