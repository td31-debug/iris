# GitHub Actions Setup Guide

## 🚀 Overview
This guide sets up GitHub Actions to automatically run Azure ML training jobs.

---

## Step 1: Create GitHub Secrets

Go to your GitHub repository → **Settings → Secrets and variables → Actions**

Add these 4 secrets:

### 1️⃣ AZURE_CREDENTIALS
This is your Azure service principal credentials.

**Get it:**
```bash
az account show
```

Then create a service principal:
```bash
az ad sp create-for-rbac --name "github-actions" --role Contributor --scopes /subscriptions/{SUBSCRIPTION_ID}
```

Copy the entire JSON output and paste it as `AZURE_CREDENTIALS`:
```json
{
  "clientId": "...",
  "clientSecret": "...",
  "subscriptionId": "...",
  "tenantId": "..."
}
```

### 2️⃣ AZURE_SUBSCRIPTION_ID
```
e15f29d3-c062-4c3d-9461-1a6f661d278f
```

### 3️⃣ AZURE_RESOURCE_GROUP
```
ml-project-rg
```

### 4️⃣ AZURE_WORKSPACE_NAME
```
MLOPS
```

---

## Step 2: Push Code to GitHub

```bash
git init
git add .
git commit -m "Add Azure ML training pipeline"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

---

## Step 3: Monitor Workflows

1. Go to your repo → **Actions** tab
2. See running workflows
3. Click workflow to see logs

---

## Workflow Files Included

### 1. `azure-ml-train.yml` 🎯 (Main)
- Runs on: `push` to main, schedule (weekly), or manual trigger
- Steps:
  - Authenticate with Azure
  - Install dependencies
  - Run local tests
  - Train model locally
  - Submit job to Azure ML (`cpi-cluster`)

### 2. `test-locally.yml` ✅
- Runs unit tests
- Validates model training
- Generates coverage reports

### 3. `deploy.yml` 🚀
- Registers model in Azure ML registry
- Triggered on: main branch push + tags

---

## Triggering Workflows Manually

**Option 1: Push to main**
```bash
git push origin main
```

**Option 2: Manual Trigger (GitHub UI)**
Go to **Actions → Azure ML Training Pipeline → Run workflow**

**Option 3: Create a Git Tag**
```bash
git tag v1.0.0
git push origin v1.0.0
```

---

## 📊 Scheduled Runs

The workflow runs automatically every **Sunday at 2 AM UTC** (weekly retraining).

To change schedule, edit `azure-ml-train.yml`:
```yaml
schedule:
  - cron: '0 2 * * 0'  # Change this
```

[Cron cheatsheet](https://crontab.guru/)

---

## ❌ Troubleshooting

### "Azure Login Failed"
- Check `AZURE_CREDENTIALS` secret is correct
- Verify service principal has `Contributor` role

### "Unknown compute target 'cpi-cluster'"
- Verify cluster exists in Azure ML Studio
- Check spelling matches exactly

### "Runner out of job timeout"
- Increase timeout in job.py or split jobs

---

## Local Testing (Before Pushing)

Test locally first:
```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# Run training
python src/train.py

# Test job submission
python src/job.py
```

---

## Next Steps

1. ✅ Add secrets to GitHub
2. ✅ Push code to GitHub repo
3. ✅ Monitor Actions tab
4. ✅ Check Azure ML Studio for submitted jobs

**You're all set! 🎉**
