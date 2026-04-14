# MLOps Command Reference

## 🚀 Quick Command Guide

### Setup & Configuration

```bash
# Set credentials (required for all commands)
export GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json

# Verify environment
echo "Project: mlops-493014"
echo "Region: us-central1"
echo "Bucket: gs://mlops-493014-bucket"
```

---

## 📚 Training Commands

### Run Complete Pipeline (All Frameworks)
```bash
python orchestrate.py
# Submits Scikit-learn, TensorFlow, and PyTorch jobs
# Shows test results and monitoring summary
```

### Individual Framework Training

**Scikit-learn**
```bash
python src/vertex_train.py
# Submits Random Forest classifier job
# Status: ✅ Production ready
```

**TensorFlow/Keras**
```bash
python src/vertex_train_tensorflow.py
# Submits deep learning job
# Model: Dense(128)→Dropout→Dense(64)→Dropout→Dense(32)→Dense(3)
```

**PyTorch**
```bash
python src/vertex_train_pytorch.py
# Submits neural network job
# Architecture: 4→128→64→32→3 neurons
```

---

## 🔍 Monitoring Commands

### List Recent Jobs
```bash
# Show 10 most recent jobs
python scripts/monitor_training.py --list

# Show 20 most recent jobs
python scripts/monitor_training.py --list --limit 20
```

### Get Job Details
```bash
# Replace <JOB_ID> with actual Vertex AI job ID
python scripts/monitor_training.py --job-id <JOB_ID>
# Shows: name, status, created time, started time, ended time, machine type
```

### Retrieve Job Logs
```bash
# Get last 50 lines of logs
python scripts/monitor_training.py --job-id <JOB_ID> --logs

# Get last 100 lines of logs
python scripts/monitor_training.py --job-id <JOB_ID> --logs --limit 100
```

---

## 📤 Model Deployment Commands

### Upload Model to Registry
```bash
# Upload Scikit-learn model
python scripts/deploy_model.py upload \
  --model-path gs://mlops-493014-bucket/models/iris_scikit \
  --framework scikit-learn \
  --version v1

# Upload TensorFlow model
python scripts/deploy_model.py upload \
  --model-path gs://mlops-493014-bucket/models/iris_tensorflow \
  --framework tensorflow \
  --version v1

# Upload PyTorch model
python scripts/deploy_model.py upload \
  --model-path gs://mlops-493014-bucket/models/iris_pytorch \
  --framework pytorch \
  --version v1
```

### Create Prediction Endpoint
```bash
python scripts/deploy_model.py endpoint
# Creates new Vertex AI endpoint for serving
# Default name: iris-prediction-endpoint
```

### List Available Endpoints
```bash
python scripts/deploy_model.py list
# Shows all prediction endpoints with IDs and deployment info
```

### Deploy Model to Endpoint
```bash
python scripts/deploy_model.py deploy \
  --model-id <MODEL_ID> \
  --endpoint-id <ENDPOINT_ID>
# Deploys trained model to prediction endpoint
```

---

## 🔄 ML Pipeline Commands

### Compile Pipeline YAML
```bash
python scripts/vertex_pipeline.py --action compile
# Generates pipeline YAML definition
# Output: gs://mlops-493014-bucket/pipelines/iris-pipeline.yaml
```

### Submit Pipeline to Vertex AI
```bash
python scripts/vertex_pipeline.py --action submit
# Compiles and submits pipeline for orchestration
# Pipeline steps: Prepare → Train → Evaluate → Deploy
```

---

## 🧪 Testing

### Test All Frameworks
```bash
python orchestrate.py
# Expected output:
#   SKLEARN: ✅ PASS
#   TENSORFLOW: ✅ PASS
#   PYTORCH: ✅ PASS
#   Result: 3/3 tests passed
```

### Verify Credentials
```bash
python -c "from google.auth import default; creds, proj = default(); print(f'✅ Credentials OK - Project: {proj}')"
```

### Check Bucket Access
```bash
gsutil ls gs://mlops-493014-bucket/
```

---

## 📊 Viewing Results

### Vertex AI Console
```
Training Jobs: https://console.cloud.google.com/vertex-ai/training/custom-jobs?project=mlops-493014
Models: https://console.cloud.google.com/vertex-ai/model-registry?project=mlops-493014
Endpoints: https://console.cloud.google.com/vertex-ai/endpoints?project=mlops-493014
```

### GCS Storage Browse
```bash
# List models
gsutil ls -r gs://mlops-493014-bucket/models/

# List datasets
gsutil ls -r gs://mlops-493014-bucket/datasets/

# List training outputs
gsutil ls -r gs://mlops-493014-bucket/training_logs/
```

