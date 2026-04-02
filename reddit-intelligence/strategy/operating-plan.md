# BloomBrain Reddit Intelligence — Operating Plan
_How I get smarter, answer better, and self-improve over time._
_Authored: 2026-03-21_

---

## THE CORE MISSION

Every question a team member asks me is an intelligence question. Whether it's about:
- Customer psychology ("why don't women talk about this openly?")
- Copy ("give me a hook for the postpartum angle")
- Product ("should we add maca? what are women saying about it?")
- Business strategy ("which pain point is most underserved in the market?")
- Brand ("how should we frame the cortisol connection in ads?")

...the answer lives somewhere in the Reddit data. My job is to know exactly where to look, pull only what's relevant, and give an answer that's grounded in real signal — not generalized AI output.

---

## PART 0: HANDLING THE GROWING DATA PROBLEM

As posts, ICPs, and profiles accumulate, query precision becomes more important — not less. Four rules, always applied:

### Rule 1 — Recency Weighting (two tiers, not one)
Customer language and pain points shift. But not all queries are equal:

| Query type | Time window | Reason |
|-----------|------------|--------|
| Intelligence / trend queries ("what's she worried about now?") | `days=14` or `days=30` | Recency matters — signals evolve |
| Language / copy queries ("give me phrases she uses") | All-time (`days=730`) | Evergreen language doesn't expire |
| Strategy / deep-dive queries | `days=90` default, adjust as needed | Balance freshness with volume |

Never apply recency weighting to language pattern queries. *"I miss wanting sex"* doesn't go stale.

### Rule 2 — Confidence Floor (tiered, not flat)
Floor of 3 is too low for real answers — it's the API minimum, not a quality threshold.

| Use case | Confidence floor | Reason |
|----------|-----------------|--------|
| Copy language, ad hooks, messaging | **7+** | Only put real signal into real content |
| Strategy / ICP answers | **5+** | Default working floor |
| Broad pattern recognition, sparse topics | **3** | Explicit exception only — flagged when used |

Over time, calibration feedback will push the working floor higher. Start tight, loosen when the data justifies it.

### Rule 3 — Two-Dimension Minimum Queries
At scale, single-dimension queries return too much noise. Always filter by at least two dimensions simultaneously:

| Question type | Dimensions to combine |
|--------------|----------------------|
| Topic deep dive | `topic_tag` + `days` |
| Subreddit-specific | `subreddit` + `confidence ≥7` |
| Copy language | `subreddit` + `topic_tag` |
| Trending signal | `topic_tag` + `days=14` |
| Broad strategy | `confidence ≥8` + `subreddit` |

Single-dimension queries reserved for: system health checks, mapping what exists, explicit wide-net requests.

### Rule 4 — Parallel Multi-Tag Queries
The API supports one topic tag per call. For complex questions, run parallel calls across related tags and merge results:

**Example — "what's the psychology behind her not wanting sex?"**
Run simultaneously:
- `GET /insights/raw?topic=low_libido&limit=1000&days=90`
- `GET /insights/raw?topic=intimacy&limit=1000&days=90`
- `GET /insights/raw?topic=stress&limit=1000&days=90`
- `GET /insights/raw?topic=hormones&limit=1000&days=90`

Merge, deduplicate by `post_id`, filter by confidence, synthesize across all four angles.
This is always better than one broad query at scale.

---

## PART 1: HOW I RETRIEVE DATA

### The Decision Engine — Which Source for Which Question

Every query gets routed before I pull any data. The routing logic:

**Step 1: What's the question type?**

| Question type | Primary source | Secondary |
|--------------|---------------|-----------|
| "What is our ICP feeling / thinking / saying?" | `GET /insights` + `GET /icps/ranked` | Supabase `icp_profiles` |
| "What are women saying about X topic?" | `GET /insights/raw?topic=X&limit=1000&days=730` | Supabase `icp_insights` filtered by topic_tags |
| "Give me verbatim language / copy phrases" | `GET /insights/language` + `icp_profiles.language_patterns` | Supabase `reddit_posts.body` (raw posts) |
| "What objections should we address?" | `GET /insights/objections` | `icp_profiles.objections` by subreddit |
| "What's trending / rising / new?" | `GET /insights/trending` | Compare `insights-log.md` entries over time |
| "Tell me about [specific archetype]" | `GET /icps/subreddit/{name}` filtered by profile name | Supabase `icp_profiles` with confidence filter |
| "What's the psychology behind X?" | High-confidence `icp_profiles` (score ≥8.0) | `icp_insights` with topic filter + raw posts |
| "Product angle — what do women want re: X ingredient?" | `GET /insights/raw?topic=supplements` | Supabase `reddit_posts` body search |
| "Competitor / market question" | Reddit data for positioning signals | `memory/competitors/` for direct competitor intel |
| "System health / data status" | `GET /health` | — |

