import json
import os
from pathlib import Path

import joblib
import numpy as np


CLASSES = {0: "setosa", 1: "versicolor", 2: "virginica"}
MODEL = None


def _find_model_path() -> Path:
    model_dir = Path(os.environ["AZUREML_MODEL_DIR"])
    candidates = sorted(model_dir.rglob("model.pkl"))
    if not candidates:
        raise FileNotFoundError(f"No model.pkl found under {model_dir}")
    return candidates[0]


def init():
    global MODEL
    MODEL = joblib.load(_find_model_path())


def _normalize_payload(payload):
    if isinstance(payload, dict):
        if "input_data" in payload:
            payload = payload["input_data"]
        elif "instances" in payload:
            payload = payload["instances"]
        else:
            payload = [payload]

    if not isinstance(payload, list):
        raise ValueError("Request payload must be a list or an object containing input_data/instances")

    rows = []
    for item in payload:
        if isinstance(item, dict):
            rows.append(
                [
                    item["sepal_length"],
                    item["sepal_width"],
                    item["petal_length"],
                    item["petal_width"],
                ]
            )
        else:
            rows.append(item)

    return np.asarray(rows, dtype=float)


def run(raw_data):
    try:
        payload = json.loads(raw_data)
        features = _normalize_payload(payload)
        predictions = MODEL.predict(features).tolist()

        if hasattr(MODEL, "predict_proba"):
            confidence = MODEL.predict_proba(features).max(axis=1).tolist()
        else:
            confidence = [None] * len(predictions)

        return {
            "predictions": predictions,
            "class_names": [CLASSES[int(prediction)] for prediction in predictions],
            "confidence": confidence,
        }
    except Exception as exc:
        return {"error": str(exc)}