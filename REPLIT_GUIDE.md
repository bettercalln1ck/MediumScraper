# 🚀 Deploy to Replit - Complete Guide (100% Free Forever)

## Why Replit?

✅ **Free forever** (no trial period)
✅ **No credit card required**
✅ **3-minute setup**
✅ **Works entirely in browser**
✅ **Automatic HTTPS**
✅ **Public URL included**

---

## 📋 Step-by-Step Deployment

### Step 1: Import from GitHub (2 minutes)

1. **Go to Replit**: https://replit.com
2. **Sign up** with GitHub (instant)
3. Click **"Create Repl"**
4. Choose **"Import from GitHub"**
5. Paste your repo URL:
   ```
   https://github.com/bettercalln1ck/MediumScraper
   ```
6. Click **"Import from GitHub"**
7. Wait 30 seconds while Replit sets up

### Step 2: Add API Keys (1 minute)

1. In your Repl, look at the left sidebar
2. Click the **🔒 "Secrets"** icon (looks like a lock)
3. Add your first secret:
   - **Key**: `GROQ_API_KEY`
   - **Value**: (paste your Groq API key from API_KEYS.txt)
   - Click **"Add new secret"**
4. Add your second secret:
   - **Key**: `FIRECRAWL_API_KEY`
   - **Value**: (paste your Firecrawl API key from API_KEYS.txt)
   - Click **"Add new secret"**

### Step 3: Run! (30 seconds)

1. Click the big green **"Run"** button at the top
2. Wait 20-30 seconds while dependencies install
3. You'll see: `Application startup complete`
4. Your API is now live! 🎉

### Step 4: Get Your URL

Look at the top right - you'll see a URL like:

```
https://mediumscraper-yourname.replit.app
```

**That's your API URL!** Copy it.

---

## 🧪 Test Your API

Open a new browser tab and try these URLs:

### 1. Health Check
```
https://your-repl-url.replit.app/health
```

Should return:
```json
{"status": "healthy"}
```

### 2. Get Stats
```
https://your-repl-url.replit.app/stats
```

Should show your Q&A statistics.

### 3. Submit a URL
```
https://your-repl-url.replit.app/scrape?url=https://medium.com/some-article
```

---

## ⚠️ Problem: Replit Apps Sleep

**Issue:** Free Replit apps sleep after 1 hour of inactivity.

**Solution:** Use UptimeRobot to ping your app every 5 minutes (keeps it awake).

---

## 🔄 Keep Your App Awake 24/7 (UptimeRobot)

### Step 1: Sign up for UptimeRobot (1 minute)

1. Go to: https://uptimerobot.com
2. Click **"Sign Up Free"**
3. Verify your email

### Step 2: Add Monitor (1 minute)

1. Click **"+ Add New Monitor"**
2. Fill in:
   - **Monitor Type**: HTTP(s)
   - **Friendly Name**: iOS Q&A Scraper
   - **URL**: `https://your-repl-url.replit.app/health`
   - **Monitoring Interval**: 5 minutes
3. Click **"Create Monitor"**

### Step 3: Done! ✅

Your app will now:
- ✅ Stay awake 24/7
- ✅ Get pinged every 5 minutes
- ✅ Never sleep
- ✅ Be always available

**Both services are 100% free forever!**

---

## 📊 Your Setup Summary

| Service | Purpose | Cost |
|---------|---------|------|
| **Replit** | Hosts your API | Free forever |
| **UptimeRobot** | Keeps it awake | Free forever |
| **Groq** | AI processing | $0.05 per million tokens |
| **Firecrawl** | Web scraping | 500 free credits/month |

**Total monthly cost: ~$0** (within free tiers)

---

## 🔧 Troubleshooting

### App Won't Start

**Check Secrets:**
- Go to 🔒 Secrets tab
- Verify both API keys are added
- Keys should NOT have quotes

**Check Console:**
- Look at the Console/Shell tab
- Read any error messages

### Import Failed

**Use Manual Setup:**
1. Create a new Python Repl
2. In Shell, run:
   ```bash
   git clone https://github.com/bettercalln1ck/MediumScraper.git
   cd MediumScraper
   pip install -r requirements.txt
   ```
3. Add Secrets
4. Click Run

### App Returns 404

**Check the Run Command:**
- Click 3 dots next to Run button → "Show hidden files"
- Open `.replit` file
- Should say: `run = "python3 main.py"`

---

## 🎯 API Endpoints Available

Once deployed, your API has these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/stats` | GET | Q&A statistics |
| `/qa` | GET | Get all Q&A pairs |
| `/scrape` | POST | Submit URL to scrape |

### Example API Call

```bash
curl -X POST "https://your-repl-url.replit.app/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://medium.com/@author/ios-article"}'
```

---

## 🔐 Security Notes

✅ **Secrets are encrypted** - Replit encrypts your API keys
✅ **Not in code** - Keys are environment variables
✅ **Not in git** - Secrets don't get committed

---

## 💰 Costs (With Free Tiers)

### Groq API
- Free tier: $5 credit (lasts months)
- After free tier: $0.05 per 1M tokens
- Your usage: ~$0.10/month (1000 articles)

### Firecrawl
- Free tier: 500 credits/month
- After free tier: $29/month unlimited
- Your usage: ~250 articles/month on free tier

### Replit
- **Free forever**
- Upgrade ($7/month) for:
  - Always-on (no sleep)
  - More CPU/RAM
  - Custom domains

### UptimeRobot
- **Free forever** for 50 monitors
- Upgrade only if you need more monitors

---

## 🚀 You're Live!

Your API is now:
✅ Deployed and running
✅ Publicly accessible
✅ Free forever
✅ Awake 24/7 (with UptimeRobot)

**Share your API URL** with clients or use it in your apps!

---

## 📱 Next Steps

1. **Test it thoroughly** - Try scraping various articles
2. **Monitor usage** - Check Groq/Firecrawl dashboards
3. **Set up webhooks** - Get notified when scraping completes
4. **Add authentication** - Protect your API if needed

---

## 💡 Pro Tips

### Make It Faster
Add to your Repl's environment:
```bash
WORKERS=2
```

### Add Custom Domain
Upgrade to Replit Hacker plan ($7/month) to use your own domain.

### Auto-Restart on Crash
Replit automatically restarts crashed apps - no config needed!

### View Logs
Click "Console" tab to see real-time logs.

---

## 🎉 Congratulations!

You've successfully deployed your iOS Q&A Scraper to Replit!

**Your API is now:**
- 🌐 Online and publicly accessible
- 🆓 Completely free
- 🔄 Always awake (with UptimeRobot)
- 🔐 Secure (encrypted secrets)

**Total setup time:** 5 minutes
**Total cost:** $0/month

Enjoy! 🚀

