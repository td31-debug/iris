from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
import json

# Load config
with open("configs/config.json") as f:
    config = json.load(f)

ml_client = MLClient(
    DefaultAzureCredential(),
    subscription_id=config["subscription_id"],
    resource_group_name=config["resource_group"],
    workspace_name=config["workspace_name"]
)

# Test connection
print("Connected to workspace:", ml_client.workspace_name)
