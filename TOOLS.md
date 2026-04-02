# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## Bloomin Intelligence (MCP)

Bloomin intelligence is available as MCP tools — call them directly, no HTTP needed.

**Available MCP tools:**
- `bloomin_search` — semantic vector search across all collections
- `bloomin_list_pages` — browse canonical pages from Postgres
- `bloomin_health` — check system health
- `bloomin_sync` — trigger embedding sync

### Collections in Milvus

| Collection | Content |
|---|---|
| `bloomin_tiktok` | TikTok video intelligence — hooks, engagement, authors, ingredient mentions |
| `bloomin_creative_testing` | Creative testing intelligence — ad ROAS, CTR, winning/losing angles, persona performance, fatiguing ads |

See skill `bloomin-search` for full tool docs and examples.

## Rule1 Creative Intelligence (MCP)

Rule1 is connected via MCP — no manual API calls needed. The agent calls Rule1 tools directly.
Use for: ad creative analysis, hit rate rules, competitor monitoring, creative strategy.
See skill `rule1-creative-intel` for full usage guide.

## Slack Channels

- **Reports channel:** `C0AMVG202KC` (the-bloombrain-reports) — reports, intelligence, automated messages
- **Main channel:** `C0ALRNYBJJG` (the-bloombrain) — interactive queries and conversations

## Repo Location

- Bloomin repo: `/home/rsenterprises/Desktop/bloomin`
- This workspace: `/home/rsenterprises/Desktop/bloomin/bloomin-openclaw`
