# 🚀 Koyeb + MongoDB Atlas Setup

## ✅ MongoDB Atlas is Ready!

Your MongoDB connection string is configured and ready to use.

---

## 📋 Configure Koyeb Environment Variable

### Step 1: Go to Koyeb Dashboard

1. Open: **https://app.koyeb.com**
2. Click on your app: **misleading-aile-personalnikhil-27cb1e20**
3. Click **Settings** tab

### Step 2: Add MONGODB_URI Environment Variable

1. Scroll to **Environment variables** section
2. Click **Add variable**
3. Fill in:
   - **Name:** `MONGODB_URI`
   - **Value:** 
     ```
     mongodb+srv://nikhilkmr6303_db_user:i020PP2CRHKhLtwo@cluster0.kyaetao.mongodb.net/medium_scraper?retryWrites=true&w=majority&appName=Cluster0
     ```
4. Click **Save**
5. Click **Deploy** to redeploy with MongoDB

### Step 3: Wait for Deployment

- Deployment takes ~2-3 minutes
- Koyeb will automatically restart your app
- Your app will now use MongoDB Atlas!

---

## 🎯 What This Changes

### BEFORE (SQLite):
- ❌ Database resets on every deployment
- ❌ Data lost when Koyeb restarts
- ❌ Have to rescrape articles each time
- ❌ No persistence

### AFTER (MongoDB Atlas):
- ✅ Data persists forever
- ✅ Survives deployments/restarts
- ✅ Automatic backups
- ✅ 512MB free storage
- ✅ ~50,000 Q&A pairs capacity
- ✅ Never lose data again!

---

## 🔧 Verify It's Working

After redeployment, test:

```bash
# Check stats (should show MongoDB)
curl https://misleading-aile-personalnikhil-27cb1e20.koyeb.app/api/stats

# Should return:
{
  "database_type": "MongoDB Atlas",
  "persistent": true,
  ...
}
```

---

## 📊 Your MongoDB Details

**Connection String:**
```
mongodb+srv://nikhilkmr6303_db_user:i020PP2CRHKhLtwo@cluster0.kyaetao.mongodb.net/medium_scraper?retryWrites=true&w=majority&appName=Cluster0
```

**Database Name:** `medium_scraper`  
**Collections:** `jobs`, `qa_pairs`  
**Storage:** 512MB (free tier)

---

## 🌐 MongoDB Atlas Dashboard

Access your data anytime at:
**https://cloud.mongodb.com**

### Features:
- ✅ View all Q&A pairs
- ✅ Run queries
- ✅ Download data
- ✅ Monitor performance
- ✅ See storage usage

---

## 🛠️ Testing Locally (Optional)

Want to test MongoDB locally before deploying?

```bash
# Set environment variable
export MONGODB_URI="mongodb+srv://nikhilkmr6303_db_user:i020PP2CRHKhLtwo@cluster0.kyaetao.mongodb.net/medium_scraper?retryWrites=true&w=majority&appName=Cluster0"

# Test connection
python3 database_mongo.py

# Should output:
# ✅ Connected to MongoDB Atlas
# ✅ Database indexes created
# ✅ MongoDB connection successful!
```

---

## ⚠️ Important Security Notes

1. **Never commit credentials to GitHub** ✅ (API_KEYS.txt is in .gitignore)
2. **Use environment variables on Koyeb** ✅ (You'll add it manually)
3. **Your MongoDB is password-protected** ✅ (Already configured)
4. **Free tier has IP whitelist** - Already set to "Allow from anywhere" for Koyeb

---

## 🎊 Benefits You'll Get

1. **Persistent Data**
   - Scrape 100 articles today
   - Redeploy tomorrow
   - All 100 articles still there! ✅

2. **No More Empty /api/qa**
   - Data survives Koyeb restarts
   - No need to rescrape every time

3. **Automatic Backups**
   - MongoDB takes daily snapshots
   - 7-day retention (free tier)

4. **Scalable**
   - Start with 512MB (free)
   - Upgrade anytime if needed
   - No code changes required

---

## 📝 Checklist

- [ ] Go to Koyeb dashboard
- [ ] Add `MONGODB_URI` environment variable
- [ ] Click Deploy/Save
- [ ] Wait 2-3 minutes for redeployment
- [ ] Test `/api/stats` endpoint
- [ ] Confirm `"database_type": "MongoDB Atlas"`
- [ ] Scrape some articles
- [ ] Check data persists after restart! 🎉

---

## 🆘 Troubleshooting

### Error: "MONGODB_URI environment variable not set"
→ Make sure you added the variable in Koyeb Settings and redeployed

### Error: "Authentication failed"
→ Double-check the username/password in the connection string

### Error: "IP not whitelisted"
→ In MongoDB Atlas → Network Access → Add "0.0.0.0/0" (Allow from anywhere)

### Can't see data in MongoDB Atlas
→ Go to https://cloud.mongodb.com → Browse Collections → medium_scraper

---

## 🎉 Ready!

Once you add the `MONGODB_URI` to Koyeb and redeploy:
- ✅ Your data will persist forever
- ✅ No more empty databases
- ✅ Professional persistent storage
- ✅ Free tier forever

**Let's make your Q&A database permanent!** 💾✨

