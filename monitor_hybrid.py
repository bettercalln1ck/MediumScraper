# monitor_hybrid.py
# HYBRID: Browser monitoring + Firecrawl scraping + Groq AI extraction
import re
import time
from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
from groq import Groq

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "your-firecrawl-api-key-here")
SIMILARITY_THRESHOLD = 0.7
CHECK_INTERVAL = 0.3

# Try to import firecrawl
try:
    from firecrawl import FirecrawlApp
    FIRECRAWL_AVAILABLE = True
except ImportError:
    FIRECRAWL_AVAILABLE = False
    print("⚠️  Firecrawl not installed. Install with: pip3 install firecrawl-py")

def normalize_question(q):
    q = q.lower().strip()
    q = re.sub(r'[^\w\s]', '', q)
    q = ' '.join(q.split())
    return q

def calculate_similarity(q1, q2):
    q1_norm = normalize_question(q1)
    q2_norm = normalize_question(q2)
    
    if q1_norm == q2_norm:
        return 1.0
    
    words1 = set(q1_norm.split())
    words2 = set(q2_norm.split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)

def is_duplicate(new_question, existing_questions, threshold=SIMILARITY_THRESHOLD):
    for existing in existing_questions:
        similarity = calculate_similarity(new_question, existing['question'])
        if similarity >= threshold:
            return True, existing['question'], similarity
    return False, None, 0.0

def is_article_url(url):
    """Check if URL is a Medium article"""
    if not url or "medium.com" not in url:
        return False
    
    skip_patterns = [
        '/search?', '/tag/', '/feed/', '/m/signin', '/plans', 
        '/me/', '/topics', '/settings', 'medium.com/?',
        '/about', '/membership', '/creators'
    ]
    
    for pattern in skip_patterns:
        if pattern in url:
            return False
    
    try:
        path = url.split('medium.com/', 1)[1] if 'medium.com/' in url else ''
        path = path.split('?')[0]
        if len(path) > 20 and '/' in path:
            return True
    except:
        pass
    
    return False

def scrape_with_firecrawl(url):
    """Scrape article using Firecrawl (better quality)"""
    if not FIRECRAWL_AVAILABLE:
        return None
    
    try:
        app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
        result = app.scrape(url, formats=['markdown'])
        
        if not result:
            return None
        
        # Get content from Document object or dict
        if hasattr(result, 'markdown'):
            return result.markdown
        elif hasattr(result, 'content'):
            return result.content
        elif isinstance(result, dict):
            if 'markdown' in result:
                return result['markdown']
            elif 'content' in result:
                return result['content']
        elif isinstance(result, str):
            return result
        return None
    except Exception as e:
        print(f"   ⚠️  Firecrawl error: {str(e)[:50]}")
        return None

def extract_qa_with_ai(content: str, url: str):
    """Extract Q&A using Groq AI"""
    if not content or len(content) < 200:
        return []
    
    # Limit content size
    content = content[:15000]
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"""Extract iOS/Swift/Apple development interview questions from this article.

Format:
Q: [question]
A: [answer if available, otherwise write "Answer not provided"]

Rules:
- ONLY iOS/Swift/SwiftUI/Apple platform content
- Include questions even without clear answers
- If answer exists, keep it 2-4 sentences
- If NO iOS questions found, return "NO_IOS_QA"

Article:
{content}

Q&A Pairs:"""
            }],
            temperature=0,
            max_tokens=2500,
            timeout=20
        )
        
        result = response.choices[0].message.content.strip()
        
        if "NO_IOS_QA" in result or not result:
            return []
        
        qa_pairs = []
        lines = result.split('\n')
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
        
        return qa_pairs
        
    except Exception as e:
        print(f"   ⚠️  AI error: {str(e)[:50]}")
        return []

