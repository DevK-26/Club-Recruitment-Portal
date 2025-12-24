# 🚀 Deployment Guide - Render + Neon (Free Forever)

Deploy your recruitment system with **100% free hosting** - no credit card required!

---

## 📋 What You'll Get

- ✅ **Web Hosting**: Render.com (Free - 750 hours/month)
- ✅ **Database**: Neon.tech PostgreSQL (Free - 3GB, unlimited time)
- ✅ **HTTPS**: Included automatically
- ✅ **Auto-deploy**: Push to GitHub = automatic deployment
- ✅ **Cost**: $0 forever 🎉

**Total Setup Time**: ~15 minutes

---

## 🎯 Prerequisites

- [ ] GitHub account (free)
- [ ] Gmail account (for email notifications)
- [ ] Code pushed to GitHub repository

---

## Step 1: Create Neon Database (3 min)

### 1. Sign Up
1. Go to https://neon.tech
2. Click **"Sign Up"** → **"Continue with GitHub"**
3. Verify email if prompted

### 2. Create Database
1. Click **"Create a project"**
2. Configure:
   - Name: `hiring-system`
   - Region: Select closest to you
   - PostgreSQL: 15 (default)
3. Click **"Create project"**

### 3. Get Connection String
1. In dashboard, find **"Connection Details"**
2. **Important**: Select **"Pooled connection"** (better performance)
3. Copy the connection string (looks like):
   ```
   postgresql://user:pass@ep-xxx.region.aws.neon.tech/db?sslmode=require
   ```
4. **Save this** - you'll need it for Render!

---

## Step 2: Deploy to Render (5 min)

### 1. Sign Up
1. Go to https://render.com
2. Click **"Get Started"** → **"Sign up with GitHub"**
3. Authorize Render

### 2. Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Select your GitHub repository
3. Configure:
   ```
   Name: hiring-system
   Environment: Python 3
   Build Command: ./build.sh
   Start Command: gunicorn run:app
   Instance Type: Free
   ```

### 3. Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**:

#### Essential (Required):
```env
FLASK_ENV=production
SECRET_KEY=<click "Generate" for random value>
DATABASE_URL=<paste Neon connection string here>
BASE_URL=https://your-app-name.onrender.com
```

#### Email Configuration (add now or later):
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
```

**Get Gmail App Password:**
1. Enable 2FA on Gmail
2. Visit: https://myaccount.google.com/apppasswords
3. Create app password → Copy it

#### Optional Settings:
```env
CLUB_NAME=Tech Club
SUPPORT_EMAIL=support@techclub.com
SESSION_TIMEOUT=3600
MAX_FAILED_ATTEMPTS=5
LOCKOUT_DURATION=900
```

### 4. Deploy
1. Click **"Create Web Service"**
2. Wait 3-5 minutes for build
3. Watch logs for completion

---

## Step 3: Create Admin User (1 min)

### Option A: Using Environment Variables (No Shell Access Needed)

If Render free tier doesn't provide shell access, use this method:

1. Go to Render dashboard → Your service → **"Environment"** tab
2. Add these additional variables:
   ```env
   ADMIN_EMAIL=admin@example.com
   ADMIN_NAME=Admin User
   ADMIN_PASSWORD=YourSecurePassword123!
   ```
3. Click **"Save Changes"** (triggers redeploy)
4. Admin will be created automatically during build
5. ✅ Done! Use these credentials to login

**Important**: After first login, you can remove these env vars for security.

### Option B: Using Shell Access (If Available)

1. Go to Render dashboard → Your service → **"Shell"** tab
2. Run:
   ```bash
   flask create-admin
   ```
3. Enter admin details (email, name, password)
4. Done!

---

## Step 4: Test Your App (1 min)

1. Visit: `https://your-app-name.onrender.com/auth/login`
2. Login with admin credentials
3. ✅ **You're live!**

---

## 🎛️ Optional: Keep App Active

Free tier spins down after 15 min. To prevent cold starts:

1. Sign up at https://uptimerobot.com (free)
2. Add monitor:
   - URL: `https://your-app.onrender.com/auth/login`
   - Interval: 5 minutes
3. ✅ App stays awake!

---

## 🔧 Common Tasks

### Update Your App
```bash
git add .
git commit -m "Update"
git push
# Render auto-deploys!
```

### View Logs
- Render dashboard → Your service → **Logs** tab

### Run Migrations
```bash
# If you update models locally:
flask db migrate -m "Description"
git add migrations/
git commit -m "Add migration"
git push
# Render runs migrations automatically
```

### Create More Admins
```bash
# In Render Shell:
flask create-admin
```

---

## 🐛 Troubleshooting

### Build Fails
- Check Render logs
- Verify all files committed to GitHub
- Ensure `build.sh` is executable

### Can't Connect to Database
- Verify `DATABASE_URL` is correct
- Check Neon project is active
- Ensure connection string has `?sslmode=require`

### No Shell Access on Render
- **Solution**: Use environment variables to create admin (see Step 3, Option A)
- **Alternative**: Switch to Fly.io or PythonAnywhere (see [ALTERNATIVE_HOSTING.md](ALTERNATIVE_HOSTING.md))

### App Crashes
- Check Render logs for errors
- Verify all environment variables are set
- Ensure `SECRET_KEY` is generated

### Emails Don't Work
- Use Gmail App Password (not regular password)
- Verify 2FA enabled on Gmail
- Check `MAIL_USERNAME` and `MAIL_PASSWORD` are set

---

## 📊 Free Tier Limits

### Neon:
- 3GB storage
- No expiration ✅
- 100 hours compute/month
- 1 concurrent connection

### Render:
- 750 hours/month
- 512MB RAM
- Spins down after 15 min inactivity
- Cold start: ~30 seconds

**Perfect for recruitment system with 100-1000 candidates!**

---

## 🔐 Security Checklist

- ✅ Never commit `.env` file
- ✅ Use strong `SECRET_KEY` (auto-generated)
- ✅ Use Gmail App Passwords
- ✅ Strong admin passwords
- ✅ Keep dependencies updated

---

## 📈 When to Upgrade

You DON'T need to upgrade unless:
- Handling 5000+ candidates
- Need always-on (no cold starts) → Render $7/month
- Need >3GB database → Neon $19/month

**Free tier is sufficient for most club recruitment!**

---

## 🔗 Important Links

- **Render Dashboard**: https://dashboard.render.com
- **Neon Dashboard**: https://console.neon.tech
- **Gmail App Passwords**: https://myaccount.google.com/apppasswords
- **UptimeRobot**: https://uptimerobot.com

---

## ✅ Deployment Checklist

- [ ] Neon database created
- [ ] Connection string saved
- [ ] Code on GitHub
- [ ] Render service created
- [ ] Environment variables set
- [ ] Build succeeded
- [ ] Admin user created
- [ ] Login tested
- [ ] (Optional) Email configured
- [ ] (Optional) UptimeRobot configured

---

## 🎉 Success!

Your recruitment system is now:
- ✅ Live on professional infrastructure
- ✅ Free forever (no expiration)
- ✅ Production-ready with PostgreSQL
- ✅ Secure with HTTPS
- ✅ Auto-deploying from GitHub

**Start recruiting! 🎓**

---

## 💡 Pro Tips

1. Bookmark Render and Neon dashboards
2. Save DATABASE_URL in password manager
3. Create backup admin account
4. Test email before recruitment cycle
5. Monitor logs first few days

---

## 🆘 Need Help?

- **Render Docs**: https://render.com/docs
- **Neon Docs**: https://neon.tech/docs
- **Check Logs**: First step for any issue

**Happy recruiting!** 🚀
