"""
Configure MLflow to track experiments with Azure ML
"""
import mlflow
import json
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient

def setup_mlflow_with_azure():
    """Setup MLflow tracking with Azure ML workspace"""
    
    # Load configuration
    with open("configs/config.json") as f:
        config = json.load(f)
    
    # Authenticate with Azure
    ml_client = MLClient(
        DefaultAzureCredential(),
        config["subscription_id"],
        config["resource_group"],
        config["workspace_name"]
    )
    
    # Get MLflow tracking URI from Azure ML workspace
    tracking_uri = ml_client.workspaces.get(
        config["workspace_name"]
    ).mlflow_tracking_uri
    
    # Set MLflow tracking to Azure ML
    mlflow.set_tracking_uri(tracking_uri)
    
    print(f"✅ MLflow connected to Azure ML workspace")
    print(f"   Tracking URI: {tracking_uri}")
    
    return ml_client

if __name__ == "__main__":
    setup_mlflow_with_azure()
