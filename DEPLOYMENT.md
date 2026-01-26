# Deployment Guide - Render & GitHub

This guide will help you deploy EduDAP Office v2 CRM to Render and GitHub.

---

## 📋 Prerequisites

1. **GitHub Account** - For code repository
2. **Render Account** - Sign up at [render.com](https://render.com)
3. **Git** - Installed on your local machine

---

## 🚀 Step 1: Push to GitHub

### 1.1 Initialize Git Repository (if not already done)

```bash
cd edudap-office-v2
git init
git add .
git commit -m "Initial commit - EduDAP Office v2 CRM"
```

### 1.2 Create GitHub Repository

1. Go to [GitHub](https://github.com) and create a new repository
2. Name it: `edudap-office-v2` (or your preferred name)
3. **DO NOT** initialize with README, .gitignore, or license

### 1.3 Push to GitHub

```bash
# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/edudap-office-v2.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## 🌐 Step 2: Deploy to Render

### 2.1 Create New Web Service

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account if not already connected
4. Select your repository: `edudap-office-v2`

### 2.2 Configure Service Settings

**Basic Settings:**
- **Name**: `edudap-office-v2` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: Leave empty (or `./` if required)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn run:app`

**Advanced Settings:**
- **Environment**: `Python 3`
- **Python Version**: `3.11.7` (or latest 3.11.x)

### 2.3 Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add:

```
SECRET_KEY=your-random-secret-key-here-generate-with-python-secrets-token-hex-32
FLASK_ENV=production
UPLOAD_FOLDER=uploads
MAX_UPLOAD_SIZE=10485760
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2.4 Create PostgreSQL Database (Recommended)

1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Name: `edudap-db`
3. Plan: **Free** (or choose paid plan for production)
4. Region: Same as your web service
5. Click **"Create Database"**

### 2.5 Link Database to Web Service

1. Go to your Web Service settings
2. Click **"Environment"** tab
3. Under **"Add Environment Variable"**, add:
   - **Key**: `DATABASE_URL`
   - **Value**: Copy from your PostgreSQL database's **"Internal Database URL"**

**OR** use the database connection string from PostgreSQL service dashboard.

### 2.6 Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Build the application
   - Start the service

3. Wait for deployment to complete (usually 2-5 minutes)

---

## ✅ Step 3: Post-Deployment Setup

### 3.1 Access Your Application

- Your app will be available at: `https://your-app-name.onrender.com`
- Render provides a free HTTPS certificate automatically

### 3.2 Create First Admin User

1. Visit your deployed URL
2. Click **"Register"**
3. Register the first user (automatically becomes Admin)
4. Login and verify admin access

### 3.3 Verify Features

Test the following:
- ✅ Registration and Login
- ✅ Dashboard search
- ✅ File upload (PDF/Excel)
- ✅ Attendance punch in/out
- ✅ Leave requests
- ✅ Expense claims
- ✅ Admin features

---

## 🔧 Configuration Options

### Using render.yaml (Alternative Method)

If you prefer using `render.yaml`:

1. The file is already included in the repository
2. In Render Dashboard:
   - Click **"New +"** → **"Blueprint"**
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`
   - Review settings and deploy

### Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | Generated 64-char hex string |
| `DATABASE_URL` | Database connection | Auto-provided by Render |
| `FLASK_ENV` | Environment mode | `production` |
| `UPLOAD_FOLDER` | Upload directory | `uploads` |
| `MAX_UPLOAD_SIZE` | Max file size (bytes) | `10485760` (10MB) |
| `PORT` | Server port | Auto-set by Render |

---

## 📝 Important Notes

### File Storage

⚠️ **Important**: Render's filesystem is **ephemeral**. Uploaded files will be lost on restart.

**Solutions:**
1. **Use External Storage** (Recommended):
   - AWS S3
   - Cloudinary
   - Google Cloud Storage
   - Update `app/utils.py` and `app/employee.py` to use cloud storage

2. **Use Render Disk** (Paid):
   - Add persistent disk to your service
   - Mount to `/uploads` directory

### Database

- **Free Tier**: PostgreSQL database is deleted after 90 days of inactivity
- **Production**: Use paid plan for persistent database

### HTTPS

- Render provides free HTTPS automatically
- Required for Geolocation API (GPS features)

### Performance

- **Free Tier**: Services spin down after 15 minutes of inactivity
- **First Request**: May take 30-60 seconds to wake up
- **Production**: Use paid plan for always-on service

---

## 🔄 Updating Your Application

### Push Updates to GitHub

```bash
git add .
git commit -m "Your update message"
git push origin main
```

Render will automatically detect changes and redeploy.

### Manual Redeploy

1. Go to Render Dashboard
2. Select your service
3. Click **"Manual Deploy"** → **"Deploy latest commit"**

---

## 🐛 Troubleshooting

### Build Fails

1. Check **"Logs"** tab in Render Dashboard
2. Verify Python version matches `runtime.txt`
3. Ensure all dependencies are in `requirements.txt`

### Application Crashes

1. Check **"Logs"** for error messages
2. Verify environment variables are set correctly
3. Check database connection string

### Database Connection Issues

1. Verify `DATABASE_URL` is set correctly
2. Use **"Internal Database URL"** from PostgreSQL dashboard
3. Ensure database is in same region as web service

### GPS Not Working

- HTTPS is required for Geolocation API
- Render provides HTTPS automatically
- Check browser console for errors

---

## 📊 Monitoring

### View Logs

1. Go to Render Dashboard
2. Select your service
3. Click **"Logs"** tab
4. View real-time application logs

### Metrics

- **Free Tier**: Basic metrics available
- **Paid Tier**: Advanced metrics and alerts

---

## 🔒 Security Checklist

Before going to production:

- [x] SECRET_KEY is set and secure
- [x] Database uses strong password
- [x] HTTPS is enabled (automatic on Render)
- [x] Environment variables are set
- [x] File upload limits are configured
- [x] Admin access is properly secured

---

## 📞 Support

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Render Support**: [render.com/support](https://render.com/support)
- **GitHub Issues**: Create issue in your repository

---

## 🎉 Success!

Your EduDAP Office v2 CRM is now live on Render!

**Next Steps:**
1. Test all features
2. Set up external file storage (if needed)
3. Configure custom domain (optional)
4. Set up monitoring and alerts
5. Create backup strategy for database

---

**Deployment Date**: January 2026  
**Status**: ✅ Ready for Production
