#!/usr/bin/env python3
# test_groq.py - Quick test to verify Groq API works

from groq import Groq
import sys

GROQ_API_KEY = "your-groq-api-key-here"

print("Testing Groq API connection...")
print("")

try:
    client = Groq(api_key=GROQ_API_KEY)
    
    # Test with a simple iOS question extraction
    test_text = """
    What is the difference between weak and strong references in Swift?
    How do you prevent retain cycles?
    What is React hooks in JavaScript?
    Explain closures in Swift.
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""Extract ONLY iOS/Swift questions. Ignore non-iOS questions.
Return one per line. If none, return "NONE".

{test_text}

iOS Questions:"""
        }],
        temperature=0,
        max_tokens=500
    )
    
    result = response.choices[0].message.content.strip()
    
    print("✅ Groq API is working!")
    print("")
    print("Test extraction result:")
    print("-" * 60)
    print(result)
    print("-" * 60)
    print("")
    print("✨ Ready to use AI-powered question extraction!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("")
    print("Check your API key at: https://console.groq.com/keys")
    sys.exit(1)

