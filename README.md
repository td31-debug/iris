# 🎯 Azure ML + MLflow Training Pipeline

> Production-ready ML project with Git reproducibility, Conda environment, Azure ML integration, and automated CI/CD.

---

## 📋 Quick Start

### **Offline Setup (Local Development)**

#### 1. Clone & Setup
```bash
git clone https://github.com/YOUR_USERNAME/iris-ml-pipeline.git
cd iris-ml-pipeline
```

#### 2. Create Conda Environment
```bash
conda env create -f environment.yml
conda activate iris-ml
```

Or with pip:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Run Locally
```bash
# Train model with MLflow tracking
python src/train.py

# View experiments
mlflow ui
# Open http://localhost:5000
```

---

### **Online Setup (Azure ML Integration)**

#### 1. Update Config
Edit `configs/config.json`:
```json
{
  "subscription_id": "YOUR_SUBSCRIPTION_ID",
  "resource_group": "YOUR_RESOURCE_GROUP",
  "workspace_name": "YOUR_WORKSPACE_NAME"
}
```

#### 2. Test Azure Connection
```bash
python src/connect_workspace.py
# Output: Connected to workspace: YOUR_WORKSPACE_NAME
```

#### 3. Create Compute Cluster
- Go to [Azure ML Studio](https://ml.azure.com)
- Compute → Compute Clusters → Create
- Name: `cpi-cluster` (you can customize)

#### 4. Submit Job to Cloud
```bash
az login  # One-time: authenticate with Azure
python src/job.py
# Check Azure ML Studio → Jobs for status
```

---

## 📁 Project Structure

```
iris-ml-pipeline/
├── .github/workflows/          # ✅ CI/CD pipelines
│   ├── azure-ml-train.yml      # Main training pipeline
│   ├── test-locally.yml        # Unit tests
│   └── deploy.yml              # Model deployment
├── configs/
│   └── config.json             # Azure credentials (git ignored)
├── src/
│   ├── train.py                # Training with MLflow
│   ├── train_with_mlflow.py    # Enhanced version with metrics
│   ├── connect_workspace.py    # Test Azure connection
│   ├── job.py                  # Submit job to Azure ML
│   ├── register_model.py       # Model registry
│   └── mlflow_config.py        # MLflow + Azure integration
├── tests/
│   └── test_train.py           # Unit tests
├── models/                     # Trained models (git ignored)
├── docs/
│   └── MLFLOW_GUIDE.md         # MLflow documentation
├── .github/
│   └── GITHUB_ACTIONS_SETUP.md # GitHub Actions setup
├── requirements.txt            # Pip dependencies
├── environment.yml             # Conda environment
├── .gitignore                  # Git exclusions
└── README.md                   # This file
```

---

## 🔑 Features

✅ **Reproducibility**
- Conda/pip dependency locking
- Fixed version numbers
- Git version control
- Experiment tracking with MLflow

✅ **Azure ML Integration**
- Workspace authentication
- Cloud job submission
- Compute cluster support
- Model registry

✅ **Automation**
- GitHub Actions CI/CD
- Automatic training runs
- Weekly scheduled jobs
- Model deployment pipeline

✅ **Experiment Tracking**
- MLflow autologging
- Metrics & parameters
- Model versioning
- Local UI + Azure ML Studio

✅ **Quality Assurance**
- Unit tests (pytest)
- Code coverage
- Local validation
- Cloud testing

---

## 🚀 CI/CD Pipeline

### Triggers
- ✅ Push to `main` branch
- ✅ Pull requests
- ✅ Weekly schedule (Sunday 2 AM UTC)
- ✅ Manual trigger

### GitHub Actions Setup
1. Go to repo → Settings → Secrets and variables → Actions
2. Add 4 secrets (see [.github/GITHUB_ACTIONS_SETUP.md](.github/GITHUB_ACTIONS_SETUP.md))
3. Push code → Workflows run automatically

---

## 📊 Monitoring

### Local MLflow
```bash
mlflow ui
# http://localhost:5000
```
- View all runs
- Compare experiments
- Export metrics

### Azure ML Studio
- [ml.azure.com](https://ml.azure.com)
- Jobs → View submitted training runs
- Models → View registered models

---

## 🧪 Testing

```bash
# Run unit tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src

# Test training locally
python src/train.py
```

---

## 🔧 Configuration

### Azure ML (`configs/config.json`)
```json
{
  "subscription_id": "YOUR_SUBSCRIPTION_ID",
  "resource_group": "YOUR_RESOURCE_GROUP",
  "workspace_name": "YOUR_WORKSPACE_NAME"
}
```

### Conda Environment
Update `environment.yml` and rebuild:
```bash
conda env update -f environment.yml --prune
```

### MLflow Tracking
- Local: `./mlruns` (default)
- Azure ML: Automatic (when using Azure credentials)

---

## 📦 Dependencies

### Core ML
- `scikit-learn` - Machine learning
- `joblib` - Model serialization

### Azure
- `azure-identity` - Authentication
- `azure-ai-ml` - Azure ML SDK

### Experiment Tracking
- `mlflow` - Experiment management

### Testing
- `pytest` - Unit tests
- `pytest-cov` - Coverage reports

---

## 🐛 Troubleshooting

### "Unknown compute target 'cpi-cluster'"
→ Create cluster in Azure ML Studio first

### "Azure login failed"
→ Run `az login` before `python src/job.py`

### "ModuleNotFoundError"
→ Verify environment: `conda activate iris-ml` or `source venv/bin/activate`

### "MLflow FileStore deprecated"
→ Warning only - use SQLite backend for production:
```python
mlflow.set_tracking_uri("sqlite:///mlflow.db")
```

---

## 📚 Documentation

- [MLflow Guide](docs/MLFLOW_GUIDE.md)
- [GitHub Actions Setup](github/GITHUB_ACTIONS_SETUP.md)
- [Azure ML Docs](https://learn.microsoft.com/en-us/azure/machine-learning)

---

## 🎓 Next Steps

1. ✅ Clone repository
2. ✅ Create Conda environment
3. ✅ Run training locally
4. ✅ Update Azure config
5. ✅ Set GitHub secrets
6. ✅ Push to main → CI/CD runs
7. ✅ Monitor Azure ML Studio

---

## 📝 License

MIT

---

## 👤 Author

Your Name / Organization

---

**Happy training! 🚀**
