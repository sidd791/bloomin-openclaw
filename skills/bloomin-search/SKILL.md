---
name: bloomin-search
description: Search Bloomin's vector intelligence database (Milvus) for historical/embedded data — TikTok hooks, customer psychology, creative testing trends. NOT for live ad metrics (use Rule1 for that).
---

# Bloomin Intelligence Search

Query the Bloomin vector database (Milvus) and canonical Postgres through MCP tools. This is the intelligence system for **historical and embedded data** — TikTok content, customer psychology, and creative testing trends. For live ad platform data, use Rule1 instead.

## How to Call — MCP Tools (Direct)

Bloomin intelligence is available as MCP tools. Call them directly by name — no HTTP, no curl, no web_fetch needed.

### `bloomin_search` — Semantic vector search

| Parameter | Type | Required | Description |
|---|---|---|---|
| `query` | string | yes | Natural language search query |
| `collection` | string | no (default: `bloomin_tiktok`) | Which Milvus collection to search |
| `top_k` | integer | no (default: 10) | Number of results (1-100) |
| `record_type` | string | no | Filter for creative_testing: `ad`, `angle_summary`, `dimension_summary`, `fatiguing_ad` |
| `source_type` | string | no | Filter by source type |

### `bloomin_list_pages` — Browse canonical pages

| Parameter | Type | Required | Description |
|---|---|---|---|
| `page_type` | string | no | Filter by type |
| `status` | string | no | Filter by status |
| `limit` | integer | no (default: 20) | Max results |

### `bloomin_health` — System health check

No parameters. Returns status of Postgres, Milvus, and upstream APIs.

### `bloomin_sync` — Trigger embedding sync

| Parameter | Type | Required | Description |
|---|---|---|---|
| `source` | string | yes | `tiktok` or `creative_testing` |
| `full` | boolean | no (default: false) | Full resync vs incremental |

## Collections

| Collection | Data | Use when asking about |
|---|---|---|
| `bloomin_tiktok` | TikTok video intelligence — hooks, engagement, authors, ingredient mentions | TikTok trends, hooks, content patterns, engagement |
| `bloomin_creative_testing` | Creative testing intelligence — ad performance, angle summaries, dimension breakdowns, fatiguing ads | Ad ROAS, CTR, winning/losing angles, creative fatigue, spend, persona performance, concept codes |

## Creative Testing Record Types

| Record Type | Content |
|---|---|
| `ad` | Individual ad creatives — headline, body, angle, persona, spend, ROAS, CTR |
| `angle_summary` | Aggregated angle performance — winner/loser tags, avg ROAS, avg CTR |
| `dimension_summary` | Performance by dimension (persona, format, etc.) with ROAS delta |
| `fatiguing_ad` | Ads showing fatigue — ROAS drop %, CTR drop % over 7d vs 14d |

## When to Use This Skill

Use this skill for **embedded intelligence** — historical data already synced into the vector database:
- Customer psychology, ICP, audience understanding
- Ad copy, hooks, subject lines, UGC scripts
- Pain points, objections, desire triggers
- Brand positioning, messaging angles
- Product signals (ingredients, cortisol, hormones)
- TikTok content performance and hook patterns
- Historical creative testing performance — weekly ad ROAS/CTR trends, winning/losing angles, fatiguing ads

## When NOT to Use This Skill

Do NOT use `bloomin_search` for these — use **Rule1 MCP tools** instead (see skill `rule1-creative-intel`):
- **Live campaign/ad metrics** (current spend, ROAS, conversions) → `list_campaigns`, `list_ads`
- **Hit rate rules and benchmarks** → `get_hit_rate_rules`
- **Frame-by-frame video creative analysis** → `get_entity`
- **Competitor ad monitoring** → Rule1 tools
- **Agency or creator performance comparisons** → `list_ads` with groupBy
- **Saved reports and dashboards** → `list_reports`, `get_report`
- **Ad naming conventions / tagging rules** → `get_keyword_tag_rules`
- **Connected ad platforms and sync status** → `list_connected_accounts`

If the user asks about "current" or "live" ad data, route to Rule1. If they ask about trends, patterns, or what women are saying, use this skill.

## Search Strategy

1. **TikTok** (`bloomin_tiktok`) for hook patterns, engagement data, and content trends
2. **Creative testing** (`bloomin_creative_testing`) for ad performance, winning angles, ROAS, fatigue signals
3. **Cross-reference** results across collections for stronger insights
4. **Summarize** findings as clean prose — see SOUL.md grounding rules

## Response Format (see SOUL.md for full rules)

Write like a smart colleague — **human, conversational, actionable**. Not a formatted report. Data-backed but not drowning in numbers.

⛔ **Never show internal metadata** — no author handles, no video IDs, no record IDs, no similarity scores.

**Example response snippet (correct format):**

> Persona2 has been the consistent winner — flagged WINNER all 4 weeks with ROAS climbing from 2.15x to 2.87x. I'd shift more budget here while it's hot.

**Rules:**
- All metrics must come from the actual tool output — no invented numbers
- Weave your interpretation naturally into the response — don't bolt on rigid "Analysis:" labels unless it's truly non-obvious
- Do NOT include any data source footer — no collection names or tool names in the response
- Show top 3 items by default, not every result. Mention if more are available.

## Examples

**TikTok hooks about hormonal health:**
→ Call `bloomin_search` with `query="hormonal health cortisol stress women"`, `collection="bloomin_tiktok"`, `top_k=10`

**Winning ad angles:**
→ Call `bloomin_search` with `query="best performing angles ROAS"`, `collection="bloomin_creative_testing"`, `record_type="angle_summary"`

**Fatiguing ads:**
→ Call `bloomin_search` with `query="fatiguing ads ROAS drop"`, `collection="bloomin_creative_testing"`, `record_type="fatiguing_ad"`
