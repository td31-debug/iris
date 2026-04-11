"""
Enhanced training script with MLflow experiment tracking
"""
import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import os

# Set MLflow tracking URI (local by default)
mlflow.set_tracking_uri("./mlruns")
mlflow.set_experiment("iris-training")

# Enable autologging - logs everything automatically!
mlflow.autolog(disable_for_unsupported_versions=True)

# Load data
print("Loading Iris dataset...")
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Start MLflow run
with mlflow.start_run(run_name="random-forest-baseline"):
    # Log parameters
    params = {
        "n_estimators": 100,
        "max_depth": 10,
        "random_state": 42,
        "test_size": 0.2
    }
    mlflow.log_params(params)
    
    # Train model
    print("Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=params["n_estimators"],
        max_depth=params["max_depth"],
        random_state=params["random_state"]
    )
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="weighted")
    recall = recall_score(y_test, y_pred, average="weighted")
    f1 = f1_score(y_test, y_pred, average="weighted")
    
    # Log metrics
    print(f"Logging metrics...")
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("f1_score", f1)
    
    # Log model artifacts
    os.makedirs("models", exist_ok=True)
    model_path = "models/model.pkl"
    joblib.dump(model, model_path)
    mlflow.log_artifact(model_path)
    
    # Log model with sklearn flavor (can be loaded later)
    mlflow.sklearn.log_model(model, "iris-model")
    
    print("\n" + "="*50)
    print("✅ Training Complete!")
    print("="*50)
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print("="*50)
    
    # Get run info
    run_id = mlflow.active_run().info.run_id
    print(f"MLflow Run ID: {run_id}")
    print(f"View results: mlflow ui")
