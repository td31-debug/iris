import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import os
import json
import sys

# Try to configure MLflow with Azure ML workspace
def setup_mlflow():
    try:
        # Check if running on Azure ML (has config.json)
        if os.path.exists("configs/config.json"):
            # Try Azure ML connection
            try:
                from azure.identity import DefaultAzureCredential
                from azure.ai.ml import MLClient
                
                with open("configs/config.json") as f:
                    config = json.load(f)
                
                ml_client = MLClient(
                    DefaultAzureCredential(),
                    config["subscription_id"],
                    config["resource_group"],
                    config["workspace_name"]
                )
                
                tracking_uri = ml_client.workspaces.get(
                    config["workspace_name"]
                ).mlflow_tracking_uri
                
                mlflow.set_tracking_uri(tracking_uri)
                print(f"✅ Connected to Azure ML MLflow")
            except Exception as e:
                print(f"⚠️  Using local MLflow: {type(e).__name__}")
                mlflow.set_tracking_uri("./mlruns")
        else:
            mlflow.set_tracking_uri("./mlruns")
            
    except Exception as e:
        print(f"⚠️  Error setting up MLflow: {str(e)[:100]}")
        mlflow.set_tracking_uri("./mlruns")

# Configure MLflow
setup_mlflow()
mlflow.set_experiment("iris-training")

# Clear any stale run ID Azure might have injected
os.environ.pop("MLFLOW_RUN_ID", None)

try:
    mlflow.autolog(disable_for_unsupported_versions=True)
except:
    print("⚠️  Autolog not available")

# Create models directory
os.makedirs("models", exist_ok=True)

# Load data
data = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42
)

# Explicitly start a fresh run
with mlflow.start_run():
    # Log parameters
    mlflow.log_params({
        "n_estimators": 100,
        "test_size": 0.2,
        "random_state": 42
    })
    
    # Train model
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    
    # Calculate metrics
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    
    # Log all metrics to Azure ML
    mlflow.log_metric("accuracy", float(accuracy))
    mlflow.log_metric("precision", float(precision))
    mlflow.log_metric("recall", float(recall))
    mlflow.log_metric("f1_score", float(f1))
    
    # Save and log model
    model_path = "models/model.pkl"
    joblib.dump(model, model_path)
    mlflow.sklearn.log_model(model, "iris-model")
    mlflow.log_artifact(model_path, "models")
    
    print("\n" + "="*60)
    print("✅ TRAINING COMPLETE")
    print("="*60)
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print("="*60 + "\n")
    
    # Flush outputs
    sys.stdout.flush()
    sys.stderr.flush()
