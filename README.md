# 🚀 Medium iOS Q&A Scraper

AI-powered system for extracting iOS interview questions and answers from Medium articles.

## ✨ Features

- 🤖 **AI-Powered Extraction** - Uses Groq API (free) to extract iOS/Swift Q&As
- 🔄 **Real-time Deduplication** - Prevents duplicate/similar questions
- 💰 **Token Optimization** - 6 output formats with 45% token savings
- 🎯 **Smart Filtering** - Only iOS/Swift/Apple content
- 📊 **Complete Q&A Pairs** - Questions AND answers together
- 🆓 **100% Free** - Uses Groq free tier (14,400 requests/day)

## 🎯 Quick Start

### 1. Install Dependencies

```bash
pip3 install groq playwright beautifulsoup4 lxml pandas
python3 -m playwright install chromium
```

### 2. Get Your Free Groq API Key

1. Go to [console.groq.com](https://console.groq.com/)
2. Sign up (free)
3. Get API key
4. Update `GROQ_API_KEY` in the scripts

### 3. Run the Scraper

```bash
# Start Chrome with debugging
./start_chrome_debug.sh

# In another terminal, run the smart monitor
python3 monitor_qa_smart.py
```

### 4. Browse Medium Articles

1. Chrome opens automatically
2. Go to Medium.com
3. Search: "ios interview questions swift"
4. **Click into actual articles** (not search results page!)
5. Watch terminal for Q&A extraction
6. Press Ctrl+C when done

## 📁 Main Scripts

| Script                     | Purpose                              |
| -------------------------- | ------------------------------------ |
| `monitor_qa_smart.py` ⭐   | Main scraper with AI + deduplication |
| `monitor_qa_debug.py`      | Debug version with verbose output    |
| `deduplicate_questions.py` | Clean existing data                  |
| `optimize_for_ai.py`       | Convert to token-efficient formats   |
| `test_groq.py`             | Test API connection                  |

## 📊 Output Formats

After scraping, run `python3 optimize_for_ai.py` to generate:

- `ios_qa_optimized.txt` - Plain text (1,417 tokens) ⭐
- `ios_qa_optimized.compact` - Most compact (1,380 tokens)
- `ios_qa_optimized.jsonl` - JSONL format
- `ios_qa_optimized.chat_jsonl` - Fine-tuning format
- `ios_qa_optimized.md` - Markdown
- `ios_qa_optimized.xml` - XML format

## 📚 Documentation

- `START_HERE.md` - Quick start guide
- `COMPLETE_SYSTEM.md` - Full system overview
- `AI_USAGE_GUIDE.md` - Token optimization
- `DEDUPLICATION_GUIDE.md` - Prevent duplicates
- `INDEX.md` - File reference

## 🎓 Example Output

```csv
question,answer,source_url
"What is ARC in Swift?","Automatic Reference Counting (ARC) tracks strong references, and when the count goes to zero, the object is deallocated. Retain cycles can be avoided by using weak or unowned references.",https://medium.com/...
```

## 💡 Tips

1. **Browse actual articles**, not search pages
2. Look for articles with "interview" or "questions" in title
3. Use debug mode if questions aren't detected: `python3 monitor_qa_debug.py`
4. Adjust similarity threshold in `monitor_qa_smart.py` (line 11)

## 🔧 Configuration

### API Key

Update in all Python scripts:

```python
GROQ_API_KEY = "your-key-here"
```

### Similarity Threshold

In `monitor_qa_smart.py`:

```python
SIMILARITY_THRESHOLD = 0.7  # 0.5=loose, 0.7=balanced, 0.9=strict
```

## 🐛 Troubleshooting

### Chrome not connecting?

```bash
./start_chrome_debug.sh
# Wait 5 seconds
python3 monitor_qa_smart.py
```

### No questions detected?

- Make sure you're on an article page (not search/home)
- Use debug mode: `python3 monitor_qa_debug.py`
- Check Chrome is running: `curl http://127.0.0.1:9222/json/version`

### API errors?

```bash
python3 test_groq.py  # Test connection
```

## 💰 Cost

**FREE!** Uses Groq free tier:

- 14,400 requests/day
- ~50-100 requests per session
- $0 cost for typical usage

## 📈 Performance

**Typical session (10 articles):**

- Time: 5-10 minutes
- Q&As extracted: 30-50
- Duplicates filtered: 10-20
- Quality: 95%+ iOS-relevant

## 🏆 What Makes This Special

1. ✅ Complete Q&A pairs (not just questions)
2. ✅ AI-powered filtering (iOS-only)
3. ✅ Real-time deduplication
4. ✅ Token-optimized outputs (45% savings)
5. ✅ 100% free
6. ✅ Production-ready

## 📝 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Contributions welcome! This is a personal project but improvements are appreciated.

## ⚠️ Disclaimer

This tool is for educational purposes. Respect Medium's Terms of Service and use responsibly.

---

**Made with ❤️ for iOS developers preparing for interviews**

**Star ⭐ if you find this useful!**
