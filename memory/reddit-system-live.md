# Reddit Intelligence System — Live Exploration Results
_Fully explored: 2026-03-21. This is the operational guide based on real API behaviour._

---

## SYSTEM STATE (as of 2026-03-21)

| Metric | Value |
|--------|-------|
| Status | ✅ Healthy |
| Total posts scraped | 1,878 |
| Posts analyzed by Claude | 1,298 |
| Posts pending analysis | 580 |
| Last scrape | 2026-03-21 16:03 UTC — 680 posts stored |
| Next scheduled scrape | 2026-03-23 |
| Scrape interval | 48 hours |
| ICP profiles built | 37 across 4 subreddits |
| Approved subreddits | 3 (deadbedrooms, perimenopause, newborns) |
| Under review | 1 (ayurveda — score 68, threshold 70) |

---

## SUBREDDITS

| Subreddit | Score | Status | Subscribers | Notes |
|-----------|-------|--------|-------------|-------|
| r/deadbedrooms | 77 | ✅ Approved | 550K | Best ICP relevance — desire loss, intimacy shutdown |
| r/perimenopause | 76 | ✅ Approved | 122K | Hormonal content, skews 40-55 |
| r/newborns | 55 | ✅ Approved | 111K | Postpartum — indirect ICP overlap |
| r/ayurveda | 68 | 🔄 Review | 31K | Natural remedies, PCOD, adaptogens |

**Next evaluations:** deadbedrooms + perimenopause + newborns → 2026-04-04. ayurveda → 2026-03-28.

---

## ICP PROFILES — ALL 37 (sorted by confidence)

### r/perimenopause (14 profiles)
| Score | Name |
|-------|------|
| 9.2 | The Sleep-Deprived Insomniac |
| 9.0 | The HRT Refugee |
| 8.8 | The Invisible Bleeder |
| 8.5 | The Medically Dismissed |
| 8.5 | The Emotional Grenade |
| 8.3 | The Urogenital Sufferer |
| 8.2 | The Body Stranger |
| 8.0 | The Cycle Chaos Navigator |
| 7.8 | The Afternoon Crash |
| 7.5 | The High Performer Fading Out |
| 7.5 | The Mood Maze |
| 7.5 | The Desire Resurrection |
| 7.2 | The Joint Pain Sufferer |
| 7.0 | The Identity in Grief |

### r/deadbedrooms (10 profiles)
| Score | Name |
|-------|------|
| 9.0 | The Desire Amnesiac ⭐ Most Bloomin-relevant |
| 8.5 | The Hormonally Derailed ⭐ |
| 8.5 | The Touch-Averse Partner |
| 8.0 | The Overloaded and Emptied Out ⭐ (Survival Mode match) |
| 7.5 | The Rejection-Wounded Recluse |
| 7.5 | The Post-Pain Avoider |
| 7.0 | The Invisible Woman |
| 7.0 | The Menopausal Erased |
| 6.5 | The Body-Betrayed |
| 6.0 | The Post-Anxiety Intimacy Crasher |

### r/newborns (7 profiles)
| Score | Name |
|-------|------|
| 9.0 | The Postpartum Identity Erasure ⭐ |
| 8.5 | The Survival Mode Insomniac |
| 8.2 | The Invisible Mental Load Carrier |
| 8.0 | The Postpartum Rage Underneath |
| 7.8 | The Postpartum Anxiety Spiral |
| 7.6 | The Postpartum Body Grief |
| 7.5 | The Intimacy Pressure Cooker |

### r/ayurveda (6 profiles — lower ICP confidence, use with caution)
| Score | Name |
|-------|------|
| 6.0 | The Hormonal Maze Walker |
| 5.5 | The Burnout Seeker |
| 5.0 | The Anxious Natural Healer |
| 4.5 | The Postpartum Restorer |
| 4.5 | The Natural Remedy Skeptic-Seeker |
| 4.5 | The Overwhelmed Ayurveda Newcomer |

**⭐ = Most aligned to Bloomin's UMS Survival Mode framework**

---

## INSIGHTS LAYER — LIVE DATA

### Global ICP Summary Paragraph (latest, generated 2026-03-21 16:09 UTC)
> "Your core customer is a woman between roughly 28 and 52 who is deeply aware that something has shifted in her desire — but has not yet named it as hormonal, treatable, or her fault to address. She loves her partner and often cannot explain why her body won't cooperate with that love; she describes the disconnect in visceral terms like 'my insides contract' or 'I just can't find it in myself to want him.' She is likely navigating at least one compounding factor — SSRIs, postpartum recovery, surgical menopause, body image damage, or a history of medical dismissal — and has often been told by a doctor that her levels are 'fine,' which leaves her with no roadmap and a quiet sense that this is just who she is now. She is not browsing for a product; she is quietly desperate, searching for someone who understands what she is experiencing before she trusts anyone enough to try a solution — so your messaging must lead with validation, accurate language, and the implicit promise that desire is not gone, it's buried."

