"""
PyTorch Training Script for Vertex AI
Trains a neural network classifier on Iris dataset
"""

from google.cloud import aiplatform
from google.auth import default as google_auth_default
import os

PROJECT_ID = "mlops-493014"
REGION = "us-central1"
BUCKET = f"gs://{PROJECT_ID}-bucket"

# Load credentials properly
try:
    credentials, project = google_auth_default()
    print(f"✅ Credentials loaded successfully")
    print(f"Project: {project}")
except Exception as e:
    print(f"❌ Error loading credentials: {e}")
    raise

# Initialize Vertex AI
aiplatform.init(
    project=PROJECT_ID,
    location=REGION,
    staging_bucket=BUCKET,
    credentials=credentials
)
print(f"✅ Vertex AI initialized — project: {PROJECT_ID}")

# Define and submit a real Vertex AI CustomJob from the local PyTorch script
job = aiplatform.CustomJob.from_local_script(
    display_name="iris-training-pytorch",
    script_path="src/train_pytorch.py",
    container_uri="us-docker.pkg.dev/vertex-ai/training/pytorch-xla.2-4.py310:latest",
    requirements=[
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "scikit-learn>=1.3.0",
        "pandas>=1.5.0",
        "numpy>=1.24.0",
        "mlflow>=2.0.0"
    ],
    replica_count=1,
    machine_type="n1-standard-4",
    staging_bucket=BUCKET,
    project=PROJECT_ID,
    location=REGION,
    credentials=credentials,
)

print("📤 Submitting PyTorch training job to Vertex AI...")
job.submit()

print("✅ PyTorch training job submitted successfully!")
print(f"🆔 Resource name: {job.resource_name}")
print(f"📊 Monitor at: https://console.cloud.google.com/vertex-ai/training/custom-jobs?project={PROJECT_ID}")
