#!/usr/bin/env python3
"""
BloomBrain Competitor Review Scraper
- Fetches competitors from Postgres
- Seeds known Trustpilot URLs
- Scrapes all star ratings from Trustpilot with pagination
- Stores reviews in Postgres (all sentiments)
- Generates PDF report
- Posts to Slack with sentiment breakdown
"""

import urllib.request, urllib.parse, json, time, subprocess, os, sys, re
from datetime import datetime, date

# ── CONFIG ──────────────────────────────────────────────────────────────────
DB_NAME = "bloomin"
PSQL = "/opt/homebrew/opt/postgresql@16/bin/psql"
SLACK_TOKEN = os.environ["SLACK_TOKEN"]
SLACK_CHANNELS = ["C0AM45T4XT8"]
REPORT_DIR = "/Users/teambloomin/.openclaw/workspace/reports"
os.makedirs(REPORT_DIR, exist_ok=True)

# ── DB HELPERS ───────────────────────────────────────────────────────────────
def db_query(sql, fetch=True):
    env = os.environ.copy()
    env["PATH"] = f"/opt/homebrew/opt/postgresql@16/bin:{env.get('PATH','')}"
    result = subprocess.run(
        [PSQL, "-d", DB_NAME, "-t", "-A", "-F", "\t", "-c", sql],
        capture_output=True, text=True, env=env
    )
    if result.returncode != 0:
        print(f"DB Error: {result.stderr}")
        return []
    if not fetch or not result.stdout.strip():
        return []
    rows = []
    for line in result.stdout.strip().split('\n'):
        if line:
            rows.append(line.split('\t'))
    return rows

def db_exec(sql):
    env = os.environ.copy()
    env["PATH"] = f"/opt/homebrew/opt/postgresql@16/bin:{env.get('PATH','')}"
    subprocess.run([PSQL, "-d", DB_NAME, "-c", sql], capture_output=True, env=env)

# ── SLACK ────────────────────────────────────────────────────────────────────
def slack_post(blocks, text=""):
    for SLACK_CHANNEL in SLACK_CHANNELS:
        _slack_post_single(SLACK_CHANNEL, blocks, text)

def _slack_post_single(SLACK_CHANNEL, blocks, text=""):
    payload = json.dumps({"channel": SLACK_CHANNEL, "text": text or "BloomBrain", "blocks": blocks}).encode()
    req = urllib.request.Request(
        "https://slack.com/api/chat.postMessage", data=payload,
        headers={"Authorization": f"Bearer {SLACK_TOKEN}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as r:
        resp = json.loads(r.read())
    return resp.get("ok"), resp.get("ts")

def slack_upload_file(filepath, filename, title, channel):
    """Upload file to Slack using multipart form upload"""
    with open(filepath, "rb") as f:
        file_data = f.read()

    boundary = "----BloomBrainBoundary"
    body = f"--{boundary}\r\n"
    body += f'Content-Disposition: form-data; name="channels"\r\n\r\n{channel}\r\n'
    body += f"--{boundary}\r\n"
    body += f'Content-Disposition: form-data; name="filename"\r\n\r\n{filename}\r\n'
    body += f"--{boundary}\r\n"
    body += f'Content-Disposition: form-data; name="title"\r\n\r\n{title}\r\n'
    body += f"--{boundary}\r\n"
    body += f'Content-Disposition: form-data; name="filetype"\r\n\r\n'
    if filename.endswith('.pdf'):
        body += "pdf\r\n"
    else:
        body += "html\r\n"
    body += f"--{boundary}\r\n"
    body += f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
    body += "Content-Type: application/octet-stream\r\n\r\n"

    body_bytes = body.encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        "https://slack.com/api/files.upload",
        data=body_bytes,
        headers={
            "Authorization": f"Bearer {SLACK_TOKEN}",
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        }
    )
    try:
        with urllib.request.urlopen(req) as r:
            resp = json.loads(r.read())
        if resp.get("ok"):
            return resp.get("file", {}).get("permalink")
        else:
            print(f"  Upload error: {resp.get('error')}")
            return None
    except Exception as e:
        print(f"  Upload exception: {e}")
        return None

# ── SCRAPER ──────────────────────────────────────────────────────────────────
def scrape_trustpilot_reviews(trustpilot_url, competitor_id):
    """Scrape all star ratings from Trustpilot with pagination"""
    if not trustpilot_url:
        return []
    reviews = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
    }
    for star in [1, 2, 3, 4, 5]:
        page = 1
        while page <= 20:  # safety cap
            if page == 1:
                url = f"{trustpilot_url}?stars={star}&sort=recency"
            else:
                url = f"{trustpilot_url}?stars={star}&sort=recency&page={page}"
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=15) as r:
                    html = r.read().decode('utf-8', errors='ignore')
                review_matches = re.findall(r'"text":"([^"]{20,1000})"', html)
                date_matches = re.findall(r'"publishedDate":"([^"]+)"', html)
                author_matches = re.findall(r'"displayName":"([^"]+)"', html)
                if not review_matches:
                    break
                sentiment = 'negative' if star <= 2 else ('neutral' if star == 3 else 'positive')
                for i, text in enumerate(review_matches):
                    if len(text) > 30:
                        review_date = date_matches[i][:10] if i < len(date_matches) else str(date.today())
                        author = author_matches[i] if i < len(author_matches) else "Anonymous"
                        reviews.append({
                            'competitor_id': competitor_id,
                            'platform': 'trustpilot',
                            'rating': star,
                            'review_text': text.replace("'", "''"),
                            'review_date': review_date,
                            'author': author.replace("'", "''"),
                            'verified': False,
                            'sentiment': sentiment,
                        })
                page += 1
                time.sleep(0.8)
            except Exception as e:
                print(f"  Error scraping {url}: {e}")
                break
    return reviews

