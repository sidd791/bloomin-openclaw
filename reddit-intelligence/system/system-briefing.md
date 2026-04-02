# Reddit Intelligence System — BloomBrain Technical Briefing
_Source: Saad's system briefing document. Saved 2026-03-18._

## What This Is
A production Reddit intelligence system built for Bloomin (trybloomin.com). It automatically:
1. Scrapes Reddit posts from approved communities
2. Runs posts through a two-stage relevance filter
3. Extracts ICP intelligence per-post using Claude
4. Aggregates into summaries of pain points, language patterns, desire triggers, objections, emerging topics

**BloomBrain's role:** Query the system via API, answer intelligence questions, trigger scrape runs when directed, surface insights on demand from Slack.

---

## Architecture (5 Layers)
1. **FastAPI backend** — port 8000, the only public-facing layer. All intelligence/scraping/config via HTTP.
2. **Supabase (PostgreSQL)** — stores subreddit registry, scraped posts, scrape logs, filtered posts, ICP insights, ICP summaries, request logs. Uses async Python client (supabase v2.7.4).
3. **Apify** — actor `TwqHBuZZPHJxiQrTU` (fatihtahta/reddit-scraper-search-fast) to fetch posts. Falls back to direct Reddit JSON if Apify returns 0 items.
4. **Anthropic Claude API** — Haiku for relevance filter (fast/cheap), Sonnet for scoring/analysis/aggregation.
5. **React frontend** — port 5680, for team visual monitoring. BloomBrain does NOT use the frontend — calls backend directly.

---

## Data Flow
1. Scrape job starts (scheduled or manual)
2. Backend fetches posts from each approved subreddit via Apify actor
3. Two-stage relevance filter runs on each post
4. Posts passing filter stored in `reddit_posts` with `relevance_passed=True`
5. Analyzer sends unanalyzed passing posts to Claude Sonnet → stored in `icp_insights`
6. When 50+ new insights since last summary → aggregator generates new `icp_summaries` record

---

## Primary Data Sources for BloomBrain
- **Primary:** `reddit_posts` table in Supabase — scraped posts with relevance filtering
- **Secondary:** ICP data from the intelligence layer API endpoints
- **Key rule:** Only use data aligned to Bloomin's ICP (women 25-45, low desire, hormonal imbalance, energy crashes, mood issues). Ignore irrelevant data.

---

## The Relevance Filter
**Stage 1 — Keyword matching (free, instant):**
Checks title+body against: desire, libido, intimacy, sex drive, low sex drive, hormones, hormonal, cortisol, perimenopause, menopause, pcos, postpartum, after baby, after pregnancy, fatigue, exhausted, no energy, low energy, mood, mood swings, anxiety, stress, overwhelmed, burned out, burnt out, supplements, adaptogens, shatavari, ashwagandha, maca, honey, natural remedies, herbal, wellness, self care, relationship, connection, spark, confidence, body image, feel like myself, not myself, lost desire, no drive, feminine energy, intimacy issues, bedroom problems, not interested in sex, marriage problems, low libido, no libido, sex life, sexual desire, hormone, hormonal balance, thyroid, adrenal

**Stage 2 — Claude Haiku binary check (only if Stage 1 fails):**
Asks: "Is this post about a personal experience a woman aged 25-45 dealing with low desire, low energy, hormonal imbalance, mood issues, or intimacy problems would relate to?" → YES/NO. Max tokens: 5.

---

## Database Tables

### `reddit_posts` (PRIMARY SOURCE)
Key fields: `id`, `post_id`, `subreddit`, `title`, `body`, `url`, `score`, `upvote_ratio`, `num_comments`, `flair`, `created_at`, `scraped_at`, `top_comments` (JSONB), `relevance_passed`, `filter_method`, `analyzed`, `apify_run_id`

### `icp_insights` (SECONDARY — per-post analysis)
Key fields: `post_id`, `subreddit`, `pain_points`, `emotional_states`, `desire_triggers`, `objections`, `language_patterns`, `purchase_intent_signals`, `topic_tags`, `icp_confidence` (0-10), `analyzed_at`, `model_used`

`icp_confidence`: 10 = reads like a Bloomin testimonial. 1 = tangentially related. Higher = more useful for copy.

### `icp_summaries` (PRIMARY QUERY TARGET)
Key fields: `top_pain_points` [{pain_point, frequency, example_quote}], `top_language_patterns` [{phrase, frequency, context}], `top_desire_triggers` [{trigger, frequency}], `top_objections` [{objection, frequency, counter_message}], `emerging_topics` [{topic, trend}], `icp_summary_paragraph`, `best_performing_subreddits`, `posts_analyzed`, `date_range_from`, `date_range_to`, `generated_at`

### `scrape_runs`, `filtered_posts`, `subreddit_registry`, `scrape_config`, `request_logs` — internal pipeline state

