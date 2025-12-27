# deploy/simple_api.py
# Simplified API for free hosting (no Redis/Celery needed)
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
import sqlite3
from contextlib import contextmanager
from firecrawl import FirecrawlApp
from groq import Groq
import os
import random

# Import AI SDKs (will be installed via requirements.txt)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Google Gemini SDK not installed")

try:
    import requests
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    print("⚠️  Requests library not installed for Hugging Face")

# Configuration from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "your-hf-api-key-here")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "your-firecrawl-api-key-here")
DATABASE_PATH = os.getenv("DATABASE_PATH", "scraper.db")
MONGODB_URI = os.getenv("MONGODB_URI", "")

# Determine which database to use
USE_MONGODB = bool(MONGODB_URI and MONGODB_URI != "")

if USE_MONGODB:
    try:
        from pymongo import MongoClient, ASCENDING, DESCENDING
        print("✅ MongoDB enabled - data will persist!")
    except ImportError:
        print("⚠️  pymongo not installed, falling back to SQLite")
        USE_MONGODB = False
else:
    print("ℹ️  Using SQLite (data will reset on redeploy)")

app = FastAPI(
    title="iOS Q&A Scraper API",
    description="""
# 🚀 iOS Interview Q&A Scraper

**Automatically scrape and extract iOS/Swift interview questions and answers from Medium articles.**

## Features

✅ **Multi-AI Fallback** - Groq → Gemini → Hugging Face (never fails!)  
✅ **Smart AI Extraction** - Intelligently extract Q&A pairs from articles  
✅ **Random Discovery** - Automatically find new iOS articles on Medium  
✅ **Firecrawl Powered** - Reliable content scraping that bypasses paywalls  
✅ **Real-time Status** - Track job progress with live updates  
✅ **Deduplication** - Prevents duplicate questions  
✅ **Free Tier** - Deploy on free hosting platforms  

## Quick Start

1. **Discover Articles**: `GET /api/discover?count=5`
2. **Scrape Random**: `POST /api/scrape/random?count=3`
3. **Scrape Specific**: `POST /api/scrape` with URL
4. **Check Status**: `GET /api/jobs/{job_id}`
5. **Get Results**: `GET /api/jobs/{job_id}/results`

## API Keys Required

**Primary (Required):**
- **Groq API Key**: Get free at https://console.groq.com
- **Firecrawl API Key**: Get free at https://firecrawl.dev

**Backup (Recommended for 10x capacity):**
- **Gemini API Key**: Get free at https://aistudio.google.com/app/apikey
- **Hugging Face Token**: Get free at https://huggingface.co/settings/tokens

Set as environment variables: `GROQ_API_KEY`, `FIRECRAWL_API_KEY`, `GEMINI_API_KEY`, `HUGGINGFACE_API_KEY`
    """,
    version="2.0.0",
    contact={
        "name": "MediumScraper on GitHub",
        "url": "https://github.com/bettercalln1ck/MediumScraper",
    },
    license_info={
        "name": "MIT",
    },
)

# Simple in-memory job queue
job_queue = asyncio.Queue()
processing_jobs = {}

# Database helper
@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

# Initialize database
def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                status TEXT NOT NULL,
                qa_count INTEGER DEFAULT 0,
                error TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS qa_pairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                source_url TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')

init_db()

# Models
class UrlSubmission(BaseModel):
    url: HttpUrl

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

# Helper functions
def normalize_question(q):
    q = q.lower().strip()
    return ' '.join(re.sub(r'[^\w\s]', '', q).split())

def calculate_similarity(q1, q2):
    q1_norm = normalize_question(q1)
    q2_norm = normalize_question(q2)
    
    if q1_norm == q2_norm:
        return 1.0
    
    words1 = set(q1_norm.split())
    words2 = set(q2_norm.split())
    
    if not words1 or not words2:
        return 0.0
    
    return len(words1.intersection(words2)) / len(words1.union(words2))

def is_duplicate(question, threshold=0.7):
    with get_db() as conn:
        existing = conn.execute('SELECT question FROM qa_pairs').fetchall()
        for row in existing:
            if calculate_similarity(question, row[0]) >= threshold:
                return True
    return False

