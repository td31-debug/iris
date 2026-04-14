"""
PyTorch Training Implementation for Iris Dataset
Trains a neural network classifier on Iris dataset with MLflow tracking
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import mlflow
import numpy as np
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from google.cloud import storage
import os

# Set random seeds for reproducibility
np.random.seed(42)
torch.manual_seed(42)

# ===== Configuration =====
LEARNING_RATE = 0.001
BATCH_SIZE = 16
EPOCHS = 100
VALIDATION_SPLIT = 0.2
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
GCS_BUCKET = "mlops-493014-bucket"
GCS_MODEL_PATH = "models/iris_pytorch"

print(f"Using device: {DEVICE}")

# ===== Data Loading =====
print("Loading Iris dataset...")
iris = load_iris()
X = iris.data  # (150, 4)
y = iris.target  # (150,)

# Preprocessing
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

# Convert to PyTorch tensors
X_train_tensor = torch.FloatTensor(X_train)
y_train_tensor = torch.LongTensor(y_train)
X_test_tensor = torch.FloatTensor(X_test)
y_test_tensor = torch.LongTensor(y_test)

# Create DataLoader
train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

print(f"✅ Data loaded: {X_train.shape[0]} training, {X_test.shape[0]} test samples")

# ===== Model Definition =====
class IrisNet(nn.Module):
    def __init__(self, input_size=4, hidden_size1=128, hidden_size2=64, hidden_size3=32, output_size=3):
        super(IrisNet, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size1)
        self.dropout1 = nn.Dropout(0.2)
        self.fc2 = nn.Linear(hidden_size1, hidden_size2)
        self.dropout2 = nn.Dropout(0.2)
        self.fc3 = nn.Linear(hidden_size2, hidden_size3)
        self.fc4 = nn.Linear(hidden_size3, output_size)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout1(x)
        x = self.relu(self.fc2(x))
        x = self.dropout2(x)
        x = self.relu(self.fc3(x))
        x = self.fc4(x)
        return x

model = IrisNet().to(DEVICE)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

print(f"✅ Model created with {sum(p.numel() for p in model.parameters())} parameters")

# ===== MLflow Tracking =====
mlflow.set_experiment("iris_pytorch_training")

with mlflow.start_run(run_name="iris_pytorch"):
    # Log hyperparameters
    mlflow.log_param("learning_rate", LEARNING_RATE)
    mlflow.log_param("batch_size", BATCH_SIZE)
    mlflow.log_param("epochs", EPOCHS)
    mlflow.log_param("model_architecture", "Dense(128)->Dropout->Dense(64)->Dropout->Dense(32)->Dense(3)")
    mlflow.log_param("optimizer", "Adam")
    mlflow.log_param("loss_function", "CrossEntropyLoss")

    # ===== Training Loop =====
    print("\n🚀 Starting training...")
    for epoch in range(EPOCHS):
        model.train()
        train_loss = 0.0
        
        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(DEVICE), batch_y.to(DEVICE)
            
            # Forward pass
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        avg_train_loss = train_loss / len(train_loader)
        
        # Validation on test set
        model.eval()
        with torch.no_grad():
            val_outputs = model(X_test_tensor.to(DEVICE))
            val_loss = criterion(val_outputs, y_test_tensor.to(DEVICE))
            val_preds = torch.argmax(val_outputs, dim=1).cpu().numpy()
        
        val_accuracy = accuracy_score(y_test, val_preds)
        
        # Log metrics every 10 epochs
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {avg_train_loss:.4f} | Val Accuracy: {val_accuracy:.4f}")
            mlflow.log_metric("train_loss", avg_train_loss, step=epoch)
            mlflow.log_metric("val_loss", val_loss.item(), step=epoch)
            mlflow.log_metric("val_accuracy", val_accuracy, step=epoch)

    # ===== Final Evaluation =====
    print("\n📊 Computing final metrics...")
    model.eval()
    with torch.no_grad():
        test_outputs = model(X_test_tensor.to(DEVICE))
        test_preds = torch.argmax(test_outputs, dim=1).cpu().numpy()
    
    test_accuracy = accuracy_score(y_test, test_preds)
    test_precision = precision_score(y_test, test_preds, average='weighted')
    test_recall = recall_score(y_test, test_preds, average='weighted')
    test_f1 = f1_score(y_test, test_preds, average='weighted')
    
    print(f"✅ Test Accuracy: {test_accuracy:.4f}")
    print(f"✅ Test Precision: {test_precision:.4f}")
    print(f"✅ Test Recall: {test_recall:.4f}")
    print(f"✅ Test F1-Score: {test_f1:.4f}")
    
    # Log final metrics
    mlflow.log_metric("final_test_accuracy", test_accuracy)
    mlflow.log_metric("final_test_precision", test_precision)
    mlflow.log_metric("final_test_recall", test_recall)
    mlflow.log_metric("final_test_f1", test_f1)

    # ===== Model Saving to GCS =====
    print("\n💾 Saving model to GCS...")
    local_model_path = "/tmp/iris_pytorch_model.pt"
    torch.save(model.state_dict(), local_model_path)

    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET)
        blob = bucket.blob(f"{GCS_MODEL_PATH}/model.pt")
        blob.upload_from_filename(local_model_path)
        
        # Also save scaler for preprocessing
        # For now, just confirm save
        print(f"✅ Model saved to gs://{GCS_BUCKET}/{GCS_MODEL_PATH}/model.pt")
        mlflow.log_artifact(local_model_path, artifact_path=GCS_MODEL_PATH)
    except Exception as e:
        print(f"⚠️  Could not save to GCS: {e}")
        print(f"Local model saved at: {local_model_path}")

print("\n✅ Training completed successfully!")
