# Supabase Tables — Structure & Data Map
_Explored: 2026-03-21_
_URL: https://svbuiarezbaxauifqpes.supabase.co_

---

## TABLE 1: `reddit_posts` (PRIMARY RAW SOURCE)
**Total rows: 1,878** | Supabase paginates at 1000 — need offset=1000 for page 2.

### Columns
| Column | Type | Notes |
|--------|------|-------|
| `id` | uuid | Internal row ID |
| `post_id` | string | Reddit post ID (e.g. `1rw4tx3`) |
| `subreddit` | string | e.g. `perimenopause` |
| `title` | string | Post title |
| `body` | text | Full post body (the gold — actual ICP language) |
| `url` | string | Direct Reddit URL |
| `score` | int | Reddit upvotes |
| `upvote_ratio` | float | e.g. 0.96 |
| `num_comments` | int | Comment count |
| `flair` | string | Post flair (often NULL) |
| `created_at` | timestamp | When post was created on Reddit |
| `scraped_at` | timestamp | When our system scraped it |
| `top_comments` | JSONB array | Usually empty `[]` — comments not scraped |
| `relevance_passed` | bool | **All rows here are True** — this table IS the relevant posts |
| `filter_method` | string | `keyword` or `ai` (Stage 1 or Stage 2 filter) |
| `analyzed` | bool | Whether Claude has analyzed this post yet |
| `apify_run_id` | string | Which scrape run fetched this |
| `relevance_score` | int | Currently 0 for all — not actively used |

### Data breakdown (full 1,878 rows)
| Subreddit | Posts |
|-----------|-------|
| r/perimenopause | 506 |
| r/newborns | 628 (347 p1 + 281 p2) |
| r/deadbedrooms | 680 (139 p1 + 541 p2) |
| r/ayurveda | 64 (8 p1 + 56 p2) |

| Filter method | Count |
|--------------|-------|
| keyword (Stage 1) | ~562 (p1) + more p2 |
| ai (Stage 2, Claude Haiku) | ~438 (p1) + more p2 |

| Analyzed | Count |
|----------|-------|
| True | 1,298 (~69%) |
| False | 580 (~31% — pending) |

⚠️ **Key note:** ALL 1,878 rows have `relevance_passed=True`. This table only contains posts that PASSED the filter. The posts that FAILED are stored separately in `filtered_posts`.

---

## TABLE 2: `filtered_posts` (REJECTED POSTS LOG)
**Total rows: 880**

### Columns
| Column | Type | Notes |
|--------|------|-------|
| `id` | uuid | Internal row ID |
| `post_id` | string | Reddit post ID |
| `subreddit` | string | Source subreddit |
| `title` | string | Post title |
| `filter_stage` | string | Always `ai` — these failed the Claude Haiku stage |
| `reason` | string | Always `not_relevant_per_claude` |
| `filtered_at` | timestamp | When it was filtered out |

### Data breakdown
| Subreddit | Rejected posts |
|-----------|---------------|
| r/perimenopause | 417 |
| r/newborns | 372 |
| r/ayurveda | 71 |
| r/deadbedrooms | 20 |

**Note:** All 880 filtered posts failed the **AI stage** (Claude Haiku binary check). None failed keyword-only. This means the keyword filter let them through but Claude said they weren't relevant to the ICP. This table is noise — I should NOT use this data for analysis.

**Ratio insight:** perimenopause has 506 passed + 417 rejected = 923 total scraped. 45% rejection rate. deadbedrooms has 680 passed + 20 rejected = 700 total. Only 3% rejection — extremely relevant community.

---

## TABLE 3: `icp_insights` (ANALYZED POST INTELLIGENCE)
**Total rows: 1,298** — matches API `/health` `analyzed_posts`

