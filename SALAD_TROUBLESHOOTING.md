# Salad Cloud Deployment Troubleshooting

## 🚫 "Access Denied, Check Permissions" Error

### Root Causes & Solutions

#### 1. **File Permissions in Container**
The container needs proper permissions to write to mounted directories.

**Solution:** Use the updated Dockerfile with non-root user:
```bash
# Rebuild with updated Dockerfile
docker-compose -f docker-compose.gpu.yml down
docker-compose -f docker-compose.gpu.yml build --no-cache
docker-compose -f docker-compose.gpu.yml up -d
```

#### 2. **Volume Mount Permissions**
Host directories might not have proper permissions.

**Solution:** Fix host directory permissions:
```bash
# On your local machine before deploying
chmod 777 models/local
chmod 777 static/uploads
chmod 777 models/cache
chmod 644 keys.txt
```

#### 3. **Salad Cloud Container Runtime Issues**
Salad Cloud might have specific runtime restrictions.

**Solution:** Use Salad-specific configuration:
```yaml
# In docker-compose.gpu.yml, add:
user: "1000:1000"
security_opt:
  - no-new-privileges:true
```

#### 4. **Docker Hub Image Permissions**
If using pre-built images, they might have restrictive permissions.

**Solution:** Build from source:
```bash
# Always build from source on Salad Cloud
docker-compose -f docker-compose.gpu.yml build --no-cache
docker-compose -f docker-compose.gpu.yml up -d
```

## 🔧 Complete Fix Process

### Step 1: Update Local Files
```bash
# Pull latest changes
git pull origin main

# Fix local permissions
chmod 777 models/local static/uploads models/cache
chmod 644 keys.txt
```

### Step 2: Clean Build
```bash
# Stop existing containers
docker-compose -f docker-compose.gpu.yml down

# Clean build cache
docker system prune -f

# Rebuild from scratch
docker-compose -f docker-compose.gpu.yml build --no-cache
```

### Step 3: Deploy with Correct Permissions
```bash
# Deploy with GPU support
docker-compose -f docker-compose.gpu.yml up -d

# Check logs for permission errors
docker-compose -f docker-compose.gpu.yml logs -f visioncraft
```

## 🐛 Other Salad Cloud Issues

### GPU Not Available
```bash
# Check if GPU runtime is available
docker run --rm --gpus all nvidia/cuda-base-ubuntu22.04 nvidia-smi

# If not available, use CPU version
docker-compose up -d --build
```

### Port Binding Issues
```bash
# Use different port if 8000 is blocked
# Edit docker-compose.gpu.yml:
ports:
  - "8080:8000"  # Use port 8080 instead
```

### Memory Issues
```bash
# Increase memory limits in docker-compose.gpu.yml
deploy:
  resources:
    limits:
      memory: 16G
    reservations:
      memory: 8G
```

## 📊 Salad Cloud Specific Settings

### Container Group Configuration
```yaml
# Recommended Salad Cloud settings:
Image: visioncraft-pro:gpu
GPU: RTX 4090 (24GB)
RAM: 16GB
Storage: 100GB
Ports: 8000
Environment: CUDA_VISIBLE_DEVICES=0
```

### Health Check Configuration
```yaml
# Salad Cloud requires working health checks
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/status"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## 🚀 Quick Deployment Script for Salad Cloud

```bash
#!/bin/bash
# Salad Cloud Deployment Script

echo "🥬 Deploying to Salad Cloud..."

# Fix permissions first
chmod 777 models/local static/uploads models/cache
chmod 644 keys.txt

# Clean and rebuild
docker-compose -f docker-compose.gpu.yml down
docker system prune -f

# Build and deploy
docker-compose -f docker-compose.gpu.yml build --no-cache
docker-compose -f docker-compose.gpu.yml up -d

echo "✅ Deployed to Salad Cloud!"
echo "🌐 Check logs: docker-compose -f docker-compose.gpu.yml logs -f"
```

## 🔍 Debugging Commands

### Check Container Status
```bash
# Container status
docker-compose -f docker-compose.gpu.yml ps

# Container logs
docker-compose -f docker-compose.gpu.yml logs visioncraft

# Live logs
docker-compose -f docker-compose.gpu.yml logs -f visioncraft
```

### Test Container Health
```bash
# Test health endpoint
curl http://localhost:8000/status

# Test API
curl http://localhost:8000/models

# Check GPU access
docker exec visioncraft-pro-gpu nvidia-smi
```

### File System Debug
```bash
# Check mounted directories
docker exec visioncraft-pro-gpu ls -la /app/models
docker exec visioncraft-pro-gpu ls -la /app/static/uploads

# Test file creation
docker exec visioncraft-pro-gpu touch /app/models/test.txt
docker exec visioncraft-pro-gpu ls -la /app/models/
```

## 📞 Getting Help

### Salad Cloud Support
- Check Salad Cloud documentation for container runtime restrictions
- Review container group logs in Salad Cloud dashboard
- Contact Salad Cloud support with container logs

### Common Solutions
1. **Always build from source** on Salad Cloud
2. **Use non-root user** in Dockerfile
3. **Set proper permissions** on host directories
4. **Check resource limits** (GPU, RAM, storage)
5. **Monitor health checks** and container logs

The updated Dockerfile with non-root user and proper permissions should resolve most "Access Denied" issues on Salad Cloud.
