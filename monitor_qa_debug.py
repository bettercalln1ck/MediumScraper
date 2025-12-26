# monitor_qa_debug.py
# Debug version with verbose output to see what's happening
import re
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")
SIMILARITY_THRESHOLD = 0.7

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

def extract_qa_pairs_with_ai(html: str, url: str):
    soup = BeautifulSoup(html, "lxml")
    article = soup.find("article") or soup
    text = article.get_text(" ", strip=True)[:15000]
    
    print(f"   📄 Article text length: {len(text)} chars")
    
    if len(text) < 200:
        print(f"   ⚠️  Article too short ({len(text)} chars), skipping")
        return []
    
    print(f"   🤖 Sending to AI for extraction...")
    
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
        
        print(f"   📥 AI response length: {len(result)} chars")
        print(f"   📝 First 100 chars: {result[:100]}...")
        
        if "NO_IOS_QA" in result or not result:
            print(f"   ℹ️  AI says: No iOS Q&A found")
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
        
        print(f"   ✅ Parsed {len(qa_pairs)} Q&A pairs from AI response")
        
        return qa_pairs
        
    except Exception as e:
        print(f"   ❌ AI extraction failed: {str(e)}")
        return []

def main():
    print("\n" + "="*70)
    print("🐛 DEBUG MODE - Q&A EXTRACTION")
    print("="*70)
    print("Shows detailed info about what's happening")
    print("="*70 + "\n")
    
    collected_qa = []
    seen_urls = set()
    stats = {
        "total_articles": 0,
        "articles_with_qa": 0,
        "total_qa_extracted": 0,
        "duplicates_found": 0,
        "unique_qa_saved": 0,
        "skipped_pages": 0
    }
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            
            contexts = browser.contexts
            if not contexts:
                print("❌ No browser contexts found.")
                return
            
            context = contexts[0]
            
            print(f"✅ Connected! Monitoring {len(context.pages)} open tabs\n")
            
            last_check = {}
            check_count = 0
            
            while True:
                time.sleep(2)
                check_count += 1
                
                for page in context.pages:
                    try:
                        current_url = page.url
                        
                        print(f"\n🔍 Checking tab: {current_url[:80]}...")
                        
                        if "medium.com" not in current_url:
                            print(f"   ⏭️  Not a Medium URL, skipping")
                            continue
                        
                        # Check if it's a page we should skip
                        skip_patterns = ['/search?', '/tag/', '/feed/', '/m/signin', '/plans', '/me/', '/topics']
                        if any(x in current_url for x in skip_patterns):
                            print(f"   ⏭️  Skipping (search/feed/signin page)")
                            stats["skipped_pages"] += 1
                            continue
                        
                        page_id = id(page)
                        if page_id not in last_check or last_check[page_id] != current_url:
                            last_check[page_id] = current_url
                            
                            if current_url not in seen_urls:
                                seen_urls.add(current_url)
                                stats["total_articles"] += 1
                                
                                print(f"   ✅ This is a new article page!")
                                print(f"   ⏳ Waiting for page to load...")
                                
                                page.wait_for_load_state("domcontentloaded", timeout=5000)
                                html = page.content()
                                
                                print(f"   📄 Page HTML length: {len(html)} chars")
                                
                                qa_pairs = extract_qa_pairs_with_ai(html, current_url)
                                
                                if qa_pairs:
                                    stats["articles_with_qa"] += 1
                                    new_pairs = 0
                                    dupes = 0
                                    
                                    for qa in qa_pairs:
                                        stats["total_qa_extracted"] += 1
                                        
                                        is_dup, similar_q, similarity = is_duplicate(
                                            qa['question'],
                                            collected_qa,
                                            SIMILARITY_THRESHOLD
                                        )
                                        
                                        if is_dup:
                                            dupes += 1
                                            stats["duplicates_found"] += 1
                                            print(f"   🔄 Duplicate: '{qa['question'][:45]}...'")
                                        else:
                                            collected_qa.append({
                                                "question": qa['question'],
                                                "answer": qa['answer'],
                                                "source_url": current_url,
                                                "timestamp": datetime.now().isoformat()
                                            })
                                            new_pairs += 1
                                            stats["unique_qa_saved"] += 1
                                    
                                    print(f"\n   ✨ Added {new_pairs} unique Q&A pairs!")
                                    if dupes > 0:
                                        print(f"   🔄 Skipped {dupes} duplicates")
                                    print(f"   📊 Total unique: {stats['unique_qa_saved']} Q&A pairs")
                                else:
                                    print(f"   ℹ️  No iOS Q&A found in this article")
                    
                    except Exception as e:
                        print(f"   ❌ Error: {str(e)[:100]}")
                
                if check_count % 15 == 0:
                    print(f"\n💭 Status: {stats['unique_qa_saved']} Q&As, {stats['skipped_pages']} pages skipped")
    
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("🛑 Stopping...")
        print("="*70)
    
    # Save results
    if collected_qa:
        df = pd.DataFrame(collected_qa)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"ios_qa_unique_{timestamp}.csv"
        json_file = f"ios_qa_unique_{timestamp}.json"
        
        df.to_csv(csv_file, index=False)
        df.to_json(json_file, orient="records", indent=2)
        
        print("\n" + "="*70)
        print("📊 SUMMARY")
        print("="*70)
        print(f"✅ Articles checked: {stats['total_articles']}")
        print(f"⏭️  Pages skipped: {stats['skipped_pages']}")
        print(f"📝 Articles with Q&A: {stats['articles_with_qa']}")
        print(f"💡 Total Q&A extracted: {stats['total_qa_extracted']}")
        print(f"🔄 Duplicates filtered: {stats['duplicates_found']}")
        print(f"⭐ Unique Q&A saved: {stats['unique_qa_saved']}")
        print(f"\n💾 Saved to: {csv_file}")
        print("="*70)
    else:
        print("\n⚠️  No Q&A pairs collected.")
        print("\n💡 TIPS:")
        print("   1. Make sure you're on actual Medium ARTICLES (not search/home)")
        print("   2. Look for articles with 'interview' or 'questions' in title")
        print("   3. Try: https://medium.com/search?q=ios+interview+questions")
        print("   4. Click into specific articles")
    
    print("\n✅ Done!\n")

if __name__ == "__main__":
    main()

