# VisionCraft Pro Docker Deployment

## 🐳 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- For GPU support: NVIDIA Docker runtime installed

### CPU-Only Deployment
```bash
# Clone the repository
git clone <repository-url>
cd VisionCraftPro

# Deploy
chmod +x deploy.sh
./deploy.sh
```

### GPU Deployment (RTX 4090)
```bash
# Use GPU-enabled compose file
docker-compose -f docker-compose.gpu.yml up -d --build
```

## 📦 Available Images

### Option 1: Build from Source (Recommended)
```bash
# CPU-only
docker-compose up -d --build

# GPU-enabled
docker-compose -f docker-compose.gpu.yml up -d --build
```

### Option 2: Use Pre-built Image
```bash
# Pull from Docker Hub (if available)
docker pull timop80/visioncraft-pro:latest
docker run -p 8000:8000 timop80/visioncraft-pro:latest
```

## 🔧 Configuration

### Environment Variables
- `HF_TOKEN`: Hugging Face token for model downloads
- `CUDA_VISIBLE_DEVICES`: GPU device selection

### Volume Mounts
- `./models`: Persistent model storage
- `./static/uploads`: Generated images storage
- `./keys.txt`: API keys and tokens

## 🚀 Deployment Options

### 1. Local Development
```bash
# Build and run locally
docker-compose up -d --build
```

### 2. Cloud Deployment

#### Docker Hub
```bash
# Push to Docker Hub
docker build -t timop80/visioncraft-pro:latest .
docker push timop80/visioncraft-pro:latest

# Pull and run on cloud
docker run -d -p 8000:8000 timop80/visioncraft-pro:latest
```

#### Salad Cloud (GPU)
```bash
# Use GPU-enabled image
docker-compose -f docker-compose.gpu.yml up -d --build

# Or use pre-built image
docker run --gpus all -d -p 8000:8000 timop80/visioncraft-pro:latest
```

#### DigitalOcean
```bash
# Create droplet with GPU support
docker-machine create -d digitalocean --digitalocean-access-token $TOKEN \
    --digitalocean-size s-4vcpu-8gb --digitalocean-image docker-20-04 \
    visioncraft-gpu

# Deploy
docker-compose -f docker-compose.gpu.yml up -d --build
```

## 📊 Performance

### CPU vs GPU Performance
| Model | CPU (8 vCPUs) | GPU (RTX 4090) |
|-------|----------------|----------------|
| SD 1.5 (512x512) | 45-90s | 2-4s |
| SDXL (1024x1024) | 3-8m | 6-12s |
| FLUX | 8-15m | 8-15s |

## 🔍 Monitoring

### Check Container Status
```bash
# View logs
docker-compose logs -f visioncraft

# Check health
curl http://localhost:8000/status
```

### Resource Monitoring
```bash
# View resource usage
docker stats visioncraft-pro

# GPU monitoring (NVIDIA)
nvidia-smi
```

## 🛠️ Troubleshooting

### Common Issues

#### Out of Memory (OOM)
```bash
# Increase container memory limit
docker-compose -f docker-compose.yml up -d --memory 16g
```

#### GPU Not Detected
```bash
# Check NVIDIA runtime
docker run --rm --gpus all nvidia/cuda-base-ubuntu22.04 nvidia-smi

# Install NVIDIA Docker runtime
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
distribution=$(lsb_release -is)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

#### Port Conflicts
```bash
# Change port in docker-compose.yml
ports:
  - "8080:8000"  # Use different port
```

## 🔄 Updates

### Update Application
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Update Dependencies
```bash
# Rebuild with new requirements
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📚 API Documentation

Once deployed, the API is available at:
- **Main UI:** `http://localhost:8000`
- **API Docs:** `http://localhost:8000/docs`
- **Status:** `http://localhost:8000/status`

## 🔒 Security

### Production Considerations
- Use HTTPS in production
- Restrict API access with authentication
- Monitor logs for suspicious activity
- Regular security updates

### Environment Variables
```bash
# Set secure HF_TOKEN
echo "HF_TOKEN=your_token_here" >> keys.txt
```

## 📝 License

This Docker setup is for VisionCraft Pro deployment. Please ensure you have appropriate licenses for all models and services used.
