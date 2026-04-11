from azure.ai.ml import MLClient, command
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import Environment
import json

# Load config
with open("configs/config.json") as f:
    config = json.load(f)

ml_client = MLClient(
    DefaultAzureCredential(),
    config["subscription_id"],
    config["resource_group"],
    config["workspace_name"]
)

# Define job with environment variables for MLflow tracking
job = command(
    code=".",  # project folder
    command="python src/train.py",
    environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:1",
    compute="cpi-cluster",  # change if needed
    display_name="iris-training-job",
    environment_variables={
        "MLFLOW_TRACKING_URI": "${MLFLOW_TRACKING_URI}",  # Azure ML sets this automatically
    }
)

# Submit job
returned_job = ml_client.jobs.create_or_update(job)

print(f"✅ Job submitted: {returned_job.name}")
print(f"📊 View in Azure ML Studio: https://ml.azure.com")
print(f"   → Jobs → {returned_job.name}")