def analyze_pain_points(review_text):
    """Tag reviews with pain point categories"""
    text = review_text.lower()
    tags = []
    mappings = {
        'slow_results': ['weeks', 'months', "didn't work", 'no results', 'no difference', 'nothing happened'],
        'taste': ['taste', 'flavor', 'smell', 'gross', 'disgusting', 'bad taste'],
        'price': ['expensive', 'pricey', 'cost', 'overpriced', 'not worth'],
        'shipping': ['shipping', 'delivery', 'arrived', 'late', 'never received'],
        'scam': ['scam', 'fraud', 'fake', 'counterfeit', 'not real'],
        'side_effects': ['side effect', 'headache', 'nausea', 'stomach', 'sick', 'reaction'],
        'no_libido_change': ['libido', 'desire', 'sex drive', 'no change', 'same as before'],
        'customer_service': ['customer service', 'support', 'refund', 'return', 'response'],
    }
    for tag, keywords in mappings.items():
        if any(kw in text for kw in keywords):
            tags.append(tag)
    return tags if tags else ['general_complaint']

def bloomin_advantage(pain_points):
    """Map pain points to Bloomin advantages"""
    advantages = {
        'slow_results': 'Bloomin: "Most users feel results within a week"',
        'scam': 'Bloomin: Ships direct from warehouse, subscription = verified fulfillment',
        'no_libido_change': 'Bloomin: Addresses root cause (cortisol blocker) not symptoms',
        'price': 'Bloomin: €44.95/mo with 90-day guarantee — value positioned clearly',
        'taste': 'Bloomin: Strawberry honey — designed to be enjoyable',
        'customer_service': 'Bloomin: Direct subscription model, full support access',
        'side_effects': 'Bloomin: Natural Ayurvedic formula, third-party tested',
        'shipping': 'Bloomin: 1-day processing, free shipping, discreet packaging',
    }
    if not pain_points:
        return 'Bloomin: Superior mechanism (cortisol-desire connection)'
    return advantages.get(pain_points[0], 'Bloomin: Cortisol-first approach addresses root cause')

