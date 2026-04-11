# Reproducibility Guide

This guide ensures your ML pipeline is fully reproducible, both locally and on Azure ML.

## ✅ What's Included

### 1. **Version Locking**
- `requirements.txt` - Exact pip versions
- `environment.yml` - Conda environment specification
- Fixed dependency versions in both

### 2. **Git Version Control**
- `.gitignore` - Excludes artifacts, credentials, cache
- Commit history tracks all code changes
- Branch protection for production

### 3. **Environment Reproducibility**

#### Create identical environment:
```bash
# Same OS, Python 3.10
conda env create -f environment.yml
conda activate iris-ml

# Verify packages
pip list
```

#### Recreate from requirements.txt:
```bash
pip install -r requirements.txt
```

### 4. **Random Seed Control**

Our training script uses fixed seeds:
```python
random_state=42  # Fixed seed in RandomForestClassifier
test_size=0.2    # Fixed train/test split ratio
```

### 5. **MLflow Experiment Tracking**

```bash
mlflow ui
```

View reproducible runs with same hyperparameters.

### 6. **Azure ML Integration**

Jobs submitted to Azure ML are logged with:
- Environment specifications
- Compute cluster info
- Input/output paths
- Run logs

## 🔄 Reproduction Steps

### Locally
```bash
# 1. Clone
git clone <repo>

# 2. Setup environment
conda env create -f environment.yml
conda activate iris-ml

# 3. Run training
python src/train.py

# 4. Get same results
mlflow ui  # View metrics
```

### On Azure ML
```bash
# 1. Update config.json
# 2. Create compute cluster
# 3. Run job
python src/job.py

# 4. View in Azure ML Studio
# → Jobs → Same name → Same metrics
```

## 📊 Expected Results

All runs should produce similar results:
- **Accuracy**: ~1.0 (100%)
- **Precision**: ~1.0
- **Recall**: ~1.0
- **F1-Score**: ~1.0

(Iris dataset is simple, perfect classification is expected)

## 🔐 Secrets Management

⚠️ **Never commit credentials!**

```bash
# ✅ Gitignored (safe)
configs/config.json         # Azure credentials
.env                        # Environment variables

# ✅ Stored in GitHub Secrets
AZURE_CREDENTIALS           # Service principal
AZURE_SUBSCRIPTION_ID       # Subscription ID
```

## 🚀 Continuous Reproducibility

- GitHub Actions rebuild environment on every push
- Tests run in clean environment
- Ensures code works on fresh machines
- Automated validation

## 📝 Adding New Dependencies

```bash
# 1. Install in active environment
pip install new-package

# 2. Update requirements.txt
pip freeze > requirements.txt

# 3. Update environment.yml manually or regenerate:
conda env export > environment.yml

# 4. Commit changes
git add requirements.txt environment.yml
git commit -m "Add new-package dependency"
```

---

**All runs are reproducible! ✅**