### Download Model Artifacts
```bash
# Create local model directory
mkdir -p local_models

# Download scikit-learn model
gsutil -m cp -r gs://mlops-493014-bucket/models/iris_scikit/ local_models/

# Download TensorFlow model
gsutil -m cp -r gs://mlops-493014-bucket/models/iris_tensorflow/ local_models/

# Download PyTorch model
gsutil -m cp -r gs://mlops-493014-bucket/models/iris_pytorch/ local_models/
```

---

## 🛠️ Troubleshooting Commands

### Verify Credentials File
```bash
# Check if credentials exist
ls -la gcp-key.json

# Show credentials summary (be careful!)
cat gcp-key.json | grep -E '"project_id"|"type"'
```

### Check GCP Permissions
```bash
# List IAM roles for service account
gcloud projects get-iam-policy mlops-493014 \
  --flatten="bindings[].members" \
  --filter="bindings.members:jenkins-vertex-sa*"
```

### List All Training Jobs (via gcloud)
```bash
gcloud ai custom-jobs list \
  --project=mlops-493014 \
  --region=us-central1
```

### Get Job Details (via gcloud)
```bash
gcloud ai custom-jobs describe <JOB_ID> \
  --project=mlops-493014 \
  --region=us-central1
```

### Stream Job Output
```bash
gcloud ai custom-jobs stream-logs <JOB_ID> \
  --project=mlops-493014 \
  --region=us-central1
```

---

## 📝 Environment Setup

### One-time Setup
```bash
# Navigate to project directory
cd /home/azureuser/cloudfiles/code/Users/tarandevnani5

# Export credentials
export GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json

# Verify Python environment
/anaconda/envs/azureml_py38/bin/python --version  # Should be 3.10+

# (Optional) Create shell alias for convenience
alias vertex-ml="export GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json && /anaconda/envs/azureml_py38/bin/python"
```

### Session Setup (Run Each Time)
```bash
# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json

# Verify setup
python -c "import google.cloud.aiplatform; print('✅ Ready to train')"
```

---

## 🔐 Security Best Practices

### Protect Credentials
```bash
# Make credentials readable by owner only
chmod 600 gcp-key.json

# Never commit credentials
echo "gcp-key.json" >> .gitignore

# Verify git ignores credentials
git status | grep -i gcp-key
```

### Rotate Credentials (if compromised)
```bash
# List service account keys
gcloud iam service-accounts keys list \
  --iam-account=jenkins-vertex-sa@mlops-493014.iam.gserviceaccount.com

# Create new key
gcloud iam service-accounts keys create new-gcp-key.json \
  --iam-account=jenkins-vertex-sa@mlops-493014.iam.gserviceaccount.com

# Delete old key (replace with KEY_ID from list)
gcloud iam service-accounts keys delete <OLD_KEY_ID> \
  --iam-account=jenkins-vertex-sa@mlops-493014.iam.gserviceaccount.com
```

---

## 💡 Common Workflows

### Simple: Train All Frameworks
```bash
export GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json
python orchestrate.py
```

### Monitor: Check Job Status
```bash
export GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json
python scripts/monitor_training.py --list
```

### Deploy: Upload Best Model
```bash
export GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json

# Register model
python scripts/deploy_model.py upload \
  --model-path gs://mlops-493014-bucket/models/iris_tensorflow \
  --framework tensorflow

# Create endpoint
python scripts/deploy_model.py endpoint

# List endpoints
python scripts/deploy_model.py list
```

### Automate: Run Full ML Pipeline
```bash
export GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json
python scripts/vertex_pipeline.py --action submit
```

---

## 📖 Documentation Files

| File | Purpose |
|------|---------|
| `README_MLOPS_PIPELINE.md` | Complete architecture & usage guide |
| `DELIVERY_SUMMARY.md` | What was delivered & test results |
| `COMMAND_REFERENCE.md` | This file - quick command lookup |
| `requirements.txt` | Python dependencies |

---

## 🎯 Cheat Sheet

```bash
# Quick setup
export GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json

# Submit all jobs
python orchestrate.py

# Monitor jobs
python scripts/monitor_training.py --list

# Deploy best model
python scripts/deploy_model.py upload --model-path <path> --framework tensorflow

# Create endpoint
python scripts/deploy_model.py endpoint

# Run full pipeline
python scripts/vertex_pipeline.py --action submit
```

---

**Last Updated:** April 11, 2026  
**Status:** ✅ Complete & Tested  
**All Commands:** Verified working
