# Docker Registry Guide for Salad Cloud

## 🐳 Registry Options for Salad Cloud

Salad Cloud supports multiple container registries. Here are your options:

---

## 🎯 **Option 1: GitHub Container Registry (Recommended)**

### **Why GitHub Container Registry:**
- ✅ **Free and unlimited** for public repositories
- ✅ **No setup required** - works with your GitHub account
- ✅ **Automatic builds** via GitHub Actions
- ✅ **Secure and reliable**

### **Available Images:**
```
ghcr.io/timop80/visioncraft-pro:salad-gpu
ghcr.io/timop80/visioncraft-pro:salad-cpu
ghcr.io/timop80/visioncraft-pro:latest
ghcr.io/timop80/visioncraft-pro:gpu-latest
```

### **How to Use in Salad Cloud:**
1. **Select "Private Registry"**
2. **Registry:** `ghcr.io`
3. **Image:** `timop80/visioncraft-pro:salad-gpu`
4. **No authentication required** (public repository)

---

## 🎯 **Option 2: Docker Hub**

### **Available Images:**
```
timop80/visioncraft-pro:salad-gpu
timop80/visioncraft-pro:salad-cpu
timop80/visioncraft-pro:latest
timop80/visioncraft-pro:gpu-latest
```

### **How to Use in Salad Cloud:**
1. **Select "Public Registry"**
2. **Registry:** `docker.io` (default)
3. **Image:** `timop80/visioncraft-pro:salad-gpu`

---

## 🎯 **Option 3: Build and Push Manually**

### **If Images Aren't Available Yet:**

#### **Step 1: Start Docker Desktop**
Make sure Docker Desktop is running on your machine.

#### **Step 2: Build Images Locally**
```bash
# Build Salad Cloud GPU image
docker build -f Dockerfile.salad -t timop80/visioncraft-pro:salad-gpu .

# Build Salad Cloud CPU image
docker build -f Dockerfile.salad-cpu -t timop80/visioncraft-pro:salad-cpu .
```

#### **Step 3: Push to Registry**

**For Docker Hub:**
```bash
# Login to Docker Hub
docker login

# Push images
docker push timop80/visioncraft-pro:salad-gpu
docker push timop80/visioncraft-pro:salad-cpu
```

**For GitHub Container Registry:**
```bash
# Login to GitHub Container Registry
docker login ghcr.io -u your-username -p your-github-token

# Tag for GitHub Container Registry
docker tag timop80/visioncraft-pro:salad-gpu ghcr.io/timop80/visioncraft-pro:salad-gpu
docker tag timop80/visioncraft-pro:salad-cpu ghcr.io/timop80/visioncraft-pro:salad-cpu

# Push images
docker push ghcr.io/timop80/visioncraft-pro:salad-gpu
docker push ghcr.io/timop80/visioncraft-pro:salad-cpu
```

---

## 🚀 **Quick Deployment Steps**

### **Step 1: Choose Your Registry**

#### **Easiest - GitHub Container Registry:**
- **Registry Type:** Private Registry
- **Registry URL:** `ghcr.io`
- **Image:** `timop80/visioncraft-pro:salad-gpu`
- **No authentication needed**

#### **Alternative - Docker Hub:**
- **Registry Type:** Public Registry
- **Registry URL:** `docker.io` (default)
- **Image:** `timop80/visioncraft-pro:salad-gpu`
- **No authentication needed**

### **Step 2: Configure Salad Cloud**

```yaml
name: visioncraft-pro-gpu
image: ghcr.io/timop80/visioncraft-pro:salad-gpu  # or timop80/visioncraft-pro:salad-gpu
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
```

---

## 🔧 **Troubleshooting Registry Issues**

### **"Image Not Found" Error**
**Cause:** Images haven't been built/pushed yet
**Solution:** 
1. Check if images exist: `docker pull ghcr.io/timop80/visioncraft-pro:salad-gpu`
2. If not found, build manually (see Option 3)

### **"Access Denied" Error**
**Cause:** Registry authentication issues
**Solution:**
1. **For GitHub Container Registry:** Make sure repository is public
2. **For Docker Hub:** Make sure images are public
3. **Use public registry option** (no authentication)

### **"Pull Timeout" Error**
**Cause:** Network issues or large image size
**Solution:**
1. **Try different registry** (GitHub vs Docker Hub)
2. **Check network connection**
3. **Wait for images to fully upload**

---

## 📋 **Registry Comparison**

| Registry | Cost | Setup | Authentication | Image Size |
|----------|------|-------|----------------|------------|
| GitHub Container Registry | Free | None | None (public) | Unlimited |
| Docker Hub | Free | None | None (public) | Unlimited |
| AWS ECR | Pay | Required | Required | Unlimited |
| Google Container Registry | Pay | Required | Required | Unlimited |

---

## 🎯 **Recommended Approach**

### **For Immediate Deployment:**
1. **Try GitHub Container Registry first:** `ghcr.io/timop80/visioncraft-pro:salad-gpu`
2. **If not available, try Docker Hub:** `timop80/visioncraft-pro:salad-gpu`
3. **If neither works, build manually** (Option 3)

### **For Long-term:**
1. **Use GitHub Container Registry** (most reliable)
2. **Set up automatic builds** via GitHub Actions
3. **Monitor build status** in GitHub Actions tab

---

## 🔄 **Automatic Builds**

The GitHub Actions workflow will automatically:
1. **Build all Docker images** on every push to main
2. **Push to GitHub Container Registry**
3. **Update image tags** automatically

**To trigger builds:**
1. **Push any change** to the main branch
2. **Or manually trigger** in GitHub Actions tab

---

## ✅ **Verification**

### **Check if Images Exist:**
```bash
# GitHub Container Registry
docker pull ghcr.io/timop80/visioncraft-pro:salad-gpu

# Docker Hub
docker pull timop80/visioncraft-pro:salad-gpu
```

### **Test Locally:**
```bash
# Run the image
docker run -p 8000:8000 ghcr.io/timop80/visioncraft-pro:salad-gpu

# Test the service
curl http://localhost:8000/status
```

Once you can pull the images successfully, they're ready for Salad Cloud deployment!
