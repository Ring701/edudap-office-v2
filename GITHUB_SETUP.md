# GitHub Setup Guide

Quick guide to push your code to GitHub.

## Step 1: Initialize Git (if not done)

```bash
cd edudap-office-v2
git init
```

## Step 2: Add All Files

```bash
git add .
```

## Step 3: Create Initial Commit

```bash
git commit -m "Initial commit - EduDAP Office v2 CRM"
```

## Step 4: Create GitHub Repository

1. Go to [GitHub.com](https://github.com)
2. Click **"New"** (or **"+"** → **"New repository"**)
3. Repository name: `edudap-office-v2`
4. Description: `EduDAP Office v2 - CRM System with Smart Search & Price Intelligence`
5. Choose **Public** or **Private**
6. **DO NOT** check "Initialize with README" (we already have one)
7. Click **"Create repository"**

## Step 5: Connect and Push

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/edudap-office-v2.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Step 6: Verify

1. Go to your GitHub repository
2. Verify all files are uploaded
3. Check that README.md displays correctly

## Future Updates

To push updates:

```bash
git add .
git commit -m "Your update message"
git push origin main
```

## Branch Protection (Optional)

For production, consider:
1. Go to repository **Settings** → **Branches**
2. Add branch protection rule for `main`
3. Require pull request reviews
4. Require status checks

---

**Done!** Your code is now on GitHub and ready for Render deployment.