**Step 2: Apply the ICP filter**

Before surfacing any data, I ask: *Is this aligned to Bloomin's ICP?*
- Women 25–52
- Low desire / hormonal stress / energy / mood / intimacy
- Primary: USA. Secondary: UK, AUS, CA
- Flag EU data clearly if it appears — never present as actionable

**Step 3: Apply confidence thresholds**

| Confidence | What I do |
|-----------|-----------|
| 8.0–10.0 | Use freely — core ICP, high signal |
| 6.0–7.9 | Use with context — note it's medium confidence |
| Below 6.0 | Pattern recognition only — don't present as definitive |
| r/ayurveda profiles | Always flag as lower-confidence, broader audience |

**Step 4: Go deep when needed**

For complex questions (psychology deep-dives, product strategy, multi-angle brand questions):
1. Pull `GET /icps/export` — full picture in one call
2. Cross-reference with `GET /insights/raw` for the specific topic
3. If the question requires verbatim language at scale → go to Supabase `reddit_posts` directly (full body text, 1,878 posts)
4. Synthesize across sources — don't just dump data, connect it

---

## PART 2: QUERY MAPPING — SPECIFIC EXAMPLES

### "Someone asks about depression"
→ Not a direct Bloomin ICP topic. But: map to adjacent signals.
→ `GET /insights/raw?topic=mood&limit=1000` + `topic=anxiety`
→ Filter for posts where depression intersects with desire/hormonal/energy
→ Surface emotional states from `icp_insights.emotional_states`
→ Flag: "Bloomin doesn't treat depression, but here's where it intersects with our ICP's experience"

### "Someone asks about dead bedrooms / no desire"
→ `GET /icps/subreddit/deadbedrooms` — all 10 profiles
→ `GET /insights/raw?topic=low_libido&limit=1000&days=730`
→ `GET /insights/raw?topic=intimacy&limit=1000&days=730`
→ Pull top language patterns specific to deadbedrooms subreddit
→ Cross with `icp_truth.md` for Bloomin framing

### "Someone asks about postpartum psychology / newborn mothers"
→ `GET /icps/subreddit/newborns` — all 7 profiles
→ `GET /insights/raw?topic=postpartum&limit=1000&days=730`
→ Look at `emotional_states` specifically — not just pain points
→ Note: these women don't self-identify as "low libido" — frame accordingly

### "Someone asks about body pain / physical symptoms"
→ Map to specific topics: fatigue, hormones, perimenopause
→ `GET /insights/raw?topic=fatigue` + `topic=hormones` + `topic=perimenopause`
→ Filter `icp_profiles` for physical symptom profiles (Urogenital Sufferer, Joint Pain Sufferer, Invisible Bleeder)
→ Surface verbatim physical language

### "Brand psychology / why won't she buy?"
→ `GET /insights/objections` — the most powerful endpoint for this
→ Cross with `calibration-log.md` for any known brand-specific objection patterns
→ Layer with confidence filter: high-confidence objections (freq ≥ 10) are the ones worth addressing in ads

---

## PART 3: THE SELF-IMPROVEMENT SYSTEM

This is the most important part. The data grows. My understanding must grow with it.

### Three Feedback Loops

**Loop 1 — Passive (happens automatically)**
Every new scrape → new posts analyzed → new ICP profiles built → I pick them up next time I query.
Nothing required from me. The pipeline does this.
My job: check `GET /health` periodically, notice when `analyzed_posts` jumps, update `insights-log.md`.

**Loop 2 — Active Calibration (most important — requires human input)**
When any team member says:
- "That's perfect" / "Use this more" → log to `calibration/calibration-log.md` as ✅ APPROVED
- "That's wrong" / "We don't say that" → log as ❌ REJECTED
- "Close but change X" → log as 🔧 REFINED
- "Never cover this" → log as 🚫 OFF-LIMITS

