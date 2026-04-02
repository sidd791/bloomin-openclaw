# Reddit Intelligence — BloomBrain Value Plan & File Structure
_Devised 2026-03-18 after reviewing live data from the system_

## The Core Idea

Saad's system produces two kinds of value:
1. **Structured intelligence** — pain points, language, objections, desire triggers (via API)
2. **Raw post-level truth** — verbatim language from real women in their exact moment of pain (via Supabase)

BloomBrain's job is to absorb both, connect them to Bloomin's brand and ICP, and get sharper every time
the team asks a question, reviews a response, or confirms/rejects an insight.

The system doesn't just answer questions. It compounds. Every interaction is a data point.
Every correction is a calibration. Over time, BloomBrain becomes the brand's most fluent voice —
because it's trained on how the customer actually speaks, not how marketers think she speaks.

---

## How BloomBrain Gets Better Over Time

### Three Learning Loops

**Loop 1 — Passive Accumulation**
New posts → filtered → analyzed → summarized by the system automatically.
BloomBrain reads the latest summary on demand. The DB does the heavy lifting.

**Loop 2 — Active Calibration (most important)**
When a team member says "this is off" or "this one is perfect" or gives feedback on a BloomBrain response,
that signal gets written to `memory/reddit-calibration.md`. Over time this file becomes the taste layer —
what Bloomin specifically finds valuable vs. not, above and beyond the raw ICP data.

**Loop 3 — Synthesis**
Periodically (or on demand), BloomBrain reads all intelligence layers and produces a synthesized
"brand truth" update — the distilled, Bloomin-specific view of the customer. This lives in
`memory/icp-truth.md` and is the single most important file for generating on-brand responses.

---

## File Structure

```
workspace/
└── memory/
    │
    ├── reddit-system-briefing.md       ✅ EXISTS — full system architecture reference
    │
    ├── icp-truth.md                    🔲 TO CREATE
    │   The living document. Bloomin's distilled understanding of her customer.
    │   Updated after each major intelligence pull or synthesis session.
    │   Sections: who she is, how she speaks, what she fears, what she wants,
    │   what has failed her, what she'd pay for, what makes her trust a brand.
    │   This is what BloomBrain reads before generating copy, strategy, or answers.
    │
    ├── reddit-calibration.md           🔲 TO CREATE
    │   Team feedback log. When someone says "yes, use this" or "this isn't us",
    │   it gets recorded here with context. Becomes the taste filter on top of raw data.
    │   Format: date | feedback type | what was accepted/rejected | why | applied learning
    │
    ├── reddit-copy-vault.md            🔲 TO CREATE
    │   Verified verbatim phrases confirmed as on-brand and copy-ready.
    │   Sourced from the intelligence layer, confirmed by team or BloomBrain judgment.
    │   Organized by use case: hooks, subject lines, pain acknowledgment, CTAs, testimonial frames.
    │   This is the ready-to-use bank. Not raw data — curated gold.
    │
    ├── reddit-intelligence-plan.md     ✅ THIS FILE — the plan itself
    │
    └── reddit-insights-log.md          🔲 TO CREATE (replaces old reddit-insights.md)
        Weekly running log of what changed in the intelligence layer.
        What rose, what fell, new language patterns, new pain points.
        Keeps a timeline of how the ICP is evolving.
```

---

## How Each File Gets Used

### `icp-truth.md`
**When:** Before answering any brand strategy question, generating copy, or giving messaging advice.
**How it gets updated:** After pulling `GET /insights`, BloomBrain distills the delta —
what's new or shifted vs. the current truth — and updates the relevant sections.
**Who benefits:** Everyone. This is the foundation of every smart answer BloomBrain gives.

### `reddit-calibration.md`
**When:** Any time a team member gives feedback on a BloomBrain response.
**Examples of what triggers an entry:**
- "That phrase is perfect, use it more"
- "We don't talk about HRT, that's not our customer"
- "This pain point is too clinical, she wouldn't say it like that"
- "This objection doesn't apply to our product"
**How it compounds:** BloomBrain reads this before answering intelligence questions.
The calibration layer overrides or filters the raw API data.
**This is the most important file for long-term improvement.**

### `reddit-copy-vault.md`
**When:** Someone needs ad copy, email hooks, UGC scripts, or landing page language.
**How it gets populated:** BloomBrain reviews `GET /insights/language` output,
filters for phrases above icp_confidence threshold and aligned to Bloomin's UMS framework,
and adds confirmed phrases with their use-case tags.
**Format per entry:** `[phrase] | [source subreddit] | [confidence] | [use case] | [UMS stage]`

### `reddit-insights-log.md`
**When:** Weekly (Monday before the briefing) or after a major scrape completes.
**How:** Pull `GET /insights/trending` + compare to prior week's log entry.
Note what's rising, what's new, what's gone quiet.
**Why:** Gives the team a temporal view — not just what she's feeling, but how her feelings are shifting.

---

## Operating Protocol (How BloomBrain Uses All This)

### Before answering any ICP/copy/strategy question:
1. Read `memory/icp-truth.md` (the distilled truth)
2. Read `memory/reddit-calibration.md` (the taste filter)
3. If needed, call the API for fresh data
4. Apply Bloomin's UMS framework and brand voice
5. Answer

### When team asks for copy/language specifically:
1. Check `memory/reddit-copy-vault.md` first (already curated)
2. If not enough there, call `GET /insights/language`
3. Filter by Bloomin ICP alignment
4. Return verbatim phrases, not paraphrased summaries

### When team gives feedback on a response:
1. Write the feedback to `memory/reddit-calibration.md` immediately
2. Note what was accepted, what was rejected, why
3. Apply the learning in the same session

### After each major scrape / new summary generated:
1. Call `GET /insights` and `GET /insights/trending`
2. Compare to `icp-truth.md` — what's new or shifted?
3. Update `icp-truth.md` with deltas
4. Append a dated entry to `reddit-insights-log.md`
5. Flag any significant shifts to the team in Slack

---

## What This Compounds Into (12-week view)

**Week 1-2:** System connected. BloomBrain can answer ICP questions accurately using live data.

**Week 3-4:** `icp-truth.md` is populated with the first real synthesis.
Answers become more Bloomin-specific, not just generic ICP intel.

**Week 5-6:** `reddit-calibration.md` has 10-15 feedback entries.
BloomBrain starts filtering out irrelevant data automatically (HRT discussions, EU signals, etc.)
Copy vault has its first 20-30 confirmed phrases.

**Week 8-10:** BloomBrain can generate first-draft ad hooks, email subject lines,
and landing page language that sounds like it came from the customer — because it literally did.

**Week 12+:** The intelligence layer is a compounding asset.
Every question asked, every answer refined, every phrase confirmed.
BloomBrain is the brand's most fluent speaker of the customer's language.

---

## What I Still Need to Execute This

1. Confirm: should I create `icp-truth.md` now by pulling the current intelligence data?
2. Confirm: what's the right Slack channel for me to flag intelligence shifts proactively?
3. When Claude connection is restored on the backend — should I trigger a fresh scrape?
