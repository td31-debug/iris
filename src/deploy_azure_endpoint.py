import argparse
import json
from pathlib import Path

from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    CodeConfiguration,
    Environment,
    ManagedOnlineDeployment,
    ManagedOnlineEndpoint,
)
from azure.identity import DefaultAzureCredential


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "configs" / "config.json"
CONDA_PATH = ROOT / "conda-yamls" / "online-inference.yml"
CODE_PATH = ROOT / "src"


def load_config():
    with CONFIG_PATH.open() as handle:
        return json.load(handle)


def get_ml_client():
    config = load_config()
    return MLClient(
        DefaultAzureCredential(),
        subscription_id=config["subscription_id"],
        resource_group_name=config["resource_group"],
        workspace_name=config["workspace_name"],
    )


def ensure_environment(ml_client, name, version):
    environment = Environment(
        name=name,
        version=version,
        image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04",
        conda_file=str(CONDA_PATH),
        description="Azure ML online inference environment for the Iris classifier",
    )
    return ml_client.environments.create_or_update(environment)


def main():
    parser = argparse.ArgumentParser(description="Deploy a registered model to an Azure ML online endpoint")
    parser.add_argument("--model-name", default="iris-classifier")
    parser.add_argument("--model-version", default="1")
    parser.add_argument("--endpoint-name", default="iris-online-endpoint")
    parser.add_argument("--deployment-name", default="blue")
    parser.add_argument("--instance-type", default="Standard_DS2_v2")
    parser.add_argument("--instance-count", type=int, default=1)
    parser.add_argument("--environment-name", default="iris-online-inference")
    parser.add_argument("--environment-version", default="1")
    args = parser.parse_args()

    ml_client = get_ml_client()
    model = ml_client.models.get(name=args.model_name, version=args.model_version)
    environment = ensure_environment(
        ml_client,
        name=args.environment_name,
        version=args.environment_version,
    )

    endpoint = ManagedOnlineEndpoint(
        name=args.endpoint_name,
        description="Online endpoint for the Iris classifier",
        auth_mode="key",
    )
    ml_client.online_endpoints.begin_create_or_update(endpoint).result()

    deployment = ManagedOnlineDeployment(
        name=args.deployment_name,
        endpoint_name=args.endpoint_name,
        model=model,
        environment=environment,
        code_configuration=CodeConfiguration(
            code=str(CODE_PATH),
            scoring_script="score.py",
        ),
        instance_type=args.instance_type,
        instance_count=args.instance_count,
    )
    ml_client.online_deployments.begin_create_or_update(deployment).result()

    endpoint = ml_client.online_endpoints.get(args.endpoint_name)
    endpoint.traffic = {args.deployment_name: 100}
    ml_client.online_endpoints.begin_create_or_update(endpoint).result()

    final_endpoint = ml_client.online_endpoints.get(args.endpoint_name)
    print(f"Endpoint:    {final_endpoint.name}")
    print(f"Deployment:  {args.deployment_name}")
    print(f"Scoring URI: {final_endpoint.scoring_uri}")


if __name__ == "__main__":
    main()