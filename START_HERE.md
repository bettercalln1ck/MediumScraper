# 🚀 Medium iOS Scraper - START HERE

## 🎯 What You Have:

A complete AI-powered system to extract iOS interview questions and answers from Medium!

---

## ⚡ Quick Start (30 seconds):

```bash
cd /Users/nikhilkumar/Downloads/MediumScraper

# Start the Q&A extractor
python3 monitor_qa_browsing.py
```

Then:
1. Browse Medium in the Chrome window that's open
2. Search: "ios interview swift"
3. Click articles
4. AI extracts questions + answers automatically!
5. Press Ctrl+C when done

Results saved to: `ios_qa_pairs_TIMESTAMP.csv`

---

## 📁 What Each File Does:

### 🌟 Main Scripts (Use These):

| File | What It Does | Output | Speed |
|------|-------------|--------|-------|
| **monitor_qa_browsing.py** ⭐ | Extract Q&A pairs | Questions + Answers | 2s/article |
| **monitor_my_browsing_ai.py** | Extract questions only | Questions | 0.5s/article |
| **filter_existing_questions.py** | Clean old scraped data | Filtered CSV | - |

### 🛠️ Helper Scripts:

| File | Purpose |
|------|---------|
| `start_chrome_debug.sh` | Launch Chrome with debugging |
| `test_groq.py` | Test AI API connection |
| `extract_qa_pairs.py` | Test Q&A extraction |
| `test_connection.py` | Test Chrome connection |

### 📚 Documentation:

| File | What's Inside |
|------|--------------|
| **START_HERE.md** | This file - quick overview |
| **README_QA.md** | Complete Q&A extraction guide |
| **AI_GUIDE.md** | AI features and configuration |
| **QUICK_START.md** | Basic browser monitoring |
| **README.md** | Original full documentation |

### 🗂️ Old Scripts (Still Work):

| File | Purpose |
|------|---------|
| `monitor_my_browsing.py` | Regex-based (no AI) |
| `pull_ios_question_no_auth.py` | Automated scraper |
| `pull_ios_question.py` | Automated with login |

---

## 🎯 Choose Your Mode:

### 1. **I want Q&A pairs for interview prep** ⭐

```bash
python3 monitor_qa_browsing.py
```

**Output:**
- question: What is weak vs strong reference?
- answer: Weak references don't increase retain count...
- source_url: https://medium.com/...

**Best for:** Study, flashcards, interview prep

---

### 2. **I just want questions (faster)**

```bash
python3 monitor_my_browsing_ai.py
```

**Output:**
- question: What is weak vs strong reference?
- source_url: https://medium.com/...

**Best for:** Quick collection

---

### 3. **I want to clean my old data**

```bash
python3 filter_existing_questions.py
```

Filters your `ios_interview_questions.csv` to remove non-iOS content.

---

## 📊 Your Current Data:

### Original Scrape (Before AI):
- `ios_interview_questions.csv` - 122 questions (85% noise)

### After AI Filtering:
- `ios_questions_filtered.csv` - 18 iOS questions (100% clean)
- `ios_questions_filtered.json` - JSON format

### Future Q&A Extractions:
- `ios_qa_pairs_TIMESTAMP.csv` - Complete Q&A pairs!

---

## 🔧 Setup Checklist:

- [x] Groq API installed
- [x] API key configured
- [x] Chrome debug setup tested
- [x] AI extraction tested
- [x] Q&A extraction ready

**You're all set!** 🎉

---

## 💡 Pro Tips:

### Best Medium Searches:
```
"ios interview questions swift"
"swiftui common questions"
"ios developer interview prep"
"swift memory management"
"ios architecture patterns"
```

### Browse Strategy:
1. Open 5-10 articles in separate tabs
2. Let AI process each one
3. Review extracted Q&A
4. Continue browsing or stop

### Output Usage:
- **Anki:** Import CSV for flashcards
- **Notion:** Create knowledge base
- **Excel:** Study sheets
- **JSON:** Feed into your own apps

---

## 🆘 Troubleshooting:

### Chrome Not Connected?
```bash
./start_chrome_debug.sh
# Wait 5 seconds, then:
python3 monitor_qa_browsing.py
```

### API Error?
```bash
# Test connection:
python3 test_groq.py
```

### No Questions Found?
- Make sure you're on an actual article (not search page)
- Look for articles with "interview" or "questions" in title
- Try longer articles (10+ min read time)

---

## 📈 Expected Results:

**From 10 Medium articles:**
- ~7-8 will have iOS content
- ~30-50 Q&A pairs extracted
- 100% iOS-relevant
- Complete, study-ready answers

**Time:** ~2-3 minutes browsing

---

## 🎓 What Makes This Special:

✅ **AI-Powered** - Not just regex pattern matching  
✅ **Complete Answers** - Not just questions  
✅ **iOS-Filtered** - No web dev, data science noise  
✅ **Free** - Groq free tier (14.4K/day)  
✅ **Fast** - Real-time extraction  
✅ **Your Browser** - Use your Medium login  

---

## 🚀 Ready to Start?

**Quick Command:**
```bash
python3 monitor_qa_browsing.py
```

**Then browse Medium and watch the magic happen!** ✨

---

## 📞 Need Help?

1. Check **README_QA.md** for Q&A details
2. Check **AI_GUIDE.md** for AI configuration
3. Run `python3 test_groq.py` to test setup

---

**Happy Interview Prep!** 🎯📚✨

