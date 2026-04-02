#!/usr/bin/env python3
"""
BloomBrain — YouTube Intelligence Scraper
Uses yt-dlp for both search AND transcript download (no Apify needed).
Weekly run: scrapes D2C supplement founder content + ingredient/niche signals.
Posts structured report to Slack, updates memory file.
"""

import json, urllib.request, time, subprocess, os, re, hashlib, shlex
from datetime import date, datetime
from collections import Counter

# ── CONFIG ───────────────────────────────────────────────────────────────────
APIFY_TOKEN = os.environ["APIFY_TOKEN"]
SLACK_TOKEN = os.environ["SLACK_TOKEN"]
CHANNELS = ["C0AM45T4XT8"]
DB_NAME = "bloomin"
PSQL = "/opt/homebrew/opt/postgresql@16/bin/psql"
MEMORY_FILE = "/Users/teambloomin/.openclaw/workspace/memory/youtube-intel.md"

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

# ── YTDLP SEARCH ─────────────────────────────────────────────────────────────
YTDLP = "/opt/homebrew/bin/yt-dlp"

def search_youtube(query, max_results=20):
    """Search YouTube via yt-dlp and return list of video dicts."""
    results = []
    try:
        r = subprocess.run(
            [YTDLP, f"ytsearch{max_results}:{query}",
             "--print", "%(id)s\t%(title)s\t%(channel)s\t%(webpage_url)s\t%(view_count)s\t%(description)s",
             "--skip-download", "--no-warnings", "--flat-playlist"],
            capture_output=True, text=True, timeout=60
        )
        for line in r.stdout.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            vid_id, title, channel, url = parts[0], parts[1], parts[2], parts[3]
            view_count = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
            description = parts[5] if len(parts) > 5 else ""
            results.append({
                "id": vid_id,
                "title": title,
                "channel": channel,
                "url": url,
                "view_count": view_count,
                "description": description[:500],
                "searchQuery": query,
            })
    except Exception as e:
        print(f"  yt-dlp search failed for '{query}': {e}")
    return results

# ── SEARCH QUERIES ────────────────────────────────────────────────────────────
SEARCH_QUERIES = [
    "women supplement brand founder story",
    "D2C supplement brand scaling",
    "supplement brand from zero to revenue",
    "women wellness brand ecommerce growth",
    "supplement subscription brand strategy",
    "DTC health brand founder interview",
    "women health brand marketing strategy",
    "supplement brand facebook ads strategy",
    "cortisol women libido connection",
    "shilajit women benefits",
    "shatavari women hormones",
    "saffron mood libido women",
    "low libido women hormones fix",
    "perimenopause libido restore",
    "women stress hormones desire",
    "cortisol blocker women supplement",
    "survival mode women hormones",
    "hormonal imbalance women supplement",
    "women adaptogen supplement review",
    "honey stick supplement women review",
    "HerSolution review",
    "Elix supplement review",
    "women libido supplement review",
    "Bonafide Ristela review",
    "S'moo supplement review",
]

SKIP_TITLE_WORDS = ["men's", "for men", "male", "erectile", "testosterone men", "retail", "brick and mortar"]

# ── TRANSCRIPT DOWNLOADER ─────────────────────────────────────────────────────
def get_transcript(video_url):
    """Download auto-subtitles via yt-dlp and return cleaned text."""
    vid_hash = hashlib.md5(video_url.encode()).hexdigest()[:8]
    out_template = f"/tmp/yt-bloom-{vid_hash}"
    try:
        subprocess.run(
            ["yt-dlp", "--write-auto-sub", "--skip-download", "--sub-format", "vtt",
             "--sub-lang", "en", "-o", out_template, video_url],
            capture_output=True, text=True, timeout=60
        )
        vtt_file = f"{out_template}.en.vtt"
        if not os.path.exists(vtt_file):
            for f in os.listdir("/tmp"):
                if f.startswith(f"yt-bloom-{vid_hash}") and f.endswith(".vtt"):
                    vtt_file = f"/tmp/{f}"
                    break
        if os.path.exists(vtt_file):
            with open(vtt_file) as f:
                raw = f.read()
            clean = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}[^\n]*\n', '', raw)
            clean = re.sub(r'^WEBVTT.*$', '', clean, flags=re.MULTILINE)
            clean = re.sub(r'<[^>]+>', '', clean)
            clean = re.sub(r'\n{3,}', '\n\n', clean).strip()
            os.remove(vtt_file)
            return clean[:8000]
    except Exception as e:
        print(f"  yt-dlp failed: {e}")
    return None

