#!/bin/bash

# Build and Push Docker Images to Docker Hub
# Run this script locally to build and push images for Salad Cloud

set -e

echo "🐳 Building VisionCraft Pro Docker images..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if logged in to Docker Hub
if ! docker info | grep -q "Username"; then
    echo "🔐 Please login to Docker Hub first:"
    echo "docker login"
    echo "Enter your Docker Hub username and password"
    read -p "Press Enter after logging in..."
fi

# Build CPU image
echo "🔨 Building CPU image..."
docker build -f Dockerfile -t timop80/visioncraft-pro:latest .
docker tag timop80/visioncraft-pro:latest timop80/visioncraft-pro:cpu-latest

# Build GPU image
echo "🚀 Building GPU image..."
docker build -f Dockerfile.gpu -t timop80/visioncraft-pro:gpu-latest .
docker tag timop80/visioncraft-pro:gpu-latest timop80/visioncraft-pro:rtx4090

# Push images
echo "📤 Pushing images to Docker Hub..."

echo "Pushing CPU image..."
docker push timop80/visioncraft-pro:latest
docker push timop80/visioncraft-pro:cpu-latest

echo "Pushing GPU image..."
docker push timop80/visioncraft-pro:gpu-latest
docker push timop80/visioncraft-pro:rtx4090

echo "✅ All images built and pushed successfully!"
echo ""
echo "🥬 Salad Cloud ready images:"
echo "CPU: timop80/visioncraft-pro:latest"
echo "GPU: timop80/visioncraft-pro:gpu-latest"
echo ""
echo "📋 Use these images in Salad Cloud dashboard"
