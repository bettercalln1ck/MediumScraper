# 📚 Swagger UI Guide

## 🌐 Access Links

### **Interactive Swagger UI**
👉 **https://misleading-aile-personalnikhil-27cb1e20.koyeb.app/docs**

### Alternative ReDoc
https://misleading-aile-personalnikhil-27cb1e20.koyeb.app/redoc

### OpenAPI Specification
https://misleading-aile-personalnikhil-27cb1e20.koyeb.app/openapi.json

---

## ✨ What is Swagger UI?

Swagger UI is an **interactive API documentation** tool that lets you:
- 📖 **Read** detailed documentation for every endpoint
- 🧪 **Test** API endpoints directly from your browser
- 👀 **See** live request/response examples
- 📊 **Understand** data models and schemas

No Postman or curl needed - everything runs in your browser!

---

## 🎯 Quick Start Tutorial

### Step 1: Open Swagger UI
Go to: https://misleading-aile-personalnikhil-27cb1e20.koyeb.app/docs

### Step 2: Try Your First Request

1. **Find the "Discovery" section** (green tag)
2. **Click** on `GET /api/discover`
3. **Click** the blue "Try it out" button
4. **Set** `count` to `3`
5. **Click** "Execute"
6. **See** 3 random iOS article URLs appear! 🎉

### Step 3: Scrape a Random Article

1. **Find** `POST /api/scrape/random`
2. **Click** "Try it out"
3. **Set** `count` to `1`
4. **Click** "Execute"
5. **Copy** the `job_id` from the response

### Step 4: Check Job Status

1. **Find** `GET /api/jobs/{job_id}`
2. **Click** "Try it out"
3. **Paste** your job_id
4. **Click** "Execute"
5. **Watch** the status (queued → processing → completed)

### Step 5: Get Results

1. **Find** `GET /api/jobs/{job_id}/results`
2. **Paste** your job_id
3. **Click** "Execute"
4. **See** all extracted Q&A pairs! 🎊

---

## 📂 API Sections (Tags)

### 🔍 **Discovery**
Find iOS articles on Medium

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/discover` | GET | Preview random iOS articles without scraping |
| `/api/scrape/random` | POST | Discover AND scrape random articles |

### 🚀 **Scraping**
Extract Q&A from specific URLs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/scrape` | POST | Scrape a specific Medium article URL |

### 📊 **Jobs**
Track scraping progress

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/jobs/{job_id}` | GET | Check job status and progress |
| `/api/jobs/{job_id}/results` | GET | Get extracted Q&A pairs |

### 📋 **Q&A**
Access the master database

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/qa` | GET | Get all Q&A pairs (with pagination) |

### ⚙️ **System**
Health and statistics

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Landing page (HTML) |
| `/health` | GET | Health check |
| `/api/stats` | GET | System statistics |

---

## 🎨 Swagger UI Features

### 1. **Try it Out**
Every endpoint has a "Try it out" button that lets you:
- Fill in parameters
- Execute real API calls
- See actual responses

### 2. **Request Body Editor**
For POST endpoints:
- Click "Try it out"
- Edit the JSON request body
- See the schema/example

### 3. **Response Viewer**
After clicking "Execute":
- See HTTP status code (200, 400, 500, etc.)
- View response headers
- Read response body (JSON)
- Download response

### 4. **Schema Browser**
At the bottom of each endpoint:
- View request schema
- View response schema
- See required vs optional fields
- Understand data types

### 5. **Code Examples**
Click "curl" tab to see:
- Ready-to-copy curl commands
- Example with your parameters
- Use in terminal/scripts

---

## 📖 Example Workflows

### Workflow 1: Scrape Random Articles

```
1. POST /api/scrape/random?count=5
   → Get 5 job IDs

2. For each job_id:
   GET /api/jobs/{job_id}
   → Check status

3. When completed:
   GET /api/jobs/{job_id}/results
   → Get Q&A pairs
```

### Workflow 2: Scrape Specific URL

```
1. POST /api/scrape
   Body: {"url": "https://medium.com/@user/article"}
   → Get job_id

2. Poll GET /api/jobs/{job_id}
   → Wait for completion

3. GET /api/jobs/{job_id}/results
   → Get extracted Q&A
```

