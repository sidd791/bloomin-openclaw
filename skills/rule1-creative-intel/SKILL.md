---
name: rule1-creative-intel
description: Query Rule1's marketing creative intelligence platform via MCP for live ad metrics, hit rate rules, creative analysis, competitor monitoring, and reports. Use for any question about current ad performance, campaigns, or platform data.
---

# Rule1 Creative Intelligence

Rule1 is an AI-powered marketing platform that analyzes ad creative performance with frame-by-frame video analysis. It is available as an MCP server — call Rule1 tools directly by name.

**Platforms supported:** Meta (Facebook/Instagram), TikTok, Pinterest

## When to Use This Skill (Rule1 is the PRIMARY source)

Use Rule1 for **live ad platform data** — anything about current campaigns, real-time metrics, or platform features:
- Live campaign, ad set, or ad metrics (current spend, ROAS, conversions)
- Hit rate rules and benchmarks
- Frame-by-frame video creative analysis
- Competitor ad monitoring
- Agency or creator performance comparisons
- Named reports and AI creative analysis
- Ad naming conventions and tagging rules
- Connected ad platforms and sync status

## When NOT to Use This Skill

Do NOT use Rule1 for these — use Bloomin (`bloomin_search`) instead:
- TikTok organic content, hooks, engagement patterns → `bloomin_tiktok`
- Customer psychology, ICP, pain points → `bloomin_tiktok`
- Historical ad angle/persona ROAS trends over weeks → `bloomin_creative_testing`
- Fatiguing ad analysis (ROAS/CTR drop trends) → `bloomin_creative_testing`

## Available MCP Tools

### Setup (MUST call first)

| Tool | Purpose |
|---|---|
| `list_my_organizations` | Get your org ID. **Call this FIRST before any other Rule1 tool.** Cache the org ID for the session. |
| `list_connected_accounts` | Show connected ad platforms (Meta, TikTok, Pinterest) and sync status |

### Campaign & Ad Data

| Tool | Purpose | Key parameters |
|---|---|---|
| `list_campaigns` | List campaigns with spend, ROAS, conversions | Filter by platform, status, date |
| `list_ad_sets` | List ad sets (Meta) / ad groups (TikTok/Pinterest) with metrics | Filter by campaign, status, date |
| `list_ads` | Full ad dashboard — status, format, tags, metrics, hit rate | Filter by status, format, tags, metrics, date; supports `groupBy` |
| `search_entities` | Search campaigns, ad sets, and ads by name across platforms | Search by name string |
| `get_entity` | Deep dive on a specific campaign, ad set, or ad — full creative analysis + AI tags | Entity ID |

### Rules & Configuration

| Tool | Purpose |
|---|---|
| `get_hit_rate_rules` | See what thresholds define a "hit" ad (min spend, ROAS, conversions, days) |
| `get_keyword_tag_rules` | See how ads are auto-categorized by naming conventions (regex patterns) |

### Reports

| Tool | Purpose |
|---|---|
| `list_reports` | List saved user reports + AI-generated creative analysis reports |
| `get_report` | Get full report details — AI analysis, top/weak ads, tag performance |
| `get_report_links` | Get dashboard + public share URLs for a report |
| `set_report_sharing` | Enable/disable public sharing on a report |

## Calling Sequence

1. Call `list_my_organizations` to get the org ID (do this once per session)
2. Use the org ID in all subsequent Rule1 tool calls
3. Call the relevant tool based on the query

## Cross-Referencing with Bloomin Intelligence

Rule1 covers **live ad performance** — what's running now and how it performs.
Bloomin covers **historical trends and audience intelligence** — what worked over time and what the audience says.

When to use BOTH (see SOUL.md routing table):
1. **"What angles should we test next?"** → Rule1 for live hit rates + Bloomin for historical angle trends
2. **"How do TikTok hooks match our ads?"** → Bloomin for organic hooks + Rule1 for ad performance
3. **"Compare current vs historical ROAS"** → Rule1 for live + Bloomin for weekly snapshots

## Examples

**"What are our current hit rate rules?"**
→ `list_my_organizations` → `get_hit_rate_rules`

**"Show me our best-performing ads right now"**
→ `list_my_organizations` → `list_ads` (filter by status=active, sort by ROAS)

**"How are our agencies performing?"**
→ `list_my_organizations` → `list_ads` with groupBy for agency breakdown

**"Analyze this specific ad creative"**
→ `list_my_organizations` → `get_entity` with the ad ID

**"What reports do we have?"**
→ `list_my_organizations` → `list_reports`

**"What's our current campaign spend and ROAS?"**
→ `list_my_organizations` → `list_campaigns`
