"""
Vertex AI Pipelines - Multi-step ML Orchestration
Compiles pipeline YAML for Vertex AI workflow submission
"""

from kfp import dsl
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
from google.cloud import aiplatform
from google.auth import default as google_auth_default

PROJECT_ID = "mlops-493014"
REGION = "us-central1"
GCS_BUCKET = f"gs://{PROJECT_ID}-bucket"
PIPELINE_PATH = f"{GCS_BUCKET}/pipelines"

# Load credentials
credentials, project = google_auth_default()
aiplatform.init(project=PROJECT_ID, location=REGION, credentials=credentials)

# ===== Pipeline Components =====

@component(
    base_image="python:3.10",
    packages_to_install=["google-cloud-storage", "scikit-learn", "pandas", "numpy"]
)
def prepare_data(
    output_dataset: Output[Dataset]
):
    """Prepare and preprocess Iris dataset"""
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
    
    # Save to dataset output (GCS)
    df_train = pd.DataFrame(X_train, columns=['f0', 'f1', 'f2', 'f3'])
    df_train['label'] = y_train
    
    output_dataset.path = f"{GCS_BUCKET}/datasets/iris_train.csv"
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
    
    print(f"✅ Model Evaluation:")
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
    
    print(f"📤 Registering model for deployment...")
    print(f"   Model path: {input_model.path}")
    print(f"   Ready for deployment to Vertex AI endpoints")

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

def compile_pipeline():
    """Compile pipeline to YAML"""
    pipeline_yaml_path = f"{PIPELINE_PATH.replace('gs://', '')}/iris-pipeline.yaml"
    
    compiler.Compiler().compile(
        pipeline_func=iris_training_pipeline,
        package_path=pipeline_yaml_path
    )
    
    print(f"✅ Pipeline compiled: {pipeline_yaml_path}")
    return pipeline_yaml_path

def submit_pipeline(pipeline_yaml_path, run_name="iris-pipeline-run"):
    """Submit pipeline to Vertex AI Pipelines"""
    print(f"\n🚀 Submitting pipeline to Vertex AI...")
    
    job = aiplatform.PipelineJob(
        display_name=run_name,
        template_path=pipeline_yaml_path,
        project=PROJECT_ID,
        location=REGION
    )
    
    job.submit()
    print(f"✅ Pipeline submitted!")
    print(f"   Job ID: {job.resource_name}")
    
    return job

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Vertex AI ML Pipeline")
    parser.add_argument("--action", choices=["compile", "submit"], default="compile",
                       help="Action to perform")
    args = parser.parse_args()
    
    if args.action == "compile":
        compile_pipeline()
    elif args.action == "submit":
        yaml_path = compile_pipeline()
        submit_pipeline(yaml_path)
