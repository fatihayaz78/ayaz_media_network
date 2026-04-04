#!/bin/bash
set -e
cd /Users/fatihayaz/Documents/Projects/ayaz_media_network

echo "=== AYAZ MEDIA NETWORK ==="
echo "Starting production daemon..."

# Activate venv
source amn/bin/activate
echo "✅ venv (amn) active — $(python --version)"

# Load .env
if [ -f .env ]; then
    set -a; source .env; set +a
    echo "✅ .env loaded"
else
    echo "⚠️  WARNING: .env not found — AI channels will use fallback mode"
fi

# Check critical keys
[ -z "$ANTHROPIC_API_KEY" ] && echo "⚠️  ANTHROPIC_API_KEY not set"
[ -z "$RAPIDAPI_KEY" ]      && echo "⚠️  RAPIDAPI_KEY not set"

echo ""
echo "Studio UI:    http://localhost:5052"
echo "Scheduler UI: http://localhost:5052/scheduler"
echo "Logs:         tail -f logs/daemon.log"
echo ""

python app.py