I read `calibration-log.md` BEFORE answering any intelligence question.
This file overrides raw data. If the founder says a phrase is wrong, I don't use it — regardless of frequency score.

**Loop 3 — Self-Correction (my responsibility)**
When I give an answer and later see it was wrong:
1. What was the source of the error? (wrong endpoint, wrong confidence filter, EU data not flagged, misread profile)
2. Document the correction in `calibration-log.md` under "self-corrections"
3. Update my decision logic if needed

### Detecting Wrong Data
If a team member gives me information that contradicts the raw data:
- I note the contradiction internally before accepting it
- If they say "women in this community talk about X" but my data shows low frequency for X → I flag this: "I'm seeing lower signal on X than expected — can you confirm where you're seeing this?"
- I do NOT blindly write contradicted info to memory files
- I DO write confirmed corrections immediately

### What the Founder Prioritises (to be built over time)
This section gets populated as I learn. Starting principles:
- Brand voice is non-negotiable — restore/return/reclaim, never boost
- UMS framework is the lens for all messaging
- USA primary, always. Never present EU signals as US-actionable.
- ICP confidence matters — don't surface weak signals as strong ones
- Direct, sharp answers. No fluff. Lead with the signal, not the methodology.

---

## PART 4: STAYING CURRENT AS THE SYSTEM GROWS

### When new posts are scraped
1. `GET /health` — note new `analyzed_posts` count
2. `GET /insights/trending` — what's rising since last check?
3. Compare to `insights-log.md` — what's shifted?
4. Update `insights-log.md` with dated entry
5. If significant shift → flag to team in Slack

### When new ICP profiles are built
1. `GET /icps/ranked` — what's new since last check?
2. Assess confidence score and Bloomin relevance
3. If score ≥ 8.0 and Bloomin-relevant → note in `icp-truth.md` if it changes the picture
4. If it refines or challenges an existing understanding → update accordingly

### When new subreddits are added
1. `GET /subreddits/all` to see new entries
2. `GET /icps/subreddit/{new_name}` once profiles are built
3. Assess fit: relevance score, audience score, ICP confidence of early profiles
4. Document in system notes

### Periodic synthesis (every 2 weeks or after major scrape)
1. Pull full `GET /icps/export`
2. Compare to `icp-truth.md` — what's changed?
3. Review `calibration-log.md` — any new patterns in feedback?
4. Update `icp-truth.md` if the picture has shifted
5. Append to `insights-log.md`

---

## PART 5: ANSWER QUALITY STANDARDS

Every answer I give should pass this check:

✅ Grounded in actual data (not generalized AI knowledge)
✅ Source cited (which endpoint / which profile / which subreddit)
✅ Confidence level stated when relevant ("this is from high-confidence profiles" vs "this is a weaker signal")
✅ Two-dimension minimum query applied (never single-dimension at scale)
✅ Recency tier correct for the question type (intelligence vs language)
✅ Confidence floor respected (7+ for copy, 5+ default, 3 only flagged)
✅ Multi-tag parallel queries run when question spans multiple topics
✅ ICP-filtered (not just any data — only Bloomin-relevant)
✅ Bloomin brand voice applied (framing, language choices)
✅ Calibration layer applied (team feedback honoured)
✅ EU data flagged if present

If I can't ground an answer in the data, I say so — and either pull fresh data or acknowledge the gap.

### Answer format by question type
| Question | Format |
|---------|--------|
| ICP psychology | Narrative first, data second. Lead with what she feels, then support with frequency/quotes. |
| Copy language | Verbatim phrases only — no paraphrase. Source + frequency + use case. |
| Trend / signal | Rising/stable/falling with evidence. Magnitude matters — flag if it's a weak signal. |
| Objection handling | Objection + frequency + counter-message + confidence note. |
| Product/brand strategy | Connect the data to the UMS framework. Don't just describe what she says — explain what it means for Bloomin. |
| System status | Numbers only. Health stats, post counts, last scrape. Clean and factual. |

---

## WHAT I STILL NEED FROM THE TEAM

1. **Feedback as we go** — every correction, approval, or "that's not us" gets logged
2. **Founder voice calibration** — over time, direct input on what matters most
3. **New subreddits to add** — when you identify new communities, I'll assess and integrate
4. **Scrape triggers when needed** — I won't scrape without direction, but I'll flag when data looks stale

---

_This plan is a living document. Update it as the system and team needs evolve._
