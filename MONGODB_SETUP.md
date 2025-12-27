# 💾 MongoDB Atlas Setup - Persistent Database

## 🎯 Why MongoDB Atlas?

**Problem:** SQLite on Koyeb resets every deployment → Data loss  
**Solution:** MongoDB Atlas (free tier) → Persistent cloud database ✅

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Create Free MongoDB Atlas Account

1. Go to: **https://www.mongodb.com/cloud/atlas/register**
2. Sign up with Google/GitHub (fastest)
3. Choose: **FREE M0 Cluster** (512MB storage)
4. Select region closest to you
5. Cluster name: `MediumScraperDB` (or anything)
6. Click **Create Cluster** (takes 1-3 minutes)

### Step 2: Create Database User

1. Go to **Database Access** (left sidebar)
2. Click **Add New Database User**
3. Username: `scraper_user`
4. Password: Click **Autogenerate Secure Password** (copy it!)
5. Database User Privileges: **Read and write to any database**
6. Click **Add User**

### Step 3: Whitelist IP Addresses

1. Go to **Network Access** (left sidebar)
2. Click **Add IP Address**
3. Click **Allow Access from Anywhere** (for testing)
   - Or add your specific IPs for production
4. Click **Confirm**

### Step 4: Get Connection String

1. Go to **Database** → Click **Connect** on your cluster
2. Choose **Connect your application**
3. Driver: **Python** | Version: **3.12 or later**
4. Copy the connection string:

```
mongodb+srv://scraper_user:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

5. Replace `<password>` with the password you copied in Step 2

### Step 5: Add to Your API Keys

Edit `/Users/nikhilkumar/Downloads/MediumScraper/API_KEYS.txt`:

```
MONGODB_URI=mongodb+srv://scraper_user:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

---

## 🔧 Update Your Application

### Install MongoDB Driver

```bash
pip3 install pymongo
```

Add to `requirements.txt`:
```
pymongo
```

### Configure Koyeb Environment Variable

1. Go to your Koyeb dashboard
2. Click your app → **Settings** → **Environment variables**
3. Add new variable:
   - Name: `MONGODB_URI`
   - Value: Your connection string from Step 4
4. Click **Save** → App will redeploy

---

## ✅ Benefits

| Feature | SQLite (Current) | MongoDB Atlas |
|---------|-----------------|---------------|
| **Persistence** | ❌ Lost on redeploy | ✅ Always persisted |
| **Free Tier** | ✅ Yes | ✅ Yes (512MB) |
| **Auto-backup** | ❌ No | ✅ Yes |
| **Scalability** | ❌ Limited | ✅ Unlimited |
| **Multi-region** | ❌ No | ✅ Yes |
| **Cost** | Free | Free (M0) |

---

## 📊 MongoDB Free Tier Limits

- **Storage:** 512 MB (enough for ~50,000 Q&A pairs!)
- **RAM:** 512 MB shared
- **Connections:** 100 concurrent
- **Backup:** Daily snapshots (7 days retention)
- **Cost:** $0 forever

Perfect for your use case! ✅

---

## 🎯 What You Get

With MongoDB Atlas:
- ✅ **Data survives redeployments**
- ✅ **Automatic backups**
- ✅ **Web-based database viewer**
- ✅ **Query anywhere, anytime**
- ✅ **No data loss**

---

## 🔗 Useful Links

- **MongoDB Atlas Dashboard:** https://cloud.mongodb.com
- **Documentation:** https://www.mongodb.com/docs/atlas/
- **Connection Troubleshooting:** https://www.mongodb.com/docs/atlas/troubleshoot-connection/
- **Free Tier Details:** https://www.mongodb.com/pricing

---

## 🆘 Troubleshooting

### Connection Error: "Authentication failed"
→ Check username/password in connection string

### Connection Error: "IP not whitelisted"
→ Add 0.0.0.0/0 to Network Access (Allow from anywhere)

### Can't see data
→ Use MongoDB Compass (free GUI) to view data visually

### Want local testing
→ Use MongoDB Community Server or keep SQLite for local dev

---

## 🎊 Next Steps

1. Follow steps 1-5 above
2. Get your `MONGODB_URI`
3. Add it to Koyeb environment variables
4. Redeploy
5. **Your data will now persist!** 🎉

---

**Ready to never lose your Q&A data again? Set it up now!** 💾✨

