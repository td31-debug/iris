# Contributing

This repository follows the Azure Actions contribution model where practical for a Python-based Azure ML project repository.

## Development Setup

1. Fork the repository and clone your fork.
2. Create a Python environment with either `environment.yml` or `requirements.txt`.
3. Install dependencies and verify local execution before opening a pull request.

## Local Validation

Run the following before pushing changes:

```bash
pytest tests/ -v
MLFLOW_TRACKING_URI=./mlruns python src/train.py
```

If your change affects Azure ML submission or deployment logic, also validate the relevant scripts locally:

```bash
python src/job.py
python src/register_model.py --name iris-classifier --version 1 --model-path models/model.pkl
python src/deploy_azure_endpoint.py --model-name iris-classifier --model-version 1 --endpoint-name iris-online-endpoint --deployment-name blue
```

## Pull Requests

1. Open pull requests against `main`.
2. Keep changes scoped and include tests for any new behavior.
3. Ensure GitHub Actions are green before requesting review.
4. Do not commit secrets, credential files, or generated artifacts.

## Release Process

This repository uses release branches and tags to align with Azure Actions repository expectations:

1. Major release line: `releases/v1`
2. Version tag format: `v1.0.0`, `v1.0.1`, etc.
3. Major tag format: `v1`

Hotfixes and minor changes should be promoted through the matching `releases/*` branch and tagged accordingly.