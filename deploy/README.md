# 🚀 iOS Q&A Scraper - Free Deployment Package

**Your complete API ready to deploy on FREE hosting!**

---

## 📦 What You Have

A simplified, production-ready API that:
- ✅ Scrapes Medium articles
- ✅ Extracts iOS Q&A with AI (Groq)
- ✅ Uses Firecrawl for reliable scraping
- ✅ Auto-deduplicates questions
- ✅ Stores in SQLite database
- ✅ **Works on FREE hosting platforms**

---

## 🎯 Quick Start (Choose One)

### Option 1: Render.com (RECOMMENDED) ⭐

**Easiest + Best Free Tier**

1. **Create GitHub repo:**
   ```bash
   cd /Users/nikhilkumar/Downloads/MediumScraper
   git init
   git add .
   git commit -m "Initial commit"
   gh repo create ios-qa-scraper --public --source=. --push
   ```

2. **Deploy on Render:**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repo
   - It auto-detects `render.yaml`
   - Click "Apply"
   - **Done!** ✅

3. **Your API is live:**
   ```
   https://ios-qa-scraper.onrender.com
   ```

---

### Option 2: Railway.app

**Simple CLI Deployment**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
cd /Users/nikhilkumar/Downloads/MediumScraper/deploy
railway login
railway init
railway up

# Get your URL
railway domain
```

---

### Option 3: Fly.io

**Global Edge Network**

```bash
# Install Fly CLI
brew install flyctl

# Deploy
cd /Users/nikhilkumar/Downloads/MediumScraper/deploy
fly auth login
fly launch
```

---

### Option 4: Test Locally First

```bash
cd /Users/nikhilkumar/Downloads/MediumScraper/deploy

# Install dependencies
pip3 install -r requirements.txt

# Run API
python3 simple_api.py

# Visit
open http://localhost:8000
```

---

## 📖 API Documentation

Once deployed, visit: `https://your-app.onrender.com/docs`

### Key Endpoints:

#### 1. Submit URL for Scraping
```bash
POST /api/scrape
Content-Type: application/json

{
  "url": "https://medium.com/@user/ios-interview-article"
}

# Response:
{
  "job_id": "abc-123",
  "status": "queued",
  "message": "Job submitted successfully"
}
```

#### 2. Check Job Status
```bash
GET /api/jobs/{job_id}

# Response:
{
  "id": "abc-123",
  "url": "https://...",
  "status": "completed",
  "qa_count": 15,
  "created_at": "2025-12-26T10:00:00"
}
```

#### 3. Get Results
```bash
GET /api/jobs/{job_id}/results

# Response:
[
  {
    "question": "What is ARC in Swift?",
    "answer": "Automatic Reference Counting...",
    "source_url": "https://...",
    "timestamp": "2025-12-26T10:00:00"
  },
  ...
]
```

#### 4. Get All Q&As
```bash
GET /api/qa?limit=50&offset=0

# Returns paginated Q&A pairs
```

#### 5. Get Statistics
```bash
GET /api/stats

# Response:
{
  "total_qa_pairs": 150,
  "total_jobs": 45,
  "completed_jobs": 42,
  "queue_size": 3
}
```

---

## 💡 Usage Examples

### Python

```python
import requests
import time

API_URL = "https://your-app.onrender.com"

# Submit URL
response = requests.post(
    f"{API_URL}/api/scrape",
    json={"url": "https://medium.com/@user/ios-interview"}
)
job = response.json()
print(f"Job submitted: {job['job_id']}")

# Wait for processing
time.sleep(30)

# Get results
results = requests.get(f"{API_URL}/api/jobs/{job['job_id']}/results")
qa_pairs = results.json()

for qa in qa_pairs:
    print(f"\nQ: {qa['question']}")
    print(f"A: {qa['answer']}")
```

### cURL

```bash
# Submit
curl -X POST https://your-app.onrender.com/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://medium.com/@user/ios-interview"}'

# Check status
curl https://your-app.onrender.com/api/jobs/abc-123

# Get results
curl https://your-app.onrender.com/api/jobs/abc-123/results

# Get all Q&As
curl https://your-app.onrender.com/api/qa?limit=10
```

### JavaScript/Fetch

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

// Wait and get results
await new Promise(resolve => setTimeout(resolve, 30000));

const results = await fetch(`${API_URL}/api/jobs/${job.job_id}/results`);
const qaPairs = await results.json();
console.log('Q&A Pairs:', qaPairs);
```

---

## 🎯 Features

### ✅ What Works:
- Submit Medium URLs for scraping
- Automatic Q&A extraction using AI
- Real-time job status tracking
- Deduplication of similar questions
- Persistent SQLite database
- RESTful API with OpenAPI docs
- Background job processing
- Health checks

### 📊 Free Tier Limits:
- **Render.com**: 750 hours/month (always on)
- **Firecrawl**: 500 scrapes/month
- **Groq**: 14,400 API calls/day

---

## 🔧 Configuration

### Environment Variables:

Set these in your hosting platform:

```bash
GROQ_API_KEY=your-groq-api-key-here
FIRECRAWL_API_KEY=your-firecrawl-api-key-here
DATABASE_PATH=/opt/render/project/data/scraper.db
PORT=8000
```

---

## 📈 Monitoring

### View Logs:

**Render:**
```bash
# Via web dashboard or CLI
render logs --tail
```

**Railway:**
```bash
railway logs
```

**Fly.io:**
```bash
fly logs
```

### Check Health:

```bash
curl https://your-app.onrender.com/health
```

---

## 🚨 Troubleshooting

### API returns 404:
- Check if service is deployed correctly
- Visit `/health` endpoint first

### Jobs stuck in "queued":
- Background worker might be starting
- Wait 30 seconds and check again
- Check logs for errors

### "Failed to scrape" errors:
- Check Firecrawl API key is correct
- Verify you have remaining credits
- Check URL is a valid Medium article

### Database errors:
- Ensure persistent disk is mounted (Render.com)
- Check DATABASE_PATH is correct

---

## 💰 Cost Breakdown

**100% FREE for moderate use:**

- **Hosting**: Free (Render: 750 hrs/month)
- **Firecrawl**: Free tier (500/month)
- **Groq**: Free tier (14,400/day)

**Total Monthly Capacity:**
- ~500 articles/month
- ~2,500 Q&A pairs extracted
- **$0 cost**

---

## 📚 Files Included

```
deploy/
├── simple_api.py       # Main API server
├── requirements.txt    # Python dependencies
├── render.yaml        # Render.com config
├── railway.json       # Railway.app config
├── fly.toml          # Fly.io config
├── Procfile          # General config
├── vercel.json       # Vercel config
├── DEPLOY_GUIDE.md   # Detailed deployment guide
├── README.md         # This file
└── .gitignore        # Git ignore rules
```

---

## 🎉 Next Steps

1. **Deploy** using your chosen platform
2. **Test** with a Medium article URL
3. **Integrate** into your workflow
4. **Share** your API with others!

---

## 🆘 Need Help?

Check `DEPLOY_GUIDE.md` for:
- Detailed platform-specific instructions
- Common issues and solutions
- Advanced configuration options

---

**Your iOS Q&A Scraper API is ready to deploy!** 🚀

Choose a platform above and you'll be live in 5 minutes!