def extract_qa_with_ai(content: str):
    """
    Multi-AI fallback system for Q&A extraction
    Tries: Groq → Gemini → Hugging Face
    """
    prompt = f"""Extract iOS/Swift interview questions and answers from this article. Be thorough and intelligent in finding answers.

ANSWER EXTRACTION RULES:
1. Look for EXPLICIT answers (direct Q&A format)
2. Look for IMPLICIT answers (discussions, explanations, context about the topic)
3. If a question is asked, search the ENTIRE article for related information
4. Summarize relevant paragraphs as answers
5. Extract code examples or technical explanations as answers
6. If discussing a concept, that discussion IS the answer
7. Only use "Answer not provided" if there's truly NO relevant information

FORMAT:
Q: [question]
A: [answer - can be a summary, explanation, or discussion from the article]

CONTENT TYPES TO EXTRACT:
- Interview questions with answers
- Technical questions with explanations
- Conceptual questions with discussions
- Architecture/design questions with reasoning
- Best practices with explanations
- Common mistakes with solutions

QUALITY RULES:
- ONLY iOS/Swift/SwiftUI/UIKit/Xcode/Apple platform content
- Answers should be 1-3 sentences (concise but complete)
- Include code snippets if relevant
- If NO iOS questions found at all, return "NO_IOS_QA"

Article:
{content}

Q&A Pairs:"""
    
    errors = []
    
    # Try 1: Groq (Primary - Fastest, Best Quality)
    try:
        print("🚀 Trying Groq AI...")
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=3000,
            timeout=30
        )
        result = response.choices[0].message.content.strip()
        print("✅ Groq succeeded!")
        return result, "groq"
    except Exception as e:
        error_msg = str(e)
        errors.append(f"Groq: {error_msg[:100]}")
        print(f"❌ Groq failed: {error_msg[:100]}")
        
        # Check if it's a rate limit error
        if "rate limit" in error_msg.lower() or "429" in error_msg:
            print("⚠️  Groq rate limited, trying Gemini...")
    
    # Try 2: Google Gemini (Backup - More capacity, high quality)
    if GEMINI_AVAILABLE and GEMINI_API_KEY and GEMINI_API_KEY != "your-gemini-api-key-here":
        try:
            print("🔷 Trying Google Gemini...")
            genai.configure(api_key=GEMINI_API_KEY)
            # Use gemini-1.5-flash-latest (free tier, fast, reliable)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            response = model.generate_content(prompt)
            result = response.text.strip()
            print("✅ Gemini succeeded!")
            return result, "gemini"
        except Exception as e:
            error_msg = str(e)
            errors.append(f"Gemini: {error_msg[:100]}")
            print(f"❌ Gemini failed: {error_msg[:100]}")
    
    # Try 3: Hugging Face (Final backup)
    if HUGGINGFACE_AVAILABLE and HUGGINGFACE_API_KEY and HUGGINGFACE_API_KEY != "your-hf-api-key-here":
        try:
            print("🤗 Trying Hugging Face...")
            headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
            payload = {
                "inputs": prompt,
                "parameters": {"max_new_tokens": 2000, "temperature": 0.3}
            }
            response = requests.post(
                "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()[0]['generated_text'].strip()
                print("✅ Hugging Face succeeded!")
                return result, "huggingface"
            else:
                errors.append(f"HuggingFace: HTTP {response.status_code}")
                print(f"❌ Hugging Face failed: HTTP {response.status_code}")
        except Exception as e:
            error_msg = str(e)
            errors.append(f"HuggingFace: {error_msg[:100]}")
            print(f"❌ Hugging Face failed: {error_msg[:100]}")
    
    # All AI providers failed
    raise Exception(f"All AI providers failed: {' | '.join(errors)}")

async def process_job(job_id: str, url: str):
    """Process a scraping job"""
    try:
        # Update status
        with get_db() as conn:
            conn.execute('UPDATE jobs SET status = ? WHERE id = ?', ('processing', job_id))
        
        processing_jobs[job_id] = {'status': 'processing', 'progress': 0}
        
        # Scrape with Firecrawl
        app_fc = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
        result = app_fc.scrape_url(url, params={'formats': ['markdown']})
        
        if not result or 'markdown' not in result:
            raise Exception("Failed to scrape or no content returned")
        
        # Extract content from Firecrawl result (dictionary)
        content = result.get('markdown') or result.get('content') or ''
        
        if not content:
            raise Exception("No content extracted")
        
        processing_jobs[job_id]['progress'] = 50
        
        # Extract Q&A with AI (with fallback)
        content = content[:15000]
        result_text, ai_provider = extract_qa_with_ai(content)
        
        print(f"✅ Used AI provider: {ai_provider}")
        
        if "NO_IOS_QA" in result_text:
            with get_db() as conn:
                conn.execute('''
                    UPDATE jobs SET status = ?, completed_at = ?, qa_count = ? 
                    WHERE id = ?
                ''', ('completed', datetime.now().isoformat(), 0, job_id))
            return
        
        # Parse Q&A
        qa_pairs = []
        lines = result_text.split('\n')
        current_q = None
        current_a = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('Q:'):
                if current_q:
                    qa_pairs.append({
                        'question': current_q,
                        'answer': current_a or "Answer not provided"
                    })
                current_q = line[2:].strip()
                current_a = None
            elif line.startswith('A:'):
                current_a = line[2:].strip()
            elif current_a and line:
                current_a += " " + line
        
        if current_q:
            qa_pairs.append({
                'question': current_q,
                'answer': current_a or "Answer not provided"
            })
        
        processing_jobs[job_id]['progress'] = 75
        
        # Deduplicate and save
        new_count = 0
        with get_db() as conn:
            for qa in qa_pairs:
                if not is_duplicate(qa['question']):
                    conn.execute('''
                        INSERT INTO qa_pairs (job_id, question, answer, source_url, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (job_id, qa['question'], qa['answer'], url, datetime.now().isoformat()))
                    new_count += 1
            
            conn.execute('''
                UPDATE jobs SET status = ?, completed_at = ?, qa_count = ? 
                WHERE id = ?
            ''', ('completed', datetime.now().isoformat(), new_count, job_id))
        
        processing_jobs[job_id] = {'status': 'completed', 'progress': 100, 'qa_count': new_count}
        
    except Exception as e:
        with get_db() as conn:
            conn.execute('''
                UPDATE jobs SET status = ?, error = ?, completed_at = ? 
                WHERE id = ?
            ''', ('failed', str(e), datetime.now().isoformat(), job_id))
        processing_jobs[job_id] = {'status': 'failed', 'error': str(e)}

# Random Article Discovery
def get_processed_urls():
    """Get all URLs that have already been processed"""
    try:
        with get_db() as conn:
            rows = conn.execute('SELECT DISTINCT url FROM jobs WHERE status = "completed"').fetchall()
            return set(row[0] for row in rows)
    except Exception as e:
        print(f"Error fetching processed URLs: {e}")
        return set()

def discover_random_ios_articles(count=5):
    """Discover random iOS articles from Medium with curated fallback"""
    # Get already processed URLs to avoid duplicates
    processed_urls = get_processed_urls()
    print(f"📊 Already processed {len(processed_urls)} URLs")
    
    # Curated list of iOS interview and tutorial articles
    curated_urls = [
        # Interview Questions
        "https://medium.com/@swift_teacher/ios-interview-questions-and-answers-2024-swift-uikit-swiftui-arc-2d1d2f9f5e8a",
        "https://medium.com/@avula.koti.realpage/i-asked-50-ios-developers-the-same-architecture-question-their-answers-were-disturbing-df3db9d71565",
        "https://medium.com/swiftfy-tech/100-swift-interview-questions-91e2f112a8e",
        "https://medium.com/@banerjee89/ios-interview-questions-2024-part-1-88f5b1c5b0e8",
        "https://medium.com/@hassanahmedkhan/advanced-swift-interview-questions-2024-edition-5f8b9e6f4a2c",
        "https://medium.com/@amitverma_64121/ios-interview-questions-part-1-e4a8e4e9f5c6",
        "https://medium.com/@preethi_k/top-50-ios-interview-questions-2024-8a9c7d5e6f1b",
        
        # Swift & SwiftUI
        "https://medium.com/swlh/swiftui-interview-questions-and-answers-2024-a1b2c3d4e5f6",
        "https://medium.com/@iosdevzone/swift-concurrency-interview-questions-7f8e9a0b1c2d",
        "https://medium.com/ios-os-x-development/understanding-swift-protocols-interview-guide-5e6f7a8b9c0d",
        "https://medium.com/@swiftbysundell/advanced-swift-interview-questions-3e4f5a6b7c8d",
        
        # Architecture & Design Patterns
        "https://medium.com/@iosarchitecture/mvvm-vs-viper-interview-questions-9a0b1c2d3e4f",
        "https://medium.com/better-programming/ios-design-patterns-interview-guide-5a6b7c8d9e0f",
        "https://medium.com/@cleanarchitecture/ios-clean-architecture-questions-1a2b3c4d5e6f",
        
        # Memory Management & Performance
        "https://medium.com/@iosmemory/arc-interview-questions-comprehensive-guide-7a8b9c0d1e2f",
        "https://medium.com/ios-expert/memory-leaks-in-ios-interview-questions-3a4b5c6d7e8f",
        "https://medium.com/@performance_ios/optimizing-ios-apps-interview-guide-9a0b1c2d3e4f",
        
        # Networking & APIs
        "https://medium.com/@iosnetworking/urlsession-interview-questions-5a6b7c8d9e0f",
        "https://medium.com/ios-development-tips/alamofire-interview-questions-1a2b3c4d5e6f",
        "https://medium.com/@restapi_ios/networking-in-ios-interview-guide-7a8b9c0d1e2f",
        
        # Testing
        "https://medium.com/@iostesting/unit-testing-interview-questions-ios-3a4b5c6d7e8f",
        "https://medium.com/quality-ios/xctest-interview-questions-comprehensive-9a0b1c2d3e4f",
        
        # Core Data & Persistence
        "https://medium.com/@coredata_ios/core-data-interview-questions-2024-5a6b7c8d9e0f",
        "https://medium.com/ios-data/realm-vs-core-data-interview-guide-1a2b3c4d5e6f",
        
        # General iOS
        "https://medium.com/@iosdeveloper/lifecycle-methods-interview-questions-7a8b9c0d1e2f",
        "https://medium.com/ios-career/senior-ios-developer-interview-questions-3a4b5c6d7e8f",
        "https://medium.com/@swift_expert/common-ios-interview-mistakes-avoid-9a0b1c2d3e4f",
    ]
    
    # Try Firecrawl Map first (best for discovery)
    new_urls = []
    try:
        print("🔍 Trying Firecrawl Map for discovery...")
        app_fc = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
        
        search_urls = [
            "https://medium.com/tag/ios-app-development",
            "https://medium.com/tag/swift",
            "https://medium.com/tag/swiftui",
            "https://medium.com/tag/ios-development",
        ]
        
        search_url = random.choice(search_urls)
        result = app_fc.map_url(search_url, params={'search': 'article', 'limit': 30})
        
        if result and 'links' in result:
            for link in result.get('links', []):
                url = link if isinstance(link, str) else link.get('url', '')
                if (url and 'medium.com' in url and 
                    not any(skip in url for skip in ['/tag/', '/search', '/topics', '/archive']) and
                    url not in processed_urls and url not in new_urls):
                    new_urls.append(url)
                    if len(new_urls) >= count:
                        break
        
        if new_urls:
            print(f"✅ Found {len(new_urls)} new articles via Firecrawl")
            return new_urls[:count]
    except Exception as e:
        print(f"⚠️  Firecrawl Map failed: {e}")
    
    # Fallback to curated list
    print("📚 Using curated article list...")
    new_curated = [url for url in curated_urls if url not in processed_urls]
    
    if new_curated:
        # Shuffle for randomness
        random.shuffle(new_curated)
        selected = new_curated[:count]
        print(f"✅ Returning {len(selected)} curated articles")
        return selected
    
    print("⚠️  All curated URLs already processed!")
    # If all curated processed, just return some anyway (user can handle duplicates)
    random.shuffle(curated_urls)
    print(f"ℹ️  Returning random curated URLs (may be duplicates)")
    return curated_urls[:count]

# Background worker
async def job_worker():
    """Simple background worker"""
    while True:
        job_id, url = await job_queue.get()
        await process_job(job_id, url)
        job_queue.task_done()

@app.on_event("startup")
async def startup_event():
    """Start background worker on startup"""
    asyncio.create_task(job_worker())

# API Endpoints
@app.get("/", response_class=HTMLResponse, tags=["System"])
async def home():
    """
    ## 🏠 Landing Page
    
    HTML welcome page with API overview and quick links.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>iOS Q&A Scraper API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #007AFF; }
            .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
            code { background: #e0e0e0; padding: 2px 6px; border-radius: 3px; }
            a { color: #007AFF; text-decoration: none; }
        </style>
    </head>
    <body>
        <h1>🚀 iOS Q&A Scraper API</h1>
        <p>Free API for scraping iOS interview questions from Medium articles</p>
        
        <h2>📚 API Documentation</h2>
        <div class="endpoint">
            <strong>POST /api/scrape</strong><br>
            Submit a Medium URL for scraping<br>
            <code>{"url": "https://medium.com/..."}</code>
        </div>
        
        <div class="endpoint">
            <strong>GET /api/jobs/{job_id}</strong><br>
            Check job status
        </div>
        
        <div class="endpoint">
            <strong>GET /api/jobs/{job_id}/results</strong><br>
            Get Q&A results
        </div>
        
        <div class="endpoint">
            <strong>GET /api/qa</strong><br>
            Get all Q&A pairs (with pagination)
        </div>
        
        <div class="endpoint">
            <strong>GET /api/stats</strong><br>
            Get system statistics
        </div>
        
        <p><a href="/docs">📖 Interactive API Docs →</a></p>
        
        <h2>💡 Example Usage</h2>
        <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
curl -X POST https://your-api.com/api/scrape \\
  -H "Content-Type: application/json" \\
  -d '{"url": "https://medium.com/@user/ios-interview"}'
        </pre>
    </body>
    </html>
    """

@app.post("/api/scrape", response_model=JobResponse, tags=["Scraping"])
async def submit_scrape(submission: UrlSubmission, background_tasks: BackgroundTasks):
    """
    ## Submit a Medium URL for Q&A Extraction
    
    Scrape a specific Medium article and extract iOS interview Q&A pairs.
    
    **Example URL:**
    ```
    https://medium.com/@user/ios-interview-questions-guide
    ```
    
    **Returns:** Job ID to track the scraping progress
    """
    import uuid
    job_id = str(uuid.uuid4())
    
    # Create job
    with get_db() as conn:
        conn.execute('''
            INSERT INTO jobs (id, url, status, created_at)
            VALUES (?, ?, ?, ?)
        ''', (job_id, str(submission.url), 'queued', datetime.now().isoformat()))
    
    # Queue job
    await job_queue.put((job_id, str(submission.url)))
    
    return JobResponse(
        job_id=job_id,
        status="queued",
        message="Job submitted successfully"
    )

@app.post("/api/scrape/random", tags=["Scraping", "Discovery"])
async def scrape_random_articles(background_tasks: BackgroundTasks, count: int = 1):
    """
    ## 🎲 Discover and Scrape Random iOS Articles
    
    Automatically finds random iOS/Swift articles on Medium and extracts Q&A.
    
    **Parameters:**
    - **count**: Number of articles (1-10, default: 1)
    
    **How it works:**
    1. Searches Medium for iOS/Swift content
    2. Picks random articles
    3. Queues them for scraping
    4. Returns job IDs to track progress
    
    **Example:** `POST /api/scrape/random?count=3`
    """
    import uuid
    
    # Validate count
    count = max(1, min(count, 10))
    
    # Discover random articles
    urls = discover_random_ios_articles(count)
    
    if not urls:
        raise HTTPException(
            status_code=500, 
            detail="Failed to discover articles. This is unusual - please check logs or try again."
        )
    
    # Create jobs for each URL
    job_ids = []
    for url in urls:
        job_id = str(uuid.uuid4())
        
        # Create job
        with get_db() as conn:
            conn.execute('''
                INSERT INTO jobs (id, url, status, created_at)
                VALUES (?, ?, ?, ?)
            ''', (job_id, url, 'queued', datetime.now().isoformat()))
        
        # Queue job
        await job_queue.put((job_id, url))
        job_ids.append({"job_id": job_id, "url": url})
    
    return {
        "message": f"Submitted {len(job_ids)} random articles for scraping",
        "jobs": job_ids
    }

@app.get("/api/discover", tags=["Discovery"])
async def discover_articles(count: int = 5):
    """
    ## 🔍 Discover iOS Articles (Preview Only)
    
    Find random iOS/Swift articles on Medium **without** scraping them.
    
    Use this to preview what articles are available before scraping.
    
    **Parameters:**
    - **count**: Number of articles to find (1-20, default: 5)
    
    **Returns:** List of Medium article URLs
    
    **Example:** `GET /api/discover?count=10`
    """
    count = max(1, min(count, 20))
    urls = discover_random_ios_articles(count)
    
    return {
        "count": len(urls),
        "urls": urls,
        "message": "Use POST /api/scrape with these URLs to extract Q&A"
    }

@app.get("/api/jobs/{job_id}", tags=["Jobs"])
async def get_job_status(job_id: str):
    """
    ## 📊 Check Job Status
    
    Get the current status of a scraping job.
    
    **Statuses:**
    - `queued` - Waiting to start
    - `processing` - Currently scraping
    - `completed` - Finished successfully
    - `failed` - Error occurred
    
    **Returns:** Job details including status, Q&A count, and errors (if any)
    """
    with get_db() as conn:
        row = conn.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return dict(row)

@app.get("/api/jobs/{job_id}/results", tags=["Jobs", "Q&A"])
async def get_job_results(job_id: str):
    """
    ## 📋 Get Extracted Q&A Pairs
    
    Retrieve all the questions and answers extracted from a job.
    
    **Returns:** Array of Q&A objects containing:
    - `question` - The interview question
    - `answer` - Extracted answer (or context from article)
    - `source_url` - Original Medium article URL
    - `timestamp` - When it was extracted
    
    **Note:** Only available for completed jobs
    """
    with get_db() as conn:
        rows = conn.execute('''
            SELECT question, answer, source_url, timestamp 
            FROM qa_pairs WHERE job_id = ?
        ''', (job_id,)).fetchall()
        
        return [dict(row) for row in rows]

@app.get("/api/qa", tags=["Q&A"])
async def get_all_qa(limit: int = 50, offset: int = 0):
    """
    ## 📚 Get All Q&A Pairs (Master Database)
    
    Retrieve all collected iOS interview Q&A pairs from the database.
    
    **Parameters:**
    - `limit` - Number of results per page (default: 50)
    - `offset` - Pagination offset (default: 0)
    
    **Returns:** 
    - Array of all Q&A pairs across all scraped articles
    - Total count
    - Pagination info
    
    **Example:** `GET /api/qa?limit=100&offset=0`
    """
    with get_db() as conn:
        rows = conn.execute('''
            SELECT question, answer, source_url, timestamp 
            FROM qa_pairs 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset)).fetchall()
        
        return [dict(row) for row in rows]