---

## Valid Topic Tags (for GET /insights/raw?topic=)
`low_libido`, `stress`, `postpartum`, `menopause`, `perimenopause`, `pcos`, `fatigue`, `mood`, `anxiety`, `relationship`, `supplements`, `ayurveda`, `natural_remedies`, `body_image`, `hormones`, `cortisol`, `intimacy`, `marriage`, `self_care`, `confidence`

---

## Operating Modes

### MODE 1 — General Intelligence Query
Trigger: "What's our ICP feeling?", "What pain points dominate?", "What should Bloomin focus on?"
Action: `GET /insights` → read `icp_summary_paragraph`, `top_pain_points`, `top_language_patterns`, `top_desire_triggers`, `top_objections`

### MODE 2 — Topic Deep Dive
Trigger: "What are women saying about perimenopause/postpartum/supplements?"
Action: `GET /insights/raw?topic={tag}&limit=20&days=30` → read `pain_points`, `language_patterns`, `desire_triggers`

### MODE 3 — Copywriting & Language
Trigger: "Give me ad copy language", "Email subject lines", "Messaging that sounds like her"
Action: `GET /insights/language` → returns verbatim phrases (NOT paraphrased — exact ICP words)

### MODE 4 — Objection Handling
Trigger: "What objections do we need to address in ads?"
Action: `GET /insights/objections` → returns objection + frequency + counter_message

### MODE 5 — Trending
Trigger: "What's rising/falling in the communities?"
Action: `GET /insights/trending` → compares two most recent summaries, classifies topics as rising/stable/falling

### MODE 6 — Trigger a Scrape
Trigger: "Run a scrape", "Refresh data", "Collect new posts"
Action: `POST /scrape` → get `scrape_run_id` → poll `GET /scrape/status/{run_id}` every 30s until "completed" or "error" → report `posts_found`, `posts_stored`, `posts_filtered`
**Only trigger when explicitly directed.**

### MODE 7 — Subreddit Status
Trigger: "Which subreddits are active?", "What's r/Menopause scoring?"
Action: `GET /subreddits` (approved only) or `GET /subreddits/all` or `GET /subreddits/{name}`

### MODE 8 — System Health Check
Trigger: "Is the system running?", "How many posts analyzed?"
Action: `GET /health` → check `status`, `last_scrape`, `database.analyzed_posts`
If status = "degraded" → report `errors` array to Finn immediately.

---

## API Reference (All Endpoints)
All require header `X-API-Key` except `GET /` and `GET /health`.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Verify server is running |
| GET | `/health` | System health, last scrape, DB stats |
| GET | `/subreddits` | All approved subreddits |
| GET | `/subreddits/all` | All subreddits all statuses |
| POST | `/subreddits/add` | Add subreddits `{"names": [...]}` |
| GET | `/subreddits/{name}` | Single subreddit detail |
| POST | `/subreddits/evaluate/{name}` | Trigger re-scoring |
| PATCH | `/subreddits/{name}/status` | Manual status override |
| POST | `/scrape` | Full scrape (Phase 1 only for manual) |
| POST | `/scrape/{subreddit}` | Scrape one subreddit |
| POST | `/scrape/phase1/{subreddit}` | Force Phase 1 for one subreddit |
| POST | `/scrape/topic/search` | Scrape by keyword match `{"keyword": "..."}` |
| GET | `/scrape/status/{run_id}` | Poll scrape status |
| GET | `/scrape/logs/recent` | Last 20 scrape runs |
| GET | `/insights` | Latest ICP summary (PRIMARY) |
| GET | `/insights/raw` | Post-level insights, filtered by topic/days/limit |
| GET | `/insights/language` | Verbatim language patterns only |
| GET | `/insights/objections` | Objections + counter_messages |
| GET | `/insights/pain-points` | Pain points + example quotes |
| GET | `/insights/trending` | Rising/falling/stable topics |
| GET | `/insights/by-subreddit/{name}` | Insights from one subreddit |
| GET | `/config` | Current scrape config |
| PATCH | `/config` | Update config |
| GET | `/config/keywords` | Current keyword list |
| POST | `/config/keywords` | Replace keyword list |
| POST | `/config/keywords/add` | Add keywords |
| POST | `/config/keywords/remove` | Remove keywords |
| POST | `/config/keywords/reset` | Restore defaults |

---

## Scraping Rules
- **Phase 1:** First-ever scrape per subreddit. Sort: "new", range: "month", max: 100 posts (configurable)
- **Phase 2:** Weekly refresh for already-scraped subreddits. Only runs on scheduler, NOT on manual `POST /scrape`
- Manual `POST /scrape` = Phase 1 subreddits only
- Concurrency: max 2 subreddits simultaneously
- Keywords never passed to Apify (causes abort). All filtering is downstream.
- Comments not scraped (`scrapeComments=False`)

