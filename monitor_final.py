# monitor_final.py
# Ultra-aggressive URL detection + accepts questions without answers
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
SIMILARITY_THRESHOLD = 0.7
CHECK_INTERVAL = 0.2  # Check 5x per second!

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
    """Very aggressive article detection"""
    if not url or "medium.com" not in url:
        return False
    
    # Skip these
    skip_patterns = [
        '/search?', '/tag/', '/feed/', '/m/signin', '/plans', 
        '/me/', '/topics', '/settings', 'medium.com/?',
        '/about', '/membership', '/creators', '/partner-program'
    ]
    
    for pattern in skip_patterns:
        if pattern in url:
            return False
    
    # If it has a decent path length, consider it an article
    try:
        path = url.split('medium.com/', 1)[1] if 'medium.com/' in url else ''
        # Remove query params
        path = path.split('?')[0]
        # Must have some path and reasonable length
        if len(path) > 20 and '/' in path:
            return True
    except:
        pass
    
    return False

def extract_qa_pairs_with_ai(html: str, url: str):
    """Extract Q&A pairs - accepts questions without answers too!"""
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
        
        qa_pairs = []
        lines = result.split('\n')
        current_q = None
        current_a = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('Q:'):
                if current_q:
                    # Save previous question (with or without answer)
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
        
        # Save last question
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
    print("🚀 FINAL MONITOR - Maximum Detection + Questions Only")
    print("="*70)
    print(f"⚡ Ultra-fast checking (5x per second)")
    print(f"✅ Accepts questions WITHOUT answers")
    print(f"🎯 Similarity threshold: {SIMILARITY_THRESHOLD}")
    print("📖 Navigate and watch - every page checked!")
    print("🛑 Press Ctrl+C when done")
    print("="*70 + "\n")
    
    collected_qa = []
    seen_urls = set()
    stats = {
        "total_articles": 0,
        "articles_with_qa": 0,
        "total_qa_extracted": 0,
        "duplicates_found": 0,
        "unique_qa_saved": 0,
        "url_changes": 0
    }
    
    last_urls = {}
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            
            contexts = browser.contexts
            if not contexts:
                print("❌ No browser contexts found.")
                print("Run: ./start_chrome_debug.sh")
                return
            
            context = contexts[0]
            
            print(f"✅ Connected!")
            print(f"💡 Watching for navigation...\n")
            print(f"[Tip: Every URL change will be shown below]\n")
            
            while True:
                time.sleep(CHECK_INTERVAL)
                
                pages = context.pages
                
                for page in pages:
                    try:
                        current_url = page.url
                        page_id = id(page)
                        
                        # Track ALL URL changes
                        if page_id not in last_urls:
                            last_urls[page_id] = current_url
                            print(f"🆕 New tab detected: {current_url[:60]}...")
                        elif last_urls[page_id] != current_url:
                            stats["url_changes"] += 1
                            print(f"\n{'='*70}")
                            print(f"🔄 URL CHANGE #{stats['url_changes']}")
                            print(f"{'='*70}")
                            print(f"From: {last_urls[page_id][:65]}")
                            print(f"To:   {current_url[:65]}")
                            
                            last_urls[page_id] = current_url
                            
                            # Check if it's an article
                            if is_article_url(current_url):
                                if current_url not in seen_urls:
                                    seen_urls.add(current_url)
                                    stats["total_articles"] += 1
                                    
                                    print(f"\n✅ THIS IS A NEW ARTICLE!")
                                    print(f"   ⏳ Waiting for content...")
                                    
                                    time.sleep(2)  # Wait for content
                                    html = page.content()
                                    
                                    print(f"   🤖 Asking AI for Q&A...")
                                    qa_pairs = extract_qa_pairs_with_ai(html, current_url)
                                    
                                    if qa_pairs:
                                        stats["articles_with_qa"] += 1
                                        new_pairs = 0
                                        dupes = 0
                                        
                                        for qa in qa_pairs:
                                            stats["total_qa_extracted"] += 1
                                            
                                            is_dup, similar_q, similarity = is_duplicate(
                                                qa['question'], collected_qa, SIMILARITY_THRESHOLD
                                            )
                                            
                                            if is_dup:
                                                dupes += 1
                                                stats["duplicates_found"] += 1
                                            else:
                                                collected_qa.append({
                                                    "question": qa['question'],
                                                    "answer": qa['answer'],
                                                    "source_url": current_url,
                                                    "timestamp": datetime.now().isoformat()
                                                })
                                                new_pairs += 1
                                                stats["unique_qa_saved"] += 1
                                        
                                        if new_pairs > 0:
                                            print(f"\n   ✨ SUCCESS! Added {new_pairs} unique Q&A!")
                                            if dupes > 0:
                                                print(f"   🔄 (Skipped {dupes} duplicates)")
                                            print(f"   📊 TOTAL: {stats['unique_qa_saved']} unique Q&A")
                                        else:
                                            print(f"\n   🔄 All {dupes} were duplicates")
                                    else:
                                        print(f"   ℹ️  No iOS Q&A found")
                                else:
                                    print(f"   ⏭️  Already processed this article")
                            else:
                                print(f"   ⏭️  Not an article (search/home/profile page)")
                            
                            print(f"{'='*70}\n")
                    
                    except Exception as e:
                        pass  # Silently continue
    
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("🛑 STOPPING...")
        print("="*70)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return
    
    # Save results
    if collected_qa:
        df = pd.DataFrame(collected_qa)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"ios_qa_final_{timestamp}.csv"
        json_file = f"ios_qa_final_{timestamp}.json"
        
        df.to_csv(csv_file, index=False)
        df.to_json(json_file, orient="records", indent=2)
        
        print("\n" + "="*70)
        print("📊 FINAL SUMMARY")
        print("="*70)
        print(f"🔄 URL changes detected: {stats['url_changes']}")
        print(f"✅ Articles processed: {stats['total_articles']}")
        print(f"📝 Articles with Q&A: {stats['articles_with_qa']}")
        print(f"💡 Total Q&A extracted: {stats['total_qa_extracted']}")
        print(f"🔄 Duplicates filtered: {stats['duplicates_found']}")
        print(f"⭐ UNIQUE Q&A SAVED: {stats['unique_qa_saved']}")
        if stats['total_qa_extracted'] > 0:
            print(f"\n📈 Dedup rate: {(stats['duplicates_found'] / stats['total_qa_extracted'] * 100):.1f}%")
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
        print("\n⚠️  No Q&A collected.")
        print(f"📊 URL changes detected: {stats['url_changes']}")
        print(f"📊 Articles checked: {stats['total_articles']}")
        print("\n💡 Did you navigate to article pages? Try clicking into articles!")
    
    print("\n✅ Done!\n")

if __name__ == "__main__":
    main()

