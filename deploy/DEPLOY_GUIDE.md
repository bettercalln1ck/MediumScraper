# 🚀 Free Deployment Guide

Deploy your iOS Q&A Scraper API on **FREE** hosting platforms!

---

## 🎯 Best Free Platforms

| Platform | Free Tier | Database | Best For |
|----------|-----------|----------|----------|
| **Render.com** ⭐ | 750 hrs/month | SQLite + disk | Production |
| **Railway.app** | $5 credit/month | SQLite | Development |
| **Fly.io** | 3 VMs free | SQLite + volume | Scaling |
| **Replit** | Always on (Hacker plan) | SQLite | Quick test |

---

## 🏆 Option 1: Render.com (RECOMMENDED)

### Why Render?
- ✅ 750 hours/month free
- ✅ Persistent disk storage (1GB)
- ✅ Auto-deploy from Git
- ✅ Free SSL certificates
- ✅ No credit card required

### Deploy Steps:

#### 1. Push to GitHub

```bash
cd /Users/nikhilkumar/Downloads/MediumScraper
git init
git add deploy/
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ios-qa-scraper.git
git push -u origin main
```

#### 2. Deploy on Render

1. Go to [render.com](https://render.com)
2. Click "New +" → "Blueprint"
3. Connect your GitHub repo
4. Render will auto-detect `render.yaml`
5. Click "Apply"
6. Wait 2-3 minutes for deployment

#### 3. Your API is Live!

```
https://ios-qa-scraper.onrender.com
```

### Test It:

```bash
# Submit a URL
curl -X POST https://your-app.onrender.com/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://medium.com/@user/ios-interview"}'

# Check status
curl https://your-app.onrender.com/api/jobs/{job_id}

# Get results
curl https://your-app.onrender.com/api/jobs/{job_id}/results
```

---

## 🚂 Option 2: Railway.app

### Why Railway?
- ✅ $5 free credit/month
- ✅ Simple deployment
- ✅ Good for development

### Deploy Steps:

#### 1. Install Railway CLI

```bash
npm install -g @railway/cli
```

#### 2. Deploy

```bash
cd /Users/nikhilkumar/Downloads/MediumScraper/deploy
railway login
railway init
railway up
```

#### 3. Set Environment Variables

```bash
railway variables set GROQ_API_KEY=your-groq-api-key-here
railway variables set FIRECRAWL_API_KEY=your-firecrawl-api-key-here
```

#### 4. Get URL

```bash
railway domain
```

---

## 🪰 Option 3: Fly.io

### Why Fly.io?
- ✅ 3 VMs free
- ✅ Global edge network
- ✅ Persistent volumes

### Deploy Steps:

#### 1. Install Fly CLI

```bash
brew install flyctl
```

#### 2. Login and Deploy

```bash
cd /Users/nikhilkumar/Downloads/MediumScraper/deploy
fly auth login
fly launch

# When prompted:
# - App name: ios-qa-scraper
# - Region: Choose closest
# - Database: No
# - Deploy now: Yes
```

#### 3. Create Volume

```bash
fly volumes create data --size 1
```

#### 4. Set Secrets

```bash
fly secrets set GROQ_API_KEY=your-groq-api-key-here
fly secrets set FIRECRAWL_API_KEY=your-firecrawl-api-key-here
```

---

## 💻 Option 4: Replit

### Why Replit?
- ✅ Instant deployment
- ✅ Built-in IDE
- ✅ Good for quick tests

### Deploy Steps:

1. Go to [replit.com](https://replit.com)
2. Create new Repl → Python
3. Upload files from `deploy/` folder
4. Click "Run"
5. Share the public URL

---

## 🌐 Option 5: Local + Ngrok (Testing)

### For Development/Testing:

```bash
# Terminal 1: Run API
cd /Users/nikhilkumar/Downloads/MediumScraper/deploy
python3 simple_api.py

# Terminal 2: Expose with Ngrok
ngrok http 8000
```

You'll get a public URL like: `https://abc123.ngrok.io`

---

## 📊 Comparison Matrix

| Feature | Render | Railway | Fly.io | Replit |
|---------|--------|---------|--------|--------|
| **Free Hours** | 750/mo | $5 credit | Always | Always |
| **Persistent DB** | ✅ Yes | ✅ Yes | ✅ Yes | ⚠️ Limited |
| **Auto-deploy** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Custom Domain** | ✅ Free | ✅ Free | ✅ Free | 💰 Paid |
| **SSL** | ✅ Free | ✅ Free | ✅ Free | ✅ Free |
| **Setup Difficulty** | ⭐ Easy | ⭐⭐ Medium | ⭐⭐⭐ Advanced | ⭐ Very Easy |

---

## 🎯 Recommended: Render.com

**Best for production** - Use Render.com:
- Most generous free tier
- Persistent storage included
- Auto-deploys from Git
- Professional setup

---

## 🔧 Post-Deployment

### 1. Test Your API

```bash
# Replace with your URL
export API_URL="https://your-app.onrender.com"

# Submit job
curl -X POST $API_URL/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://medium.com/@anios4991/all-about-closures-and-functions-for-swift-interview-9d7cb4d9a014"}'

# Get stats
curl $API_URL/api/stats

# View all Q&As
curl $API_URL/api/qa?limit=10
```

### 2. Monitor Usage

- **Render**: Dashboard → Your Service → Metrics
- **Railway**: Dashboard → Your Project → Metrics
- **Fly.io**: `fly dashboard`

### 3. View Logs

```bash
# Render
render logs --tail

# Railway
railway logs

# Fly.io
fly logs
```

---

## 💡 Usage Examples

### Web Interface

Visit: `https://your-app.onrender.com`

### API Integration

```python
import requests

API_URL = "https://your-app.onrender.com"

# Submit URL
response = requests.post(
    f"{API_URL}/api/scrape",
    json={"url": "https://medium.com/@user/ios-interview"}
)
job = response.json()
print(f"Job ID: {job['job_id']}")

# Wait and get results
import time
time.sleep(30)

results = requests.get(f"{API_URL}/api/jobs/{job['job_id']}/results")
qa_pairs = results.json()

for qa in qa_pairs:
    print(f"Q: {qa['question']}")
    print(f"A: {qa['answer']}\n")
```

### JavaScript/Node.js

```javascript
const API_URL = 'https://your-app.onrender.com';

// Submit URL
const response = await fetch(`${API_URL}/api/scrape`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'https://medium.com/@user/ios-interview'
  })
});

const job = await response.json();
console.log('Job ID:', job.job_id);

// Get results after processing
const results = await fetch(`${API_URL}/api/jobs/${job.job_id}/results`);
const qaPairs = await results.json();
console.log('Q&A Pairs:', qaPairs);
```

---

## 🚨 Important Notes

### API Rate Limits (Free Tiers):

- **Firecrawl**: 500 requests/month
- **Groq**: 14,400 requests/day

### Monitor Your Usage:
- Track at firecrawl.dev/dashboard
- Track at console.groq.com

### Cold Starts:
Free tiers may "sleep" after inactivity:
- **Render**: After 15 minutes
- **Railway**: After 30 minutes
- **Fly.io**: No sleep

**Solution**: First request takes 10-30 seconds to wake up.

---

## 🎉 You're Done!

Your iOS Q&A Scraper API is now live and free!

**Share your API:**
```
https://your-app.onrender.com/docs
```

**Need help?** Check the logs or redeploy! 🚀

