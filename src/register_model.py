"""
Register trained model in Azure ML Model Registry
"""
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Model
import json
import os

# Load config
with open("configs/config.json") as f:
    config = json.load(f)

ml_client = MLClient(
    DefaultAzureCredential(),
    config["subscription_id"],
    config["resource_group"],
    config["workspace_name"]
)

# Register model
if os.path.exists("models/model.pkl"):
    model = Model(
        path="models/model.pkl",
        name="iris-classifier",
        version="1",
        description="Random Forest classifier trained on Iris dataset"
    )
    
    registered_model = ml_client.models.create_or_update(model)
    print(f"Model registered: {registered_model.name} (v{registered_model.version})")
else:
    print("Model artifact not found!")
