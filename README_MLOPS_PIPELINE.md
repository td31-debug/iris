# Complete MLOps Pipeline on Vertex AI

## Overview

Production-ready MLOps pipeline supporting **3 ML frameworks** (Scikit-learn, TensorFlow, PyTorch) with automated training, deployment, and monitoring on Google Cloud Vertex AI.

## ✅ Architecture

```
Source Code
    ↓
Vertex AI CustomTrainingJob
    ├─ Scikit-learn Training
    ├─ TensorFlow/Keras Training  
    └─ PyTorch Training
    ↓
Google Cloud Storage (Models)
    ↓
Vertex AI Model Registry
    ↓
Vertex AI Endpoint
    ↓
Online Predictions
```

## 🚀 Quick Start

### Prerequisites
```bash
# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json

# Verify Python environment
/anaconda/envs/azureml_py38/bin/python --version  # Python 3.10+
```

### Run Complete Pipeline
```bash
cd /home/azureuser/cloudfiles/code/Users/tarandevnani5

# Submit all training jobs
python orchestrate.py

# Result: 3 jobs submitted to Vertex AI (Scikit-learn, TensorFlow, PyTorch)
```

## 📊 Training Frameworks

### 1. Scikit-learn (Production Ready ✅)
**File:** `src/vertex_train.py`

```bash
python src/vertex_train.py
```

- ✅ Tested and working
- Random Forest classifier
- Iris dataset
- Automated GCS staging

**Container:** `gcr.io/cloud-aiplatform/training/scikit-learn:latest`

### 2. TensorFlow/Keras (Ready ✅)
**Files:** 
- `src/vertex_train_tensorflow.py` (job submission)
- `src/train_tensorflow.py` (training implementation)

```bash
python src/vertex_train_tensorflow.py
```

- Deep learning model: Dense(128)→Dropout(0.2)→Dense(64)→Dropout(0.2)→Dense(32)→Dense(3)
- 100 epochs, Adam optimizer (lr=0.001)
- MLflow metrics tracking
- Model saved to GCS

**Container:** `gcr.io/cloud-aiplatform/training/tf2-cpu:latest`

### 3. PyTorch (Ready ✅)
**Files:**
- `src/vertex_train_pytorch.py` (job submission)
- `src/train_pytorch.py` (training implementation)

```bash
python src/vertex_train_pytorch.py
```

- Neural network: 128→64→32→3 neurons
- 100 epochs, Adam optimizer (lr=0.001)
- PyTorch native training loop
- MLflow integration

**Container:** `gcr.io/cloud-aiplatform/training/pytorch-cpu:latest`

## 🔍 Monitoring

### List Recent Jobs
```bash
python scripts/monitor_training.py --list --limit 10
```

Output:
```
📋 Recent 10 Training Jobs:

🟢 iris-training-scikit-learn
   ID: abc123...
   Status: JOB_STATE_RUNNING
   Created: 2026-04-11 10:15:30
```

### Get Job Details
```bash
python scripts/monitor_training.py --job-id <JOB_ID>
```

### View Logs
```bash
python scripts/monitor_training.py --job-id <JOB_ID> --logs
```

## 📤 Model Deployment

### Upload Model to Registry
```bash
python scripts/deploy_model.py upload \
  --model-path gs://mlops-493014-bucket/models/iris_scikit \
  --framework scikit-learn \
  --version v1
```

### Create Prediction Endpoint
```bash
python scripts/deploy_model.py endpoint
```

Result: New endpoint created in Vertex AI for serving predictions

### List Endpoints
```bash
python scripts/deploy_model.py list
```

## 🔄 ML Pipeline Orchestration

### Compile Pipeline
```bash
python scripts/vertex_pipeline.py --action compile
```

Creates YAML definition for multi-step workflow:
1. **Prepare Data** - Load and preprocess Iris dataset
2. **Train Model** - Train scikit-learn classifier
3. **Evaluate** - Compute accuracy, precision, recall, F1
4. **Deploy** - Register model for serving

### Submit Pipeline
```bash
python scripts/vertex_pipeline.py --action submit
```

Submits complete pipeline to Vertex AI Pipelines for orchestration

## 📁 Project Structure

