# Quick Deploy Checklist

Use this checklist for fast deployment to Render.

## ✅ Pre-Deployment Checklist

- [ ] All code is committed to Git
- [ ] Code is pushed to GitHub
- [ ] `.env` file is NOT committed (it's in .gitignore)
- [ ] `SECRET_KEY` is ready (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] All dependencies are in `requirements.txt`
- [ ] `Procfile` exists and is correct
- [ ] `runtime.txt` specifies Python version

## 🚀 Render Deployment Steps

### 1. Create Web Service
- [ ] Go to [Render Dashboard](https://dashboard.render.com)
- [ ] Click **"New +"** → **"Web Service"**
- [ ] Connect GitHub account
- [ ] Select repository: `edudap-office-v2`

### 2. Configure Service
- [ ] **Name**: `edudap-office-v2`
- [ ] **Region**: Choose closest region
- [ ] **Branch**: `main`
- [ ] **Build Command**: `pip install -r requirements.txt`
- [ ] **Start Command**: `gunicorn run:app`

### 3. Add Environment Variables
- [ ] `SECRET_KEY` = (your generated key)
- [ ] `FLASK_ENV` = `production`
- [ ] `UPLOAD_FOLDER` = `uploads`
- [ ] `MAX_UPLOAD_SIZE` = `10485760`

### 4. Create Database
- [ ] Click **"New +"** → **"PostgreSQL"**
- [ ] Name: `edudap-db`
- [ ] Plan: Free (or paid for production)
- [ ] Copy **Internal Database URL**

### 5. Link Database
- [ ] Go back to Web Service
- [ ] Add environment variable: `DATABASE_URL` = (database URL from step 4)

### 6. Deploy
- [ ] Click **"Create Web Service"**
- [ ] Wait for build to complete (2-5 minutes)
- [ ] Check logs for any errors

### 7. Post-Deployment
- [ ] Visit your app URL: `https://your-app.onrender.com`
- [ ] Register first user (becomes Admin)
- [ ] Test login
- [ ] Test key features

## 🔍 Verification Tests

After deployment, test:

- [ ] Registration works
- [ ] Login works
- [ ] Dashboard loads
- [ ] Search functionality
- [ ] File upload (PDF/Excel)
- [ ] Attendance punch in/out
- [ ] Leave request
- [ ] Expense claim
- [ ] Admin features accessible

## ⚠️ Important Notes

1. **File Storage**: Render's filesystem is ephemeral. Files will be lost on restart.
   - Consider using external storage (S3, Cloudinary) for production

2. **Database**: Free tier database is deleted after 90 days of inactivity

3. **Service**: Free tier spins down after 15 minutes of inactivity
   - First request after spin-down takes 30-60 seconds

4. **HTTPS**: Automatically provided by Render (required for GPS features)

## 🐛 Troubleshooting

**Build fails?**
- Check logs in Render Dashboard
- Verify Python version in `runtime.txt`
- Ensure all dependencies in `requirements.txt`

**App crashes?**
- Check logs for error messages
- Verify all environment variables are set
- Check database connection

**Database issues?**
- Use "Internal Database URL" from PostgreSQL dashboard
- Ensure database is in same region as web service

## 📞 Need Help?

- See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guide
- Check Render documentation: [render.com/docs](https://render.com/docs)
- Review application logs in Render Dashboard

---

**Status**: Ready to deploy! 🚀
