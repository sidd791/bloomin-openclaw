#!/usr/bin/env python3
"""
BloomBrain — TikTok Intelligence Scraper
Uses Apify API (clockworks~tiktok-scraper) to pull videos from niche hashtags.
Filters for Bloomin-relevant content, stores in DB, posts report to Slack.
Runs daily at 07:00 AM GMT+1.
"""

import json, urllib.request, time, subprocess, os, re
from datetime import date, datetime
from collections import Counter

# ── CONFIG ───────────────────────────────────────────────────────────────────
APIFY_TOKEN = os.environ["APIFY_TOKEN"]
SLACK_TOKEN = os.environ["SLACK_TOKEN"]
CHANNELS = ["C0AM45T4XT8"]
DB_NAME = "bloomin"
PSQL = "/opt/homebrew/opt/postgresql@16/bin/psql"
MEMORY_FILE = "/Users/teambloomin/.openclaw/workspace/memory/tiktok-insights.md"

# ── DB HELPERS ───────────────────────────────────────────────────────────────
env = os.environ.copy()
env["PATH"] = f"/opt/homebrew/opt/postgresql@16/bin:{env.get('PATH','')}"

def db_exec(sql):
    subprocess.run([PSQL, "-d", DB_NAME, "-c", sql], capture_output=True, env=env)

def db_query(sql):
    r = subprocess.run([PSQL, "-d", DB_NAME, "-t", "-A", "-F", "\t", "-c", sql],
                       capture_output=True, text=True, env=env)
    if not r.stdout.strip():
        return []
    return [line.split('\t') for line in r.stdout.strip().split('\n') if line]

# ── SLACK HELPERS ─────────────────────────────────────────────────────────────
def slack_post(blocks, text="BloomBrain"):
    for ch in CHANNELS:
        payload = json.dumps({"channel": ch, "text": text, "blocks": blocks}).encode()
        req = urllib.request.Request(
            "https://slack.com/api/chat.postMessage", data=payload,
            headers={"Authorization": f"Bearer {SLACK_TOKEN}", "Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as r:
            pass
        time.sleep(0.3)

# ── APIFY HELPER ─────────────────────────────────────────────────────────────
def apify_run(actor_id, input_data, timeout_secs=300):
    """Run Apify actor and return dataset items list"""
    url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_TOKEN}"
    payload = json.dumps(input_data).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        run = json.loads(r.read())
    run_id = run["data"]["id"]
    dataset_id = run["data"]["defaultDatasetId"]
    print(f"  Apify run started: {run_id}")

    deadline = time.time() + timeout_secs
    status = "RUNNING"
    while time.time() < deadline:
        time.sleep(10)
        status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}"
        with urllib.request.urlopen(status_url) as r:
            status = json.loads(r.read())["data"]["status"]
        print(f"  Status: {status}")
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            break

    if status != "SUCCEEDED":
        print(f"  Apify run {status}")
        return []

    items = []
    offset = 0
    limit = 200
    while True:
        items_url = (f"https://api.apify.com/v2/datasets/{dataset_id}/items"
                     f"?token={APIFY_TOKEN}&offset={offset}&limit={limit}")
        with urllib.request.urlopen(items_url) as r:
            batch = json.loads(r.read())
        if not batch:
            break
        items.extend(batch)
        if len(batch) < limit:
            break
        offset += limit

    print(f"  Fetched {len(items)} items from dataset")
    return items

# ── HASHTAGS ─────────────────────────────────────────────────────────────────
HASHTAGS = [
    "hormonehealth", "lowlibido", "womenshealth", "cortisol", "shatavari",
    "womenover40", "perimenopause", "hormonalimbalance", "libidohealth",
    "adaptogens", "shilajit", "saffron", "supplementsforwomen",
    "womenshormones", "cortisolfatigue", "honeystick", "desirerestored", "stressrelief"
]

# ── BLOOMIN RELEVANCE ─────────────────────────────────────────────────────────
BLOOMIN_KEYWORDS = [
    "cortisol", "libido", "desire", "estrogen", "progesterone", "perimenopause", "menopause",
    "hormone", "shilajit", "shatavari", "saffron", "ashwagandha", "maca", "low libido",
    "sex drive", "intimacy", "supplement", "adaptogen", "stress", "burnout",
    "honey stick", "honeystick", "women wellness", "female health"
]

INGREDIENTS = ["shilajit", "shatavari", "saffron", "ashwagandha", "maca", "cortisol", "adaptogens"]

