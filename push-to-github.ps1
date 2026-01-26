# PowerShell Script to Push Project to GitHub
# Run this script AFTER installing Git

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GitHub Push Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Git is installed
$gitCheck = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCheck) {
    Write-Host "ERROR: Git is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Git first:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "2. Install with default settings" -ForegroundColor Yellow
    Write-Host "3. Restart PowerShell" -ForegroundColor Yellow
    Write-Host "4. Run this script again" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit
}

Write-Host "✓ Git is installed" -ForegroundColor Green
Write-Host ""

# Navigate to project directory
$projectPath = "C:\Users\lenovo\edudap-office-v2"
Set-Location $projectPath
Write-Host "Current directory: $projectPath" -ForegroundColor Cyan
Write-Host ""

# Initialize git if not already done
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✓ Git repository initialized" -ForegroundColor Green
    Write-Host ""
}

# Check if remote exists
$remoteCheck = git remote -v 2>&1
if ($LASTEXITCODE -ne 0 -or $remoteCheck -eq "") {
    Write-Host "⚠ No remote repository configured!" -ForegroundColor Yellow
    Write-Host ""
    $githubUser = Read-Host "Enter your GitHub username"
    $repoName = Read-Host "Enter repository name (default: edudap-office-v2)"
    if ([string]::IsNullOrWhiteSpace($repoName)) {
        $repoName = "edudap-office-v2"
    }
    
    Write-Host ""
    Write-Host "Adding remote: https://github.com/$githubUser/$repoName.git" -ForegroundColor Cyan
    git remote add origin "https://github.com/$githubUser/$repoName.git"
    Write-Host "✓ Remote added" -ForegroundColor Green
    Write-Host ""
}

# Add all files
Write-Host "Adding all files..." -ForegroundColor Yellow
git add .
Write-Host "✓ All files added" -ForegroundColor Green
Write-Host ""

# Check if there are changes to commit
$status = git status --porcelain
if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Host "No changes to commit. Everything is up to date!" -ForegroundColor Green
    Write-Host ""
} else {
    # Commit
    Write-Host "Committing changes..." -ForegroundColor Yellow
    git commit -m "Full project update including all files"
    Write-Host "✓ Changes committed" -ForegroundColor Green
    Write-Host ""
}

# Set branch to main
Write-Host "Setting branch to main..." -ForegroundColor Yellow
git branch -M main
Write-Host "✓ Branch set to main" -ForegroundColor Green
Write-Host ""

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "You may be prompted for GitHub credentials" -ForegroundColor Cyan
Write-Host ""

try {
    git push -u origin main
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✓ Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "ERROR: Failed to push to GitHub" -ForegroundColor Red
    Write-Host "Possible reasons:" -ForegroundColor Yellow
    Write-Host "1. Repository doesn't exist on GitHub - create it first" -ForegroundColor Yellow
    Write-Host "2. Authentication failed - check your credentials" -ForegroundColor Yellow
    Write-Host "3. Network issues" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To create repository:" -ForegroundColor Cyan
    Write-Host "1. Go to https://github.com/new" -ForegroundColor Cyan
    Write-Host "2. Create repository with same name" -ForegroundColor Cyan
    Write-Host "3. DO NOT initialize with README" -ForegroundColor Cyan
    Write-Host "4. Run this script again" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