# ── VIDEO ANALYSIS ────────────────────────────────────────────────────────────
def analyze_video(title, description, transcript):
    """Return (takeaways, relevance, summary)."""
    content = f"{title}\n{description or ''}\n{transcript or ''}"
    cl = content.lower()

    takeaways = []

    # Revenue/scale signals
    if re.search(r'\$[\d,]+[km]?', cl):
        takeaways.append("Revenue/scale metric mentioned")
    if re.search(r'(scaled|grew from|revenue of)', cl):
        takeaways.append("Scaling story")
    if re.search(r'(facebook|meta|tiktok)\s*(ads|creative|strategy)', cl):
        takeaways.append("Paid ads strategy")
    if re.search(r'(subscription|ltv|retention|churn)', cl):
        takeaways.append("Subscription/retention insight")
    if re.search(r'(guarantee|money.?back|bundle|offer)', cl):
        takeaways.append("Offer structure insight")
    if re.search(r'(hook|creative|scroll.?stop|ad copy)', cl):
        takeaways.append("Creative strategy insight")

    # Ingredient signals
    for ing in ["shilajit", "shatavari", "saffron", "ashwagandha", "maca", "cortisol", "adaptogen"]:
        if ing in cl:
            takeaways.append(f"Mentions {ing}")

    if not takeaways:
        takeaways = ["General supplement/wellness content"]

    # Bloomin relevance score
    score = sum([
        "cortisol" in cl,
        any(w in cl for w in ["libido", "desire", "sex drive"]),
        any(i in cl for i in ["shilajit", "shatavari", "saffron"]),
        any(w in cl for w in ["women", "female", "hormonal"]),
        any(w in cl for w in ["d2c", "dtc", "supplement brand", "ecommerce"]),
        "subscription" in cl,
        any(w in cl for w in ["facebook ads", "meta ads", "tiktok ads"]),
        re.search(r'\$[\d,]+[km]?', cl) is not None,
    ])
    relevance = "High" if score >= 4 else ("Medium" if score >= 2 else "Low")
    summary = (transcript or description or title)[:500]
    return takeaways[:8], relevance, summary

# ── DB INSERT ─────────────────────────────────────────────────────────────────
def insert_video(video_url, title, channel, query, summary, takeaways, relevance, has_transcript, week_of):
    """Insert a youtube video record, escaping text fields safely."""
    def esc(s):
        return (s or "").replace("'", "''")

    # Build ARRAY literal with individual dollar-quoted elements using index-unique tags
    array_parts = []
    for i, t in enumerate(takeaways):
        tag = f"$tk{i}$"
        array_parts.append(f"{tag}{t}{tag}")
    takeaway_arr = ", ".join(array_parts)

    sql = f"""
        INSERT INTO youtube_videos (video_url, title, channel, search_query, transcript_summary, key_takeaways, bloomin_relevance, has_transcript, week_of)
        VALUES (
            '{esc(video_url[:500])}',
            '{esc(title[:500])}',
            '{esc(channel[:255])}',
            '{esc(query[:255])}',
            '{esc(summary[:1000])}',
            ARRAY[{takeaway_arr}],
            '{esc(relevance)}',
            {str(has_transcript).lower()},
            '{week_of}'
        ) ON CONFLICT DO NOTHING
    """
    db_exec(sql)

# ── SLACK REPORT ──────────────────────────────────────────────────────────────
def post_slack_report(today_str, week_of, total_scraped, total_stored, videos):
    from collections import Counter

    high = [v for v in videos if v["relevance"] == "High"]
    medium = [v for v in videos if v["relevance"] == "Medium"]
    low_count = len(videos) - len(high) - len(medium)
    with_transcript = sum(1 for v in videos if v["has_transcript"])

    # 1. Header
    slack_post([
        {"type": "header", "text": {"type": "plain_text", "text": f"🎬 YouTube Founder Intelligence", "emoji": True}},
        {"type": "context", "elements": [{"type": "mrkdwn",
            "text": f"📅 {today_str}  |  🔍 {len(SEARCH_QUERIES)} queries  |  🎬 {total_scraped} scraped  |  💾 {total_stored} stored  ·  🔴 {len(high)} high  ·  🟡 {len(medium)} medium  ·  ⚪ {low_count} low"}]},
        {"type": "divider"},
    ])
    time.sleep(0.5)

    # 2. Top 5 high-relevance videos
    top5 = sorted(high, key=lambda x: x.get("view_count", 0), reverse=True)[:5]
    if not top5:
        top5 = sorted(videos, key=lambda x: x.get("view_count", 0), reverse=True)[:5]

    for v in top5:
        url = v.get("url", "")
        title = v["title"][:80]
        linked = f"<{url}|{title}>" if url else title
        bullets = "\n".join([f"  • {t}" for t in v["takeaways"][:3]])
        transcript_flag = "📝 transcript" if v.get("has_transcript") else "no transcript"
        slack_post([
            {"type": "section", "text": {"type": "mrkdwn",
                "text": f"*🎥 {linked}*\n_{v.get('channel', '')}_ · *{v['relevance']}* relevance · {transcript_flag}\n{bullets}"}},
            {"type": "divider"},
        ])
        time.sleep(0.3)

    # 3. Signals summary
    all_takeaways = [t for v in videos for t in v["takeaways"]]
    takeaway_counts = Counter(all_takeaways).most_common(10)
    ing_signals = [(t, c) for t, c in takeaway_counts if "Mentions" in t]
    strat_signals = [(t, c) for t, c in takeaway_counts if "Mentions" not in t]

    ing_lines = "\n".join([f"• *{t.replace('Mentions ', '')}*  —  {c}x" for t, c in ing_signals]) or "• _None detected_"
    strat_lines = "\n".join([f"• *{t}*  —  {c}x" for t, c in strat_signals[:5]]) or "• _None detected_"

    slack_post([
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*🌿 Ingredient Signals*\n\n{ing_lines}"}},
        {"type": "divider"},
    ])
    time.sleep(0.5)
    slack_post([
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*📈 Strategy Signals*\n\n{strat_lines}"}},
        {"type": "divider"},
    ])
    time.sleep(0.5)

    # 4. Footer
    slack_post([
        {"type": "context", "elements": [
            {"type": "mrkdwn", "text": f"🌸 *BloomBrain* · {today_str} · YouTube via yt-dlp · Next run: next week"}
        ]},
    ])