# ── HOOK PATTERN DETECTION ────────────────────────────────────────────────────
def detect_hook_pattern(text):
    t = (text or "").lower()
    if any(w in t for w in ["?", "why ", "do you ", "have you ", "are you ", "is your "]):
        return "question"
    if any(w in t for w in ["struggling", "tired of", "sick of", "stop ", "suffering", "can't", "cannot"]):
        return "pain_agitate"
    if any(w in t for w in ["i went from", "changed my", "restored", "got my back", "came back", "finally"]):
        return "transformation"
    if any(w in t for w in ["%", "million", "studies", "research", "clinical", "proven", "found that"]):
        return "stat"
    if any(w in t for w in ["my doctor", "thousands", "reviews", "worked for me", "changed my life"]):
        return "social_proof"
    return "other"

# ── PROCESS VIDEO ITEM ────────────────────────────────────────────────────────
def process_video(item):
    """Extract and classify a single Apify TikTok item."""
    raw_text = item.get("text") or ""

    # Hook: first non-empty line, max 200 chars
    lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
    hook = lines[0][:200] if lines else ""

    caption = raw_text[:500]
    caption_lower = caption.lower()

    # Match hashtag
    item_hashtags = [h.get("name", "").lower() for h in (item.get("hashtags") or [])]
    hashtag = next((h for h in HASHTAGS if h.lower() in item_hashtags), "unknown")

    # Bloomin relevance
    bloomin_relevant = any(kw in caption_lower for kw in BLOOMIN_KEYWORDS)

    # Counts
    play_count = item.get("playCount") or 0
    like_count = item.get("diggCount") or 0
    comment_count = item.get("commentCount") or 0
    share_count = item.get("shareCount") or 0
    engagement_rate = round((like_count + comment_count + share_count) / max(play_count, 1), 4)

    # Ingredient mentions
    ingredient_mentions = [ing for ing in INGREDIENTS if ing in caption_lower]

    # Author
    author_meta = item.get("authorMeta") or {}
    author = author_meta.get("name") or ""

    video_url = item.get("webVideoUrl") or ""
    hook_pattern = detect_hook_pattern(hook)

    return {
        "hashtag": hashtag,
        "hook": hook,
        "caption": caption,
        "view_count": play_count,
        "like_count": like_count,
        "comment_count": comment_count,
        "share_count": share_count,
        "engagement_rate": engagement_rate,
        "author": author[:255],
        "video_url": video_url[:500],
        "ingredient_mentions": ingredient_mentions,
        "hook_pattern": hook_pattern,
        "bloomin_relevant": bloomin_relevant,
    }

# ── DB INSERT ─────────────────────────────────────────────────────────────────
def insert_video(v):
    ing_arr = "{" + ",".join(v["ingredient_mentions"]) + "}"
    hook_esc = v["hook"].replace("$", "\\$")
    caption_esc = v["caption"].replace("$", "\\$")
    author_esc = v["author"].replace("$", "\\$")
    video_url_esc = v["video_url"].replace("$", "\\$")

    sql = f"""
        INSERT INTO tiktok_videos (
            hashtag, hook, caption, view_count, like_count, comment_count, share_count,
            engagement_rate, author, video_url, ingredient_mentions, hook_pattern,
            bloomin_relevant, run_date
        ) VALUES (
            $tag${v['hashtag']}$tag$,
            $hook${hook_esc}$hook$,
            $cap${caption_esc}$cap$,
            {v['view_count']}, {v['like_count']}, {v['comment_count']}, {v['share_count']},
            {v['engagement_rate']},
            $auth${author_esc}$auth$,
            $vurl${video_url_esc}$vurl$,
            '{ing_arr}'::text[],
            '{v['hook_pattern']}',
            {str(v['bloomin_relevant']).lower()},
            CURRENT_DATE
        ) ON CONFLICT DO NOTHING
    """
    db_exec(sql)

