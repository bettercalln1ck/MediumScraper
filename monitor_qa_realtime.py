# monitor_qa_realtime.py
# AI-powered Q&A extraction with INSTANT navigation detection
import re
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
from groq import Groq

# Configuration
import os
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")
SIMILARITY_THRESHOLD = 0.7  # Adjust: 0.5=loose, 0.7=balanced, 0.9=strict

def normalize_question(q):
    """Normalize question for comparison"""
    q = q.lower().strip()
    q = re.sub(r'[^\w\s]', '', q)  # Remove punctuation
    q = ' '.join(q.split())  # Normalize whitespace
    return q

def calculate_similarity(q1, q2):
    """Calculate similarity between two questions (0-1)"""
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
    """Check if new question is duplicate of existing ones"""
    for existing in existing_questions:
        similarity = calculate_similarity(new_question, existing['question'])
        if similarity >= threshold:
            return True, existing['question'], similarity
    return False, None, 0.0

def extract_qa_pairs_with_ai(html: str, url: str):
    """Extract Question & Answer pairs using AI"""
    soup = BeautifulSoup(html, "lxml")
    article = soup.find("article") or soup
    text = article.get_text(" ", strip=True)[:15000]
    
    if len(text) < 200:
        return []
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"""Extract iOS/Swift/Apple development interview questions AND their answers from this article.

Format:
Q: [question]
A: [answer - comprehensive but concise, 2-4 sentences]

Rules:
- ONLY iOS/Swift/SwiftUI/Apple platform content
- Each answer must be 2-4 sentences
- Skip questions without clear answers
- If NO iOS Q&A pairs found, return "NO_IOS_QA"

Article:
{text}

Q&A Pairs:"""
            }],
            temperature=0,
            max_tokens=2500,
            timeout=20
        )
        
        result = response.choices[0].message.content.strip()
        
        if "NO_IOS_QA" in result or not result:
            return []
        
        # Parse Q&A pairs
        qa_pairs = []
        lines = result.split('\n')
        current_q = None
        current_a = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('Q:'):
                if current_q and current_a:
                    qa_pairs.append({
                        'question': current_q,
                        'answer': current_a
                    })
                current_q = line[2:].strip()
                current_a = None
            elif line.startswith('A:'):
                current_a = line[2:].strip()
            elif current_a and line:
                current_a += " " + line
        
        if current_q and current_a:
            qa_pairs.append({
                'question': current_q,
                'answer': current_a
            })
        
        return qa_pairs
        
    except Exception as e:
        print(f"   ⚠️  AI extraction failed: {str(e)[:50]}")
        return []

def process_url(url, seen_urls, collected_qa, stats, page):
    """Process a URL for Q&A extraction"""
    if url in seen_urls:
        return
    
    if "medium.com" not in url:
        return
    
    # Skip non-article pages
    skip_patterns = ['/search?', '/tag/', '/feed/', '/m/signin', '/plans', '/me/', '/topics', '/settings']
    if any(x in url for x in skip_patterns):
        print(f"⏭️  Skipping (not an article): {url[:60]}...")
        return
    
    seen_urls.add(url)
    stats["total_articles"] += 1
    
    print(f"\n🔍 NEW PAGE: {url[:60]}...")
    print(f"   ⏳ Waiting for page to load...")
    
    try:
        page.wait_for_load_state("domcontentloaded", timeout=5000)
        html = page.content()
        
        print(f"   🤖 Extracting Q&A with AI...")
        qa_pairs = extract_qa_pairs_with_ai(html, url)
        
        if qa_pairs:
            stats["articles_with_qa"] += 1
            new_pairs = 0
            dupes = 0
            
            for qa in qa_pairs:
                stats["total_qa_extracted"] += 1
                
                # Check for duplicates
                is_dup, similar_q, similarity = is_duplicate(
                    qa['question'],
                    collected_qa,
                    SIMILARITY_THRESHOLD
                )
                
                if is_dup:
                    dupes += 1
                    stats["duplicates_found"] += 1
                    print(f"   🔄 Duplicate ({similarity:.0%}): '{qa['question'][:45]}...'")
                else:
                    collected_qa.append({
                        "question": qa['question'],
                        "answer": qa['answer'],
                        "source_url": url,
                        "timestamp": datetime.now().isoformat()
                    })
                    new_pairs += 1
                    stats["unique_qa_saved"] += 1
            
            if new_pairs > 0:
                print(f"\n   ✨ Added {new_pairs} unique Q&A pairs!")
                if dupes > 0:
                    print(f"   🔄 Skipped {dupes} duplicates")
            else:
                print(f"\n   🔄 All {dupes} Q&A pairs were duplicates (skipped)")
            
            print(f"   📊 Total unique: {stats['unique_qa_saved']} Q&A pairs")
        else:
            print(f"   ℹ️  No iOS Q&A found in this article")
    
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")

