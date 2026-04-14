#!/bin/bash

# Setup IAM permissions for Jenkins Vertex AI Service Account
# This script grants necessary roles to jenkins-vertex-sa@mlops-493014.iam.gserviceaccount.com

set -e

PROJECT_ID="mlops-493014"
SERVICE_ACCOUNT="jenkins-vertex-sa"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "🔐 Setting up IAM permissions for Vertex AI service account..."
echo "Service Account: $SERVICE_ACCOUNT_EMAIL"
echo "Project: $PROJECT_ID"
echo ""

# Grant Storage Admin
echo "📦 Granting storage.admin role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/storage.admin" \
  --quiet || echo "⚠️  Storage Admin already assigned or error occurred"

# Grant Vertex AI Admin
echo "🤖 Granting aiplatform.admin role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/aiplatform.admin" \
  --quiet || echo "⚠️  Vertex AI Admin already assigned or error occurred"

# Grant Service Account User
echo "👤 Granting iam.serviceAccountUser role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/iam.serviceAccountUser" \
  --quiet || echo "⚠️  Service Account User already assigned or error occurred"

# Grant Compute Admin (for running training jobs)
echo "💻 Granting compute.admin role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/compute.admin" \
  --quiet || echo "⚠️  Compute Admin already assigned or error occurred"

echo ""
echo "✅ IAM permissions setup complete!"
echo ""
echo "Verifying permissions..."
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:${SERVICE_ACCOUNT_EMAIL}" \
  --format="table(bindings.role)" | grep -E "aiplatform|storage|compute|iam"

echo ""
echo "🎉 Ready to run Vertex AI training jobs!"
