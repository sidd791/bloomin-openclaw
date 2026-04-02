# BloomBrain Config
_Agent-level preferences and settings_

## Target Markets
- USA (primary), UK (secondary), Australia, Canada
- ❌ NOT EU / Netherlands / Germany — filter these out of all research and reports

## Slack Channels
- ✅ **ALL reports go to:** `C0ALRNYBJJG`
- ✅ **Competitor reports ALSO go to:** `C0AM45T4XT8` (Usama's testing channel)
- ❌ **NEVER send to:** `C0AKYQKLA3C` — not reports, not notifications, nothing, ever

## Report Format
- Always use Slack Block Kit JSON (not plain text)
- Use: header, section, divider, context, fields blocks
- Send via Slack API directly: `POST https://slack.com/api/chat.postMessage`

## Report Delivery Schedule
- Daily 7:00am → TikTok report (`tiktok-daily-report`)
- Daily 7:30am → FB Ad Library (`fb-adlibrary-monitor`)
- Monday 6:00am → Reddit insights (`reddit-weekly-insights`)
- Monday 7:00am → Weekly Founder Briefing (`weekly-founder-briefing`)
- Tuesday 6:00am → Trustpilot reviews (`trustpilot-review-mining`)
- Wednesday 6:00am → YouTube founder intel (`youtube-founder-intel`)
- Thursday 6:00am → Offer intelligence (`offer-intelligence-monitor`)

## Reddit Intelligence System (Saad's System)
- API Base URL: see `REDDIT_INTEL_API_URL` in .env
- X-API-Key: see `REDDIT_INTEL_API_KEY` in .env
- SUPABASE_URL: see `SUPABASE_URL` in .env
- SUPABASE_ANON_KEY: see `SUPABASE_ANON_KEY` in .env

## Cron Job IDs
- tiktok-daily-report: d7f09371-ad5e-426a-9d89-02c714bb7338
- fb-adlibrary-monitor: e560cb18-f91f-4a46-90ee-37d371a69122
- reddit-weekly-insights: 43dcb391-f0b2-4e54-b639-e5d42f19ca23
- weekly-founder-briefing: d8f88dd4-544a-48fe-a361-614f30743478
- trustpilot-review-mining: 7db767c1-2a7e-40f8-8479-6d419462017a
- youtube-founder-intel: 7085d16a-cf14-455a-acd3-3bb68cbcbf3b
- offer-intelligence-monitor: b161f3d8-53f5-4ff7-a261-fd181b0c2c9a
