from azure.ai.ml import MLClient, command
from azure.identity import DefaultAzureCredential
import json
import sys

try:
    # Load config
    with open("configs/config.json") as f:
        config = json.load(f)
    
    ml_client = MLClient(
        DefaultAzureCredential(),
        config["subscription_id"],
        config["resource_group"],
        config["workspace_name"]
    )
    
    # Define job with proper environment and dependencies
    job = command(
        code=".",
        command="pip install --upgrade scikit-learn joblib mlflow azure-ai-ml azure-identity -q && python src/train.py",
        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:1",
        compute="cpi-cluster",
        display_name="iris-training-job",
        description="Iris classification training with MLflow tracking",
        outputs={"outputs": {"type": "uri_folder", "mode": "rw_mount"}},
    )
    
    # Submit job
    returned_job = ml_client.jobs.create_or_update(job)
    
    print("\n" + "="*70)
    print("✅ JOB SUBMITTED SUCCESSFULLY")
    print("="*70)
    print(f"Job Name: {returned_job.name}")
    print(f"Status:   Running...")
    print("\n📊 View Results in Azure ML Studio:")
    print(f"   Jobs: https://ml.azure.com/jobs/{returned_job.name}")
    print("   Experiments: https://ml.azure.com/experiments/iris-training")
    print("\n⏳ Job Progress:")
    print("   - Installing dependencies...")
    print("   - Training model...")
    print("   - Logging metrics...")
    print("   - Saving artifacts...")
    print("\n✅ Metrics will appear in portal within 5-10 minutes")
    print("="*70 + "\n")
    
    sys.stdout.flush()
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