# ── MEMORY FILE ───────────────────────────────────────────────────────────────
def update_memory(today_str, week_of, total_scraped, total_stored, videos):
    high_count = sum(1 for v in videos if v["relevance"] == "High")
    medium_count = sum(1 for v in videos if v["relevance"] == "Medium")
    with_transcript = sum(1 for v in videos if v["has_transcript"])

    all_takeaways = [t for v in videos for t in v["takeaways"]]
    top_signals = ", ".join([f"{t} ({c})" for t, c in Counter(all_takeaways).most_common(3)]) or "none"

    entry = f"""
## {today_str} (Week of {week_of})
- Queries: {len(SEARCH_QUERIES)} run
- Total: {total_scraped} scraped, {total_stored} stored
- Relevance: {high_count} high · {medium_count} medium
- Transcripts: {with_transcript} downloaded
- Top signals: {top_signals}
"""
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "a") as f:
        f.write(entry)

# ── MAIN ──────────────────────────────────────────────────────────────────────
def run():
    print("🌸 BloomBrain YouTube Intel starting...")
    today_str = date.today().strftime("%Y-%m-%d")
    week_of = date.today().strftime("%Y-%m-%d")

    # Search YouTube via yt-dlp for all queries
    print(f"  Searching YouTube for {len(SEARCH_QUERIES)} queries (20 results each)...")
    all_items = []
    seen_ids = set()
    for query in SEARCH_QUERIES:
        print(f"  → {query}")
        results = search_youtube(query, max_results=20)
        for r in results:
            if r["id"] not in seen_ids:
                seen_ids.add(r["id"])
                all_items.append(r)
        time.sleep(1)  # be polite

    total_scraped = len(all_items)
    print(f"  Raw unique videos: {total_scraped}")

    processed_videos = []
    total_stored = 0

    for item in all_items:
        try:
            title = item.get("title", "").strip()
            video_url = item.get("url", "").strip()
            channel = item.get("channel", "").strip()
            description = item.get("description", "").strip()
            view_count = item.get("view_count", 0)
            query = item.get("searchQuery", "").strip()

            if not title or not video_url:
                continue

            # Filter irrelevant titles
            if any(skip in title.lower() for skip in SKIP_TITLE_WORDS):
                print(f"  Skipping: {title[:60]}")
                continue

            # Attempt transcript
            print(f"  Processing: {title[:60]}")
            transcript = get_transcript(video_url)
            has_transcript = transcript is not None

            # Analyse
            takeaways, relevance, summary = analyze_video(title, description, transcript)

            # Store in DB
            insert_video(video_url, title, channel, query, summary, takeaways, relevance, has_transcript, week_of)
            total_stored += 1

            processed_videos.append({
                "url": video_url,
                "title": title,
                "channel": channel,
                "takeaways": takeaways,
                "relevance": relevance,
                "has_transcript": has_transcript,
                "view_count": view_count,
                "summary": summary,
            })

        except Exception as e:
            print(f"  Error processing video: {e}")
            continue

    print(f"  Stored: {total_stored} videos")

    # Record scrape run
    db_exec(f"""
        INSERT INTO scrape_runs (pipeline, status, records_scraped, completed_at)
        VALUES ('youtube_founder_intel', 'completed', {total_stored}, now())
    """)

    # Post Slack report
    print("  Posting to Slack...")
    post_slack_report(today_str, week_of, total_scraped, total_stored, processed_videos)

    # Update memory
    update_memory(today_str, week_of, total_scraped, total_stored, processed_videos)

    print(f"✅ YouTube Intel done. {total_scraped} raw → {total_stored} stored.")

if __name__ == "__main__":
    run()
