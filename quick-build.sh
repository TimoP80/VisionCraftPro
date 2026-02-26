#!/bin/bash

# Quick build and push to Docker Hub
# Run this locally to get images working immediately

set -e

echo "🐳 Quick Build for Docker Hub"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Login to Docker Hub
echo "🔐 Logging in to Docker Hub..."
docker login

# Build and push Salad Cloud GPU image
echo "🔨 Building Salad Cloud GPU image..."
docker build -f Dockerfile.salad -t timop80/visioncraft-pro:salad-gpu .
docker tag timop80/visioncraft-pro:salad-gpu timop80/visioncraft-pro:salad-latest

echo "📤 Pushing to Docker Hub..."
docker push timop80/visioncraft-pro:salad-gpu
docker push timop80/visioncraft-pro:salad-latest

# Build and push Salad Cloud CPU image
echo "🔨 Building Salad Cloud CPU image..."
docker build -f Dockerfile.salad-cpu -t timop80/visioncraft-pro:salad-cpu .

echo "📤 Pushing to Docker Hub..."
docker push timop80/visioncraft-pro:salad-cpu

echo "✅ Images pushed to Docker Hub!"
echo ""
echo "🥬 Use this in Salad Cloud:"
echo "Registry: Public Registry"
echo "Image: timop80/visioncraft-pro:salad-gpu"
echo ""
echo "🔍 Verify with:"
echo "docker pull timop80/visioncraft-pro:salad-gpu"
