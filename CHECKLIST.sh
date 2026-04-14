#!/bin/bash
# Quick checklist for completing the Vertex AI + Jenkins setup

echo "════════════════════════════════════════════════════════════"
echo "Vertex AI MLOps Project - Setup Checklist"
echo "════════════════════════════════════════════════════════════"
echo ""

STATUS="✅ COMPLETED"
TODO="❌ TODO (Run from Windows with gcloud)"
BLOCKED="⏸️ BLOCKED (Need permissions)"

echo "$STATUS Step 1: Created service account key"
echo "         File: gcp-key.json"
echo "         Service Account: jenkins-vertex-sa@mlops-493014.iam.gserviceaccount.com"
echo ""

echo "$STATUS Step 2: Created training script"
echo "         File: src/vertex_train.py"
echo "         Framework: Scikit-learn"
echo ""

echo "$STATUS Step 3: Secured credentials"
echo "         Added gcp-key.json to .gitignore"
echo ""

echo "$BLOCKED Step 4: Grant IAM Permissions (REQUIRED)"
echo "         Location: Your Windows machine"
echo "         Command: See SETUP_GUIDE.md"
echo "         Roles needed:"
echo "           - Storage Admin"
echo "           - Vertex AI Administrator" 
echo "           - Compute Administrator"
echo "           - Service Account User"
echo ""

echo "$TODO Step 5: Test training script (After Step 4)"
echo "         Command: export GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json"
echo "                  python src/vertex_train.py"
echo ""

echo "$TODO Step 6: Create Jenkinsfile"
echo "         Location: root/Jenkinsfile"
echo "         Trigger: Manual or SCM webhook"
echo ""

echo "$TODO Step 7: Add TensorFlow/Keras support"
echo "         File: src/vertex_train_tensorflow.py"
echo ""

echo "$TODO Step 8: Add PyTorch support"
echo "         File: src/vertex_train_pytorch.py"
echo ""

echo "$TODO Step 9: Create Vertex AI Pipelines"
echo "         File: pipelines/training_pipeline.yaml"
echo ""

echo "$TODO Step 10: Setup Jenkins integration"
echo "         Jenkins job → GCP Service Account Credentials"
echo "         Trigger model training on-demand or scheduled"
echo ""

echo "════════════════════════════════════════════════════════════"
echo ""
echo "📋 Next Action Required:"
echo ""
echo "Run these commands on your WINDOWS machine:"
echo ""
echo "  1. Open PowerShell"
echo "  2. Run: gcloud auth login"
echo "  3. Then copy-paste the commands from SETUP_GUIDE.md"
echo ""
echo "After that, the training script will work!"
echo ""
echo "════════════════════════════════════════════════════════════"
