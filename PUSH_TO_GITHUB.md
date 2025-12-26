# 🚀 Push to GitHub - Quick Guide

## Option 1: PRIVATE Repository (Keep API Key) ⭐ RECOMMENDED

```bash
# 1. Initialize and commit
git add .
git commit -m "Initial commit: iOS Q&A scraper with AI"

# 2. Create repo on GitHub:
#    Go to: https://github.com/new
#    Name: MediumScraper (or your choice)
#    ✅ Make it PRIVATE
#    ❌ Don't initialize with README

# 3. Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/MediumScraper.git
git branch -M main
git push -u origin main
```

**Safe!** API key stays private, only you can see it.

---

## Option 2: PUBLIC Repository (Remove API Key First)

```bash
# 1. Replace API key with placeholder
sed -i '' 's/your-groq-api-key-here/your-groq-api-key-here/g' *.py

# 2. Commit
git add .
git commit -m "Initial commit: iOS Q&A scraper with AI"

# 3. Create repo on GitHub:
#    Go to: https://github.com/new
#    Name: MediumScraper (or your choice)
#    ✅ Make it PUBLIC
#    ❌ Don't initialize with README

# 4. Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/MediumScraper.git
git branch -M main
git push -u origin main

# 5. Add your key back locally (NOT committed)
# Edit each .py file and add your real key back
```

**Safe for sharing!** Others can clone and use with their own keys.

---

## 🎯 Quick Commands (Private Repo):

```bash
cd /Users/nikhilkumar/Downloads/MediumScraper

git add .
git commit -m "Initial commit: iOS Q&A scraper with AI"

# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/MediumScraper.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username!

---

## ✅ What Will Be Committed:

**Included:**
- All scripts (.py)
- Documentation (.md)
- Shell scripts (.sh)
- .gitignore

**Excluded (in .gitignore):**
- Your scraped data (*.csv, *.json)
- Chrome profile
- Python cache
- IDE settings

**Total files:** ~15 files, ~50KB

---

## 🔐 Security Checklist:

- [ ] Decided: Private or Public?
- [ ] If Public: Replaced API key with placeholder
- [ ] Created repo on GitHub
- [ ] Replaced YOUR_USERNAME in commands
- [ ] Pushed successfully

---

**Pro Tip:** Start with PRIVATE, you can make it public later!
