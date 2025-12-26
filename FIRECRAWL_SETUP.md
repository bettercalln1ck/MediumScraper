# 🔥 Firecrawl Hybrid Setup Guide

## 🚀 Quick Setup (3 steps)

### Step 1: Install Firecrawl

```bash
pip3 install firecrawl-py
```

### Step 2: Get Free API Key

1. Go to: **https://firecrawl.dev**
2. Click "Sign Up" (free account)
3. Go to Dashboard → API Keys
4. Copy your API key

### Step 3: Add API Key to Script

Open `monitor_hybrid.py` and replace:

```python
FIRECRAWL_API_KEY = "YOUR_FIRECRAWL_API_KEY_HERE"
```

With your actual key:

```python
FIRECRAWL_API_KEY = "fc-xxxxxxxxxxxxx"
```

---

## 🎯 How to Use

### Start the Hybrid Monitor:

```bash
# 1. Make sure Chrome is in debug mode
./start_chrome_debug.sh

# 2. Run hybrid monitor
python3 monitor_hybrid.py
```

### What You'll See:

```
✅ Connected to Chrome!
💡 Browse Medium articles...

====================================================================
📄 NEW ARTICLE #1
====================================================================
🔗 https://medium.com/@user/ios-interview-guide...
   🔥 Scraping with Firecrawl...
   ✅ Scraped! (12450 chars)
   🤖 Extracting Q&A with AI...
   
   ✨ Added 8 unique Q&A!
   📊 TOTAL: 8 unique Q&A
====================================================================

(Continue browsing, each article auto-processed!)
```

---

## 🔥 How It Works

1. **You browse** Medium naturally in Chrome
2. **Script detects** when you visit an article
3. **Firecrawl scrapes** the article (bypasses Medium's blocks)
4. **Groq AI extracts** iOS Q&A pairs
5. **Deduplication** filters similar questions
6. **Auto-saves** to CSV/JSON

---

## ✨ Advantages

### vs. Pure Playwright:
- ✅ Better Medium bypass (no blocks!)
- ✅ Cleaner content extraction
- ✅ More reliable
- ✅ LLM-optimized output

### vs. Pure Firecrawl:
- ✅ Easy article discovery (browse naturally)
- ✅ Real-time feedback
- ✅ No need to manually collect URLs

---

## 💰 Free Tier Limits

- **500 credits/month** (free)
- **1 credit = 1 article**
- **~16 articles/day** on free tier

**Good for:** Interview prep, collecting 100-500 Q&As

**Need more?** Hobby plan: $20/month for 5,000 articles

---

## 🎯 Best Practices

1. **Start Chrome debug mode first**
   ```bash
   ./start_chrome_debug.sh
   ```

2. **Browse to article pages** (not search results)

3. **Watch terminal** for extraction feedback

4. **Let it process** (takes 2-3 seconds per article)

5. **Results auto-save** when you Ctrl+C

---

## 🐛 Troubleshooting

### "Firecrawl not installed"
```bash
pip3 install firecrawl-py
```

### "Please set your Firecrawl API key"
- Get key from https://firecrawl.dev
- Update `FIRECRAWL_API_KEY` in `monitor_hybrid.py`

### "Chrome not in debug mode"
```bash
./start_chrome_debug.sh
# Wait 5 seconds
python3 monitor_hybrid.py
```

### "Firecrawl failed"
- Check your API key
- Check free tier credits remaining (500/month)
- Try again (might be temporary API issue)

---

## 📊 Sample Output

After browsing 10 articles:

```
📊 HYBRID SESSION SUMMARY
====================================================================
🔄 URL changes: 15
📄 Articles detected: 10
🔥 Firecrawl success: 9
❌ Firecrawl errors: 1
📝 Articles with Q&A: 8
💡 Total Q&A: 45
🔄 Duplicates: 12
⭐ UNIQUE SAVED: 33

📈 Dedup rate: 26.7%

💾 Saved to:
   • ios_qa_hybrid_20251226_031500.csv
   • ios_qa_hybrid_20251226_031500.json
====================================================================
```

---

## 🎓 Comparison: All Methods

| Method | Detection | Scraping | Quality | Cost |
|--------|-----------|----------|---------|------|
| **monitor_final.py** | Manual polling | Playwright | Medium | Free |
| **monitor_hybrid.py** | Manual polling | Firecrawl | High | $0-$20 |

**Hybrid = Best!** ⭐

---

## 🚀 Ready to Start?

```bash
# Install
pip3 install firecrawl-py

# Get key from firecrawl.dev
# Add to monitor_hybrid.py

# Run
./start_chrome_debug.sh
python3 monitor_hybrid.py

# Browse Medium and watch magic happen! ✨
```

---

## 💡 Pro Tips

1. **Use free tier wisely** - Browse to find good articles first
2. **Check credit usage** at firecrawl.dev/dashboard
3. **Combine with monitor_final.py** - Use free version to explore, hybrid for final collection
4. **Export results** - Use `optimize_for_ai.py` after collection

---

**Questions?** Check the main README.md or contact support!

