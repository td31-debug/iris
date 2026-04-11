from google.cloud import aiplatform
import os

PROJECT_ID = "mlops-493014"
REGION = "us-central1"
BUCKET = f"gs://{PROJECT_ID}-bucket"

aiplatform.init(project=PROJECT_ID, location=REGION)

job = aiplatform.CustomTrainingJob(
    display_name="iris-training-jenkins",
    script_path="src/train.py",
    container_uri="us-docker.pkg.dev/vertex-ai/training/scikit-learn-cpu.1-0:latest",
    requirements=["scikit-learn", "mlflow", "joblib"],
)

model = job.run(
    replica_count=1,
    machine_type="n1-standard-4",
    sync=True
)

print("✅ Vertex AI training job complete")