# ── PDF GENERATOR ────────────────────────────────────────────────────────────
def generate_pdf_report(report_data, run_id):
    """Generate PDF report from scraped data"""
    timestamp = datetime.now().strftime("%Y-%m-%d")
    filename = f"competitor-review-report-{timestamp}.md"
    filepath = os.path.join(REPORT_DIR, filename)
    pdf_path = filepath.replace('.md', '.pdf')

    md = f"""# Bloomin Competitor Review Intelligence Report
**Date:** {timestamp} | **Run ID:** {run_id} | **Total Reviews:** {report_data['total_reviews']} | **Competitors:** {len(report_data['competitors'])}

---

## Executive Summary

This report analyzes **{report_data['total_reviews']} reviews (all star ratings)** across **{len(report_data['competitors'])} competitors** in Bloomin's niche.

**Key findings:**
"""

    all_pain_points = []
    for comp in report_data['competitors']:
        for r in comp['reviews']:
            all_pain_points.extend(r.get('pain_points', []))

    from collections import Counter
    top_pain_points = Counter(all_pain_points).most_common(5)

    for pain, count in top_pain_points:
        md += f"\n- **{pain.replace('_', ' ').title()}** — mentioned {count}x across competitors"

    md += "\n\n---\n\n## Competitor Breakdown\n"

    for comp in report_data['competitors']:
        md += f"\n### {comp['name']}\n"
        md += f"**URL:** {comp['url']} | **Category:** {comp['category']} | **Threat Level:** {comp['threat_level'].upper()}\n\n"

        if not comp['reviews']:
            md += "_No reviews found or Trustpilot not available._\n\n---\n"
            continue

        neg = [r for r in comp['reviews'] if r.get('sentiment') == 'negative']
        neu = [r for r in comp['reviews'] if r.get('sentiment') == 'neutral']
        pos = [r for r in comp['reviews'] if r.get('sentiment') == 'positive']
        md += f"**{len(comp['reviews'])} reviews analyzed** (🔴 {len(neg)} negative · ⚪ {len(neu)} neutral · 🟢 {len(pos)} positive)\n\n"
        md += "#### Top Complaints (1-2★)\n\n"

        for r in neg[:5]:
            md += f"> _{r['review_text'][:300]}_\n"
            md += f"> — {r['author']}, {r['review_date']} | ⭐{'⭐' * (r['rating']-1)}\n\n"
            md += f"**Pain Point:** {', '.join(r.get('pain_points', ['general']))}\n"
            md += f"**Bloomin Advantage:** {r.get('bloomin_advantage', '')}\n\n"

        md += "---\n"

    md += f"\n## Recommended Actions for Bloomin\n\n"

    action_map = {
        'slow_results': '**Lead with speed:** "Most users feel a difference within the first week" — put this front and center in all creative',
        'scam': '**Own EU safety:** "No third-party sellers. Ships directly from our warehouse." — message for UK/US cold traffic',
        'no_libido_change': '**Own the mechanism:** Competitors fail because they boost, not restore. Use the handbrake metaphor in Layer 2 copy',
        'taste': '**Taste as differentiator:** Strawberry honey is a sensory experience. Make this a feature in UGC briefs',
        'price': '**Anchor the guarantee:** 90-day MBG > competitor 67-day. Frame as "try it for 3 months, risk-free"',
    }

    for i, (pain, _) in enumerate(top_pain_points[:5], 1):
        if pain in action_map:
            md += f"{i}. {action_map[pain]}\n\n"

    md += f"\n---\n*Generated by BloomBrain · {datetime.now().strftime('%Y-%m-%d %H:%M')} · bloomin.competitor_reviews*\n"

    with open(filepath, 'w') as f:
        f.write(md)

    html_path = filepath.replace('.md', '.html')
    html = f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; color: #1a1a1a; line-height: 1.6; }}
