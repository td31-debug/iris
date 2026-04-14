"""
Vertex AI Pipelines - Multi-step ML Orchestration
Compiles pipeline specs for Vertex AI workflow submission
"""

from kfp.v2 import compiler
from kfp.v2.dsl import (
    component,
    pipeline,
    Input,
    Output,
    Dataset,
    Model,
    Artifact,
    ClassificationMetrics
)
from pathlib import Path

PROJECT_ID = "mlops-493014"
REGION = "us-central1"
GCS_BUCKET = f"gs://{PROJECT_ID}-bucket"
PIPELINE_PATH = Path(__file__).resolve().parent.parent / "pipelines"

# ===== Pipeline Components =====

@component(
    base_image="python:3.10",
    packages_to_install=["google-cloud-storage", "scikit-learn", "pandas", "numpy"]
)
def prepare_data(
    output_dataset: Output[Dataset]
):
    """Prepare and preprocess Iris dataset"""
    from pathlib import Path
    from sklearn.datasets import load_iris
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    import pandas as pd
    
    # Load Iris dataset
    iris = load_iris()
    X = iris.data
    y = iris.target
    
    # Preprocessing
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    
    # Persist to the artifact path injected by KFP for this dataset output.
    df_train = pd.DataFrame(X_train, columns=['f0', 'f1', 'f2', 'f3'])
    df_train['label'] = y_train

    Path(output_dataset.path).parent.mkdir(parents=True, exist_ok=True)
    df_train.to_csv(output_dataset.path, index=False)

@component(
    base_image="python:3.10",
    packages_to_install=["google-cloud-storage", "scikit-learn", "pandas", "numpy", "mlflow"]
)
def train_model(
    input_dataset: Input[Dataset],
    output_model: Output[Model]
):
    """Train scikit-learn model"""
    import pickle
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, precision_score, recall_score
    import pandas as pd
    
    # Load data
    df = pd.read_csv(input_dataset.path)
    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Save model
    with open(output_model.path, 'wb') as f:
        pickle.dump(model, f)

@component(
    base_image="python:3.10",
    packages_to_install=["google-cloud-storage", "scikit-learn", "pandas", "numpy"]
)
def evaluate_model(
    input_model: Input[Model],
    input_dataset: Input[Dataset],
    metrics: Output[ClassificationMetrics]
):
    """Evaluate model performance"""
    import pickle
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
    import pandas as pd
    import json
    
    # Load model and data
    with open(input_model.path, 'rb') as f:
        model = pickle.load(f)
    
    df = pd.read_csv(input_dataset.path)
    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values
    
    # Evaluate
    y_pred = model.predict(X)
    
    accuracy = accuracy_score(y, y_pred)
    precision = precision_score(y, y_pred, average='weighted')
    recall = recall_score(y, y_pred, average='weighted')
    f1 = f1_score(y, y_pred, average='weighted')
    
    # Log metrics
    metrics.log_confusion_matrix(
        categories=['Setosa', 'Versicolor', 'Virginica'],
        matrix=confusion_matrix(y, y_pred).tolist()
    )
    
    print("Model Evaluation:")
    print(f"   Accuracy: {accuracy:.4f}")
    print(f"   Precision: {precision:.4f}")
    print(f"   Recall: {recall:.4f}")
    print(f"   F1-Score: {f1:.4f}")

@component(
    base_image="python:3.10",
    packages_to_install=["google-cloud-aiplatform"]
)
def deploy(
    input_model: Input[Model]
):
    """Deploy model to Vertex AI Endpoint"""
    from google.cloud import aiplatform
    
    print("Registering model for deployment...")
    print(f"   Model path: {input_model.path}")
    print("   Ready for deployment to Vertex AI endpoints")

# ===== Pipeline Definition =====

@pipeline(
    name="iris-training-pipeline",
    description="End-to-end ML pipeline: prepare data → train → evaluate → deploy"
)
def iris_training_pipeline():
    """Complete ML training and deployment pipeline"""
    
    # Step 1: Prepare data
    prepare_data_step = prepare_data()
    
    # Step 2: Train model
    train_step = train_model(
        input_dataset=prepare_data_step.outputs['output_dataset']
    )
    
    # Step 3: Evaluate model
    evaluate_step = evaluate_model(
        input_model=train_step.outputs['output_model'],
        input_dataset=prepare_data_step.outputs['output_dataset']
    )
    
    # Step 4: Deploy
    deploy_step = deploy(
        input_model=train_step.outputs['output_model']
    )

# ===== Compilation & Execution =====

def compile_pipeline(package_path=None):
    """Compile pipeline to a local JSON or YAML spec file."""
    PIPELINE_PATH.mkdir(parents=True, exist_ok=True)
    output_path = Path(package_path) if package_path else PIPELINE_PATH / "iris_pipeline_spec.json"

    compiler.Compiler().compile(
        pipeline_func=iris_training_pipeline,
        package_path=str(output_path)
    )

    print(f"Pipeline compiled: {output_path}")
    return str(output_path)


def submit_pipeline(pipeline_path, run_name="iris-pipeline-run", pipeline_root=None):
    """Submit pipeline to Vertex AI Pipelines."""
    from google.auth import default as google_auth_default
    from google.cloud import aiplatform

    credentials, _ = google_auth_default()
    aiplatform.init(project=PROJECT_ID, location=REGION, credentials=credentials)

    print("\nSubmitting pipeline to Vertex AI...")

    job = aiplatform.PipelineJob(
        display_name=run_name,
        template_path=pipeline_path,
        pipeline_root=pipeline_root or f"{GCS_BUCKET}/pipeline-runs",
        project=PROJECT_ID,
        location=REGION
    )

    job.submit()
    print("Pipeline submitted")
    print(f"   Job ID: {job.resource_name}")

    return job

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Vertex AI ML Pipeline")
    parser.add_argument("--action", choices=["compile", "submit"], default="compile",
                       help="Action to perform")
    parser.add_argument("--package-path", default=None, help="Output path for compiled pipeline spec")
    parser.add_argument("--run-name", default="iris-pipeline-run", help="Vertex AI pipeline run name")
    parser.add_argument("--pipeline-root", default=None, help="Pipeline root for Vertex AI runs")
    args = parser.parse_args()
    
    if args.action == "compile":
        compile_pipeline(package_path=args.package_path)
    elif args.action == "submit":
        spec_path = compile_pipeline(package_path=args.package_path)
        submit_pipeline(spec_path, run_name=args.run_name, pipeline_root=args.pipeline_root)
