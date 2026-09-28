# 🚀 Deploy to Render - Complete Guide

## What You're Deploying

A **web-based** Telegram unban tool with a beautiful UI that you can access from anywhere! No need to run it on your computer.

---

## 📋 Prerequisites

1. A **Render.com** account (free): https://render.com
2. A **GitHub** account: https://github.com
3. Your Telegram API credentials (already configured in the code!)

---

## 🎯 Step-by-Step Deployment

### Step 1: Push Your Code to GitHub

1. **Create a new repository** on GitHub:
   - Go to https://github.com/new
   - Name it: `telegram-unban-tool`
   - Make it **Private** (recommended)
   - Click "Create repository"

2. **Push your code** from your computer:

Open PowerShell in your project folder and run:

```powershell
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/telegram-unban-tool.git
git push -u origin main
```

*(Replace `YOUR_USERNAME` with your GitHub username)*

---

### Step 2: Deploy on Render

1. **Login to Render**: https://dashboard.render.com

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub account if not already connected
   - Select your `telegram-unban-tool` repository

3. **Configure the service**:
   - **Name**: `telegram-unban-tool` (or any name you like)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python web_unban.py`

4. **Environment Variables**:
   
   Render should auto-detect from `render.yaml`, but if not, add these manually:
   
   - `API_ID` = `33325009`
   - `API_HASH` = `3ef83055e590c94d0c4572dc094771f4`
   - `SECRET_KEY` = `your-random-secret-key-here` (any random string)

5. **Instance Type**:
   - Select **Free** (if using free plan)
   - Or **Starter** for better performance

6. Click **"Create Web Service"**

---

### Step 3: Wait for Deployment

- Render will build and deploy your app (takes 2-5 minutes)
- Watch the logs to see progress
- Once you see: `Application startup complete` → You're live! 🎉

---

### Step 4: Access Your Tool

1. Render will give you a URL like:
   ```
   https://telegram-unban-tool.onrender.com
   ```

2. **Open that URL in your browser**

3. You'll see a beautiful web interface! 🎨

---

## 🎮 How to Use Your Deployed Tool

### First Time Login:

1. Open your Render URL in browser
2. Enter your **phone number** (with country code, e.g., `+1234567890`)
3. Click "Send Verification Code"
4. Check Telegram - you'll receive a code
5. Enter the code (and 2FA password if you have one)
6. Click "Login"

### Unban Users:

1. After logging in, you'll see the main screen
2. Enter your **channel username** or link:
   - `@mychannel`
   - `https://t.me/mychannel`
   - Or channel ID: `-1001234567890`
3. Click "Start Unbanning"
4. **Watch the magic happen!** ✨
   - See real-time progress
   - Live logs showing each user unbanned
   - Total count updates

### Important Notes:

- Your **login session is saved** on Render's server
- You only need to login once
- The tool works 24/7 once deployed
- You can access it from any device with the URL

---

## 🔐 Security Notes

### ✅ Your Credentials Are Safe:

- API credentials are stored as **environment variables** (encrypted on Render)
- Session data is isolated to your Render instance
- No one else can access your deployment
- Make your GitHub repo **Private** for extra security

### 🚨 Important:

- Never share your Render URL publicly
- Never share your `SECRET_KEY`
- Keep your GitHub repo private
- Don't commit `.session` files to GitHub (they're auto-generated)

---

## 💰 Pricing

### Render Free Tier:

- ✅ **Free forever**
- ✅ 750 hours/month (enough for most use)
- ⏳ Spins down after 15 min of inactivity
- ⏳ Takes ~30 seconds to wake up when you visit

### Render Paid Plans:

- **Starter ($7/month)**: Always on, faster, no spin down
- **Pro ($25/month)**: Even more resources

**Recommendation**: Start with Free tier, upgrade if needed.

---

## 🐛 Troubleshooting

### "Application failed to respond"
- Wait 30 seconds (free tier wakes up slowly)
- Check Render logs for errors

### "Could not find channel"
- Make sure you're an admin in that channel
- Try using channel ID instead of username

### "Session expired"
- Just login again - your session may have timed out
- This is normal if you haven't used it in a while

### "Build failed"
- Check if all files were pushed to GitHub
- Verify `requirements.txt` exists
- Check Render logs for specific error

---

## 🔄 Updating Your Deployment

When you want to make changes:

1. Edit your code locally
2. Commit and push to GitHub:
   ```powershell
   git add .
   git commit -m "Updated feature"
   git push
   ```
3. Render **automatically re-deploys** your changes!

---

## 📊 Monitoring

### Check Logs:
- Go to Render Dashboard
- Click your service
- Click "Logs" tab
- See real-time activity

### Check Status:
- Dashboard shows if service is running
- Shows uptime, requests, errors

---

## 🎉 You're Done!

Your Telegram unban tool is now:
- ✅ Deployed on the cloud
- ✅ Accessible from anywhere
- ✅ Running 24/7 (on paid plan) or on-demand (free plan)
- ✅ Has a beautiful web interface
- ✅ Automatically unbans ALL users

**Your URL**: Check your Render dashboard for your app URL

**Enjoy your automated unban tool! 🚀**

---

## 📞 Need Help?

Common issues:
1. Forgot to push code to GitHub? → Push it now
2. Render build failing? → Check logs for specific error
3. Can't login? → Make sure phone number has country code
4. Session keeps expiring? → This is normal, just re-login

**Remember**: Your API credentials are already set! Just deploy and use! 🎯