### Columns
| Column | Type | Notes |
|--------|------|-------|
| `id` | uuid | Internal row ID |
| `post_id` | string | Links back to `reddit_posts.post_id` |
| `subreddit` | string | Source subreddit |
| `pain_points` | JSONB array | Pain points extracted from this post |
| `emotional_states` | JSONB array | Emotional states identified |
| `desire_triggers` | JSONB array | What she wants / desire triggers |
| `objections` | JSONB array | Objections to solutions |
| `language_patterns` | JSONB array | Verbatim phrases used |
| `purchase_intent_signals` | JSONB array | Any signals of willingness to buy |
| `topic_tags` | JSONB array | Tags like `['low_libido', 'intimacy', 'hormones']` |
| `icp_confidence` | float | 0–10 score. 10 = reads like a Bloomin testimonial |
| `analyzed_at` | timestamp | When Claude analyzed it |
| `model_used` | string | Which Claude model (Sonnet) |

This is the post-level analysis. Each row = one analyzed Reddit post.
The API endpoint `GET /insights/raw` directly queries this table.

---

## TABLE 4: `icp_profiles` (THE GOLD — SYNTHESIZED ICP ARCHETYPES)
**Total rows: 37** — confirmed matches API `/icps/ranked`

### Columns
| Column | Type | Notes |
|--------|------|-------|
| `id` | uuid | Profile ID |
| `subreddit` | string | Which subreddit this profile came from |
| `name` | string | Profile name e.g. "The Desire Amnesiac" |
| `description` | text | Full archetype description |
| `pain_points` | JSONB array | Distilled pain points |
| `emotional_state` | string | Dominant emotional state description |
| `desire_triggers` | JSONB array | What she wants |
| `objections` | JSONB array | Objections to solutions |
| `language_patterns` | JSONB array | Verbatim phrases |
| `post_count` | int | How many posts this profile is based on |
| `confidence_score` | float | 0–10. How well this profile represents Bloomin's ICP |
| `first_seen_at` | timestamp | When profile was created |
| `last_confirmed` | timestamp | Last time pattern was confirmed in new data |

The API endpoints `/icps/*` query this table directly. **100% match confirmed** between Supabase direct query and API response.

---

## CROSS-REFERENCE: Supabase vs API — DO THEY MATCH?

| Data point | Supabase direct | API | Match? |
|-----------|----------------|-----|--------|
| Total posts | 1,878 | 1,878 (`/health`) | ✅ |
| Analyzed posts | 1,298 | 1,298 (`/health`) | ✅ |
| Pending analysis | 580 | 580 (`/health`) | ✅ |
| ICP profiles | 37 | 37 (`/icps/ranked`) | ✅ |
| ICP profiles per subreddit | perimenopause:14, deadbedrooms:10, newborns:7, ayurveda:6 | Same | ✅ |

**Conclusion: The API is a clean abstraction layer over Supabase. The data is identical.**

---

## HOW TO QUERY SUPABASE DIRECTLY

Base URL: `https://svbuiarezbaxauifqpes.supabase.co/rest/v1/{table}`

Headers required:
```
apikey: {SUPABASE_ANON_KEY}
Authorization: Bearer {SUPABASE_ANON_KEY}
```

**⚠️ Pagination:** Supabase returns max 1,000 rows by default. For `reddit_posts` (1,878 rows), need two calls:
- Page 1: `?limit=1000`
- Page 2: `?limit=1000&offset=1000`

**Filtering examples:**
- Only analyzed posts: `?analyzed=eq.true`
- Only relevant posts: `?relevance_passed=eq.true`
- By subreddit: `?subreddit=eq.perimenopause`
- High confidence insights: use `icp_insights?icp_confidence=gte.7`

**Select specific columns:** `?select=title,body,subreddit,score`

**Get total count:** Add header `Prefer: count=exact` and read `content-range` response header.

---

## WHEN TO USE SUPABASE DIRECT vs API

| Use case | Use |
|----------|-----|
| Full post bodies (verbatim raw language) | Supabase `reddit_posts` directly |
| All 1,878 posts at once | Supabase (API limited by topic/days) |
| ICP profiles | API `/icps/*` (cleaner) |
| Aggregated insights/summaries | API `/insights/*` (pre-computed) |
| Post-level analysis with topic tags | API `/insights/raw` OR Supabase `icp_insights` |
| Investigating a specific post | Supabase `reddit_posts` by `post_id` |
| Posts pending analysis | Supabase `reddit_posts?analyzed=eq.false` |
