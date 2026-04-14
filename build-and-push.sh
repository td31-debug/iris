#!/bin/bash
# Build and push Iris Classifier to Azure Container Registry

REGISTRY_NAME="${1:-2f596df8a623474cb48335e39273f387}"
IMAGE_NAME="${2:-iris-classifier}"
IMAGE_TAG="${3:-latest}"

ACR_LOGIN_SERVER="$REGISTRY_NAME.azurecr.io"
FULL_IMAGE_NAME="$ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG"

echo "🐳 Building and pushing Iris Classifier Docker image..."
echo "   Registry: $REGISTRY_NAME"
echo "   Image: $FULL_IMAGE_NAME"
echo ""

# Step 1: Build image
echo "1️⃣  Building Docker image..."
docker build -t $IMAGE_NAME .
if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi
echo "✅ Build complete"

# Step 2: Login to ACR
echo ""
echo "2️⃣  Logging in to Azure Container Registry..."
az acr login --name $REGISTRY_NAME
if [ $? -ne 0 ]; then
    echo "❌ ACR login failed"
    exit 1
fi
echo "✅ Login successful"

# Step 3: Tag image
echo ""
echo "3️⃣  Tagging image..."
docker tag $IMAGE_NAME $FULL_IMAGE_NAME
echo "✅ Tagged as $FULL_IMAGE_NAME"

# Step 4: Push to ACR
echo ""
echo "4️⃣  Pushing to Azure Container Registry..."
docker push $FULL_IMAGE_NAME
if [ $? -ne 0 ]; then
    echo "❌ Docker push failed"
    exit 1
fi
echo "✅ Push complete"

echo ""
echo "✅ SUCCESS! Image available at:"
echo "   $FULL_IMAGE_NAME"
