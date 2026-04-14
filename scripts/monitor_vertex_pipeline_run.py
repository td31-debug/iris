import argparse
from urllib.parse import parse_qs, urlparse

from google.auth import default as google_auth_default
from google.cloud import aiplatform


PROJECT_ID = "mlops-493014"
REGION = "us-central1"


def resolve_pipeline_resource(reference):
    if reference.startswith("projects/"):
        return reference

    if reference.startswith("https://console.cloud.google.com/"):
        parsed = urlparse(reference)
        project = parse_qs(parsed.query).get("project", [PROJECT_ID])[0]
        marker = "/runs/"
        if marker not in parsed.path:
            raise ValueError("Unsupported Vertex AI pipeline URL format")
        run_id = parsed.path.split(marker, 1)[1].split("/", 1)[0]
        return f"projects/{project}/locations/{REGION}/pipelineJobs/{run_id}"

    return f"projects/{PROJECT_ID}/locations/{REGION}/pipelineJobs/{reference}"


def print_pipeline_details(reference):
    credentials, _ = google_auth_default()
    aiplatform.init(project=PROJECT_ID, location=REGION, credentials=credentials)

    resource_name = resolve_pipeline_resource(reference)
    pipeline_job = aiplatform.PipelineJob.get(resource_name)
    start_time = getattr(pipeline_job, "start_time", None)
    end_time = getattr(pipeline_job, "end_time", None)
    error = getattr(pipeline_job, "error", None)

    print(f"Display name: {pipeline_job.display_name}")
    print(f"Resource name: {pipeline_job.resource_name}")
    print(f"State: {pipeline_job.state.name}")
    print(f"Created: {pipeline_job.create_time}")
    print(f"Started: {start_time if start_time else 'Not available'}")
    print(f"Ended: {end_time if end_time else 'Not available'}")

    if error:
        print(f"Error code: {error.code}")
        print(f"Error message: {error.message}")

    run_id = pipeline_job.resource_name.rsplit("/", 1)[-1]
    print(
        "Console URL: "
        f"https://console.cloud.google.com/vertex-ai/pipelines/locations/{REGION}/runs/{run_id}?project={PROJECT_ID}"
    )


def main():
    parser = argparse.ArgumentParser(description="Inspect a Vertex AI pipeline run")
    parser.add_argument("--run", required=True, help="Pipeline console URL, resource name, or run id")
    args = parser.parse_args()
    print_pipeline_details(args.run)


if __name__ == "__main__":
    main()