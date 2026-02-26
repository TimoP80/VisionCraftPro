#!/bin/bash

# VisionCraft Pro Docker Deployment Script

set -e

echo "🚀 Starting VisionCraft Pro Docker Deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories with proper permissions
echo "📁 Creating directories..."
mkdir -p models/local
mkdir -p static/uploads
mkdir -p models/cache

# Set proper permissions for Docker volumes
chmod 777 models/local
chmod 777 static/uploads
chmod 777 models/cache

# Ensure keys.txt has proper permissions
if [ -f "keys.txt" ]; then
    chmod 644 keys.txt
    echo "✅ Set permissions for keys.txt"
else
    echo "⚠️  keys.txt not found - please create it with your HF_TOKEN"
fi

# Build and start the container
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting VisionCraft Pro container..."
docker-compose up -d

echo "✅ VisionCraft Pro is now running!"
echo "🌐 Access it at: http://localhost:8000"
echo "📊 Check logs with: docker-compose logs -f visioncraft"
echo "🛑 Stop with: docker-compose down"
