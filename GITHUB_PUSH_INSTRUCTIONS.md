# GitHub Push Instructions

## ⚠️ Git Not Found

Git is not installed or not in your system PATH. Here are your options:

---

## Option 1: Install Git (Recommended)

### Download and Install Git:
1. Go to: https://git-scm.com/download/win
2. Download Git for Windows
3. Install with default settings
4. Restart your terminal/PowerShell
5. Then run the commands below

### After Installing Git, Run These Commands:

```bash
# Navigate to project folder
cd C:\Users\lenovo\edudap-office-v2

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Full project update including all files"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/edudap-office-v2.git

# Push to main branch
git branch -M main
git push -u origin main
```

---

## Option 2: Use GitHub Desktop (Easier - No Command Line)

### Steps:
1. Download GitHub Desktop: https://desktop.github.com
2. Install and sign in with your GitHub account
3. Click **"File"** → **"Add Local Repository"**
4. Browse to: `C:\Users\lenovo\edudap-office-v2`
5. If it says "This directory does not appear to be a Git repository":
   - Click **"Create a repository"**
   - Name: `edudap-office-v2`
   - Click **"Create Repository"**
6. You'll see all your files
7. Write commit message: "Full project update including all files"
8. Click **"Commit to main"**
9. Click **"Publish repository"** (if first time) or **"Push origin"** (if already published)

---

## Option 3: Upload via GitHub Web Interface

### Steps:
1. Go to GitHub.com and create a new repository
2. Name it: `edudap-office-v2`
3. **DO NOT** initialize with README
4. On the repository page, click **"uploading an existing file"**
5. Drag and drop ALL files from `C:\Users\lenovo\edudap-office-v2`
6. Scroll down and click **"Commit changes"**

---

## Option 4: Use the ZIP File Method

Since you already have the ZIP file:
1. Extract the ZIP file
2. Upload extracted files to GitHub (Option 3 above)

---

## 🔍 Check if Git is Installed

Run this command to check:
```powershell
where.exe git
```

If it shows a path, Git is installed but may need to be added to PATH.

---

## 📝 If You Need to Set Up Remote

If you already have a GitHub repository:

```bash
# Check if remote exists
git remote -v

# If no remote, add it:
git remote add origin https://github.com/YOUR_USERNAME/edudap-office-v2.git

# If remote exists but wrong URL, update it:
git remote set-url origin https://github.com/YOUR_USERNAME/edudap-office-v2.git
```

---

## ✅ Recommended Approach

**For easiest setup: Use GitHub Desktop (Option 2)**

It's the simplest way and doesn't require command line knowledge.

---

**Need Help?**
- Git Installation: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git
- GitHub Desktop: https://desktop.github.com
- GitHub Help: https://help.github.com
