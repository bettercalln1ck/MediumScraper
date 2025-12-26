# test_url_detection.py
# Simple test to verify URL detection is working
import time
from playwright.sync_api import sync_playwright

print("\n" + "="*70)
print("🧪 URL DETECTION TEST")
print("="*70)
print("This will show EVERY URL change in real-time")
print("Try clicking links in Chrome to test!")
print("Press Ctrl+C to stop")
print("="*70 + "\n")

try:
    with sync_playwright() as p:
        print("Connecting to Chrome...")
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        
        contexts = browser.contexts
        if not contexts:
            print("❌ No browser contexts found")
            print("Run: ./start_chrome_debug.sh")
            exit()
        
        context = contexts[0]
        print(f"✅ Connected! Monitoring {len(context.pages)} tabs\n")
        
        last_urls = {}
        change_count = 0
        
        while True:
            time.sleep(0.3)  # Check 3x per second
            
            pages = context.pages
            
            for page in pages:
                try:
                    current_url = page.url
                    page_id = id(page)
                    
                    # First time seeing this page
                    if page_id not in last_urls:
                        last_urls[page_id] = current_url
                        print(f"🆕 Tab {len(last_urls)}: {current_url[:70]}")
                    
                    # URL changed!
                    elif last_urls[page_id] != current_url:
                        change_count += 1
                        print(f"\n" + "="*70)
                        print(f"🔄 URL CHANGE #{change_count}")
                        print("="*70)
                        print(f"From: {last_urls[page_id][:65]}")
                        print(f"To:   {current_url[:65]}")
                        print("="*70 + "\n")
                        
                        last_urls[page_id] = current_url
                
                except Exception as e:
                    print(f"Error: {e}")
            
            # Status every 10 seconds
            if int(time.time()) % 10 == 0:
                print(f"💭 Monitoring... {change_count} URL changes detected")
                time.sleep(1)  # Prevent multiple prints

except KeyboardInterrupt:
    print(f"\n\n✅ Test complete! Detected {change_count} URL changes")

except Exception as e:
    print(f"\n❌ Error: {e}")

