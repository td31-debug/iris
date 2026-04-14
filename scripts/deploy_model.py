"""
Deploy Trained Models to Vertex AI Endpoints
Supports serving models for online predictions
"""

from google.cloud import aiplatform
from google.auth import default as google_auth_default
import argparse
import time

PROJECT_ID = "mlops-493014"
REGION = "us-central1"
GCS_BUCKET = f"gs://{PROJECT_ID}-bucket"

# Load credentials
credentials, project = google_auth_default()
aiplatform.init(project=PROJECT_ID, location=REGION, credentials=credentials)

def upload_model(model_path, framework="scikit-learn", version="v1"):
    """Upload model to Vertex AI Model Registry"""
    print(f"\n📤 Uploading {framework} model to registry...")
    
    display_name = f"iris-{framework.replace('_', '-')}-{version}"
    
    try:
        model = aiplatform.Model.upload(
            display_name=display_name,
            artifact_uri=model_path,
            serving_container_image_uri=_get_serving_image(framework),
            serving_container_predict_route="/predict",
            serving_container_health_route="/health",
            labels={
                "framework": framework,
                "version": version,
                "dataset": "iris"
            }
        )
        
        print(f"✅ Model uploaded successfully!")
        print(f"   Model ID: {model.resource_name}")
        print(f"   Display Name: {display_name}")
        
        return model
        
    except Exception as e:
        print(f"❌ Error uploading model: {e}")
        return None

def _get_serving_image(framework):
    """Get appropriate serving container image"""
    images = {
        "scikit-learn": "us-docker.pkg.dev/vertex-ai/prediction/scikit-learn-cpu.1-0:latest",
        "tensorflow": "us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.11:latest",
        "pytorch": "us-docker.pkg.dev/vertex-ai/prediction/pytorch-cpu.1-13:latest"
    }
    return images.get(framework, images["scikit-learn"])

def create_endpoint(display_name="iris-prediction-endpoint"):
    """Create Vertex AI Endpoint"""
    print(f"\n🔗 Creating endpoint...")
    
    try:
        endpoint = aiplatform.Endpoint.create(
            display_name=display_name,
            project=PROJECT_ID,
            location=REGION
        )
        
        print(f"✅ Endpoint created successfully!")
        print(f"   Endpoint ID: {endpoint.resource_name}")
        
        return endpoint
        
    except Exception as e:
        print(f"❌ Error creating endpoint: {e}")
        return None

def deploy_model_to_endpoint(model, endpoint, traffic_percentage=100):
    """Deploy model to endpoint"""
    print(f"\n🚀 Deploying model to endpoint...")
    
    try:
        endpoint.deploy(
            model=model,
            deployed_model_display_name=model.display_name,
            machine_type="n1-standard-2",
            min_replica_count=1,
            max_replica_count=3,
            traffic_percentage=traffic_percentage
        )
        
        print(f"✅ Model deployed successfully!")
        print(f"   Endpoint: {endpoint.resource_name}")
        print(f"   Prediction URL: {endpoint.predict_request_response_logging_opt_out is False}")
        
        return endpoint
        
    except Exception as e:
        print(f"❌ Error deploying model: {e}")
        return None

def list_endpoints():
    """List all prediction endpoints"""
    print(f"\n📋 Available Endpoints:\n")
    
    endpoints = aiplatform.Endpoint.list(
        order_by="create_time desc"
    )
    
    count = 0
    for endpoint in endpoints:
        print(f"Name: {endpoint.display_name}")
        print(f"ID: {endpoint.resource_name.split('/')[-1]}")
        print(f"Created: {endpoint.create_time}")
        print(f"Deployed Models: {len(endpoint.list_models()) if hasattr(endpoint, 'list_models') else 'Unknown'}")
        print()
        count += 1
    
    if count == 0:
        print("No endpoints found")

def test_endpoint(endpoint, test_data):
    """Test endpoint with sample data"""
    print(f"\n🧪 Testing endpoint predictions...")
    
    try:
        # Use online prediction
        response = endpoint.predict(instances=[test_data])
        
        print(f"✅ Prediction successful!")
        print(f"   Response: {response}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return None

def undeploy_model(endpoint, deployed_model_id):
    """Undeploy a model from endpoint"""
    print(f"\n🛑 Undeploying model...")
    
    try:
        endpoint.undeploy(deployed_model_id=deployed_model_id)
        print(f"✅ Model undeployed successfully!")
    except Exception as e:
        print(f"❌ Error undeploying model: {e}")

def main():
    parser = argparse.ArgumentParser(description="Deploy Models to Vertex AI Endpoints")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Upload model command
    upload_parser = subparsers.add_parser("upload", help="Upload model to registry")
    upload_parser.add_argument("--model-path", required=True, help="GCS path to model")
    upload_parser.add_argument("--framework", choices=["scikit-learn", "tensorflow", "pytorch"], 
                              default="scikit-learn", help="ML framework")
    upload_parser.add_argument("--version", default="v1", help="Model version")
    
    # Create endpoint command
    subparsers.add_parser("endpoint", help="Create prediction endpoint")
    
    # List endpoints command
    subparsers.add_parser("list", help="List prediction endpoints")
    
    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy model to endpoint")
    deploy_parser.add_argument("--model-id", required=True, help="Vertex AI Model ID")
    deploy_parser.add_argument("--endpoint-id", required=True, help="Vertex AI Endpoint ID")
    
    args = parser.parse_args()
    
    if args.command == "upload":
        upload_model(
            model_path=args.model_path,
            framework=args.framework,
            version=args.version
        )
    
    elif args.command == "endpoint":
        create_endpoint()
    
    elif args.command == "list":
        list_endpoints()
    
    elif args.command == "deploy":
        print(f"Deploy command - would fetch model {args.model_id} and endpoint {args.endpoint_id}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
