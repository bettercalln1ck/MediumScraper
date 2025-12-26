#!/bin/bash
# start_chrome_debug.sh
# Launches Chrome with remote debugging enabled

echo "🚀 Starting Chrome with remote debugging..."
echo ""
echo "This will:"
echo "  ✓ Close any running Chrome instances"
echo "  ✓ Reopen Chrome with debugging enabled on port 9222"
echo "  ✓ Use a separate profile (you'll need to log into Medium)"
echo ""

# Kill any existing Chrome processes
killall -9 "Google Chrome" 2>/dev/null
sleep 2

# Create debug profile directory
mkdir -p "$HOME/ChromeDebugProfile"

# Start Chrome with remote debugging
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/ChromeDebugProfile" \
  > /dev/null 2>&1 &

echo "⏳ Waiting for Chrome to start..."
sleep 5

# Verify it's working
if curl -s http://127.0.0.1:9222/json/version > /dev/null 2>&1; then
    echo "✅ Chrome started successfully with remote debugging!"
    echo ""
    echo "📝 Note: This is a fresh Chrome profile."
    echo "   Log into Medium.com in this browser window."
    echo ""
    echo "Now run: python3 monitor_my_browsing.py"
else
    echo "❌ Chrome didn't start properly. Check /tmp/chrome_debug.log"
fi
echo ""

