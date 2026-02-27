#!/bin/bash

# Build and push VisionCraft Pro to Docker Hub
set -e

echo "🐳 Building VisionCraft Pro for Docker Hub..."

# Check if we're logged in
if ! docker info | grep -q "Username"; then
    echo "🔐 Please login to Docker Hub first:"
    echo "docker login"
    read -p "Press Enter after logging in..."
fi

# Build the Salad Cloud GPU image
echo "🔨 Building Salad Cloud GPU image..."
docker build -f Dockerfile.salad -t timop80/visioncraft-pro:salad-gpu .

# Verify image exists
echo "📋 Checking if image was built..."
docker images | grep visioncraft-pro

# Push to Docker Hub
echo "📤 Pushing to Docker Hub..."
docker push timop80/visioncraft-pro:salad-gpu

# Also push with latest tag
echo "🏷️  Tagging as latest..."
docker tag timop80/visioncraft-pro:salad-gpu timop80/visioncraft-pro:latest
docker push timop80/visioncraft-pro:latest

echo "✅ Success! Images pushed to Docker Hub:"
echo "   - timop80/visioncraft-pro:salad-gpu"
echo "   - timop80/visioncraft-pro:latest"
echo ""
echo "🥬 Use this in Salad Cloud:"
echo "   Registry: Public Registry"
echo "   Image: timop80/visioncraft-pro:salad-gpu"