### Workflow 3: Build Q&A Dataset

```
1. POST /api/scrape/random?count=20
   → Scrape 20 random articles

2. Wait for all to complete

3. GET /api/qa?limit=1000
   → Download entire Q&A dataset
```

---

## 🔑 Understanding Responses

### Job Response
```json
{
  "job_id": "uuid-here",
  "status": "queued",
  "message": "Job submitted successfully"
}
```

### Job Status Response
```json
{
  "id": "uuid",
  "url": "https://medium.com/...",
  "status": "completed",
  "qa_count": 12,
  "error": null,
  "created_at": "2025-12-27T...",
  "completed_at": "2025-12-27T..."
}
```

**Status Values:**
- `queued` - Waiting to start
- `processing` - Currently scraping
- `completed` - Done successfully
- `failed` - Error occurred

### Q&A Results Response
```json
[
  {
    "question": "What is SwiftUI?",
    "answer": "SwiftUI is Apple's declarative framework...",
    "source_url": "https://medium.com/...",
    "timestamp": "2025-12-27T..."
  }
]
```

---

## 🎓 Pro Tips

### Tip 1: Use Pagination
```
GET /api/qa?limit=100&offset=0   (first 100)
GET /api/qa?limit=100&offset=100 (next 100)
```

### Tip 2: Monitor with Stats
```
GET /api/stats
```
Returns:
- Total jobs processed
- Success/failure rates
- Total Q&A collected

### Tip 3: Health Checks
```
GET /health
```
Use for uptime monitoring (UptimeRobot, etc.)

### Tip 4: Download Swagger Spec
```
GET /openapi.json
```
- Import into Postman
- Generate client SDKs
- Use in other tools

---

## 🌟 Advanced Features

### Custom Descriptions
Every endpoint has:
- **Summary** - One-line description
- **Description** - Detailed explanation
- **Parameters** - Type, format, constraints
- **Responses** - Status codes and schemas

### Tags for Organization
Endpoints grouped by:
- Discovery
- Scraping  
- Jobs
- Q&A
- System

### Data Models
Click "Schemas" at bottom to see:
- `UrlSubmission`
- `JobResponse`
- And more...

---

## 🔗 Integration Examples

### In Python
```python
import requests

# Discover articles
response = requests.get(
    "https://your-api.com/api/discover?count=5"
)
urls = response.json()["urls"]

# Scrape article
response = requests.post(
    "https://your-api.com/api/scrape",
    json={"url": urls[0]}
)
job_id = response.json()["job_id"]
```

### In JavaScript
```javascript
// Discover articles
const response = await fetch(
  'https://your-api.com/api/discover?count=5'
);
const data = await response.json();

// Scrape article
const scrapeResponse = await fetch(
  'https://your-api.com/api/scrape',
  {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({url: data.urls[0]})
  }
);
const job = await scrapeResponse.json();
```

### Using curl (from Swagger)
```bash
curl -X POST "https://your-api.com/api/scrape/random?count=3" \
  -H "accept: application/json"
```

---

## 🎨 Customization

Your Swagger UI includes:
- ✅ Custom title and description
- ✅ Version information (2.0.0)
- ✅ Contact/license info
- ✅ Organized endpoint tags
- ✅ Rich markdown documentation
- ✅ Examples for all endpoints

---

## 📱 Mobile Friendly

Swagger UI works on:
- 💻 Desktop browsers
- 📱 Mobile browsers
- 📟 Tablets
- All screen sizes

---

## 🆘 Need Help?

### Common Issues

**Can't see endpoints?**
- Refresh the page
- Clear browser cache
- Check URL is correct

**"Try it out" not working?**
- Check network connection
- Verify API is deployed
- Check for CORS errors in console

**Responses slow?**
- Firecrawl/Groq API rate limits
- Large articles take longer
- Check `/health` endpoint

---

## 🎉 You're Ready!

**Open Swagger UI now:**
👉 https://misleading-aile-personalnikhil-27cb1e20.koyeb.app/docs

**Try it yourself and start scraping iOS Q&A!** 🚀

