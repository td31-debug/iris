#!/bin/bash
# Quick start - run all training pipeline steps

echo "📊 Azure ML Training Pipeline"
echo "=============================="

# Step 1: Install dependencies
echo "1️⃣ Installing dependencies..."
pip install mlflow -q

# Step 2: Run training with MLflow
echo "2️⃣ Training model with MLflow tracking..."
python src/train.py

# Step 3: View MLflow UI
echo "3️⃣ Opening MLflow UI..."
echo "Run this command to view experiments:"
echo "  mlflow ui"
echo ""
echo "Then open: http://localhost:5000"
