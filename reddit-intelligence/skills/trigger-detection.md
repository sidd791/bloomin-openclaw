# Trigger Detection — Intelligence System Auto-Fire
_Read this before answering any customer/copy/brand question._
_Expandable: new data sources slot in below without changing the trigger logic._
_Last updated: 2026-03-21_

---

## HOW THIS WORKS

When a question is asked, run it through the trigger taxonomy below.
If it matches any category → fire the specified data pulls before generating any answer.
Never answer a triggered question from general AI knowledge alone.

---

## TRIGGER TAXONOMY

### CATEGORY 1 — Customer Psychology & ICP
**Triggers:** "why does she...", "what does she feel...", "how does she think about...", "what's her mindset", "customer understanding", "who is our customer", "ICP", "target audience", "women with low desire", "what motivates her", "what stops her"

**Data pulls:**
1. `GET /insights` → `icp_summary_paragraph` + `top_pain_points` + `top_desire_triggers`
2. `GET /icps/ranked` → full profile list, filter confidence ≥7
3. For specific psychology angle → `GET /insights/raw?topic={most_relevant_tag}&limit=1000&days=90` + parallel tags if needed
4. Load: `intelligence/icp-truth.md`
5. Load: `calibration/calibration-log.md`

**Answer format:** Narrative first (who she is, what she feels), data second (frequency, quotes, source)

---

### CATEGORY 2 — Copy, Hooks & Messaging Language
**Triggers:** "ad copy", "hook", "subject line", "headline", "UGC script", "landing page", "email copy", "give me language", "how should we say", "write something", "messaging", "words she uses"

**Data pulls:**
1. `GET /insights/language` → verbatim phrases, all-time (no recency window — language is evergreen)
2. `GET /icps/subreddit/{most_relevant_subreddit}` → `language_patterns` arrays, confidence ≥7
3. `GET /insights/raw?topic={tag}&limit=1000&days=730` → `language_patterns` field per post, confidence ≥7
4. Load: `calibration/calibration-log.md` → approved/rejected phrases

**Answer format:** Verbatim phrases only. No paraphrase. Source (subreddit) + frequency + use case + UMS stage.

---

### CATEGORY 3 — Pain Points & Objections
**Triggers:** "pain points", "what's blocking her", "objections", "why won't she buy", "what she's worried about", "barriers", "hesitations", "what stops her", "what she's afraid of"

**Data pulls:**
1. `GET /insights/pain-points` → ranked list with example quotes
2. `GET /insights/objections` → objection + frequency + counter_message
3. `GET /insights/raw?topic={tag}&limit=1000&days=90` → `pain_points` + `objections` fields
4. Load: `intelligence/icp-truth.md` → objections table

**Answer format:** Objection + frequency + counter-message + confidence note. High-frequency objections first.

---

### CATEGORY 4 — Trends & Market Signals
**Triggers:** "what's trending", "what's rising", "what's new", "what's women talking about", "what's changing", "emerging topics", "what should we focus on now"

**Data pulls:**
1. `GET /insights/trending` → rising/stable/falling topics
2. Compare against `intelligence/insights-log.md` → what's shifted since last log entry
3. `GET /insights/raw?topic={rising_tag}&limit=200&days=14` → confirm signal strength

**Answer format:** Rising/stable/falling with evidence. Always state signal strength (is this 200 posts or 8 posts?). Weak signals flagged explicitly.

---

### CATEGORY 5 — Product & Ingredient Signals
**Triggers:** "what are women saying about [ingredient]", "maca", "shatavari", "ashwagandha", "cortisol", "supplement", "what ingredients should we focus on", "product angle", "what's working for them"

**Data pulls:**
1. `GET /insights/raw?topic=supplements&limit=1000&days=730` + `topic=ayurveda` + `topic=natural_remedies` (parallel)
2. `GET /insights/raw?topic=hormones&limit=1000&days=365`
3. Supabase `reddit_posts` body search if ingredient is specific (direct text search in post body)
4. Load: `intelligence/icp-truth.md` → hero ingredients section

**Answer format:** What women are actually saying about it (verbatim) + sentiment + frequency + Bloomin positioning implication.

---

### CATEGORY 6 — Brand Positioning & Strategy
**Triggers:** "how should we position", "what angle", "brand strategy", "what should we focus on", "messaging framework", "how do we stand out", "what's our edge", "what does Bloomin solve"

**Data pulls:**
1. `GET /icps/export` → full picture in one call
2. `GET /insights/objections` → what she doesn't believe yet
3. `GET /insights/trending` → what's rising that we could own
4. Load: `intelligence/icp-truth.md` (full)
5. Load: `calibration/calibration-log.md`

**Answer format:** Connect data to UMS framework. Don't just describe — prescribe. What the data says → what Bloomin should do.

---

### CATEGORY 7 — Subreddit / Community Deep Dive
**Triggers:** "what's r/[name] saying", "perimenopause community", "deadbedrooms", "postpartum", "newborns subreddit", "what's happening in [community]"

**Data pulls:**
1. `GET /icps/subreddit/{name}` → all profiles + aggregated data + weekly scores
2. `GET /insights/by-subreddit/{name}?limit=1000` → raw post-level insights
3. Supabase `reddit_posts?subreddit=eq.{name}&analyzed=eq.true` → full posts if deep dive needed

**Answer format:** Community character → top profiles → key language → Bloomin relevance rating.

---

## PARALLEL QUERY PATTERN

