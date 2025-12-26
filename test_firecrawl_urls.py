# test_firecrawl_urls.py
# Quick test with your two URLs
from firecrawl import FirecrawlApp
from groq import Groq

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "your-firecrawl-api-key-here")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")

urls = [
    "https://medium.com/is-a-code/ios-interview-swift-closures-devils-advocate-e1e749fbd7ef",
    "https://medium.com/@ios-interview/must-prepare-ios-interview-questions-for-faang-companies-19b48a1295d2"
]

print("\n" + "="*70)
print("🧪 TESTING FIRECRAWL WITH YOUR URLS")
print("="*70 + "\n")

app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

for i, url in enumerate(urls, 1):
    print(f"\n📄 TEST {i}/2")
    print(f"🔗 {url[:65]}...")
    
    try:
        print(f"   🔥 Scraping...")
        result = app.scrape(url, formats=['markdown'])
        
        print(f"   ✅ Got result!")
        print(f"   📊 Result type: {type(result)}")
        
        if isinstance(result, dict):
            print(f"   🔑 Keys: {list(result.keys())}")
            
            # Try to get content
            content = None
            if 'markdown' in result:
                content = result['markdown']
                print(f"   ✅ Found markdown content: {len(content)} chars")
            elif 'content' in result:
                content = result['content']
                print(f"   ✅ Found content: {len(content)} chars")
            
            if content and len(content) > 100:
                print(f"   📄 Preview: {content[:150]}...")
                
                # Test AI extraction
                print(f"\n   🤖 Testing AI extraction...")
                client = Groq(api_key=GROQ_API_KEY)
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{
                        "role": "user",
                        "content": f"""Extract iOS questions from this (just count them):

{content[:2000]}

How many iOS interview questions do you see?"""
                    }],
                    temperature=0,
                    max_tokens=100,
                    timeout=10
                )
                
                print(f"   ✅ AI says: {response.choices[0].message.content.strip()}")
        
        elif isinstance(result, str):
            print(f"   ✅ Got string content: {len(result)} chars")
            print(f"   📄 Preview: {result[:150]}...")
        
        print(f"   ✅ SUCCESS!")
    
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print(f"   " + "-"*65)

print("\n" + "="*70)
print("✅ Test complete!")
print("="*70 + "\n")
