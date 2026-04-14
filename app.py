from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

MODEL_PATH = Path(__file__).resolve().parent / "models" / "model.pkl"
model = joblib.load(MODEL_PATH)

CLASSES = {0: "setosa", 1: "versicolor", 2: "virginica"}

app = FastAPI(title="Iris Classifier API", version="1.0.0")


class IrisInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


@app.get("/")
def root():
    return {"message": "Iris Classifier API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/predict")
def predict(data: IrisInput):
    features = np.array(
        [[data.sepal_length, data.sepal_width, data.petal_length, data.petal_width]]
    )
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0]

    return {
        "prediction": int(prediction),
        "class_name": CLASSES[int(prediction)],
        "confidence": float(max(probability)),
    }
