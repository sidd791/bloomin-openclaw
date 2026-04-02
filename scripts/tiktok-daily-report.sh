#!/bin/bash
# BloomBrain — Daily TikTok Intelligence Report
# Scrapes hashtags via Apify and posts to Slack #general

set -e

export PATH="/opt/homebrew/bin:$PATH"

WORKSPACE="/Users/teambloomin/.openclaw/workspace"
REPORT_FILE="$WORKSPACE/research/tiktok/latest-report.json"
mkdir -p "$WORKSPACE/research/tiktok"

# Run Apify TikTok scraper
cat > /tmp/tiktok-daily-input.json << 'EOF'
{
  "hashtags": ["hormonehealth", "lowlibido", "womenshealth", "cortisol", "shatavari"],
  "resultsPerPage": 20,
  "shouldDownloadVideos": false,
  "shouldDownloadCovers": false
}
EOF

echo "[$(date)] Starting TikTok scrape..."
apify call clockworks/tiktok-scraper --input-file /tmp/tiktok-daily-input.json --output-dataset > "$REPORT_FILE" 2>&1

echo "[$(date)] Scrape complete. Sending to OpenClaw for analysis..."

# Post to OpenClaw for analysis and Slack delivery
# OpenClaw will pick this up via heartbeat or direct message
echo "TIKTOK_REPORT_READY:$REPORT_FILE" >> "$WORKSPACE/research/tiktok/pending-reports.txt"

echo "[$(date)] Done."
