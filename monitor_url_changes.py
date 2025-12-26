# monitor_url_changes.py
# Optimized URL change detection with visual feedback
import re
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
from groq import Groq

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")
SIMILARITY_THRESHOLD = 0.7
CHECK_INTERVAL = 0.3  # Check 3x per second

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
    
    # Skip these patterns
    skip_patterns = [
        '/search?', '/tag/', '/feed/', '/m/signin', '/plans', 
        '/me/', '/topics', '/settings', 'medium.com/?', 
        'medium.com/tag', 'medium.com/topics'
    ]
    
    if any(x in url for x in skip_patterns):
        return False
    
    # Must have @ (user article) or publication name followed by a long slug
    if "/@" in url:
        parts = url.split("/@", 1)
        if len(parts) > 1:
            after_at = parts[1]
            # Should have username/article-title-slug
            if "/" in after_at:
                slug = after_at.split("/", 1)[1]
                # Article slugs are usually at least 20 chars
                if len(slug) > 15:
                    return True
    
    # Or publication article: medium.com/publication-name/article-slug
    elif url.count('/') >= 4:  # Has enough path segments
        parts = url.split('medium.com/', 1)
        if len(parts) > 1:
            path = parts[1]
            segments = [s for s in path.split('/') if s]
            # Should have publication and long article slug
            if len(segments) >= 2 and len(segments[-1]) > 15:
                return True
    
    return False

def extract_qa_pairs_with_ai(html: str, url: str):
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
        
        qa_pairs = []
        lines = result.split('\n')
        current_q = None
        current_a = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('Q:'):
                if current_q and current_a:
                    qa_pairs.append({'question': current_q, 'answer': current_a})
                current_q = line[2:].strip()
                current_a = None
            elif line.startswith('A:'):
                current_a = line[2:].strip()
            elif current_a and line:
                current_a += " " + line
        
        if current_q and current_a:
            qa_pairs.append({'question': current_q, 'answer': current_a})
        
        return qa_pairs
        
    except Exception as e:
        print(f"   ⚠️  AI error: {str(e)[:50]}")
        return []

def main():
    print("\n" + "="*70)
    print("🔄 SMART URL MONITOR - Auto-detects navigation")
    print("="*70)
    print(f"⚡ Checking for URL changes 3x per second")
    print(f"🎯 Similarity threshold: {SIMILARITY_THRESHOLD}")
    print("📖 Just browse Medium - I'll catch every article!")
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
    
    last_urls = {}
    check_count = 0
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            
            contexts = browser.contexts
            if not contexts:
                print("❌ No browser contexts found.")
                print("Run: ./start_chrome_debug.sh")
                return
            
            context = contexts[0]
            pages = context.pages
            
            print(f"✅ Connected! Watching {len(pages)} tab(s)")
            print(f"💡 Navigate to Medium articles...\n")
            
            while True:
                time.sleep(CHECK_INTERVAL)
                check_count += 1
                
                # Refresh page list
                pages = context.pages
                
                for page in pages:
                    try:
                        current_url = page.url
                        page_id = id(page)
                        
                        # URL changed?
                        if page_id not in last_urls or last_urls[page_id] != current_url:
                            old_url = last_urls.get(page_id, "")
                            last_urls[page_id] = current_url
                            
                            # Show all URL changes (for debugging)
                            if old_url and old_url != current_url:
                                print(f"🔄 URL changed:")
                                print(f"   From: {old_url[:60]}...")
                                print(f"   To:   {current_url[:60]}...")
                            
                            # Is it a new article?
                            if is_article_url(current_url) and current_url not in seen_urls:
                                seen_urls.add(current_url)
                                stats["total_articles"] += 1
                                
                                print(f"\n✅ NEW ARTICLE DETECTED!")
                                print(f"📄 {current_url[:65]}...")
                                print(f"   ⏳ Loading content...")
                                
                                # Wait for content
                                time.sleep(1.5)
                                html = page.content()
                                
                                print(f"   🤖 Extracting Q&A...")
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
                                        print(f"\n   ✨ Added {new_pairs} unique Q&A pairs!")
                                        if dupes > 0:
                                            print(f"   🔄 Skipped {dupes} duplicates")
                                    else:
                                        print(f"\n   🔄 All {dupes} were duplicates")
                                    
                                    print(f"   📊 Total: {stats['unique_qa_saved']} unique Q&A pairs\n")
                                else:
                                    print(f"   ℹ️  No iOS Q&A found\n")
                            elif current_url in seen_urls and is_article_url(current_url):
                                print(f"   ⏭️  Already processed this article\n")
                    
                    except Exception as e:
                        pass
                
                # Status update every 20 seconds
                if check_count % 60 == 0:
                    print(f"💭 Monitoring... {stats['unique_qa_saved']} Q&As collected")
    
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("🛑 Stopping...")
        print("="*70)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
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
        print("📊 SESSION SUMMARY")
        print("="*70)
        print(f"✅ Articles: {stats['total_articles']}")
        print(f"📝 With Q&A: {stats['articles_with_qa']}")
        print(f"💡 Total extracted: {stats['total_qa_extracted']}")
        print(f"🔄 Duplicates: {stats['duplicates_found']}")
        print(f"⭐ Unique saved: {stats['unique_qa_saved']}")
        if stats['total_qa_extracted'] > 0:
            print(f"\n📈 Dedup rate: {(stats['duplicates_found'] / stats['total_qa_extracted'] * 100):.1f}%")
        print(f"\n💾 Files:")
        print(f"   • {csv_file}")
        print(f"   • {json_file}")
        print("="*70 + "\n")
        
        if len(df) > 0:
            print("📋 Sample:")
            for i, row in df.head(2).iterrows():
                print(f"\n{i+1}. Q: {row['question'][:65]}...")
                print(f"   A: {row['answer'][:65]}...")
    else:
        print("\n⚠️  No Q&A collected.")
        print("💡 Make sure you're clicking into actual articles!")
    
    print("\n✅ Done!\n")

if __name__ == "__main__":
    main()

