import argparse
import json
from pathlib import Path

from azure.ai.ml import MLClient
from azure.ai.ml.entities import PipelineJob
from azure.identity import DefaultAzureCredential
from google.auth import default as google_auth_default
from google.cloud import aiplatform


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "configs" / "config.json"
DEFAULT_VERTEX_JOB = ROOT / "pipelines" / "iris_pipeline_job.json"
DEFAULT_AZUREML_JOB = ROOT / "pipelines" / "iris_azureml_pipeline_job.json"


def load_json(path):
    return json.loads(Path(path).read_text())


def resolve_relative_path(base_path, candidate):
    candidate_path = Path(candidate)
    if candidate_path.is_absolute():
        return str(candidate_path)
    return str((Path(base_path).parent / candidate_path).resolve())


def get_ml_client():
    config = json.loads(CONFIG_PATH.read_text())
    return MLClient(
        DefaultAzureCredential(),
        subscription_id=config["subscription_id"],
        resource_group_name=config["resource_group"],
        workspace_name=config["workspace_name"],
    )


def upload_vertex(job_path, validate_only=False):
    payload = load_json(job_path)
    if validate_only:
        print(json.dumps(payload, indent=2))
        return

    credentials, _ = google_auth_default()
    aiplatform.init(project="mlops-493014", location="us-central1", credentials=credentials)

    template_path = payload.get("templatePath") or payload.get("templateUri")
    if payload.get("templatePath"):
        template_path = resolve_relative_path(job_path, template_path)
    runtime_config = payload.get("runtimeConfig", {})
    job = aiplatform.PipelineJob(
        display_name=payload.get("displayName", "iris-pipeline-run"),
        template_path=template_path,
        pipeline_root=runtime_config.get("gcsOutputDirectory"),
        parameter_values=runtime_config.get("parameterValues", {}),
        labels=payload.get("labels", {}),
        project="mlops-493014",
        location="us-central1",
    )
    job.submit()
    print(job.resource_name)


def upload_azureml(job_path, validate_only=False):
    payload = load_json(job_path)
    pipeline_job = PipelineJob._load_from_dict(payload, context={"base_path": str(ROOT)}, additional_message="")
    if validate_only:
        print(pipeline_job._to_dict())
        return

    ml_client = get_ml_client()
    result = ml_client.jobs.create_or_update(pipeline_job)
    print(result.name)


def main():
    parser = argparse.ArgumentParser(description="Upload a pipeline job JSON to Vertex AI or Azure ML")
    parser.add_argument("--target", choices=["vertex", "azureml"], required=True)
    parser.add_argument("--job-file", default=None)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    if args.target == "vertex":
        upload_vertex(args.job_file or DEFAULT_VERTEX_JOB, validate_only=args.validate_only)
    else:
        upload_azureml(args.job_file or DEFAULT_AZUREML_JOB, validate_only=args.validate_only)


if __name__ == "__main__":
    main()