### Top Pain Points (frequency from 100 analyzed posts)
1. [34] Complete/near-complete loss of sexual desire — no explanation
2. [22] Intimacy dead months/years with no active solution pursuit
3. [20] Relationship on verge of collapse due to desire gap
4. [19] Physical aversion/disgust at partner's touch despite emotional love
5. [18] Painful sex due to vaginal dryness (post-hysterectomy, postpartum, hormonal)
6. [16] SSRI-induced libido suppression + inability to orgasm
7. [15] Sex mechanical/dissociative — going through motions
8. [14] Body image blocking physical intimacy
9. [12] Postpartum intimacy breakdown
10. [11] Medical dismissal — told levels "fine" with no treatment

### Top Verbatim Language Phrases
- "going through the motions" [12]
- "dead bedroom" [19]
- "it felt like there was sand inside her" [4]
- "my insides contract" [5]
- "I want to fix it if I can" [8]
- "I just need to talk to somebody" [7]
- "there must be something wrong with me" [9]
- "it was like a light switch turned her off" [6]
- "I can't find it in myself to want him" [7]
- "losing myself in this process" [6]

### Top Objections + Counter-Messages
1. [21] "Nothing is physically wrong with me" → Lead with education, not diagnosis
2. [16] "Problem is relational, not fixable with a product" → Help her feel like herself first
3. [14] "Can't afford therapy" → Position as accessible first step, no prescription/waitlist
4. [13] "Doctor said levels fine" → Validate frustration; 'within range' ≠ 'optimal'
5. [12] "Tried things before, nothing lasted" → Root-cause support, honest timelines
6. [11] "This is just who I am now — across relationships" → 'Your baseline can shift'
7. [9] "Scared this is permanent" → Use post-hysterectomy/post-SSRI recovery stories
8. [8] "Body image is the real blocker" → Internal wellbeing changes body relationship

### Trending Topics (rising)
- Post-SSRI sexual dysfunction and libido recovery 🔥
- Surgical menopause and forced hormonal shutdown in women under 50 🔥
- Postpartum desire loss persisting well beyond the newborn phase 🔥
- Body image as primary driver of intimacy avoidance 🔥
- Medical gaslighting — told "normal" despite active suffering 🔥
- Neurodivergence (sensory sensitivity, ADHD) as underexplored libido factor 🔥

---

## API BEHAVIOUR — CONFIRMED LIMITS & QUIRKS

### /icps endpoints
- `GET /icps` — returns ALL profiles, no pagination needed
- `GET /icps/ranked?limit=N` — max confirmed limit: 200. **Default is 50 — always pass limit=200 to see all 37**
- `GET /icps/export` — best single call for full picture; includes aggregated data per subreddit
- `GET /icps/subreddit/{name}` — returns profiles + weekly scores + aggregated arrays in one call
- `GET /icps?subreddit=X` — filter works; returns subset

### /insights endpoints
- `GET /insights` — ⚠️ `top_language_patterns` frequency shows as `?` in raw output — use `GET /insights/language` instead for verbatim phrases
- `GET /insights/raw` — default: 20 records, 30 days. Max: limit=200, days=365
- `GET /insights/raw?topic=X` — confirmed record counts by topic (limit=200, days=365):
  - hormones: 200 | self_care: 200 | fatigue: 200 | mood: 200 | anxiety: 200 | stress: 200
  - postpartum: 200 | low_libido: 108 | perimenopause: 145 | intimacy: 149
  - natural_remedies: 89 | menopause: 88 | relationship: 141 | supplements: 64
  - body_image: 50 | ayurveda: 49 | cortisol: 46 | confidence: 19 | pcos: 8 | marriage: 37
- `GET /insights/by-subreddit/{name}?limit=500` — confirmed returns up to 500 records (perimenopause tested)
- `GET /insights/trending` — compares only the 2 most recent summaries. Currently only 2 summaries exist.

### /subreddits endpoints
- `GET /subreddits` — returns approved only (3 currently)
- `GET /subreddits/all` — returns all 4 including "review" status
- Full scoring breakdown available: relevance_score, audience_score, activity_score, brand_safety_score

### /scrape endpoints
- Scrape logs: 19 runs logged. Last 3 stored 680, 30, 674 posts.
- Manual `POST /scrape` triggers Phase 1 only
- Phase 2 (incremental refresh) runs on scheduler only

### /config
- Current: max_posts_per_subreddit = 2500 (high ceiling)
- 57 keywords active
- Scrape interval: 48 hours
- Report schedule: Monday 09:00

### /chat
- Creates persistent chat sessions with Claude using live ICP data
- Sessions survive across calls (session ID required)
- BloomBrain should use this sparingly — direct API calls are faster for specific queries

### /docs
- Full Swagger/UI available at http://187.127.96.93/docs

---

## CONFIRMED PARAMETER LIMITS (updated 2026-03-21 — limits removed by Saad)

| Endpoint | Parameter | Min | Default | Max | Notes |
|----------|-----------|-----|---------|-----|-------|
| `/icps/ranked` | `limit` | 1 | **returns ALL** | **No hard cap** | Returns all 37 with any large value |
| `/insights/raw` | `limit` | 1 | 20 | **No hard cap** | 1000 tested → 1000 records returned |
| `/insights/raw` | `days` | 1 | 30 | **No hard cap** | 730 tested → works fine |
| `/insights/by-subreddit/{name}` | `limit` | 1 | 50 | **No hard cap** | 5000 tested → returns all available (506 for perimenopause) |

