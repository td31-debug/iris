"""
Unit tests for training script
"""
import pytest
import os
import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


def test_model_training():
    """Test that model trains successfully"""
    data = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.2, random_state=42
    )
    
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    
    # Check model is trained
    assert model.n_estimators > 0
    assert hasattr(model, 'classes_')


def test_model_prediction():
    """Test that model can make predictions"""
    data = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.2, random_state=42
    )
    
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    
    # Check predictions are valid
    assert len(predictions) == len(X_test)
    assert all(p in model.classes_ for p in predictions)


def test_model_accuracy():
    """Test model achieves reasonable accuracy"""
    data = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.2, random_state=42
    )
    
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    
    # RandomForest on Iris should achieve > 90% accuracy
    assert accuracy > 0.9, f"Accuracy {accuracy} is below 90%"


def test_model_persistence():
    """Test model can be saved and loaded"""
    data = load_iris()
    X_train, y_train = data.data[:100], data.target[:100]
    
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    
    # Save model
    os.makedirs("models", exist_ok=True)
    test_path = "models/test_model.pkl"
    joblib.dump(model, test_path)
    
    # Load model
    loaded_model = joblib.load(test_path)
    
    # Verify loaded model works
    assert loaded_model is not None
    assert hasattr(loaded_model, 'predict')
    
    # Cleanup
    if os.path.exists(test_path):
        os.remove(test_path)
