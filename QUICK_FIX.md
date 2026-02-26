# Quick Fix for Salad Cloud Authentication

## 🚨 Problem: "Auth Required" Error

This happens when:
1. GitHub Container Registry images aren't public yet
2. GitHub Actions workflow hasn't run
3. Repository is private

---

## 🚀 **Immediate Solution: Use Docker Hub**

### **Step 1: Update Salad Cloud Configuration**
```
Registry Type: Public Registry
Registry URL: docker.io (or leave blank)
Image: timop80/visioncraft-pro:salad-gpu
```

### **Step 2: Test the Image**
```bash
# Test if you can pull the image
docker pull timop80/visioncraft-pro:salad-gpu
```

---

## 🔧 **If Docker Hub Image Doesn't Work**

### **Option A: Build and Push Manually (5 minutes)**

1. **Start Docker Desktop**
2. **Run the quick build script:**
   ```bash
   chmod +x quick-build.sh
   ./quick-build.sh
   ```
3. **Use the image in Salad Cloud** (configuration above)

### **Option B: Fix GitHub Container Registry**

#### **Make Repository Public:**
1. **Go to:** https://github.com/TimoP80/VisionCraftPro
2. **Settings → Scroll to "Danger Zone"**
3. **"Change repository visibility" → Make public**
4. **Wait 2-3 minutes** for changes to propagate

#### **Trigger GitHub Actions:**
1. **Go to Actions tab** in your repository
2. **Click "Build and Push Docker Image" workflow**
3. **Click "Run workflow" → "Run workflow"**
4. **Wait 5-10 minutes** for build to complete

#### **Use GitHub Container Registry:**
```
Registry Type: Private Registry
Registry URL: ghcr.io
Image: timop80/visioncraft-pro:salad-gpu
Username: your-github-username
Password: your-github-token (with read:packages scope)
```

---

## 🎯 **Recommended Approach**

### **Fastest Path (5 minutes):**
1. **Use Docker Hub option** (no auth needed)
2. **If image not found, run quick-build.sh**
3. **Deploy immediately**

### **Most Reliable (10 minutes):**
1. **Make repository public**
2. **Trigger GitHub Actions**
3. **Use GitHub Container Registry**

---

## 📋 **Working Configuration Templates**

### **Docker Hub (No Auth):**
```yaml
name: visioncraft-pro-gpu
image: timop80/visioncraft-pro:salad-gpu
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

### **GitHub Container Registry (With Auth):**
```yaml
name: visioncraft-pro-gpu
image: ghcr.io/timop80/visioncraft-pro:salad-gpu
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

## 🔍 **Verification Commands**

### **Test Docker Hub:**
```bash
docker pull timop80/visioncraft-pro:salad-gpu
```

### **Test GitHub Container Registry:**
```bash
docker pull ghcr.io/timop80/visioncraft-pro:salad-gpu
```

### **Test Local Build:**
```bash
docker build -f Dockerfile.salad -t test-image .
docker run -p 8000:8000 test-image
curl http://localhost:8000/status
```

---

## ✅ **Success Indicators**

✅ **Docker pull succeeds** without authentication errors  
✅ **Container starts** in Salad Cloud  
✅ **Health check passes**  
✅ **Web interface loads** at port 8000  
✅ **Image generation works**  

---

## 🚨 **If Still Failing**

### **Check Repository Visibility:**
- **Public:** GitHub Container Registry should work
- **Private:** Use Docker Hub or make repository public

### **Check GitHub Actions:**
- **Actions tab** → See if workflow ran successfully
- **If failed**, check error logs and re-run

### **Check Image Existence:**
- **Docker Hub:** https://hub.docker.com/r/timop80/visioncraft-pro
- **GitHub Container Registry:** https://github.com/TimoP80/VisionCraftPro/pkgs/container/visioncraft-pro

The Docker Hub option should work immediately without any authentication!
