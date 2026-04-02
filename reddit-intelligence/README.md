# Reddit Intelligence System — BloomBrain
_Root folder for everything related to Saad's Reddit intelligence pipeline._
_Last updated: 2026-03-21_

---

## What This Is

Saad's production Reddit intelligence system scrapes approved communities, filters posts for Bloomin ICP relevance, analyzes them with Claude, and builds ICP profiles over time. BloomBrain queries this system via API and direct Supabase access to answer brand, copy, and strategy questions.

**Current state:** 4 subreddits, 1,878 posts scraped, 1,298 analyzed, 37 ICP profiles built.

---

## Folder Structure

```
reddit-intelligence/
│
├── README.md                    ← you are here
│
├── system/                      ← technical system knowledge
│   ├── credentials.md           ← API keys + Supabase access
│   ├── api-reference.md         ← every endpoint documented
│   ├── system-briefing.md       ← full architecture + operating modes
│   ├── system-live.md           ← live exploration results + limits + playbook
│   └── supabase-structure.md    ← all 4 table schemas + query patterns
│
├── intelligence/                ← live ICP data + insights (updated regularly)
│   ├── icp-truth.md             ← 🔑 Bloomin's distilled ICP truth (THE file)
│   ├── icp-profiles/            ← individual profile deep-dives per subreddit
│   │   ├── perimenopause.md
│   │   ├── deadbedrooms.md
│   │   ├── newborns.md
│   │   └── ayurveda.md
│   ├── insights-log.md          ← weekly running log of what's changing
│   └── copy-vault.md            ← confirmed verbatim phrases ready for ads
│
├── calibration/                 ← team feedback + taste filter
│   └── calibration-log.md       ← every "yes/no/that's off" from the team
│
├── strategy/                    ← plans, roadmaps, analysis
│   └── intelligence-plan.md     ← long-term learning strategy + 12-week roadmap
│
└── skills/                      ← future automation scripts + skill files
    └── (skills added here as built)
```

---

## Auto-Trigger Rule

Any question about customers, copy, psychology, pain points, desire, messaging, brand, product, or market trends automatically fires this intelligence system before generating any answer. The trigger skill defines exactly which data to pull for each question type.

**Trigger skill:** `skills/trigger-detection.md`

---

## Quick Start

**"What's our ICP feeling?"**
→ Read `intelligence/icp-truth.md` first, then call `GET /insights`

**"Give me copy language"**
→ Check `intelligence/copy-vault.md`, then `GET /insights/language`

**"Deep dive on a subreddit"**
→ Read `intelligence/icp-profiles/{subreddit}.md`, then `GET /icps/subreddit/{name}`

**"Is the system running?"**
→ `GET /health` (no auth needed)

**Credentials:** `system/credentials.md`
**Full API reference:** `system/api-reference.md`
