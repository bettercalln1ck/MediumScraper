# firecrawl_simple.py
# Simple approach: Just paste Medium URLs and let Firecrawl + AI do the work
import re
from datetime import datetime
import pandas as pd
from groq import Groq
from firecrawl import FirecrawlApp

# Configuration
import os
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "your-firecrawl-api-key-here")
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

def scrape_and_extract(url, collected_qa, stats):
    """Scrape article and extract Q&A"""
    print(f"\n{'='*70}")
    print(f"📄 PROCESSING ARTICLE #{stats['total_articles'] + 1}")
    print(f"{'='*70}")
    print(f"🔗 {url[:65]}...")
    
    try:
        # Scrape with Firecrawl
        print(f"   🔥 Scraping with Firecrawl...")
        app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
        result = app.scrape(url, formats=['markdown'])
        
        if not result:
            print(f"   ❌ Firecrawl failed - no content returned")
            stats["firecrawl_errors"] += 1
            return
        
        # Get content from Document object or dict
        content = None
        if hasattr(result, 'markdown'):
            content = result.markdown
        elif hasattr(result, 'content'):
            content = result.content
        elif isinstance(result, dict):
            if 'markdown' in result:
                content = result['markdown']
            elif 'content' in result:
                content = result['content']
        elif isinstance(result, str):
            content = result
        
        if not content:
            print(f"   ❌ Could not extract content from result (type: {type(result)})")
            stats["firecrawl_errors"] += 1
            return
        stats["firecrawl_success"] += 1
        print(f"   ✅ Scraped! ({len(content)} chars)")
        
        # Extract Q&A with AI
        print(f"   🤖 Extracting Q&A with AI...")
        content = content[:15000]  # Limit size
        
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
            print(f"   ℹ️  No iOS Q&A found")
            return
        
        # Parse Q&A pairs
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
                        "source_url": url,
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
            print(f"   ℹ️  No Q&A extracted")
    
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        stats["firecrawl_errors"] += 1

def main():
    print("\n" + "="*70)
    print("🔥 FIRECRAWL SIMPLE - Just Paste URLs!")
    print("="*70)
    print("✨ No browser monitoring needed")
    print("🔥 Just paste Medium article URLs")
    print("🤖 Firecrawl + AI does the rest")
    print("="*70 + "\n")
    
    collected_qa = []
    stats = {
        "total_articles": 0,
        "firecrawl_success": 0,
        "firecrawl_errors": 0,
        "articles_with_qa": 0,
        "total_qa": 0,
        "duplicates": 0,
        "unique_saved": 0
    }
    
    print("📝 ENTER MEDIUM ARTICLE URLS")
    print("(One per line, press Enter after each)")
    print("(Type 'done' when finished)\n")
    
    urls = []
    while True:
        url = input("URL: ").strip()
        
        if url.lower() == 'done':
            break
        
        if url and "medium.com" in url:
            urls.append(url)
            print(f"   ✅ Added ({len(urls)} total)")
        elif url:
            print(f"   ⚠️  Not a Medium URL, skipped")
    
    if not urls:
        print("\n⚠️  No URLs provided. Exiting.")
        return
    
    print(f"\n🚀 Processing {len(urls)} articles...\n")
    
    for i, url in enumerate(urls, 1):
        stats["total_articles"] += 1
        scrape_and_extract(url, collected_qa, stats)
        print(f"{'='*70}\n")
    
    # Save results
    if collected_qa:
        df = pd.DataFrame(collected_qa)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"ios_qa_firecrawl_{timestamp}.csv"
        json_file = f"ios_qa_firecrawl_{timestamp}.json"
        
        df.to_csv(csv_file, index=False)
        df.to_json(json_file, orient="records", indent=2)
        
        print("\n" + "="*70)
        print("📊 FINAL SUMMARY")
        print("="*70)
        print(f"📄 Articles processed: {stats['total_articles']}")
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
    
    print("\n✅ Done!\n")

if __name__ == "__main__":
    main()

