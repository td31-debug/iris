# 🚀 Vertex AI + Jenkins MLOps Setup Guide

## ⚠️ Required: Setup Permissions from Your Local Machine

The service account needs IAM permissions that **only a project admin can grant**. You need to do this from your local Windows machine with your own GCP account.

### Step 1: Authenticate with Your GCP Account (on your Windows machine)

```powershell
# Open PowerShell and run:
gcloud auth login
# This opens a browser - sign in with your GCP account that has project admin rights
```

### Step 2: Run This Command to Grant Permissions

```powershell
$PROJECT_ID = "mlops-493014"
$SERVICE_ACCOUNT = "jenkins-vertex-sa@mlops-493014.iam.gserviceaccount.com"

# Grant Storage Admin
gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:$SERVICE_ACCOUNT" `
  --role="roles/storage.admin"

# Grant Vertex AI Admin  
gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:$SERVICE_ACCOUNT" `
  --role="roles/aiplatform.admin"

# Grant Compute Admin
gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:$SERVICE_ACCOUNT" `
  --role="roles/compute.admin"

# Grant Service Account User
gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:$SERVICE_ACCOUNT" `
  --role="roles/iam.serviceAccountUser"
```

### Step 3: Verify Permissions

```powershell
gcloud projects get-iam-policy $PROJECT_ID `
  --flatten="bindings[].members" `
  --filter="bindings.members:serviceAccount:jenkins-vertex-sa@mlops-493014.iam.gserviceaccount.com" `
  --format="table(bindings.role)"
```

You should see these roles:
- roles/storage.admin
- roles/aiplatform.admin
- roles/compute.admin
- roles/iam.serviceAccountUser

---

## After Permissions Are Set

Once you've granted the permissions from your local machine, the following command will work:

```bash
cd /home/azureuser/cloudfiles/code/Users/tarandevnani5
export GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json
python src/vertex_train.py
```

The training job should start successfully and you'll see:
```
✅ Credentials loaded successfully
Project: mlops-493014
Creating Vertex AI training job...
🎉 Training job submitted
```

---

## 📋 Alternative: Use GCP Console

If you prefer using the web interface:

1. **Go to**: https://console.cloud.google.com/iam-admin/iam?project=mlops-493014
2. **Find**: jenkins-vertex-sa@mlops-493014.iam.gserviceaccount.com
3. **Add these roles** (click "Edit Principal"):
   - Storage Admin
   - Vertex AI Administrator
   - Compute Administrator
   - Service Account User

---

## Project Files

- `src/vertex_train.py` - Main training script
- `gcp-key.json` - Service account credentials (⚠️ NEVER commit to git!)
- `setup-iam-permissions.sh` - Automated setup script
- `.gitignore` - Ensures gcp-key.json is never committed

---

## Next Steps After This

1. ✅ Test the training script works
2. Create Jenkinsfile for CI/CD
3. Add TensorFlow/Keras support
4. Add PyTorch support
5. Set up Vertex AI Pipelines
