# 🔑 API Key Setup

## ⚠️ IMPORTANT: API Key Security

Your Groq API key is currently hardcoded in the scripts. Before sharing/deploying:

### Option 1: Environment Variable (Recommended)

1. Remove hardcoded key from scripts
2. Use environment variable instead:

```python
import os
GROQ_API_KEY = os.getenv('GROQ_API_KEY', 'your-key-here')
```

3. Set in terminal:
```bash
export GROQ_API_KEY="your-actual-key"
```

### Option 2: Config File

1. Create `config.py` (already in .gitignore):
```python
GROQ_API_KEY = "your-key-here"
```

2. Import in scripts:
```python
from config import GROQ_API_KEY
```

3. Add to `.gitignore`:
```
config.py
```

### Option 3: For Public Repos

If sharing on GitHub publicly:
1. Replace actual key with placeholder in all scripts
2. Add instructions in README for users to get their own key

## 📝 Scripts with API Key:

- `monitor_qa_smart.py`
- `monitor_qa_debug.py`
- `deduplicate_questions.py`
- `test_groq.py`

## 🔒 Current Status:

✅ `.gitignore` configured to exclude data files  
⚠️ API key is hardcoded (replace before public sharing)

## 🎯 Quick Fix Before Pushing:

If you want to make it public-ready, run:

```bash
# Replace API key with placeholder in all scripts
sed -i '' 's/gsk_[a-zA-Z0-9]*/your-groq-api-key-here/g' *.py
```

Then users can add their own key!