def main():
    print("\n" + "="*70)
    print("⚡ REALTIME Q&A EXTRACTION (Instant Navigation Detection)")
    print("="*70)
    print("✅ Real-time navigation detection enabled")
    print(f"🎯 Similarity threshold: {SIMILARITY_THRESHOLD}")
    print("📖 Navigate to any Medium article - instantly detected!")
    print("🛑 Press Ctrl+C when done")
    print("="*70 + "\n")
    
    collected_qa = []
    seen_urls = set()
    stats = {
        "total_articles": 0,
        "articles_with_qa": 0,
        "total_qa_extracted": 0,
        "duplicates_found": 0,
        "unique_qa_saved": 0
    }
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            
            contexts = browser.contexts
            if not contexts:
                print("❌ No browser contexts found.")
                print("Run: ./start_chrome_debug.sh")
                return
            
            context = contexts[0]
            
            print(f"✅ Connected to Chrome!")
            print(f"📱 Monitoring {len(context.pages)} open tabs\n")
            
            # Track pages
            monitored_pages = {}
            
            # Process existing pages
            for page in context.pages:
                try:
                    page_id = id(page)
                    monitored_pages[page_id] = True
                    
                    # Set up navigation listener
                    def make_handler(pg):
                        def handler():
                            url = pg.url
                            if url and "medium.com" in url:
                                print(f"\n🔄 Navigation detected!")
                                process_url(url, seen_urls, collected_qa, stats, pg)
                        return handler
                    
                    page.on("load", make_handler(page))
                    
                    # Process current URL
                    if page.url:
                        process_url(page.url, seen_urls, collected_qa, stats, page)
                
                except Exception as e:
                    print(f"⚠️  Could not monitor tab: {str(e)[:50]}")
            
            print(f"\n💡 Ready! Navigate to Medium articles in Chrome...")
            print(f"🚀 Each navigation will be instantly detected!\n")
            
            # Keep monitoring for new tabs
            while True:
                time.sleep(1)
                
                # Check for new tabs
                for page in context.pages:
                    page_id = id(page)
                    if page_id not in monitored_pages:
                        try:
                            monitored_pages[page_id] = True
                            
                            # Set up navigation listener
                            def make_handler(pg):
                                def handler():
                                    url = pg.url
                                    if url and "medium.com" in url:
                                        print(f"\n🔄 Navigation detected!")
                                        process_url(url, seen_urls, collected_qa, stats, pg)
                                return handler
                            
                            page.on("load", make_handler(page))
                            
                            print(f"✅ New tab detected and monitored!")
                            
                            # Process current URL if it's Medium
                            if page.url and "medium.com" in page.url:
                                process_url(page.url, seen_urls, collected_qa, stats, page)
                        
                        except Exception as e:
                            print(f"⚠️  Could not monitor new tab: {str(e)[:50]}")
    
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("🛑 Stopping monitor...")
        print("="*70)
    
    except Exception as e:
        print(f"\n❌ Connection error: {e}")
        return
    
    # Save results
    if collected_qa:
        df = pd.DataFrame(collected_qa)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"ios_qa_unique_{timestamp}.csv"
        json_file = f"ios_qa_unique_{timestamp}.json"
        
        df.to_csv(csv_file, index=False)
        df.to_json(json_file, orient="records", indent=2)
        
        print("\n" + "="*70)
        print("📊 SESSION SUMMARY - REALTIME Q&A EXTRACTION")
        print("="*70)
        print(f"✅ Articles checked: {stats['total_articles']}")
        print(f"📝 Articles with Q&A: {stats['articles_with_qa']}")
        print(f"💡 Total Q&A extracted: {stats['total_qa_extracted']}")
        print(f"🔄 Duplicates filtered: {stats['duplicates_found']}")
        print(f"⭐ Unique Q&A saved: {stats['unique_qa_saved']}")
        if stats['total_qa_extracted'] > 0:
            print(f"\n📈 Deduplication rate: {(stats['duplicates_found'] / stats['total_qa_extracted'] * 100):.1f}%")
        print(f"\n💾 Saved to:")
        print(f"   - {csv_file}")
        print(f"   - {json_file}")
        print("="*70 + "\n")
        
        print("📋 Sample unique Q&A pairs:")
        for i, row in df.head(3).iterrows():
            print(f"\n{i+1}. Q: {row['question'][:70]}...")
            print(f"   A: {row['answer'][:70]}...")
    else:
        print("\n⚠️  No unique Q&A pairs collected.")
    
    print("\n✅ Done!\n")

if __name__ == "__main__":
    main()

