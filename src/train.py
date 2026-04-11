import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
import os
import json

# Try to configure MLflow with Azure ML workspace
def setup_mlflow():
    try:
        # Check if running on Azure ML (has config.json)
        if os.path.exists("configs/config.json"):
            # Try Azure ML connection (won't work in local sklearn env, but OK to fail)
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

# Log parameters directly (no start_run context)
mlflow.log_params({
    "n_estimators": 100,
    "test_size": 0.2,
    "random_state": 42
})

# Train model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Calculate and log metrics
accuracy = accuracy_score(y_test, model.predict(X_test))
mlflow.log_metric("accuracy", accuracy)

# Save model
joblib.dump(model, "models/model.pkl")
mlflow.sklearn.log_model(model, "iris-model")

print(f"Model trained and saved! Accuracy: {accuracy:.4f}")