### Practical ceilings (actual data in DB, not API limits)
- `/icps/ranked` — 37 profiles total currently
- `/insights/raw?topic=low_libido&days=730` — 1000 records returnable, actual DB records vary by topic
- `/insights/by-subreddit/perimenopause` — 506 records total in DB
- High `days` values (730+) just return all available data — no error

### Error behaviour
- **Missing/wrong API key** → `{"detail": "Invalid or missing API key"}` (same message for both)
- **Non-existent subreddit** (`/subreddits/{name}`) → `{"detail": "Subreddit 'X' not found"}`
- **Non-existent ICP subreddit** (`/icps/subreddit/{name}`) → empty result (no error, just 0 profiles)
- **Invalid topic tag** (`/insights/raw?topic=X`) → 0 records returned silently (no error)
- **Non-existent scrape run** → `{"detail": "Scrape run 'X' not found"}`
- **`limit=0`** → still a validation error (min is 1)

### Key defaults to know
- `/icps/ranked` with no limit → returns ALL profiles in DB
- `/insights/raw` with no params → 20 records, last 30 days
- `days=1` and `days=7` currently return same 20 records (all data is from today)
- Invalid topic tags return 0 records silently — always use valid tags from the confirmed list
- Use large limits freely now (e.g. `limit=10000`) to ensure you get everything

### Notes on /config
- `max_posts_to_analyze` field is NOT returned in GET /config response (only in docs)
- `max_posts_per_subreddit` currently 2500 (very high ceiling)
- Report schedule: Monday 09:00 UTC

---

## OPERATING PLAYBOOK — HOW TO GET MAXIMUM VALUE

### Decision tree: which endpoint to use?

**"What's our ICP?"** → `GET /insights` (narrative) + `GET /icps/ranked?limit=200` (full profiles)

**"Copy language / ad hooks"** → `GET /insights/language` (verbatim) + `/icps/subreddit/{name}` language_patterns arrays

**"What's she feeling about X topic?"** → `GET /insights/raw?topic={tag}&limit=200&days=365`
Best tags for Bloomin: `low_libido`, `hormones`, `intimacy`, `postpartum`, `stress`, `fatigue`, `perimenopause`

**"What objections to address in ads?"** → `GET /insights/objections` (includes counter_messages)

**"What's rising?"** → `GET /insights/trending`

**"Show me the ICP profiles for a specific community"** → `GET /icps/subreddit/{name}`

**"Full picture for a strategy session"** → `GET /icps/export` (single call, everything)

**"System health before big operation"** → `GET /health`

### ICP confidence filtering
- Score 8.0+ = high confidence, use freely for copy and messaging
- Score 6.0–7.9 = medium confidence, use with caveats
- Score below 6.0 = low confidence, use for pattern recognition only, don't treat as core ICP
- For Bloomin specifically: deadbedrooms + newborns profiles 8.0+ are the sweet spot

### What to ignore / filter out
- r/ayurveda profiles (confidence 4.5–6.0) — too broad, not Bloomin-specific enough
- Raw posts with icp_confidence < 4 — marginal relevance
- Any data from EU/international unless flagged as relevant signal (see SOUL.md)
- Relational/psychological profiles (Rejection-Wounded Recluse, Post-Anxiety Crasher) — outside supplement positioning

### Bloomin UMS alignment
The system data maps directly to UMS stages:
- **Stage 1 (Diagnosis):** Pain points 1, 5 — "something's wrong but I don't know what"
- **Stage 2 (Disqualification):** Objections 1, 3, 4 — "I tried X and it didn't work"
- **Stage 3 (Breakthrough):** Trending topics — cortisol/survival mode link
- **Stage 4 (Activation):** Desire triggers in ICP profiles — "wanting to want again"

---

## NOTES & OBSERVATIONS FROM EXPLORATION

1. The insights layer `top_language_patterns` has a display bug — shows `?` for phrase field in `GET /insights`. Use `GET /insights/language` directly instead.
2. All 37 ICP profiles were built from just the first batch of scraped posts. As the 580 pending posts get analyzed, more profiles will be created.
3. r/newborns has a low relevance_score (12) but still got approved and has produced 7 strong ICP profiles — the postpartum angle is real signal.
4. r/ayurveda is currently "review" status (score 68 vs threshold 70). It may get approved on next evaluation (2026-03-28). ICP profiles from it are lower confidence but capture the "natural remedy seeker" archetype.
5. The /chat endpoint works — it uses live ICP data. This is basically a second AI layer inside the system. Useful for delegating complex analysis but BloomBrain should handle most queries directly.
6. Reports generate PDFs and post to Slack — but we haven't tested this yet. Use `POST /reports/generate` when needed.
7. `max_posts_per_subreddit` is currently set to 2500 — this is very high. Actual posts stored suggests scrapes haven't hit that ceiling yet (680 in latest run).