# ── SLACK REPORT ──────────────────────────────────────────────────────────────
def post_slack_report(today_str, total_raw, total_relevant, relevant_videos):
    from collections import Counter

    # 1. Header
    slack_post([
        {"type": "header", "text": {"type": "plain_text", "text": "📱 TikTok Intelligence Report", "emoji": True}},
        {"type": "context", "elements": [{"type": "mrkdwn",
            "text": f"📅 {today_str}  |  #️⃣ {len(HASHTAGS)} hashtags  |  🎬 {total_raw} videos scraped  |  🌸 {total_relevant} Bloomin-relevant stored"}]},
        {"type": "divider"},
    ])
    time.sleep(0.5)

    # 2. Top 8 videos by views
    top8 = sorted(relevant_videos, key=lambda x: x["view_count"], reverse=True)[:8]
    lines = "\n".join([
        f"• *{v['view_count']:,} views*  ·  [{v['hook_pattern']}]  ·  _{v['hook'][:100]}_"
        for v in top8
    ]) if top8 else "• _No relevant videos this run_"
    slack_post([
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*🔥 Top 8 Hooks by Views*\n\n{lines}"}},
        {"type": "divider"},
    ])
    time.sleep(0.5)

    # 3. Hook pattern breakdown
    pattern_counts = Counter(v["hook_pattern"] for v in relevant_videos)
    pattern_lines = "\n".join([f"• *{p}*  —  {c} videos" for p, c in pattern_counts.most_common()])
    if not pattern_lines:
        pattern_lines = "• _No data_"
    slack_post([
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*🎣 Hook Pattern Breakdown*\n\n{pattern_lines}"}},
        {"type": "divider"},
    ])
    time.sleep(0.5)

    # 4. Ingredient mentions
    ing_counts = Counter(ing for v in relevant_videos for ing in v["ingredient_mentions"])
    ing_lines = "\n".join([f"• *{i}*  —  {c} mentions" for i, c in ing_counts.most_common()]) if ing_counts else "• _None detected_"
    slack_post([
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*🌿 Ingredient Mentions*\n\n{ing_lines}"}},
        {"type": "divider"},
    ])
    time.sleep(0.5)

    # 5. Footer
    slack_post([
        {"type": "context", "elements": [
            {"type": "mrkdwn", "text": f"🌸 *BloomBrain* · {today_str} · TikTok via Apify · Next run: tomorrow 07:00 AM GMT+1"}
        ]},
    ])

# ── MEMORY FILE ───────────────────────────────────────────────────────────────
def update_memory(today_str, total_raw, total_relevant, relevant_videos):
    pattern_counts = Counter(v["hook_pattern"] for v in relevant_videos)
    ing_counts = Counter(ing for v in relevant_videos for ing in v["ingredient_mentions"])
    top_patterns = ", ".join([f"{p} ({c})" for p, c in pattern_counts.most_common(3)]) or "none"
    top_ings = ", ".join([f"{i} ({c})" for i, c in ing_counts.most_common(3)]) or "none"
    highest_views = max((v["view_count"] for v in relevant_videos), default=0)

    entry = f"""
## {today_str}
- Hashtags: {len(HASHTAGS)} scraped
- Total: {total_raw} scraped, {total_relevant} stored
- Top patterns: {top_patterns}
- Top ingredients: {top_ings}
- Highest views: {highest_views:,}
"""
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "a") as f:
        f.write(entry)

# ── MAIN ──────────────────────────────────────────────────────────────────────
def run():
    print("🌸 BloomBrain TikTok Scraper starting...")
    today_str = date.today().strftime("%Y-%m-%d")

    # Run Apify actor
    print(f"  Launching Apify actor for {len(HASHTAGS)} hashtags...")
    items = apify_run(
        "clockworks~tiktok-scraper",
        {
            "hashtags": HASHTAGS,
            "resultsPerPage": 100,
            "shouldDownloadVideos": False,
            "shouldDownloadCovers": False,
        },
        timeout_secs=600,
    )

    total_raw = len(items)
    print(f"  Raw items: {total_raw}")

    # Process + filter
    relevant_videos = []
    for item in items:
        try:
            v = process_video(item)
            if v["bloomin_relevant"]:
                insert_video(v)
                relevant_videos.append(v)
        except Exception as e:
            print(f"  Error processing video: {e}")
            continue

    total_relevant = len(relevant_videos)
    print(f"  Bloomin-relevant stored: {total_relevant}")

    # Record scrape run
    db_exec(f"""
        INSERT INTO scrape_runs (pipeline, status, records_scraped, completed_at)
        VALUES ('tiktok_intelligence', 'completed', {total_relevant}, now())
    """)

    # Post Slack report
    print("  Posting to Slack...")
    post_slack_report(today_str, total_raw, total_relevant, relevant_videos)

    # Update memory
    update_memory(today_str, total_raw, total_relevant, relevant_videos)

    print(f"✅ TikTok scraper done. {total_raw} raw → {total_relevant} stored.")

if __name__ == "__main__":
    run()
