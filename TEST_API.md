# 🧪 Testing Your Deployed API

## 📍 Step 1: Get Your API URL

### In Koyeb Dashboard:

1. Go to: https://app.koyeb.com
2. Click on your app
3. Look for the **"Public URL"** or **"Domain"** section
4. Copy your URL - it looks like:
   ```
   https://your-app-name-your-org.koyeb.app
   ```

---

## ✅ Step 2: Test Health Check (Browser)

The easiest test - just open in your browser:

```
https://your-app-name.koyeb.app/health
```

**Expected Response:**
```json
{
  "status": "healthy"
}
```

✅ If you see this, your API is working!

---

## 📊 Step 3: Test Statistics Endpoint

### In Browser:
```
https://your-app-name.koyeb.app/stats
```

**Expected Response:**
```json
{
  "total_questions": 0,
  "total_processed_urls": 0,
  "last_updated": null
}
```

(Will show 0 initially since you haven't scraped anything yet)

---

## 🔍 Step 4: Test Scraping (Terminal/Command Line)

### Using curl:

```bash
curl -X POST "https://your-app-name.koyeb.app/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://medium.com/@swift_teacher/ios-interview-questions-and-answers-2024-swift-uikit-swiftui-arc-2d1d2f9f5e8a"
  }'
```

**Expected Response:**
```json
{
  "job_id": "abc123...",
  "status": "processing",
  "message": "URL submitted for processing"
}
```

---

## 🎯 Step 5: Check Scraping Results

### Get All Q&A Pairs:

**In Browser:**
```
https://your-app-name.koyeb.app/qa
```

**Using curl:**
```bash
curl https://your-app-name.koyeb.app/qa
```

**Expected Response:**
```json
{
  "count": 1,
  "data": [
    {
      "question": "What is ARC in iOS?",
      "answer": "Automatic Reference Counting...",
      "source_url": "https://medium.com/...",
      "timestamp": "2025-12-27T10:30:00"
    }
  ]
}
```

---

## 🌐 Step 6: Test in Browser (Easy Visual Testing)

### Using Your Browser's Developer Tools:

1. Open your browser
2. Press `F12` or right-click → "Inspect"
3. Go to **"Console"** tab
4. Paste this JavaScript:

```javascript
// Test health
fetch('https://your-app-name.koyeb.app/health')
  .then(r => r.json())
  .then(d => console.log('Health:', d));

// Test stats
fetch('https://your-app-name.koyeb.app/stats')
  .then(r => r.json())
  .then(d => console.log('Stats:', d));

// Test scraping
fetch('https://your-app-name.koyeb.app/scrape', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    url: 'https://medium.com/@swift_teacher/ios-interview-questions-and-answers-2024-swift-uikit-swiftui-arc-2d1d2f9f5e8a'
  })
})
  .then(r => r.json())
  .then(d => console.log('Scrape Result:', d));
```

---

## 📱 Step 7: Test with Postman (Optional)

### Download Postman:
https://www.postman.com/downloads/

### Create Requests:

**1. Health Check:**
- Method: `GET`
- URL: `https://your-app-name.koyeb.app/health`
- Click "Send"

**2. Submit URL to Scrape:**
- Method: `POST`
- URL: `https://your-app-name.koyeb.app/scrape`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
  ```json
  {
    "url": "https://medium.com/@author/article-url"
  }
  ```
- Click "Send"

**3. Get All Q&A:**
- Method: `GET`
- URL: `https://your-app-name.koyeb.app/qa`
- Click "Send"

---

## 📋 All Available Endpoints

### 1. **Health Check**
```
GET /health
```
Response: `{"status": "healthy"}`

### 2. **Get Statistics**
```
GET /stats
```
Response: Total Q&A count, processed URLs, last updated

### 3. **Submit URL to Scrape**
```
POST /scrape
Body: {"url": "https://medium.com/article-url"}
```
Response: Job ID and status

### 4. **Get All Q&A Pairs**
```
GET /qa
```
Response: Array of all scraped questions and answers

### 5. **API Documentation (Swagger)**
```
GET /docs
```
Opens interactive API documentation in browser

---

## 🎯 Quick Test Script (Copy & Paste)

Save this as `test_api.sh` and run it:

```bash
#!/bin/bash

# Replace with your actual Koyeb URL
API_URL="https://your-app-name.koyeb.app"

echo "🧪 Testing API..."
echo ""

echo "1️⃣ Health Check:"
curl -s "$API_URL/health" | python3 -m json.tool
echo ""

echo "2️⃣ Stats:"
curl -s "$API_URL/stats" | python3 -m json.tool
echo ""

echo "3️⃣ Submitting URL to scrape:"
curl -s -X POST "$API_URL/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://medium.com/@swift_teacher/ios-interview-questions-and-answers-2024-swift-uikit-swiftui-arc-2d1d2f9f5e8a"}' | python3 -m json.tool
echo ""

echo "4️⃣ Waiting 10 seconds for scraping..."
sleep 10

echo "5️⃣ Getting Q&A results:"
curl -s "$API_URL/qa" | python3 -m json.tool
echo ""

echo "✅ Test complete!"
```

Make it executable and run:
```bash
chmod +x test_api.sh
./test_api.sh
```

---

## 🔍 View Live Logs in Koyeb

To see what's happening in real-time:

1. Go to **Koyeb dashboard**
2. Click your app
3. Go to **"Logs"** tab
4. See live requests, responses, errors

When you submit a URL to scrape, you'll see:
```
INFO: Starting scraping for URL: https://...
INFO: Extracted 5 Q&A pairs
INFO: Saved to database
```

---

## 🎨 Interactive API Docs (Swagger)

Koyeb includes automatic API documentation!

### Access it:
```
https://your-app-name.koyeb.app/docs
```

This opens an interactive interface where you can:
- ✅ See all endpoints
- ✅ Try requests directly in browser
- ✅ See request/response schemas
- ✅ Test with different parameters

---

## 💡 Example Test URLs

Here are some good Medium articles about iOS to test with:

```
https://medium.com/@swift_teacher/ios-interview-questions-and-answers-2024-swift-uikit-swiftui-arc-2d1d2f9f5e8a

https://medium.com/ios-os-x-development/50-ios-interview-questions-and-answers-part-1-6d0b0e1b0c9c

https://medium.com/@malekbenboubaker/ios-interview-questions-2024-part-1-ef9c8c9e9e9e
```

---

## ✅ What Success Looks Like

### Healthy API:
- `/health` returns `{"status": "healthy"}`
- `/stats` returns valid JSON
- `/docs` opens Swagger UI
- Logs show no errors

### Working Scraper:
- POST to `/scrape` returns job_id
- After 10-20 seconds, `/qa` shows extracted questions
- Logs show "Extracted X Q&A pairs"

### If Something's Wrong:
- Check Koyeb logs for errors
- Verify environment variables are set
- Make sure API keys are correct
- Try redeploying

---

## 🚀 Quick Start Test (30 seconds)

1. **Get your URL** from Koyeb dashboard
2. **Open in browser:**
   ```
   https://your-app-name.koyeb.app/docs
   ```
3. **Try the health endpoint** - click "Try it out" → "Execute"
4. **Submit a URL** - use the POST /scrape endpoint with a Medium URL
5. **Check results** - use GET /qa endpoint

Done! Your API is working! 🎉

---

## 📞 Need Help?

If any test fails:
1. Check Koyeb logs
2. Verify environment variables
3. Make sure deployment status is "Running" (green)
4. Try redeploying

Let me know what error you see! 💬

