#!/usr/bin/env python3
"""
BloomBrain — Facebook Ad Library Scraper
Uses Playwright + Chrome cookies (no Meta API token needed)
Runs daily at 7:30am
"""

from playwright.sync_api import sync_playwright
import json, re, time, os, shutil, subprocess, urllib.request
from datetime import datetime

SLACK_TOKEN = os.environ["SLACK_TOKEN"]
CHANNELS = ["C0AM45T4XT8"]
CHROME_SRC = os.path.expanduser("~/Library/Application Support/Google/Chrome")
TMP_PROFILE = "/tmp/chrome-profile-fb"
DB_NAME = "bloomin"
PSQL = "/opt/homebrew/opt/postgresql@16/bin/psql"

env = os.environ.copy()
env["PATH"] = f"/opt/homebrew/opt/postgresql@16/bin:{env.get('PATH','')}"

SEARCH_QUERIES = [
    "libido supplement women",
    "shilajit honey sticks",
    "female desire supplement",
    "shatavari women supplement",
    "women desire restore supplement",
    "cortisol women libido supplement",
    "women libido honey",
    "shilajit women supplement",
    "saffron libido women",
    "honey stick supplement women",
    "low libido women supplement",
    "womens sexual wellness supplement",
    "adaptogen women libido",
    "perimenopause libido supplement",
    "women cortisol supplement",
    "ashwagandha women libido",
    "maca women supplement",
    "female hormonal balance supplement",
]

def db_exec(sql):
    subprocess.run([PSQL,"-d",DB_NAME,"-c",sql],capture_output=True,env=env)

def db(sql):
    r = subprocess.run([PSQL,"-d",DB_NAME,"-t","-A","-F","\t","-c",sql],
                      capture_output=True,text=True,env=env)
    if not r.stdout.strip(): return []
    return [line.split('\t') for line in r.stdout.strip().split('\n') if line]

def post(blocks):
    for ch in CHANNELS:
        payload = json.dumps({"channel":ch,"text":"BloomBrain FB Ads","blocks":blocks}).encode()
        req = urllib.request.Request("https://slack.com/api/chat.postMessage",data=payload,
            headers={"Authorization":f"Bearer {SLACK_TOKEN}","Content-Type":"application/json"})
        with urllib.request.urlopen(req) as r:
            resp = json.loads(r.read())
        print(f"  {'✅' if resp.get('ok') else '❌ '+resp.get('error','')} → #{ch}")
    time.sleep(0.5)

def T(headers, rows):
    def cell(t,bold=False):
        el={"type":"text","text":str(t)[:80]}
        if bold: el["style"]={"bold":True}
        return {"type":"rich_text","elements":[{"type":"rich_text_section","elements":[el]}]}
    return {"type":"table","rows":[[cell(h,True) for h in headers]]+[[cell(c) for c in row] for row in rows]}

def refresh_chrome_profile():
    """Copy fresh Chrome cookies to tmp dir"""
    if not os.path.exists(TMP_PROFILE):
        os.makedirs(TMP_PROFILE, exist_ok=True)
    
    for item in ['Default/Cookies', 'Default/Local Storage']:
        src = os.path.join(CHROME_SRC, item)
        dst = os.path.join(TMP_PROFILE, item)
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.isfile(src):
                try:
                    shutil.copy2(src, dst)
                except: pass
            elif not os.path.exists(dst):
                try:
                    shutil.copytree(src, dst)
                except: pass

def scrape_fb_ads():
    all_ads = []
    
    refresh_chrome_profile()
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=TMP_PROFILE,
            headless=True,
            channel="chrome",
            args=['--no-sandbox','--disable-blink-features=AutomationControlled'],
        )
        page = browser.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        for query in SEARCH_QUERIES:
            encoded = query.replace(' ', '+')
            url = f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&q={encoded}&search_type=keyword_unordered&media_type=all"
            
            print(f"  Scraping: '{query}'")
            try:
                page.goto(url, wait_until='domcontentloaded', timeout=25000)
                time.sleep(4)
                
                # Scroll to load more
                for _ in range(10):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(2)
                
                body = page.inner_text('body')
                
                # Check logged in
                if 'Log in to Facebook' in body[:500]:
                    print("  ⚠️ Not logged in")
                    continue
                
                # Count results
                count_m = re.search(r'~?([\d,]+) results', body)
                result_count = count_m.group(1) if count_m else '?'
                
                # Parse advertisers
                lines = [l.strip() for l in body.split('\n') if l.strip()]
                for i, line in enumerate(lines):
                    if line == 'Sponsored' and i > 0:
                        advertiser = lines[i-1]
                        ad_text = ' '.join(lines[i+1:i+6]) if i+6 < len(lines) else ''
                        start_date = ''
                        for j in range(max(0,i-12), i):
                            if 'Started running on' in lines[j]:
                                start_date = re.sub(r'Started running on ', '', lines[j])
                        
                        skip = ['Meta Ad Library','Ad Library','United States','Log in','Ad Library Report',
                                'Ad Library API','Branded Content','System status','Subscribe to email',
                                'FAQ','About ads','Privacy','Terms','Cookies']
                        
                        if (advertiser and 2 < len(advertiser) < 80 and 
                            advertiser not in skip and not advertiser.isdigit()):
                            all_ads.append({
                                'advertiser': advertiser,
                                'query': query,
                                'result_count': result_count,
                                'ad_text': ad_text[:300],
                                'started': start_date,
                                'date': datetime.now().strftime('%Y-%m-%d')
                            })
                
                print(f"    ~{result_count} results in Ad Library")
                time.sleep(2)
                
            except Exception as e:
                print(f"  Error: {e}")
        
        browser.close()
    
    return all_ads

