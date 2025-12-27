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

# Configuration from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "your-firecrawl-api-key-here")
DATABASE_PATH = os.getenv("DATABASE_PATH", "scraper.db")

app = FastAPI(
    title="iOS Q&A Scraper API",
    description="Free API for scraping iOS interview questions from Medium",
    version="1.0.0"
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
        
        content = result.get('markdown', '') or result.get('content', '')
        
        if not content:
            raise Exception("No content extracted")
        
        processing_jobs[job_id]['progress'] = 50
        
        # Extract Q&A with AI
        content = content[:15000]
        client = Groq(api_key=GROQ_API_KEY)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"""Extract iOS/Swift interview questions and answers from this article. Be thorough and intelligent in finding answers.

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
            }],
            temperature=0.3,
            max_tokens=3000,
            timeout=30
        )
        
        result_text = response.choices[0].message.content.strip()
        
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
@app.get("/", response_class=HTMLResponse)
async def home():
    """Landing page"""
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

@app.post("/api/scrape", response_model=JobResponse)
async def submit_scrape(submission: UrlSubmission, background_tasks: BackgroundTasks):
    """Submit a URL for scraping"""
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

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status"""
    with get_db() as conn:
        row = conn.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return dict(row)

@app.get("/api/jobs/{job_id}/results")
async def get_job_results(job_id: str):
    """Get Q&A results"""
    with get_db() as conn:
        rows = conn.execute('''
            SELECT question, answer, source_url, timestamp 
            FROM qa_pairs WHERE job_id = ?
        ''', (job_id,)).fetchall()
        
        return [dict(row) for row in rows]

@app.get("/api/qa")
async def get_all_qa(limit: int = 50, offset: int = 0):
    """Get all Q&A pairs"""
    with get_db() as conn:
        rows = conn.execute('''
            SELECT question, answer, source_url, timestamp 
            FROM qa_pairs 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset)).fetchall()
        
        return [dict(row) for row in rows]

@app.get("/api/stats")
async def get_stats():
    """Get statistics"""
    with get_db() as conn:
        total_qa = conn.execute('SELECT COUNT(*) FROM qa_pairs').fetchone()[0]
        total_jobs = conn.execute('SELECT COUNT(*) FROM jobs').fetchone()[0]
        completed = conn.execute('SELECT COUNT(*) FROM jobs WHERE status = "completed"').fetchone()[0]
        
        return {
            'total_qa_pairs': total_qa,
            'total_jobs': total_jobs,
            'completed_jobs': completed,
            'queue_size': job_queue.qsize()
        }

@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