def main():
    print("\n" + "="*70)
    print("🚀 HYBRID MONITOR - Browser + Firecrawl + AI")
    print("="*70)
    print("✨ Browse naturally in Chrome")
    print("🔥 Firecrawl scrapes detected articles")
    print("🤖 Groq AI extracts Q&A pairs")
    print("🎯 Real-time deduplication")
    print("🛑 Press Ctrl+C when done")
    print("="*70 + "\n")
    
    if not FIRECRAWL_AVAILABLE:
        print("❌ Firecrawl not installed!")
        print("Run: pip3 install firecrawl-py")
        print("Then update FIRECRAWL_API_KEY in this file\n")
        return
    
    if FIRECRAWL_API_KEY == "YOUR_FIRECRAWL_API_KEY_HERE":
        print("❌ Please set your Firecrawl API key!")
        print("1. Get free key: https://firecrawl.dev")
        print("2. Update FIRECRAWL_API_KEY in monitor_hybrid.py\n")
        return
    
    collected_qa = []
    seen_urls = set()
    stats = {
        "url_changes": 0,
        "articles_detected": 0,
        "firecrawl_success": 0,
        "firecrawl_errors": 0,
        "articles_with_qa": 0,
        "total_qa": 0,
        "duplicates": 0,
        "unique_saved": 0
    }
    
    last_urls = {}
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            
            contexts = browser.contexts
            if not contexts:
                print("❌ Chrome not in debug mode")
                print("Run: ./start_chrome_debug.sh\n")
                return
            
            context = contexts[0]
            
            print(f"✅ Connected to Chrome!")
            print(f"💡 Browse Medium articles...\n")
            
            while True:
                time.sleep(CHECK_INTERVAL)
                
                pages = context.pages
                
                for page in pages:
                    try:
                        current_url = page.url
                        page_id = id(page)
                        
                        if page_id not in last_urls:
                            last_urls[page_id] = current_url
                        elif last_urls[page_id] != current_url:
                            stats["url_changes"] += 1
                            last_urls[page_id] = current_url
                            
                            if is_article_url(current_url) and current_url not in seen_urls:
                                seen_urls.add(current_url)
                                stats["articles_detected"] += 1
                                
                                print(f"\n{'='*70}")
                                print(f"📄 NEW ARTICLE #{stats['articles_detected']}")
                                print(f"{'='*70}")
                                print(f"🔗 {current_url[:65]}...")
                                
                                # Scrape with Firecrawl
                                print(f"   🔥 Scraping with Firecrawl...")
                                content = scrape_with_firecrawl(current_url)
                                
                                if content:
                                    stats["firecrawl_success"] += 1
                                    print(f"   ✅ Scraped! ({len(content)} chars)")
                                    
                                    # Extract Q&A with AI
                                    print(f"   🤖 Extracting Q&A with AI...")
                                    qa_pairs = extract_qa_with_ai(content, current_url)
                                    
                                    if qa_pairs:
                                        stats["articles_with_qa"] += 1
                                        new_pairs = 0
                                        dupes = 0
                                        
                                        for qa in qa_pairs:
                                            stats["total_qa"] += 1
                                            
                                            is_dup, similar_q, similarity = is_duplicate(
                                                qa['question'], collected_qa, SIMILARITY_THRESHOLD
                                            )
                                            
                                            if is_dup:
                                                dupes += 1
                                                stats["duplicates"] += 1
                                            else:
                                                collected_qa.append({
                                                    "question": qa['question'],
                                                    "answer": qa['answer'],
                                                    "source_url": current_url,
                                                    "timestamp": datetime.now().isoformat()
                                                })
                                                new_pairs += 1
                                                stats["unique_saved"] += 1
                                        
                                        if new_pairs > 0:
                                            print(f"\n   ✨ Added {new_pairs} unique Q&A!")
                                            if dupes > 0:
                                                print(f"   🔄 Skipped {dupes} duplicates")
                                            print(f"   📊 TOTAL: {stats['unique_saved']} unique Q&A")
                                        else:
                                            print(f"\n   🔄 All {dupes} were duplicates")
                                    else:
                                        print(f"   ℹ️  No iOS Q&A found")
                                else:
                                    stats["firecrawl_errors"] += 1
                                    print(f"   ❌ Firecrawl failed")
                                
                                print(f"{'='*70}\n")
                    
                    except Exception as e:
                        pass
    
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("🛑 STOPPING...")
        print("="*70)
    
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        return
    
    # Save results
    if collected_qa:
        df = pd.DataFrame(collected_qa)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"ios_qa_hybrid_{timestamp}.csv"
        json_file = f"ios_qa_hybrid_{timestamp}.json"
        
        df.to_csv(csv_file, index=False)
        df.to_json(json_file, orient="records", indent=2)
        
        print("\n" + "="*70)
        print("📊 HYBRID SESSION SUMMARY")
        print("="*70)
        print(f"🔄 URL changes: {stats['url_changes']}")
        print(f"📄 Articles detected: {stats['articles_detected']}")
        print(f"🔥 Firecrawl success: {stats['firecrawl_success']}")
        print(f"❌ Firecrawl errors: {stats['firecrawl_errors']}")
        print(f"📝 Articles with Q&A: {stats['articles_with_qa']}")
        print(f"💡 Total Q&A: {stats['total_qa']}")
        print(f"🔄 Duplicates: {stats['duplicates']}")
        print(f"⭐ UNIQUE SAVED: {stats['unique_saved']}")
        if stats['total_qa'] > 0:
            print(f"\n📈 Dedup rate: {(stats['duplicates'] / stats['total_qa'] * 100):.1f}%")
        print(f"\n💾 Saved to:")
        print(f"   • {csv_file}")
        print(f"   • {json_file}")
        print("="*70 + "\n")
        
        if len(df) > 0:
            print("📋 Sample Q&A:")
            for i, row in df.head(3).iterrows():
                print(f"\n{i+1}. Q: {row['question'][:65]}...")
                print(f"   A: {row['answer'][:65]}...")
    else:
        print("\n⚠️  No Q&A collected")
        print(f"📊 Articles detected: {stats['articles_detected']}")
        print(f"📊 Firecrawl attempts: {stats['firecrawl_success'] + stats['firecrawl_errors']}")
    
    print("\n✅ Done!\n")

if __name__ == "__main__":
    main()