---

## Subreddit Scoring
- **≥70 total_score** → "approved"
- **50-69** → "review"
- **<50** → "rejected"
- Re-evaluation runs every 14 days
- Manually added via `POST /subreddits/add` → always approved (fixed scores, bypasses Claude scoring)

---

## Key Rules for BloomBrain
1. **Don't grab random data.** Only query/surface data aligned to Bloomin's ICP and brand.
2. **Primary source = Supabase `reddit_posts` table** (filtered posts)
3. **Secondary source = Intelligence layer API** (insights, summaries)
4. **Only trigger scrapes when explicitly directed**
5. **Higher `icp_confidence` scores = more useful for copy and messaging**
6. **`GET /insights`** is the go-to for general intelligence questions
7. Always check `GET /health` before major operations if system status is uncertain

---

## PRIMARY OPERATING PRIORITY (Updated 2026-03-21)

**The single most important job:** Query Supabase `reddit_posts` directly and analyze the filtered post data.
This could be 20,000–30,000+ posts. That raw post data is the primary intelligence source.
The API intelligence layer (insights, summaries) is secondary — it's pre-aggregated, useful, but derived.

**Continuous learning loop:**
Every response from a team member is a calibration signal. Every correction, every "this is perfect", every
"this doesn't fit" — capture it in `memory/reddit-calibration.md`. The system compounds. The goal is that
BloomBrain gets sharper with every interaction.

**ICP filter — applies to BOTH Supabase and API data:**
There will be data in the DB that doesn't fit Bloomin's ICP. Ignore it. Only surface data aligned to:
women 25–45, low desire, hormonal imbalance, stress/cortisol, energy crashes, mood issues.
Don't grab random data. Every answer should be grounded in Bloomin's brand, customers, and products.

---

## Full Trigger Phrases Reference (Updated 2026-03-21)

| Input | Action |
|-------|--------|
| "What's our ICP feeling right now?" | GET /insights → icp_summary_paragraph + top_pain_points |
| "Give me the top pain points with quotes" | GET /insights/pain-points |
| "What language is she using?" | GET /insights/language → verbatim phrases |
| "What objections do we need to address?" | GET /insights/objections → objection + counter_message |
| "What's trending this week?" | GET /insights/trending → rising/falling/stable |
| "What are women saying about perimenopause?" | GET /insights/raw?topic=perimenopause&limit=20&days=30 |
| "What are postpartum conversations looking like?" | GET /insights/raw?topic=postpartum&limit=20&days=14 |
| "Run a scrape and let me know when done" | POST /scrape → poll status → report stats |
| "Scrape just r/weddingplanning" | POST /scrape/weddingplanning → poll until complete |
| "How many posts analyzed?" | GET /health → database.analyzed_posts |
| "Is the system running?" | GET /health → status + last_scrape.completed_at |
| "What are our approved subreddits?" | GET /subreddits → names + total_scores |
| "What is r/Menopause scoring?" | GET /subreddits/Menopause → full scoring breakdown |
| "Give me something for ad copy" | GET /insights/language → top 10 verbatim phrases with context |
| "What desire triggers are most common?" | GET /insights → top_desire_triggers |
| "What were the key themes from last batch?" | GET /insights → icp_summary_paragraph + top_pain_points + emerging_topics |
| "Increase posts per scrape to 150" | PATCH /config {"max_posts_per_subreddit": 150} → confirm |
| "Add keyword 'cycle syncing'" | POST /config/keywords/add {"keywords": ["cycle syncing"]} → confirm |
| "What subreddits are under review?" | GET /subreddits/all → filter status = "review" |
| "When was the last scrape?" | GET /health → last_scrape.completed_at + posts_stored |

---

## Core Operating Priorities (Reinforced 2026-03-21)

1. **PRIMARY job = direct Supabase query on `reddit_posts`** — could be 20,000–30,000 posts. This is the raw truth. Read it, analyze it, filter to Bloomin ICP.
2. **Secondary = intelligence layer API** (`GET /insights`, `/language`, `/objections`, etc.) — aggregated summaries, use as supporting layer.
3. **ICP filter is strict** — only surface data relevant to Bloomin: women 25-45, low desire, hormonal stress, energy, mood. Ignore off-brand data. The DB has noise — that's expected.
4. **Learning loop is core** — every team response, correction, or approval sharpens my understanding. Write calibration notes to `memory/reddit-calibration.md` in real time.
5. **Scrape only when explicitly directed** — never autonomously.

## What I Still Need (from Saad)
- [ ] API base URL (where the FastAPI backend is hosted)
- [ ] API key (`X-API-Key` value)
- [ ] Supabase project URL + service key (for direct DB queries on `reddit_posts`)
