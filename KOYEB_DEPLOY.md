# 🚀 Deploy to Koyeb.com - Step-by-Step Guide

## ✅ Why Koyeb?

- **Free forever** (not a trial)
- **No credit card required**
- **Always on** (never sleeps)
- **512MB RAM included**
- **Professional hosting**
- **Auto-scaling**
- **Free SSL certificate**

---

## 📋 Step-by-Step Deployment

### Step 1: Sign Up (1 minute)

1. Go to: **https://www.koyeb.com**
2. Click **"Sign Up"** or **"Get Started"**
3. Choose **"Sign up with GitHub"** (easiest)
4. Authorize Koyeb to access your GitHub

✅ **No credit card needed!**

---

### Step 2: Create App (2 minutes)

1. In Koyeb dashboard, click **"Create App"**
2. Choose **"GitHub"** as the deployment source
3. Click **"Install the Koyeb GitHub App"**
4. Select your repository: **`MediumScraper`**
5. Click **"Install"**

---

### Step 3: Configure Deployment (3 minutes)

#### Builder Settings:
- **Builder**: Choose **"Buildpack"** (auto-detects Python)
- **Branch**: `main`
- **Build command**: Leave empty (auto-detected)
- **Run command**: 
  ```
  uvicorn simple_api:app --host 0.0.0.0 --port $PORT
  ```

#### Instance Settings:
- **Instance type**: **Free** (nano)
- **Regions**: Choose closest to you (e.g., Washington DC, Frankfurt)
- **Scaling**: 1 instance

#### Port Configuration:
- **Port**: `8000`
- **Protocol**: HTTP

---

### Step 4: Add Environment Variables (2 minutes)

Click **"Environment Variables"** section and add:

**Variable 1:**
- **Key**: `GROQ_API_KEY`
- **Value**: (your Groq API key from API_KEYS.txt)
- **Type**: Secret (toggle the eye icon)

**Variable 2:**
- **Key**: `FIRECRAWL_API_KEY`
- **Value**: (your Firecrawl API key from API_KEYS.txt)
- **Type**: Secret (toggle the eye icon)

**Variable 3:**
- **Key**: `PORT`
- **Value**: `8000`
- **Type**: Plain text

---

### Step 5: Deploy! (1 click)

1. Review all settings
2. Click **"Deploy"** button at the bottom
3. Wait 2-3 minutes while Koyeb:
   - Clones your repo
   - Detects Python
   - Installs dependencies from `requirements.txt`
   - Starts your API

---

## 🎯 Your API is Live!

Once deployed, you'll get a URL like:

```
https://your-app-name-your-org.koyeb.app
```

### Test Your API:

1. **Health Check:**
   ```
   https://your-app-name.koyeb.app/health
   ```
   Should return: `{"status": "healthy"}`

2. **Get Stats:**
   ```
   https://your-app-name.koyeb.app/stats
   ```

3. **Submit URL to Scrape:**
   ```bash
   curl -X POST "https://your-app-name.koyeb.app/scrape" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://medium.com/@author/ios-article"}'
   ```

---

## 📊 Monitor Your App

In Koyeb dashboard you can:

- ✅ View **real-time logs**
- ✅ See **metrics** (CPU, RAM, requests)
- ✅ Check **deployment history**
- ✅ Update **environment variables**
- ✅ Redeploy with one click

---

## 🔧 Troubleshooting

### Build Failed?

**Check logs** in Koyeb dashboard:
1. Click on your app
2. Go to "Logs" tab
3. Look for error messages

**Common issues:**
- Missing `requirements.txt` - Fixed ✅
- Wrong run command - Use: `uvicorn simple_api:app --host 0.0.0.0 --port $PORT`
- Missing environment variables - Add them in dashboard

### App Shows "Unhealthy"?

1. Check if port is correct (8000)
2. Verify environment variables are set
3. Check logs for startup errors

### Can't Access URL?

1. Make sure app status is "Healthy" (green)
2. Wait 1-2 minutes after deployment
3. Check if you're using HTTPS (not HTTP)

---

## 💡 Pro Tips

### Auto-Deploy on Git Push

Koyeb automatically redeploys when you push to GitHub!

```bash
cd /Users/nikhilkumar/Downloads/MediumScraper
git add .
git commit -m "Update API"
git push
```

Koyeb will detect the push and redeploy automatically! 🚀

### View Logs in Real-Time

In Koyeb dashboard:
- Go to your app
- Click "Logs" tab
- See live logs as requests come in

### Custom Domain (Optional)

Free plan includes:
- Custom domains
- Automatic SSL
- Just add domain in settings

---

## 📈 Free Tier Limits

Koyeb free tier includes:

- ✅ **512MB RAM**
- ✅ **0.1 CPU**
- ✅ **100GB bandwidth/month**
- ✅ **1 service (app)**
- ✅ **Always on** (never sleeps!)
- ✅ **Unlimited requests** (within bandwidth)

**This is enough for:**
- ~10,000 API requests/month
- ~500 article scrapes/month
- Testing and small production use

---

## 🎉 You're All Set!

Your iOS Q&A Scraper is now:
- ✅ Live on Koyeb
- ✅ Always on (24/7)
- ✅ Free forever
- ✅ Professional hosting
- ✅ Auto-deploys on git push

**Share your API URL and start scraping!** 🚀

---

## 📝 Quick Reference

**Your API URL:**
```
https://your-app-name.koyeb.app
```

**API Endpoints:**
- `GET /health` - Health check
- `GET /stats` - Get statistics
- `GET /qa` - Get all Q&A pairs
- `POST /scrape` - Submit URL to scrape

**Environment Variables:**
- `GROQ_API_KEY` - Your Groq API key
- `FIRECRAWL_API_KEY` - Your Firecrawl API key
- `PORT` - 8000

**Resources:**
- Dashboard: https://app.koyeb.com
- Docs: https://www.koyeb.com/docs
- Status: https://status.koyeb.com

---

## 🆘 Need Help?

- Check Koyeb docs: https://www.koyeb.com/docs
- View logs in dashboard
- Check GitHub repo: https://github.com/bettercalln1ck/MediumScraper

Enjoy your free, always-on API! 🎉

