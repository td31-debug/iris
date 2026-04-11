import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import os
import sys

# ── MLflow setup ──────────────────────────────────────────
os.environ.pop("MLFLOW_RUN_ID", None)  # clear any stale Azure-injected run ID

tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "./mlruns")
mlflow.set_tracking_uri(tracking_uri)
mlflow.set_experiment("iris-training")
print(f"📍 MLflow tracking: {tracking_uri}")

# ── Data ──────────────────────────────────────────────────
data = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42
)

# ── Training ──────────────────────────────────────────────
os.makedirs("models", exist_ok=True)

with mlflow.start_run():
    params = {"n_estimators": 100, "test_size": 0.2, "random_state": 42}
    mlflow.log_params(params)

    model = RandomForestClassifier(
        n_estimators=params["n_estimators"],
        random_state=params["random_state"]
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    metrics = {
        "accuracy":  float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, average="weighted", zero_division=0)),
        "recall":    float(recall_score(y_test, y_pred, average="weighted", zero_division=0)),
        "f1_score":  float(f1_score(y_test, y_pred, average="weighted", zero_division=0)),
    }
    mlflow.log_metrics(metrics)

    # Save model
    try:
        import joblib
        model_path = "models/model.pkl"
        joblib.dump(model, model_path)
        mlflow.log_artifact(model_path)
    except ImportError:
        pass

    # Log model to MLflow registry
    try:
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="iris-model",
            registered_model_name="iris-rf-classifier"
        )
    except Exception as e:
        print(f"⚠️  Model registry skipped: {type(e).__name__}")

    # ── Output ────────────────────────────────────────────
    print("\n" + "="*60)
    print("✅ TRAINING COMPLETE")
    print("="*60)
    for k, v in metrics.items():
        print(f"{k.capitalize():<12}: {v:.4f}")
    print("="*60)
    sys.stdout.flush()