def run():
    print("🌸 BloomBrain FB Ad Library Scraper starting...")
    today = datetime.now().strftime("%Y-%m-%d")
    
    all_ads = scrape_fb_ads()
    
    # Deduplicate by advertiser
    seen = set()
    unique_ads = []
    for ad in all_ads:
        key = ad['advertiser'].lower()
        if key not in seen:
            seen.add(key)
            unique_ads.append(ad)
    
    print(f"Total unique advertisers: {len(unique_ads)}")
    
    # Store in DB
    for ad in unique_ads:
        name_esc = ad['advertiser'].replace("'","''")
        text_esc = ad['ad_text'].replace("'","''")[:300]
        query_esc = ad['query'].replace("'","''")
        db_exec(f"""
            INSERT INTO competitor_mentions (competitor_name, platform, post_title, post_text, score, subreddit, url, sentiment)
            VALUES ($${name_esc}$$, 'facebook_ads', $${query_esc}$$, $${text_esc}$$, 0,
            'meta_ad_library', 'https://www.facebook.com/ads/library/', 'neutral')
            ON CONFLICT DO NOTHING
        """)
    
    # Find new advertisers not in competitor DB
    existing_names = {r[0].lower() for r in db("SELECT LOWER(name) FROM competitors")}
    new_advertisers = [
        ad for ad in unique_ads 
        if not any(ex in ad['advertiser'].lower() or ad['advertiser'].lower() in ex 
                  for ex in existing_names)
    ]
    
    # Get yesterday's advertisers to find truly new ones today
    yesterday_ads = db(f"""
        SELECT DISTINCT LOWER(competitor_name) FROM competitor_mentions 
        WHERE platform='facebook_ads' AND scraped_at < NOW() - INTERVAL '12 hours'
    """)
    yesterday_names = {r[0] for r in yesterday_ads if r}
    brand_new_today = [ad for ad in new_advertisers 
                       if ad['advertiser'].lower() not in yesterday_names]
    
    print(f"New to DB: {len(new_advertisers)}, Brand new today: {len(brand_new_today)}")
    
    # Group by query for report
    by_query = {}
    for ad in unique_ads:
        q = ad['query']
        if q not in by_query: by_query[q] = []
        by_query[q].append(ad)
    
    # Post report
    today = datetime.now().strftime("%Y-%m-%d")

    # 1. Header
    post([
        {"type": "header", "text": {"type": "plain_text", "text": "📢 Facebook Ad Library Report", "emoji": True}},
        {"type": "context", "elements": [{"type": "mrkdwn",
            "text": f"📅 {today}  |  🔍 {len(SEARCH_QUERIES)} keyword searches  |  👤 {len(unique_ads)} unique advertisers  |  🆕 {len(brand_new_today)} new since yesterday"}]},
        {"type": "divider"},
    ])
    time.sleep(0.3)

    # 2. Advertisers by query (one section per query, max 6 results each)
    for q, ads in by_query.items():
        if not ads:
            continue
        lines = "\n".join([
            f"• *{a['advertiser']}*  ·  {a['started'][:15] if a['started'] else 'recent'}  ·  _{a['ad_text'][:80]}_"
            for a in ads[:6]
        ])
        post([
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*🔎 \"{q}\"*\n\n{lines}"}},
            {"type": "divider"},
        ])
        time.sleep(0.3)

    # 3. New advertisers summary (if any)
    if brand_new_today:
        lines = "\n".join([
            f"• *{a['advertiser']}*  ·  via _{a['query']}_  ·  _{a['ad_text'][:80]}_"
            for a in brand_new_today[:10]
        ])
        post([
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*🆕 {len(brand_new_today)} Brand New Advertisers Today*\n\n{lines}"}},
            {"type": "divider"},
        ])
        time.sleep(0.3)

    # 4. Footer
    post([
        {"type": "context", "elements": [
            {"type": "mrkdwn", "text": f"🌸 *BloomBrain* · {today} · FB Ad Library via Playwright + Chrome · Next run: tomorrow 07:30 AM GMT+1"}
        ]},
    ])

    print("✅ FB Ad Library report posted to both channels")

if __name__ == "__main__":
    run()