h1 {{ color: #e91e63; border-bottom: 2px solid #e91e63; padding-bottom: 10px; }}
h2 {{ color: #333; border-bottom: 1px solid #eee; }}
h3 {{ color: #555; }}
blockquote {{ background: #f9f9f9; border-left: 4px solid #e91e63; margin: 10px 0; padding: 10px 15px; font-style: italic; }}
strong {{ color: #e91e63; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ border: 1px solid #ddd; padding: 8px; }}
</style>
</head><body>
"""
    html_body = md
    html_body = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_body)
    html_body = re.sub(r'_(.+?)_', r'<em>\1</em>', html_body)
    html_body = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'^- (.+)$', r'<li>\1</li>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'^---$', r'<hr>', html_body, flags=re.MULTILINE)
    html_body = html_body.replace('\n\n', '</p><p>')

    html += f"<p>{html_body}</p></body></html>"
    with open(html_path, 'w') as f:
        f.write(html)

    try:
        from weasyprint import HTML
        HTML(filename=html_path).write_pdf(pdf_path)
        if os.path.exists(pdf_path):
            print(f"  ✅ PDF generated: {pdf_path}")
            return pdf_path, md
    except Exception as e:
        print(f"  ⚠️ PDF generation error: {e}")

    return html_path, md

# ── MAIN ──────────────────────────────────────────────────────────────────────
def run():
    print("🌸 BloomBrain Competitor Review Scraper starting...")

    # Log scrape run
    db_exec("INSERT INTO scrape_runs (pipeline, status) VALUES ('competitor_reviews', 'running')")
    run_rows = db_query("SELECT id FROM scrape_runs ORDER BY id DESC LIMIT 1")
    run_id = run_rows[0][0] if run_rows else "1"

    # ── Seed known Trustpilot URLs ────────────────────────────────────────────
    KNOWN_TRUSTPILOT_URLS = {
        "Cymbiotika": "https://www.trustpilot.com/review/cymbiotika.com",
        "Moon Juice": "https://www.trustpilot.com/review/moonjuice.com",
        "Gaia Herbs": "https://www.trustpilot.com/review/gaiaherbs.com",
        "S'moo": "https://www.trustpilot.com/review/thesmoo.com",
        "Mixhers Libido": "https://www.trustpilot.com/review/mixhers.com",
        "Bonafide Ristela": "https://www.trustpilot.com/review/hellobonafide.com",
        "BetterAlt SHE-Lajit": "https://www.trustpilot.com/review/thebetteralt.com",
        "For Hers": "https://www.trustpilot.com/review/forhers.com",
        "Tribe Organics": "https://www.trustpilot.com/review/tribeorganics.com",
        "Natruveda": "https://www.trustpilot.com/review/natruveda.com",
        "Dr. Jolene Brighten Essentials": "https://www.trustpilot.com/review/drbrighten.com",
        "BrainMD Happy Saffron": "https://www.trustpilot.com/review/brainmd.com",
        "Addyi (flibanserin)": "https://www.trustpilot.com/review/addyi.com",
    }
    for comp_name, tp_url in KNOWN_TRUSTPILOT_URLS.items():
        name_esc = comp_name.replace("'", "''")
        db_exec(
            f"UPDATE competitors SET trustpilot_url='{tp_url}' "
            f"WHERE name='{name_esc}' AND (trustpilot_url IS NULL OR trustpilot_url='')"
        )
    print(f"  Seeded Trustpilot URLs for {len(KNOWN_TRUSTPILOT_URLS)} competitors")

    # Get qualifying competitors with Trustpilot URLs
    competitors_rows = db_query(
        "SELECT id, name, url, trustpilot_url, category, threat_level FROM competitors WHERE qualifies = true ORDER BY threat_level DESC"
    )

    print(f"Found {len(competitors_rows)} competitors to process")

    report_data = {'total_reviews': 0, 'competitors': []}
    total_stored = 0
    total_negative = 0
    total_neutral = 0
    total_positive = 0

    for row in competitors_rows:
        comp_id, name, url, tp_url, category, threat = row[0], row[1], row[2], row[3], row[4], row[5]
        print(f"\n📊 Processing: {name}")

        comp_data = {
            'name': name, 'url': url or '', 'category': category,
            'threat_level': threat, 'reviews': []
        }

        if tp_url and tp_url != '':
            reviews = scrape_trustpilot_reviews(tp_url, comp_id)
            print(f"  Scraped {len(reviews)} reviews")

            for r in reviews:
                is_negative = r['rating'] <= 2

                if is_negative:
                    pain_points = analyze_pain_points(r['review_text'])
                    advantage = bloomin_advantage(pain_points)
                    pain_tags = "{" + ",".join(pain_points) + "}"
                else:
                    pain_points = []
                    advantage = ""
                    pain_tags = "{}"

                db_exec(f"""
                    INSERT INTO competitor_reviews
                    (competitor_id, platform, rating, review_text, review_date, author, verified, sentiment, pain_point_tags, bloomin_advantage)
                    VALUES (
                        {r['competitor_id']}, '{r['platform']}', {r['rating']},
                        $${r['review_text']}$$,
                        '{r['review_date']}', $${r['author']}$$, {r['verified']},
                        '{r['sentiment']}', '{pain_tags}'::text[], $${advantage}$$
                    )
                """)

                r['pain_points'] = pain_points
                r['bloomin_advantage'] = advantage
                comp_data['reviews'].append(r)
                total_stored += 1

                if r['sentiment'] == 'negative':
                    total_negative += 1
                elif r['sentiment'] == 'neutral':
                    total_neutral += 1
                else:
                    total_positive += 1
        else:
            print(f"  No Trustpilot URL — skipping review scrape")

        report_data['competitors'].append(comp_data)
        time.sleep(1)

    report_data['total_reviews'] = total_stored
    print(f"\n✅ Total reviews stored: {total_stored} "
          f"(🔴 {total_negative} neg · ⚪ {total_neutral} neu · 🟢 {total_positive} pos)")

    # Generate report
    print("\n📄 Generating report...")
    report_path, report_md = generate_pdf_report(report_data, run_id)
    report_filename = os.path.basename(report_path)

    # Update scrape run
    db_exec(f"""
        UPDATE scrape_runs SET status='completed', records_scraped={total_stored},
        completed_at=NOW(), report_url='{report_path}' WHERE id={run_id}
    """)

    # Post Slack report
    print("\n📤 Posting to Slack...")

    today = date.today().strftime("%Y-%m-%d")

    from collections import Counter
    all_pain_points = []
    for comp in report_data['competitors']:
        for r in comp['reviews']:
            all_pain_points.extend(r.get('pain_points', []))
    top_pains = Counter(all_pain_points).most_common(6)

    total_negative = sum(1 for comp in report_data['competitors'] for r in comp['reviews'] if r.get('sentiment') == 'negative')
    total_positive = sum(1 for comp in report_data['competitors'] for r in comp['reviews'] if r.get('sentiment') == 'positive')
    total_neutral = total_stored - total_negative - total_positive

    # 1. Header
    slack_post([
        {"type": "header", "text": {"type": "plain_text", "text": "🔴 Competitor Review Intelligence", "emoji": True}},
        {"type": "context", "elements": [{"type": "mrkdwn",
            "text": f"📅 {today}  |  📊 {total_stored} reviews  |  🔴 {total_negative} negative  ·  🟡 {total_neutral} neutral  ·  🟢 {total_positive} positive  |  🏢 {len([c for c in report_data['competitors'] if c['reviews']])} competitors"}]},
        {"type": "divider"},
    ])
    time.sleep(0.5)

    # 2. Competitor overview
    comp_lines = []
    for comp in report_data['competitors']:
        count = len(comp['reviews'])
        if count > 0:
            comp_lines.append(f"• *{comp['name']}*  ·  {comp['threat_level'].upper()} threat  ·  {count} reviews")
        else:
            comp_lines.append(f"• *{comp['name']}*  ·  _no Trustpilot data_")
    slack_post([
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*🏢 Competitor Coverage*\n\n" + "\n".join(comp_lines)}},
        {"type": "divider"},
    ])
    time.sleep(0.5)

    # 3. Pain points
    if top_pains:
        pain_lines = "\n".join([f"• *{p.replace('_', ' ').title()}*  —  {c}x across competitors" for p, c in top_pains])
    else:
        pain_lines = "• _Insufficient negative review data this run_"
    slack_post([
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*🔍 Top Customer Pain Points (1-2★)*\n\n{pain_lines}"}},
        {"type": "divider"},
    ])
    time.sleep(0.5)

    # 4. Bloomin advantages
    slack_post([
        {"type": "section", "text": {"type": "mrkdwn",
            "text": "*🎯 Bloomin Advantages (from competitor failures)*\n\n"
                    "• *Speed*  —  Most users feel results within a week vs competitors' 60-day complaints\n"
                    "• *Mechanism*  —  Cortisol-first explains WHY it works; competitors don't educate → churn\n"
                    "• *Trust*  —  Direct ships from warehouse; no counterfeit risk flagged in reviews\n"
                    "• *Taste*  —  Honey format enjoyable; capsule competitors see taste complaints\n"
                    "• *Guarantee*  —  90-day MBG frames value clearly vs competitors' shorter windows"}},
        {"type": "divider"},
    ])
    time.sleep(0.5)

    # 5. Footer
    slack_post([
        {"type": "context", "elements": [
            {"type": "mrkdwn", "text": f"🌸 *BloomBrain* · {today} · Trustpilot via HTTP scraper · Next run: tomorrow 09:00 AM GMT+1"}
        ]},
    ])

    time.sleep(0.5)

    # Upload the report file
    print(f"Uploading {report_filename}...")
    for upload_channel in SLACK_CHANNELS:
        try:
            permalink = slack_upload_file(
                report_path, report_filename,
                f"Competitor Review Report — {today}",
                upload_channel
            )
            if permalink:
                print(f"✅ File uploaded to {upload_channel}: {permalink}")
            else:
                print(f"⚠️ File upload incomplete for {upload_channel}")
        except Exception as e:
            print(f"⚠️ File upload error for {upload_channel}: {e}")
            _slack_post_single(upload_channel, [
                {"type": "section", "text": {"type": "mrkdwn",
                    "text": f"📎 *Report saved locally:* `{report_path}`\n_File upload unavailable — report accessible on Mac Mini_"}}
            ])

    print(f"\n🌸 Done! Report: {report_path}")

if __name__ == "__main__":
    run()
