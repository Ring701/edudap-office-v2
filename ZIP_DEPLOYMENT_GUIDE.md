# 📦 ZIP File Deployment Guide

This guide shows you how to deploy EduDAP Office v2 CRM using the ZIP file - **NO COMMAND LINE TOOLS NEEDED!**

---

## 🎯 What You Need

1. **GitHub Account** - [Sign up here](https://github.com)
2. **Render Account** - [Sign up here](https://render.com)
3. **The ZIP file**: `edudap-office-v2-DEPLOY.zip`

---

## 📤 Step 1: Upload to GitHub (5 minutes)

### 1.1 Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon (top right) → **"New repository"**
3. Fill in:
   - **Repository name**: `edudap-office-v2`
   - **Description**: `EduDAP Office v2 - CRM System`
   - **Visibility**: Choose Public or Private
   - **DO NOT** check "Add a README file"
   - **DO NOT** add .gitignore or license
4. Click **"Create repository"**

### 1.2 Upload ZIP File Contents

**Option A: Using GitHub Web Interface (Easiest)**

1. On your new repository page, click **"uploading an existing file"** link
2. Drag and drop all files from the ZIP file OR click **"choose your files"**
3. Scroll down and click **"Commit changes"**

**Option B: Using GitHub Desktop (Recommended)**

1. Download [GitHub Desktop](https://desktop.github.com)
2. Install and sign in
3. Click **"File"** → **"Add Local Repository"**
4. Click **"Create a New Repository"**
5. Choose location and name it `edudap-office-v2`
6. Extract the ZIP file to that location
7. In GitHub Desktop, you'll see all files
8. Write commit message: "Initial commit"
9. Click **"Publish repository"**
10. Choose to publish to GitHub

**Option C: Extract and Upload via Web**

1. Extract the ZIP file to a folder on your computer
2. Go to your GitHub repository
3. Click **"Add file"** → **"Upload files"**
4. Drag the entire folder contents or select all files
5. Click **"Commit changes"**

---

## 🌐 Step 2: Deploy to Render (10 minutes)

### 2.1 Create Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Sign in or create account (free)
3. Click **"New +"** button (top right)
4. Click **"Web Service"**

### 2.2 Connect GitHub Repository

1. Click **"Connect account"** if not connected
2. Authorize Render to access GitHub
3. Select your repository: `edudap-office-v2`
4. Click **"Connect"**

### 2.3 Configure Service Settings

Fill in these settings:

**Basic Settings:**
- **Name**: `edudap-office-v2` (or your preferred name)
- **Region**: Choose closest to your users (e.g., Singapore, US)
- **Branch**: `main` (or `master` if that's your default)
- **Root Directory**: Leave **EMPTY**
- **Runtime**: `Python 3`
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```
  gunicorn run:app
  ```

### 2.4 Add Environment Variables

Click **"Advanced"** → Scroll to **"Environment Variables"**

Click **"Add Environment Variable"** for each:

1. **SECRET_KEY**
   - Key: `SECRET_KEY`
   - Value: Generate one at https://www.random.org/strings/ (64 characters) OR use: `python -c "import secrets; print(secrets.token_hex(32))"` if you have Python

2. **FLASK_ENV**
   - Key: `FLASK_ENV`
   - Value: `production`

3. **UPLOAD_FOLDER**
   - Key: `UPLOAD_FOLDER`
   - Value: `uploads`

4. **MAX_UPLOAD_SIZE**
   - Key: `MAX_UPLOAD_SIZE`
   - Value: `10485760`

### 2.5 Create PostgreSQL Database

1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Fill in:
   - **Name**: `edudap-db`
   - **Database**: `edudap`
   - **User**: `edudap_user`
   - **Region**: Same as your web service
   - **Plan**: **Free** (or paid for production)
3. Click **"Create Database"**
4. Wait for database to be created (1-2 minutes)

### 2.6 Link Database to Web Service

1. Go back to your Web Service settings
2. Scroll to **"Environment Variables"**
3. Click **"Add Environment Variable"**
4. Key: `DATABASE_URL`
5. Value: Go to your PostgreSQL database dashboard
   - Click on **"Internal Database URL"**
   - Copy the entire URL (starts with `postgresql://`)
   - Paste it as the value
6. Click **"Save Changes"**

### 2.7 Deploy!

1. Scroll to bottom of Web Service settings
2. Click **"Create Web Service"**
3. Wait for deployment (2-5 minutes)
4. Watch the build logs - it will show progress

---

## ✅ Step 3: Verify Deployment (5 minutes)

### 3.1 Check Deployment Status

1. In Render Dashboard, your service will show **"Live"** when ready
2. Click on your service to see the URL
3. Your app will be at: `https://your-app-name.onrender.com`

### 3.2 Test Your Application

1. Visit your app URL
2. Click **"Register"**
3. Create first account (automatically becomes Admin)
4. Login
5. Test features:
   - ✅ Dashboard search
   - ✅ File upload
   - ✅ Attendance
   - ✅ Leave request
   - ✅ Admin features

---

## 🔑 Quick Reference: Environment Variables

When setting up Render, use these exact values:

| Variable | Value | Notes |
|----------|-------|-------|
| `SECRET_KEY` | Random 64-char string | Generate at random.org |
| `FLASK_ENV` | `production` | Exact value |
| `DATABASE_URL` | From PostgreSQL dashboard | Auto-provided |
| `UPLOAD_FOLDER` | `uploads` | Exact value |
| `MAX_UPLOAD_SIZE` | `10485760` | Exact value |

---

## 🎯 Quick Checklist

### GitHub Setup
- [ ] Created GitHub account
- [ ] Created new repository
- [ ] Uploaded all files from ZIP
- [ ] Files are visible in repository

### Render Setup
- [ ] Created Render account
- [ ] Created Web Service
- [ ] Connected GitHub repository
- [ ] Set build command: `pip install -r requirements.txt`
- [ ] Set start command: `gunicorn run:app`
- [ ] Added all 5 environment variables
- [ ] Created PostgreSQL database
- [ ] Linked DATABASE_URL
- [ ] Deployed successfully

### Verification
- [ ] App is live on Render
- [ ] Can access the URL
- [ ] Registration works
- [ ] Login works
- [ ] Dashboard loads

---

## 🐛 Troubleshooting

### Build Fails
- Check **"Logs"** tab in Render
- Verify Python version (should be 3.11+)
- Ensure all files uploaded correctly

### App Crashes
- Check **"Logs"** for error messages
- Verify all environment variables are set
- Check DATABASE_URL is correct

### Can't Connect to Database
- Use **"Internal Database URL"** from PostgreSQL dashboard
- Ensure database is in same region as web service
- Check DATABASE_URL starts with `postgresql://`

### GPS Not Working
- HTTPS is required (Render provides automatically)
- Check browser console for errors
- Ensure you're accessing via HTTPS URL

---

## 📝 Important Notes

### File Storage
⚠️ **Render's filesystem is temporary** - uploaded files will be lost on restart.

**Solutions:**
- For production: Use external storage (AWS S3, Cloudinary)
- For testing: Files will work but may disappear

### Free Tier Limitations
- Services spin down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- Database deleted after 90 days of inactivity

### HTTPS
- Render provides free HTTPS automatically
- Required for GPS features to work

---

## 🎉 Success!

Your EduDAP Office v2 CRM is now live!

**Your app URL**: `https://your-app-name.onrender.com`

**Next Steps:**
1. Register first admin user
2. Test all features
3. Share with your team
4. Consider upgrading to paid plan for production

---

## 📞 Need Help?

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Render Support**: [render.com/support](https://render.com/support)
- **GitHub Help**: [help.github.com](https://help.github.com)

---

**Deployment Method**: ZIP File Upload  
**No Command Line Required!** ✅
