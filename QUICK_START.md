# 🚀 Quick Start Guide - Browser Monitoring

The easiest way to scrape Medium without bot detection!

## What You'll Do

1. ✅ Open Chrome with your existing Medium login
2. ✅ Browse Medium articles normally
3. ✅ Script auto-detects questions in background
4. ✅ Press Ctrl+C when done - results saved automatically

## Step-by-Step

### 1️⃣ Start Chrome with Debugging

```bash
cd /Users/nikhilkumar/Downloads/MediumScraper
./start_chrome_debug.sh
```

Chrome will close and reopen (your profile/logins preserved).

### 2️⃣ Start the Monitor

Open a **new terminal window** and run:

```bash
cd /Users/nikhilkumar/Downloads/MediumScraper
python3 monitor_my_browsing.py
```

You'll see:
```
✅ Connected! Monitoring 1 open tabs
💡 Browse Medium articles - questions will be detected automatically
```

### 3️⃣ Browse Medium

In the Chrome window:
1. Go to `medium.com`
2. Search: "ios interview questions swift"
3. Click on interesting articles
4. Read at your own pace
5. Open multiple articles in new tabs if you want

**The monitor will show:**
```
✨ Found 15 new questions!
   📄 https://medium.com/@someone/ios-interview-guide...
   📊 Total: 15 questions
```

### 4️⃣ When Done

In the terminal with the monitor, press **Ctrl+C**

Results saved to:
- `my_browsing_questions_TIMESTAMP.csv`
- `my_browsing_questions_TIMESTAMP.json`

## 💡 Tips

- **Multiple tabs work!** Open several articles - all monitored
- **Take your time** - No rush, no rate limits
- **Already logged in** - Your Medium membership works
- **Zero detection** - You're the human, not a bot

## ❓ Troubleshooting

**"No browser contexts found"**
- Make sure you ran `./start_chrome_debug.sh` first
- Chrome must be running with debugging enabled

**"Connection error"**
- Chrome might have crashed - restart with `./start_chrome_debug.sh`
- Check Chrome is running: `ps aux | grep Chrome`

## 📊 What Gets Detected

The monitor looks for:
- Questions ending with "?"
- Lines starting with: what, why, how, when, where, which, explain, describe, etc.
- Minimum 15 characters (filters out noise)

All questions are:
- ✅ Deduplicated (no repeats)
- ✅ Timestamped (when found)
- ✅ Source-linked (URL saved)

---

**Need help?** Check the main [README.md](README.md) for more options!

