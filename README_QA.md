# 🎓 iOS Interview Q&A Extractor

Extract **complete Question & Answer pairs** from Medium articles using AI!

## 🌟 What's New:

Instead of just questions, now you get **COMPLETE Q&A PAIRS**!

### Before:
```csv
question,source_url
"What is the difference between weak and strong references?",https://...
```

### After:
```csv
question,answer,source_url
"What is the difference between weak and strong references?","Weak references don't increase the retain count and allow ARC to deallocate the object. Strong references increase retain count and keep the object in memory. Use weak for delegates and closures to prevent retain cycles.",https://...
```

## 🚀 Quick Start:

### Method 1: Live Q&A Extraction (Recommended)

```bash
# Make sure Chrome is running with debugging
python3 monitor_qa_browsing.py
```

Then browse Medium articles in Chrome - AI extracts Q&A pairs automatically!

### Method 2: Extract from Specific URL

```bash
python3 extract_qa_pairs.py
```

Edit the script to add your target URLs.

## 📊 What You Get:

### Example Output:

```
Q: How does iOS handle screenshot prevention compared to Android?
A: iOS provides no official API to prevent users from capturing their screen, unlike Android which offers native methods to block screenshots within an app. This is due to Apple's design philosophy of prioritizing user control and data access. As a result, iOS apps must rely on workarounds to protect sensitive content.

Q: What is a practical solution to prevent screenshot capture in SwiftUI?
A: A reliable workaround in SwiftUI is to use UITextField to mask secure content by utilizing its isSecureTextEntry property, which natively obscures the content and applies to screenshots, screen recordings, and the app switcher. This method does not require external libraries and works on all iOS versions.
```

## 💡 Use Cases:

✅ **Interview Prep** - Study complete Q&A pairs  
✅ **Flashcards** - Import into Anki/Quizlet  
✅ **Knowledge Base** - Build iOS documentation  
✅ **Training Data** - Create AI training datasets  
✅ **Study Notes** - Comprehensive iOS reference  

## 📁 Output Format:

### CSV Format:
```csv
question,answer,source_url,timestamp
"What is...",""Answer text...",https://...,2024-12-24T...
```

### JSON Format:
```json
[
  {
    "question": "What is...",
    "answer": "Answer text...",
    "source_url": "https://...",
    "timestamp": "2024-12-24T..."
  }
]
```

## ⚙️ Configuration:

Edit `monitor_qa_browsing.py`:

```python
# Line 12: API key (already set)
GROQ_API_KEY = "your-key"

# Line 20: Context length
text = article.get_text()[:15000]  # Increase for longer articles

# Line 33: Answer length
"Each answer must be 2-4 sentences"  # Adjust as needed
```

## 🎯 Quality Control:

The AI ensures:
- ✅ Only iOS/Swift/Apple content
- ✅ Questions have complete answers
- ✅ Answers are 2-4 sentences (concise but comprehensive)
- ✅ Technical accuracy maintained
- ✅ Proper formatting

## 💰 Cost:

**Groq Free Tier:**
- Free up to 14,400 requests/day
- ~1-2 requests per article (depending on length)
- Can extract ~200 articles/day for **FREE**

## 📈 Performance:

**Sample Results:**
- 10 articles browsed
- 8 contained iOS Q&A
- 47 Q&A pairs extracted
- 100% iOS-relevant
- Complete answers included

**Time:**
- ~2-3 seconds per article
- Faster than manual extraction
- Better quality than regex

## 🔧 Tips:

### 1. Best Articles for Q&A:
- "iOS Interview Questions" lists
- Tutorial articles with explanations
- Technical deep-dives
- Architecture guides

### 2. Search Terms:
- "ios interview questions"
- "swift interview guide"
- "ios developer interview"
- "swiftui common questions"

### 3. Browse Strategy:
- Open 5-10 articles in tabs
- Let monitor process each one
- Review extracted Q&A
- Continue browsing

## 📚 Example Session:

```bash
$ python3 monitor_qa_browsing.py

✅ Connected! Monitoring 1 open tabs
💡 Browse Medium articles - AI will extract Q&A pairs

🔍 Extracting from: https://medium.com/@someone/ios-interview...
✨ Extracted 12 Q&A pairs!
   📊 Total: 12 Q&A pairs from 1 articles

🔍 Extracting from: https://medium.com/@another/swift-closures...
✨ Extracted 8 Q&A pairs!
   📊 Total: 20 Q&A pairs from 2 articles

[Press Ctrl+C when done]

📊 SESSION SUMMARY - Q&A EXTRACTION
✅ Articles checked: 5
📝 Articles with Q&A: 4
💡 Total Q&A pairs extracted: 35

💾 Saved to:
   - ios_qa_pairs_20241224_163045.csv
   - ios_qa_pairs_20241224_163045.json
```

## 🆚 Comparison:

| Feature | Questions Only | Q&A Pairs |
|---------|---------------|-----------|
| Questions | ✅ | ✅ |
| Answers | ❌ | ✅ |
| Study Value | Low | High |
| Interview Prep | Partial | Complete |
| Flashcards | No | Yes |

## 🚀 Next Steps:

1. **Start monitoring:**
   ```bash
   python3 monitor_qa_browsing.py
   ```

2. **Browse Medium** for iOS content

3. **Review extracted Q&A** in CSV/JSON files

4. **Import to your tool:**
   - Anki (flashcards)
   - Notion (knowledge base)
   - Excel (study sheet)
   - Your own app

---

**Questions?** Check [AI_GUIDE.md](AI_GUIDE.md) for more AI features!

