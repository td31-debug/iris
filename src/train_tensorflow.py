"""
TensorFlow/Keras Training Script
Runs on Vertex AI Custom Training Job
Trains a neural network on Iris dataset
"""

import tensorflow as tf
from tensorflow import keras
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_iris
import mlflow
import mlflow.keras
import os
import json

# Setup MLflow
mlflow.set_experiment("iris-tensorflow-training")

# Load and prepare data
print("📥 Loading Iris dataset...")
iris = load_iris()
X = iris.data
y = iris.target

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Normalize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"✅ Data loaded: {X_train.shape[0]} training, {X_test.shape[0]} test samples")

# Start MLflow run
with mlflow.start_run():
    # Log parameters
    mlflow.log_param("framework", "tensorflow")
    mlflow.log_param("train_samples", X_train.shape[0])
    mlflow.log_param("test_samples", X_test.shape[0])
    mlflow.log_param("features", X_train.shape[1])
    mlflow.log_param("classes", len(np.unique(y_train)))
    
    # Build model
    print("🏗️ Building TensorFlow model...")
    model = keras.Sequential([
        keras.layers.Dense(128, activation='relu', input_shape=(4,)),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dense(3, activation='softmax')  # 3 iris classes
    ])
    
    # Compile
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Log model architecture
    mlflow.log_param("layers", len(model.layers))
    mlflow.log_param("optimizer", "Adam")
    
    # Train
    print("🚀 Training model...")
    history = model.fit(
        X_train_scaled, y_train,
        epochs=100,
        batch_size=16,
        validation_split=0.2,
        verbose=0
    )
    
    # Evaluate
    print("📊 Evaluating model...")
    test_loss, test_accuracy = model.evaluate(X_test_scaled, y_test, verbose=0)
    
    # Log metrics
    mlflow.log_metric("train_accuracy", float(history.history['accuracy'][-1]))
    mlflow.log_metric("train_loss", float(history.history['loss'][-1]))
    mlflow.log_metric("val_accuracy", float(history.history['val_accuracy'][-1]))
    mlflow.log_metric("val_loss", float(history.history['val_loss'][-1]))
    mlflow.log_metric("test_accuracy", float(test_accuracy))
    mlflow.log_metric("test_loss", float(test_loss))
    
    print(f"✅ Test Accuracy: {test_accuracy:.4f}")
    print(f"✅ Test Loss: {test_loss:.4f}")
    
    # Save model in a Keras 3 compatible way
    keras_model_path = "/tmp/iris_tensorflow.keras"
    export_model_path = "/gcs/mlops-493014-bucket/models/iris_tensorflow_savedmodel"

    model.save(keras_model_path)
    model.export(export_model_path)
    mlflow.keras.log_model(model, "iris_model")

    print(f"💾 Keras model saved to {keras_model_path}")
    print(f"💾 Exported SavedModel to {export_model_path}")
    
    print("\n✅ Training complete!")