For complex questions spanning multiple topics, run simultaneously:
```
Topic 1: GET /insights/raw?topic=low_libido&limit=1000&days=90
Topic 2: GET /insights/raw?topic=stress&limit=1000&days=90
Topic 3: GET /insights/raw?topic=hormones&limit=1000&days=90
Topic 4: GET /insights/raw?topic=intimacy&limit=1000&days=90
```
Merge results → deduplicate by `post_id` → filter by confidence floor → synthesize.

---

## DATA SOURCE REGISTRY

All active intelligence sources. New sources added here when integrated.

### SOURCE 1 — Reddit Intelligence (ACTIVE)
- **Type:** Community posts — organic customer voice
- **Coverage:** Desire, hormones, perimenopause, postpartum, intimacy, supplements
- **Access:** API (`http://187.127.96.93/api`) + Supabase direct
- **Credentials:** `system/credentials.md`
- **Best for:** Customer psychology, verbatim language, pain points, objections, trends
- **Confidence system:** icp_confidence 0–10
- **Trigger categories:** All 7 above

### SOURCE 2 — (placeholder)
_Next data source slots in here. Same structure: type, coverage, access, credentials, best for, confidence system, which trigger categories it feeds._

### SOURCE 3 — (placeholder)
_e.g. Meta Ad Library — competitor ad intelligence_

### SOURCE 4 — (placeholder)
_e.g. Trustpilot / Shopify reviews — customer purchase behaviour + post-purchase sentiment_

### SOURCE 5 — (placeholder)
_e.g. TikTok intelligence — content trends + hook patterns_

---

## ROUTING LOGIC — WHICH SOURCE FOR WHICH QUESTION

As more sources are added, this table determines which source(s) fire for each category:

| Category | Reddit | Source 2 | Source 3 | Source 4 | Source 5 |
|----------|--------|----------|----------|----------|----------|
| Customer psychology | ✅ PRIMARY | | | | |
| Copy & language | ✅ PRIMARY | | | | |
| Pain points | ✅ PRIMARY | | | ⬜ future | |
| Trends | ✅ PRIMARY | | | | ⬜ future |
| Product signals | ✅ PRIMARY | | | | |
| Brand positioning | ✅ PRIMARY | | ⬜ future | | |
| Community deep dive | ✅ PRIMARY | | | | |

_Update this table as new sources are added. Mark PRIMARY, SECONDARY, or SUPPORTING._

---

## CORE RULE — NO RAW DATA DUMPING (non-negotiable)

Grabbing data from the system and pasting it directly at the user is wrong. Always.

**What I must do instead:**

```
1. Understand what the user is actually asking for
        ↓
2. Pull data from the system (API / Supabase)
        ↓
3. Analyse: what in this data is relevant to their specific request?
        ↓
4. Blend: how does the data connect to their requirement?
        ↓
5. Articulate: synthesise into a clear, useful answer
        ↓
6. Deliver: structured, intelligent output — not a data dump
```

**The test before delivering any answer:**
- Did I process the data or just copy it? → Process it
- Is this answering their actual question or just showing what I found? → Answer the question
- Would a smart strategist present information this way? → If no, rewrite

**Examples of wrong vs right:**

❌ Wrong — raw dump:
> "Here are the top pain points from the system: [paste list of 10 pain points with frequencies]"

✅ Right — synthesised answer:
> "The dominant signal for this angle is X — women describe it as [specific quote], which tells us [implication for the ask]. For the product page, this translates to [specific recommendation], because [reason grounded in data]."

❌ Wrong — raw language pasted:
> "Women say: 'it was like a light switch turned off', 'my insides contract', 'I can't find it in myself to want him'"

✅ Right — translated and contextualised:
> "The core psychological truth here is that she experiences desire loss as sudden and involuntary — not a choice. For [the specific output requested], this means the copy should convey [X], because that's what will make her feel recognised without feeling exposed."

**The intelligence is in the synthesis. The data is the ingredient, not the dish.**

---

## CONTEXT TRANSLATION RULE (critical — calibrated 2026-03-21)

Reddit language is raw ICP truth. How it gets used depends entirely on the output context.

| Output context | How to use Reddit data |
|---------------|----------------------|
| Internal intelligence / strategy answers | Verbatim phrases are fine — they're insights for the team |
| Ad copy (social, paid) | Translate to brand voice — keep the feeling, remove the confession |
| Website / product page | Must be product-anchored. Pain → mechanism → restoration. Never paste raw Reddit quotes. |
| Email subject lines | Can be more emotionally raw — but still brand-voiced, not relationship-confessional |
| UGC scripts | Closer to raw — but framed as her journey, not her shame |

**The test for product page / website copy:**
- Would this embarrass her if someone read it over her shoulder? → Rephrase
- Does this connect back to the product mechanism? → Must
- Is this a confession or a recognition? → Should feel like recognition, never confession

**The translation pattern (always apply for website/product copy):**
- Raw insight: *"it was like a light switch turned off"*
- Product translation: *"When desire disappears, it's not you — it's your hormones in survival mode"*

- Raw insight: *"I miss wanting sex"*
- Product translation: *"Bloomin doesn't create desire. It removes the hormonal blocker so desire can return on its own."*

**When someone asks for product page / website / ad copy → always ask yourself:**
Does this copy name the pain AND connect to the product mechanism? If not — rewrite until it does both.

---

## QUALITY GATES (applied to every triggered answer)

Before delivering any answer:
- [ ] Data pulled from at least one live source (not general AI knowledge)
- [ ] Two-dimension minimum query applied
- [ ] Confidence floor respected (7+ copy, 5+ default, 3 flagged only)
- [ ] Recency tier correct (14-30d intelligence, all-time language)
- [ ] EU data flagged if present
- [ ] Calibration log checked
- [ ] Source cited in answer
- [ ] Brand voice applied (restore/return/reclaim — never boost/enhance)
