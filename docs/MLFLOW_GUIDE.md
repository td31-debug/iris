# MLflow Integration Guide

## 🎯 What is MLflow?

MLflow is an experiment tracking system that logs:
- **Metrics** (accuracy, loss, F1-score, etc.)
- **Parameters** (hyperparameters, config)
- **Models** (trained model artifacts)
- **Artifacts** (plots, data, logs)

---

## 📦 Installation

```bash
pip install mlflow
```

---

## 🚀 Usage Options

### Option 1: Local MLflow (Default)
```bash
python src/train.py
```

View results:
```bash
mlflow ui
```
Then open: **http://localhost:5000**

---

### Option 2: MLflow + Azure ML Integration
```python
from src.mlflow_config import setup_mlflow_with_azure
setup_mlflow_with_azure()
```

This connects MLflow to your Azure ML workspace for centralized tracking.

---

## 📊 View Experiments

### Local UI
```bash
mlflow ui
```
- Open http://localhost:5000
- Compare runs, metrics, artifacts
- Export results

### Azure ML Studio
1. Go to Azure ML workspace
2. Click "Experiments" sidebar
3. View all logged runs

---

## 🔍 What Gets Logged Automatically?

With `mlflow.autolog()`:
- ✅ Hyperparameters (n_estimators, max_depth, etc.)
- ✅ Metrics (accuracy, precision, recall, F1)
- ✅ Model artifacts
- ✅ Training duration
- ✅ Input/output shapes

---

## 📝 Custom Logging

```python
mlflow.log_params({"learning_rate": 0.01})
mlflow.log_metric("accuracy", 0.95)
mlflow.log_artifact("plots/confusion_matrix.png")
```

---

## 📂 Project Structure

```
project/
├── mlruns/                # Local MLflow artifacts
├── src/
│   ├── train.py           # Training with MLflow
│   ├── train_with_mlflow.py  # Enhanced version with full metrics
│   └── mlflow_config.py   # Azure ML integration
├── configs/config.json
└── models/model.pkl
```

---

## 🔄 GitHub Actions Integration

Already configured! MLflow runs automatically when you push code.

See `.github/workflows/azure-ml-train.yml`

---

## 💾 Save MLflow Runs

Export run data:
```bash
mlflow experiments list
mlflow runs list --experiment-name iris-training
```

---

## 🎓 Next Steps

1. Run training: `python src/train.py`
2. View UI: `mlflow ui`
3. Compare experiments
4. Push to GitHub for CI/CD
5. View in Azure ML Studio
