# Reddit Intelligence System — Credentials
_Saved 2026-03-21. From Saad._

## API
- **Base URL:** set in environment variable `REDDIT_INTEL_API_URL`
- **X-API-Key:** set in environment variable `REDDIT_INTEL_API_KEY`

## Supabase
- **URL:** set in environment variable `SUPABASE_URL`
- **Anon Key:** set in environment variable `SUPABASE_ANON_KEY`

## Primary Tables (query these directly via Supabase)
1. **`filtered_posts`** — posts that passed minimum relevance verification
2. **`reddit_posts`** — all posts analyzed by Claude, full details (primary raw source)
3. **`icp_profiles`** — MOST IMPORTANT — ICP profiles built after analyzing batches of posts (~every 200 posts)
