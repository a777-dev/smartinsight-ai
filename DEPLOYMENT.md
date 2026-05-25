# 🚀 Deployment Guide for SmartInsight AI

This guide will help you deploy the app to **Streamlit Cloud** (free, instant, zero-downtime).

## Prerequisites

- A **GitHub account** (free: github.com)
- A **Streamlit Cloud account** (free: streamlit.io/cloud)

## Step 1: Initialize Git (If Not Already Done)

```bash
cd /path/to/behavioral-advisor

# Initialize git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: SmartInsight AI - Behavioral Intelligence Platform"

# Rename branch to main (if needed)
git branch -M main
```

## Step 2: Create a GitHub Repository

1. Go to **github.com** and log in
2. Click **+** in top-right corner → **New repository**
3. Name it: `smartinsight-ai` (or whatever you prefer)
4. Keep it **Public** (required for free Streamlit Cloud deployment)
5. **Do NOT** initialize with README (we already have one)
6. Click **Create repository**

## Step 3: Push Code to GitHub

After creating the repository, you'll see instructions. Run:

```bash
git remote add origin https://github.com/YOUR_USERNAME/smartinsight-ai.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 4: Deploy to Streamlit Cloud

1. Go to **[streamlit.io/cloud](https://share.streamlit.io)**
2. Click **New app** button
3. Under "Deploy an app":
   - **Repository:** Select your `smartinsight-ai` repo
   - **Branch:** Select `main`
   - **Main file path:** Enter `Home.py`
4. Click **Deploy**

Streamlit Cloud will:
- Pull your code from GitHub
- Install dependencies from `requirements.txt`
- Run the app automatically
- Assign you a free URL like: `https://yourname-smartinsight-ai.streamlit.app`

**⏱️ First deployment takes ~3-5 minutes** (includes model training)

## Step 5: Test Your App

Your app is now live! Share your URL with anyone:
```
https://yourname-smartinsight-ai.streamlit.app
```

## After Deployment

### Making Updates

Any time you push new code to GitHub:

```bash
git add .
git commit -m "Update: description of changes"
git push
```

Streamlit Cloud will **automatically redeploy** (~30 seconds) with zero downtime.

### Custom Domain (Optional)

Upgrade your Streamlit account to use a custom domain like `smartinsight.your-company.com`

### Performance & Scaling

- **Concurrent users:** Unlimited (scales automatically)
- **Memory:** 1 GB RAM (sufficient for our models)
- **Storage:** 1 GB (sufficient for all artifacts)
- **Runtime:** Cold start ~3-5 min (first run), <1 sec thereafter

## Troubleshooting

### Models not training on first run

- Check the **Streamlit Cloud logs** (Settings → View logs)
- Cold start may take up to 5 minutes
- Refresh the page after 3 minutes if stuck

### Theme not applying

- Clear browser cache
- Ensure `.streamlit/config.toml` has `base = "dark"`

### Dependencies not installing

- Ensure `requirements.txt` is in the root directory
- Check for typos in package names
- View logs for detailed error messages

### "Repo not found" error

- Verify GitHub repo is **public**
- Check spelling of repository URL
- Ensure you have push access

## Monitoring Your App

**On Streamlit Cloud Dashboard:**

- View logs in real-time
- Check resource usage
- Monitor deployment status
- Restart the app if needed

## Sharing Your App

- **Direct link:** `https://yourname-smartinsight-ai.streamlit.app`
- **GitHub link:** `https://github.com/yourname/smartinsight-ai`
- **Social media:** Share your live URL directly!

## Keeping Your App Running

The free Streamlit Cloud will:
- ✅ Keep your app live 24/7
- ✅ Auto-scale for concurrent users
- ✅ Handle all infrastructure
- ✅ Never charge you (free plan)

## Advanced: Environment Variables (Optional)

If you need secrets or config:

1. Go to Streamlit Cloud App Settings
2. Click "Secrets"
3. Add any secrets as key-value pairs

Then access in your code:
```python
import streamlit as st
my_secret = st.secrets["my_key"]
```

---

**Your app is now deployed! 🎉**

Need help? Visit: [docs.streamlit.io](https://docs.streamlit.io)
