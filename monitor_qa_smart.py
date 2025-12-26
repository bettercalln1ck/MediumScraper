# monitor_qa_smart.py
# AI-powered Q&A extraction with real-time deduplication
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

def main():
    print("\n" + "="*70)
    print("🎓 SMART Q&A EXTRACTION (With Deduplication)")
    print("="*70)
    print("✅ Real-time duplicate detection enabled")
    print(f"🎯 Similarity threshold: {SIMILARITY_THRESHOLD}")
    print("📖 Browse Medium articles - AI extracts unique Q&A pairs!")
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
            
            print(f"✅ Connected! Monitoring {len(context.pages)} open tabs")
            print(f"💡 Browse Medium articles - duplicates will be filtered\n")
            
            last_check = {}
            check_count = 0
            
            while True:
                time.sleep(2)
                check_count += 1
                
                for page in context.pages:
                    try:
                        current_url = page.url
                        
                        if "medium.com" not in current_url:
                            continue
                        
                        if any(x in current_url for x in ['/search?', '/tag/', '/feed/', '/m/signin', '/plans']):
                            continue
                        
                        page_id = id(page)
                        if page_id not in last_check or last_check[page_id] != current_url:
                            last_check[page_id] = current_url
                            
                            if current_url not in seen_urls:
                                seen_urls.add(current_url)
                                stats["total_articles"] += 1
                                
                                page.wait_for_load_state("domcontentloaded", timeout=5000)
                                html = page.content()
                                
                                print(f"🔍 Extracting from: {current_url[:60]}...")
                                qa_pairs = extract_qa_pairs_with_ai(html, current_url)
                                
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
                                            print(f"      Similar to: '{similar_q[:45]}...'")
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
                                        print(f"✨ Added {new_pairs} unique Q&A pairs!")
                                        if dupes > 0:
                                            print(f"   🔄 Skipped {dupes} duplicates")
                                    else:
                                        print(f"   🔄 All {dupes} Q&A pairs were duplicates (skipped)")
                                    
                                    print(f"   📊 Total unique: {stats['unique_qa_saved']} Q&A pairs\n")
                                else:
                                    print(f"   (No iOS Q&A found)\n")
                    
                    except Exception as e:
                        pass
                
                if check_count % 30 == 0:
                    print(f"💭 Monitoring... {stats['unique_qa_saved']} unique Q&A pairs ({stats['duplicates_found']} dupes filtered)")
    
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
        print("📊 SESSION SUMMARY - SMART Q&A EXTRACTION")
        print("="*70)
        print(f"✅ Articles checked: {stats['total_articles']}")
        print(f"📝 Articles with Q&A: {stats['articles_with_qa']}")
        print(f"💡 Total Q&A extracted: {stats['total_qa_extracted']}")
        print(f"🔄 Duplicates filtered: {stats['duplicates_found']}")
        print(f"⭐ Unique Q&A saved: {stats['unique_qa_saved']}")
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

