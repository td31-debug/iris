#!/usr/bin/env pwsh
# Build and push Iris Classifier to Azure Container Registry

param(
    [string]$RegistryName = "2f596df8a623474cb48335e39273f387",
    [string]$ImageName = "iris-classifier",
    [string]$ImageTag = "latest"
)

$AcrLoginServer = "$RegistryName.azurecr.io"
$FullImageName = "$AcrLoginServer/$ImageName`:$ImageTag"

Write-Host "🐳 Building and pushing Iris Classifier Docker image..." -ForegroundColor Cyan
Write-Host "   Registry: $RegistryName"
Write-Host "   Image: $FullImageName"
Write-Host ""

# Step 1: Build image
Write-Host "1️⃣  Building Docker image..." -ForegroundColor Yellow
docker build -t $ImageName .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Build complete" -ForegroundColor Green

# Step 2: Login to ACR
Write-Host ""
Write-Host "2️⃣  Logging in to Azure Container Registry..." -ForegroundColor Yellow
az acr login --name $RegistryName
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ACR login failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Login successful" -ForegroundColor Green

# Step 3: Tag image
Write-Host ""
Write-Host "3️⃣  Tagging image..." -ForegroundColor Yellow
docker tag $ImageName $FullImageName
Write-Host "✅ Tagged as $FullImageName" -ForegroundColor Green

# Step 4: Push to ACR
Write-Host ""
Write-Host "4️⃣  Pushing to Azure Container Registry..." -ForegroundColor Yellow
docker push $FullImageName
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker push failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Push complete" -ForegroundColor Green

Write-Host ""
Write-Host "✅ SUCCESS! Image available at:" -ForegroundColor Green
Write-Host "   $FullImageName" -ForegroundColor Cyan