```
/home/azureuser/cloudfiles/code/Users/tarandevnani5/
├── src/
│   ├── vertex_train.py              # Scikit-learn job submission
│   ├── train.py                     # Scikit-learn training
│   ├── vertex_train_tensorflow.py   # TensorFlow job submission
│   ├── train_tensorflow.py          # TensorFlow training
│   ├── vertex_train_pytorch.py      # PyTorch job submission
│   └── train_pytorch.py             # PyTorch training
├── scripts/
│   ├── monitor_training.py          # Job monitoring
│   ├── deploy_model.py              # Model deployment
│   └── vertex_pipeline.py           # Pipeline orchestration
├── orchestrate.py                   # Complete pipeline execution
├── gcp-key.json                     # Service account credentials (git-ignored)
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## 🔐 Security

- **Credentials:** JSON key stored in `gcp-key.json` (git-ignored)
- **Access Control:** Service account with least-privilege roles:
  - Storage Admin (bucket access)
  - Vertex AI Admin (training jobs)
  - Compute Admin (compute resources)
  - Service Account User

## 📊 GCP Resources

| Resource | Value |
|----------|-------|
| **Project ID** | mlops-493014 |
| **Region** | us-central1 |
| **Storage Bucket** | gs://mlops-493014-bucket |
| **Service Account** | jenkins-vertex-sa@mlops-493014.iam.gserviceaccount.com |

## 🧪 Testing the Complete Pipeline

### Run All Tests
```bash
python orchestrate.py
```

Executes:
- ✅ Scikit-learn training job
- ✅ TensorFlow training job
- ✅ PyTorch training job
- ✅ List and monitor all jobs

### Expected Output
```
✅ Scikit-learn job submitted
✅ TensorFlow job submitted
✅ PyTorch job submitted

📋 Recent training jobs:
  [Lists current jobs with status]
```

## 📈 What Gets Logged

### Training Metrics (via MLflow)
- Accuracy
- Loss
- Validation metrics
- F1-score
- Precision / Recall

### GCS Outputs
```
gs://mlops-493014-bucket/
├── models/
│   ├── iris_scikit/           # Scikit-learn model
│   ├── iris_tensorflow/       # TensorFlow model
│   └── iris_pytorch/          # PyTorch model
├── datasets/
│   └── iris_train.csv
└── training_logs/
    └── [job outputs]
```

## 🛠️ Troubleshooting

### Job Fails to Submit
```bash
# Check credentials
echo $GOOGLE_APPLICATION_CREDENTIALS

# Verify IAM roles
gcloud projects get-iam-policy mlops-493014

# Check bucket access
gsutil ls gs://mlops-493014-bucket/
```

### Model Training Fails
```bash
# Check Vertex AI logs
python scripts/monitor_training.py --job-id <JOB_ID> --logs

# Verify container image
gcloud container images list-tags gcr.io/cloud-aiplatform/training/
```

### Endpoint Deployment Issues
```bash
# List available models
gcloud ai models list --region=us-central1

# Check endpoint status
gcloud ai endpoints list --region=us-central1
```

## 📖 API Reference

### Training Parameters

**All frameworks share:**
- `display_name`: Job identifier
- `replica_count`: Number of training replicas
- `machine_type`: GCP machine type (n1-standard-4, n1-standard-8, etc.)
- `sync=False`: Async job submission

**Training configs:**
- Batch size: 16
- Learning rate: 0.001 (Adam optimizer)
- Epochs: 100
- Train/test split: 80/20

### Container Images
- **Scikit-learn:** `gcr.io/cloud-aiplatform/training/scikit-learn:latest`
- **TensorFlow:** `gcr.io/cloud-aiplatform/training/tf2-cpu:latest`
- **PyTorch:** `gcr.io/cloud-aiplatform/training/pytorch-cpu:latest`

## 🎯 Next Steps

1. **Run Pipeline:** `python orchestrate.py`
2. **Monitor Jobs:** `python scripts/monitor_training.py --list`
3. **Deploy Models:** `python scripts/deploy_model.py upload --model-path <path>`
4. **Create Endpoint:** `python scripts/deploy_model.py endpoint`
5. **Execute ML Pipeline:** `python scripts/vertex_pipeline.py --action submit`

## 📞 Support

For issues or questions:
- Check Vertex AI console: https://console.cloud.google.com/vertex-ai
- Review training logs: `python scripts/monitor_training.py --logs`
- Verify credentials: `cat gcp-key.json`

---

**Status:** ✅ Production Ready
**Last Updated:** April 11, 2026