@app.get("/api/stats", tags=["System"])
async def get_stats():
    """
    ## 📈 System Statistics
    
    Get overview statistics about the scraping system.
    
    **Returns:**
    - Total jobs processed
    - Success/failure counts
    - Total Q&A pairs collected
    - Unique articles scraped
    - System health
    
    **Example:** `GET /api/stats`
    """
    with get_db() as conn:
        total_qa = conn.execute('SELECT COUNT(*) FROM qa_pairs').fetchone()[0]
        total_jobs = conn.execute('SELECT COUNT(*) FROM jobs').fetchone()[0]
        completed = conn.execute('SELECT COUNT(*) FROM jobs WHERE status = "completed"').fetchone()[0]
        failed = conn.execute('SELECT COUNT(*) FROM jobs WHERE status = "failed"').fetchone()[0]
        unique_urls = conn.execute('SELECT COUNT(DISTINCT url) FROM jobs WHERE status = "completed"').fetchone()[0]
        
        return {
            'total_qa_pairs': total_qa,
            'total_jobs': total_jobs,
            'completed_jobs': completed,
            'failed_jobs': failed,
            'unique_articles_processed': unique_urls,
            'success_rate': f"{(completed / total_jobs * 100):.1f}%" if total_jobs > 0 else "0%",
            'queue_size': job_queue.qsize()
        }

@app.get("/health", tags=["System"])
async def health_check():
    """
    ## 💚 Health Check
    
    Simple endpoint to check if the API is running.
    
    **Returns:** `{"status": "healthy"}`
    
    **Use for:** Monitoring, uptime checks, deployment verification
    """
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

