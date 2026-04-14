"""Register a trained model in the Azure ML model registry."""

import argparse
import json
import os
import sys

from azure.ai.ml import MLClient
from azure.ai.ml.entities import Model
from azure.identity import DefaultAzureCredential


def load_config():
    with open("configs/config.json") as handle:
        return json.load(handle)


def get_ml_client():
    config = load_config()
    return MLClient(
        DefaultAzureCredential(),
        config["subscription_id"],
        config["resource_group"],
        config["workspace_name"],
    )


def main():
    parser = argparse.ArgumentParser(description="Register a trained model in Azure ML")
    parser.add_argument("--model-path", default="models/model.pkl")
    parser.add_argument("--name", default="iris-classifier")
    parser.add_argument("--version", default="1")
    parser.add_argument(
        "--description",
        default="Random Forest classifier trained on Iris dataset",
    )
    args = parser.parse_args()

    if not os.path.exists(args.model_path):
        print(f"Model artifact not found: {args.model_path}", file=sys.stderr)
        sys.exit(1)

    ml_client = get_ml_client()
    model = Model(
        path=args.model_path,
        name=args.name,
        version=args.version,
        description=args.description,
    )
    registered_model = ml_client.models.create_or_update(model)
    print(f"Model registered: {registered_model.name} (v{registered_model.version})")


if __name__ == "__main__":
    main()
