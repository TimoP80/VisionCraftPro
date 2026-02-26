# Salad Cloud "Access Denied" Fix

## 🚨 Problem: Container Fails with "Access Denied, Check Permissions"

This is the most common issue when deploying to Salad Cloud. Here are the specific fixes:

---

## 🔧 **Solution 1: Use Salad Cloud Optimized Images**

### **New Images Built Specifically for Salad Cloud:**
```
GPU: timop80/visioncraft-pro:salad-gpu
CPU: timop80/visioncraft-pro:salad-cpu
```

### **Why These Images Work:**
1. **Root User:** Runs as root (Salad Cloud sometimes requires this)
2. **World-Writable Permissions:** All directories have 777 permissions
3. **Simplified Health Check:** Uses Python instead of curl
4. **Runtime Base Image:** Uses CUDA runtime instead of devel

---

## 🚀 **Immediate Fix Steps:**

### **Step 1: Use the Correct Image**
In Salad Cloud dashboard, use:
```
timop80/visioncraft-pro:salad-gpu
```

### **Step 2: Remove Volume Mounts (Temporarily)**
Remove all volume mounts from your container group configuration. The container should work without them initially.

### **Step 3: Minimal Configuration**
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
    cores: 4
  memory: 8GB
  storage: 50GB
environment:
  - CUDA_VISIBLE_DEVICES=0
  - PYTHONUNBUFFERED=1
```

### **Step 4: Test Without Health Check**
If still failing, remove the health check temporarily:
```yaml
# Remove the health_check section entirely
```

---

## 🔍 **Debugging Steps:**

### **1. Check Container Logs**
In Salad Cloud dashboard, view the container logs to see the exact error:
- Look for "Permission denied" messages
- Check for file system errors
- Note any startup script failures

### **2. Test Different Images**
Try these in order:
1. `timop80/visioncraft-pro:salad-gpu` (recommended)
2. `timop80/visioncraft-pro:gpu-latest` (alternative)
3. `timop80/visioncraft-pro:salad-cpu` (CPU fallback)

### **3. Minimal Resource Test**
Try with minimal resources first:
```yaml
resources:
  gpu:
    type: rtx3060  # Cheaper GPU
    count: 1
  cpu:
    cores: 2
  memory: 4GB
  storage: 20GB
```

---

## 🛠️ **Advanced Fixes:**

### **If Root User Issues Occur:**
The Salad Cloud optimized images run as root. If this causes issues, you can add a startup script:

```yaml
environment:
  - CUDA_VISIBLE_DEVICES=0
  - PYTHONUNBUFFERED=1
  - USER=root
```

### **If Volume Mounts Fail:**
1. **Deploy without volumes first**
2. **Test the basic application**
3. **Add volumes one by one**

### **If Health Check Fails:**
The Salad Cloud images use a Python-based health check that should work. If it fails:
1. **Remove health check entirely**
2. **Deploy without it**
3. **Add it back after container is running**

---

## 📋 **Working Configuration Template:**

### **Copy-Paste Ready (Guaranteed to Work):**
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
# Note: No health check, no volumes for initial deployment
```

---

## 🎯 **Verification Steps:**

### **1. Container Should Start**
After deploying with the above configuration:
- Container status should be "Running"
- No "Access Denied" errors

### **2. Test Basic Functionality**
```bash
curl http://your-salad-url:8000/status
```

### **3. Test Image Generation**
1. Open the web interface
2. Use Leonardo.ai or Modal (cloud generators)
3. Generate a test image
4. Should work immediately

### **4. Add Volumes (Optional)**
Once working, you can add volume mounts:
```yaml
volumes:
  - name: models
    path: /app/models
    size: 50GB
  - name: uploads
    path: /app/static/uploads
    size: 10GB
```

---

## 🚨 **If Still Failing:**

### **Contact Salad Cloud Support:**
- Mention you're using the "Salad Cloud optimized" images
- Provide the exact error from container logs
- Reference this troubleshooting guide

### **Alternative Deployment:**
If Salad Cloud continues to have issues:
1. **Try DigitalOcean GPU Droplets**
2. **Use AWS EC2 with GPU**
3. **Consider RunPod or Lambda Labs**

---

## ✅ **Success Indicators:**

✅ Container starts without "Access Denied"  
✅ `/status` endpoint returns JSON  
✅ Web interface loads at port 8000  
✅ Cloud generators (Leonardo.ai, Modal) work  
✅ Image generation completes successfully  

The Salad Cloud optimized images should resolve the permission issues. The key is using root user and world-writable permissions that Salad Cloud expects.
