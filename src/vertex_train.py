from google.cloud import aiplatform
from google.auth import default as google_auth_default
import os

PROJECT_ID = "mlops-493014"
REGION = "us-central1"
BUCKET = f"gs://{PROJECT_ID}-bucket"

# Load credentials properly
try:
    credentials, project = google_auth_default()
    print("Credentials loaded successfully")
    print(f"Project: {project}")
except Exception as e:
    print(f"Error loading credentials: {e}")
    raise

# Initialize Vertex AI
aiplatform.init(
    project=PROJECT_ID,
    location=REGION,
    staging_bucket=BUCKET,
    credentials=credentials
)
print(f"Vertex AI initialized - project: {PROJECT_ID}")

# Define and submit a real Vertex AI CustomJob from the local training script
job = aiplatform.CustomJob.from_local_script(
    display_name="iris-training-jenkins",
    script_path="src/train.py",
    container_uri="us-docker.pkg.dev/vertex-ai/training/sklearn-cpu.1-6:latest",
    requirements=["scikit-learn==1.3.2", "mlflow", "joblib"],
    replica_count=1,
    machine_type="n1-standard-4",
    staging_bucket=BUCKET,
    project=PROJECT_ID,
    location=REGION,
    credentials=credentials,
)

print("Submitting training job to Vertex AI...")
job.submit()

print("Vertex AI training job submitted successfully!")
print(f"Resource name: {job.resource_name}")