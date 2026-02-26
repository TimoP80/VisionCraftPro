# Salad Cloud Deployment Guide

## 🥬 Quick Deploy with Pre-built Image

### 📦 Available Docker Images

#### **GPU Version (Recommended for RTX 4090)**
```
timop80/visioncraft-pro:gpu-latest
```

#### **CPU Version**
```
timop80/visioncraft-pro:latest
```

---

## 🚀 Salad Cloud Deployment Steps

### Step 1: Create Container Group

1. **Go to Salad Cloud Dashboard**
2. **Click "Create Container Group"**
3. **Choose "Docker Image" as source**

### Step 2: Configure Container

#### **GPU Configuration (RTX 4090)**
```yaml
Image: timop80/visioncraft-pro:gpu-latest
GPU: RTX 4090 (24GB)
RAM: 16GB
Storage: 100GB
Ports: 8000
```

#### **CPU Configuration**
```yaml
Image: timop80/visioncraft-pro:latest
CPU: 8 vCPUs
RAM: 16GB
Storage: 50GB
Ports: 8000
```

### Step 3: Environment Variables

Add these environment variables:

#### **Required for GPU:**
```
CUDA_VISIBLE_DEVICES=0
PYTHONUNBUFFERED=1
```

#### **Optional:**
```
HF_TOKEN=your_huggingface_token_here
```

### Step 4: Volume Mounts (Optional)

For persistent storage, add volume mounts:

```yaml
/models: /app/models
/uploads: /app/static/uploads
```

### Step 5: Health Check

Add health check for monitoring:

```yaml
Health Check: HTTP GET /status
Interval: 30 seconds
Timeout: 10 seconds
Retries: 3
```

---

## 🔧 Container Group YAML Template

### **GPU Version (Copy-Paste Ready)**
```yaml
name: visioncraft-pro-gpu
image: timop80/visioncraft-pro:gpu-latest
ports:
  - "8000:8000"
resources:
  gpu:
    type: rtx4090
    count: 1
  cpu:
    cores: 8
  memory: 16GB
  storage: 100GB
environment:
  - CUDA_VISIBLE_DEVICES=0
  - PYTHONUNBUFFERED=1
health_check:
  path: /status
  interval: 30
  timeout: 10
  retries: 3
volumes:
  - name: models
    path: /app/models
    size: 50GB
  - name: uploads
    path: /app/static/uploads
    size: 10GB
```

### **CPU Version (Copy-Paste Ready)**
```yaml
name: visioncraft-pro-cpu
image: timop80/visioncraft-pro:latest
ports:
  - "8000:8000"
resources:
  cpu:
    cores: 8
  memory: 16GB
  storage: 50GB
environment:
  - PYTHONUNBUFFERED=1
health_check:
  path: /status
  interval: 30
  timeout: 10
  retries: 3
volumes:
  - name: models
    path: /app/models
    size: 50GB
  - name: uploads
    path: /app/static/uploads
    size: 10GB
```

---

## 🎯 Deployment Instructions

### **Method 1: Salad Cloud Dashboard (Easiest)**

1. **Login to Salad Cloud**
2. **Navigate to Container Groups**
3. **Click "Create Container Group"**
4. **Choose "Docker Image"**
5. **Enter image name:** `timop80/visioncraft-pro:gpu-latest`
6. **Configure resources** (see templates above)
7. **Add environment variables**
8. **Set up health check**
9. **Click "Deploy"**

### **Method 2: Salad CLI**

```bash
# Install Salad CLI
pip install salad-cloud

# Login
salad login

# Deploy GPU version
salad container create \
  --name visioncraft-pro-gpu \
  --image timop80/visioncraft-pro:gpu-latest \
  --gpu-type rtx4090 \
  --gpu-count 1 \
  --cpu-cores 8 \
  --memory 16GB \
  --storage 100GB \
  --port 8000 \
  --env CUDA_VISIBLE_DEVICES=0 \
  --env PYTHONUNBUFFERED=1
```

---

## 🔍 Post-Deployment Verification

### **Check Container Status**
```bash
# Access your container
curl http://your-salad-url:8000/status

# Should return:
{
  "device": "GPU",
  "model_loaded": false,
  "current_model": null,
  "gpu_name": "NVIDIA RTX 4090"
}
```

### **Test Image Generation**
1. **Open:** `http://your-salad-url:8000`
2. **Select:** Leonardo.ai or Modal (cloud generators)
3. **Enter prompt:** "A majestic dragon on crystal mountain"
4. **Click Generate**
5. **Expected time:** 2-15 seconds

---

## 📊 Performance Expectations

### **RTX 4090 Performance**
| Model | Resolution | Time | VRAM Usage |
|-------|-------------|-------|-------------|
| SD 1.5 | 512x512 | 2-4s | 2-4GB |
| SDXL | 1024x1024 | 6-12s | 6-8GB |
| FLUX | 1024x1024 | 8-15s | 8-12GB |

### **CPU Performance (8 vCPUs)**
| Model | Resolution | Time | RAM Usage |
|-------|-------------|-------|-----------|
| SD 1.5 | 512x512 | 45-90s | 2-4GB |
| SDXL | 1024x1024 | 3-8m | 6-12GB |

---

## 🔧 Configuration Tips

### **GPU Optimization**
```yaml
# Best performance settings
resources:
  gpu:
    type: rtx4090
    count: 1
  cpu:
    cores: 4  # More CPU doesn't help much
  memory: 16GB  # RTX 4090 has 24GB VRAM
```

### **Cost Optimization**
```yaml
# For development/testing
resources:
  gpu:
    type: rtx3060  # Cheaper option
    count: 1
  cpu:
    cores: 4
  memory: 8GB
```

### **Storage Optimization**
```yaml
# Separate volumes for different purposes
volumes:
  - name: models
    path: /app/models
    size: 50GB    # Model storage
  - name: uploads
    path: /app/static/uploads
    size: 10GB    # Generated images
```

---

## 🚨 Troubleshooting

### **Common Issues**

#### **Container Won't Start**
- **Check image name:** `timop80/visioncraft-pro:gpu-latest`
- **Verify GPU availability:** RTX 4090 might be sold out
- **Check resource limits:** Ensure enough RAM/storage

#### **Permission Errors**
- **Pre-built image** should have proper permissions
- **Check volume mounts** if using custom volumes
- **Verify environment variables**

#### **Performance Issues**
- **Check GPU type:** Ensure RTX 4090 is selected
- **Monitor VRAM usage:** Don't exceed 24GB
- **Adjust batch size:** Use smaller batches if OOM

---

## 📞 Support

### **Salad Cloud Documentation**
- [Salad Cloud Docs](https://docs.salad.cloud/)
- [Container Groups Guide](https://docs.salad.cloud/container-groups)

### **VisionCraft Pro Support**
- [GitHub Issues](https://github.com/TimoP80/VisionCraftPro/issues)
- [Discord Community](https://discord.gg/visioncraft)

---

## 🎯 Quick Start Summary

1. **Image:** `timop80/visioncraft-pro:gpu-latest`
2. **GPU:** RTX 4090
3. **RAM:** 16GB
4. **Storage:** 100GB
5. **Ports:** 8000
6. **Environment:** `CUDA_VISIBLE_DEVICES=0`
7. **Deploy!** 🚀

Your VisionCraft Pro instance should be running on Salad Cloud in minutes!
