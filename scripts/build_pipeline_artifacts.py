import json
from pathlib import Path

from azure.ai.ml import dsl, command

from vertex_pipeline import compile_pipeline


ROOT = Path(__file__).resolve().parent.parent
PIPELINES_DIR = ROOT / "pipelines"
VERTEX_SPEC_PATH = PIPELINES_DIR / "iris_pipeline_spec.json"
VERTEX_JOB_PATH = PIPELINES_DIR / "iris_pipeline_job.json"
AZUREML_JOB_PATH = PIPELINES_DIR / "iris_azureml_pipeline_job.json"
PROJECT_ID = "mlops-493014"
GCS_BUCKET = f"gs://{PROJECT_ID}-bucket"


def normalize_repo_path(value):
    if not isinstance(value, str):
        return value

    try:
        path = Path(value)
    except (TypeError, ValueError):
        return value

    if not path.is_absolute():
        return value

    try:
        relative_path = path.relative_to(ROOT)
    except ValueError:
        return value

    return "." if not relative_path.parts else relative_path.as_posix()


def normalize_paths(payload):
    if isinstance(payload, dict):
        return {key: normalize_paths(value) for key, value in payload.items()}
    if isinstance(payload, list):
        return [normalize_paths(value) for value in payload]
    return normalize_repo_path(payload)


def build_vertex_pipeline_spec():
    return compile_pipeline(package_path=str(VERTEX_SPEC_PATH))


def build_vertex_pipeline_job():
    payload = {
        "displayName": "iris-pipeline-run",
        "templatePath": "pipelines/iris_pipeline_spec.json",
        "labels": {
            "project": "iris",
            "repo": "td31-debug-iris",
            "pipeline": "vertex-ai"
        },
        "runtimeConfig": {
            "gcsOutputDirectory": f"{GCS_BUCKET}/pipeline-runs",
            "parameterValues": {}
        }
    }
    VERTEX_JOB_PATH.write_text(json.dumps(payload, indent=2) + "\n")
    return str(VERTEX_JOB_PATH)


def build_azureml_pipeline_job():
    train_component = command(
        name="train_iris_component",
        display_name="train_iris_component",
        code=".",
        command="python src/train.py",
        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:1",
        compute="cpi-cluster",
    )

    @dsl.pipeline(name="iris-azureml-pipeline", description="Azure ML pipeline for Iris training")
    def iris_azureml_pipeline():
        train_component()

    pipeline_job = iris_azureml_pipeline()
    payload = normalize_paths(pipeline_job._to_dict())
    AZUREML_JOB_PATH.write_text(json.dumps(payload, indent=2) + "\n")
    return str(AZUREML_JOB_PATH)


def main():
    PIPELINES_DIR.mkdir(parents=True, exist_ok=True)
    results = {
        "vertex_pipeline_spec": build_vertex_pipeline_spec(),
        "vertex_pipeline_job": build_vertex_pipeline_job(),
        "azureml_pipeline_job": build_azureml_pipeline_job(),
    }
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()