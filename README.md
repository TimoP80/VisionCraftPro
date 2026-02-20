# VisionCraft Pro - Professional AI Image Generator

**Author:** Timo Pitkänen (tpitkane@gmail.com)

A powerful desktop application for AI-powered image generation featuring multiple cloud providers and local generation capabilities. Optimized for GPUs with 8GB VRAM and designed for professional use with access to cutting-edge AI models.

## 🎨 Features

### **Multi-Provider Generation Engine**
- **Replicate API**: Access premium models like FLUX.1 Schnell, FLUX.1.1 Pro, SDXL, and more
- **Azure AI**: Enterprise-grade generation with FLUX-1.1-pro
- **Leonardo.ai Integration**: Professional cloud-based models
- **Local Generation**: Stable Diffusion for offline privacy
- **Seamless Switching**: Easy transition between all providers

### **Professional Desktop Application**
- **Native Desktop Window**: Not a browser tab - real desktop software
- **Professional UI**: Modern, responsive interface with gradient effects
- **One-Click Launch**: No command line knowledge required
- **Automatic Backend**: Server starts automatically in the background

### **Advanced Features**
- **VRAM Optimized**: Specifically designed for 8GB VRAM GPUs (GTX 1070, RTX 3060, etc.)
- **Memory Management**: Advanced FP16 quantization, CPU offloading, VAE slicing
- **Real-time Monitoring**: VRAM usage, generation time, system status
- **Persistent Gallery**: All generated images automatically saved
- **API Key Management**: Secure storage and GUI input for cloud services
- **Multiple Aspect Ratios**: 1:1, 16:9, 9:16, 4:3, 3:4, 2:3, 3:2
- **Quality Controls**: Adjustable steps, guidance, and quality settings

### **Replicate API Integration**
- **FLUX Models**: FLUX.1 Schnell ($0.003), FLUX.1.1 Pro ($0.015) - Premium quality
- **Stable Diffusion XL**: High-quality generation with version hash support
- **SDXL Turbo**: Fast generation with jyoung105 model
- **Kandinsky 2.2**: Artistic style generation
- **Smart Aspect Ratio Mapping**: Automatic optimization for each model

### **Azure AI Integration**
- **FLUX-1.1-pro**: Enterprise-grade image generation
- **Azure OpenAI Endpoint**: Reliable production deployment
- **Gallery Integration**: Automatic saving of generated images

### **Leonardo.ai Integration**
- **Model Selection**: Phoenix 1.0, Phoenix 0.9, Universal models
- **Style Presets**: Creative, Dynamic, Artistic, Photographic, Cinematic, and more
- **Quality Levels**: Standard, High, Ultra quality options
- **API Polling**: Reliable status checking and image retrieval

## 🖥️ System Requirements

### **Minimum Requirements**
- **GPU**: NVIDIA GPU with at least 8GB VRAM (GTX 1070, RTX 3060, 3070, 4060, etc.)
- **CUDA**: CUDA 11.8 or higher
- **Python**: 3.9 or higher
- **RAM**: 16GB or more recommended
- **Storage**: 10GB free disk space for models and generated images

### **Optional Requirements**
- **Internet Connection**: Required for cloud generation (Replicate, Azure AI, Leonardo.ai)
- **API Keys**: Required for cloud-based generation features
  - Replicate API key for FLUX and SDXL models
  - Azure AI key for FLUX-1.1-pro
  - Leonardo.ai key for Phoenix models

**Tested with GTX 1070 (8GB VRAM)** - Fully optimized for this GPU and similar 8GB cards.

## 🚀 Quick Start

### **Method 1: Desktop Application (Recommended)**
1. Double-click `Launch_VisionCraft_Pro.bat`
2. Wait for the desktop window to open
3. Start generating images immediately!

### **Method 2: Command Line**
```bash
# Activate virtual environment
venv_gtx1070\Scripts\activate.bat

# Launch desktop app
python simple_desktop.py
```

### **Method 3: Web Server (Traditional)**
```bash
# Activate virtual environment
venv_gtx1070\Scripts\activate.bat

# Start web server
python app.py

# Open browser to http://localhost:8000
```

## 📦 Installation

### **Windows Installation**
1. **Download the application files**
2. **Run the setup** (if included) or extract to folder
3. **Double-click** `Launch_VisionCraft_Pro.bat`
4. **Wait** for automatic dependency installation
5. **Enjoy** your desktop app!

### **Manual Installation**
```bash
# Clone or download the repository
git clone <repository-url>
cd windsurf-project

# Create virtual environment
python -m venv venv_gtx1070
venv_gtx1070\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Install desktop dependencies
pip install pywebview

# Launch the app
python simple_desktop.py
```

## 🎮 Usage Guide

### **Getting Started**
1. **Launch application** using your preferred method
2. **Select your generation method**:
   - **Replicate API**: Premium FLUX and SDXL models
   - **Azure AI**: Enterprise-grade FLUX-1.1-pro
   - **Leonardo.ai**: Cloud generation with professional models
   - **Local Models**: Use your GPU for offline generation
3. **Configure settings**: Model, aspect ratio, quality, etc.
4. **Enter your prompt**: Describe the image you want to create
5. **Generate**: Click the generate button and wait for results

### **Replicate API Generation**
- **API Key**: Set your Replicate API key in the GUI
- **Model Selection**: FLUX.1 Schnell, FLUX.1.1 Pro, SDXL, SDXL Turbo, Kandinsky 2.2
- **Aspect Ratios**: Automatic optimization for each model (1:1, 16:9, 9:16, 4:3, 3:4, 2:3, 3:2)
- **Resolution**: 512x512 to 2048x2048 depending on model
- **Advantages**: Highest quality, latest models, professional results

### **Azure AI Generation**
- **API Key**: Set your Azure AI key in the GUI
- **Model**: FLUX-1.1-pro (1024x1024)
- **Endpoint**: Azure OpenAI deployment endpoint
- **Advantages**: Enterprise reliability, consistent quality

### **Local Generation (Stable Diffusion)**
- **Model Selection**: Choose from available local models
- **Resolution**: 512x512 to 1024x1024 (depending on VRAM)
- **Settings**: Steps (15-50), Guidance (1-20), Seed control
- **Advantages**: Free, offline, private generation

### **Leonardo.ai Cloud Generation**
- **API Key**: Set your Leonardo.ai API key in the GUI
- **Model Selection**: Phoenix 1.0, Phoenix 0.9, Universal
- **Aspect Ratios**: 1:1, 16:9, 9:16, 4:3, 3:4, 2:3, 3:2
- **Style Presets**: Creative, Dynamic, Artistic, Photographic, etc.
- **Quality Levels**: Standard, High, Ultra
- **Advantages**: Professional models, style presets

### **Gallery Management**
- **Automatic Saving**: All images saved to gallery
- **Persistent Storage**: Images survive app restarts
- **Easy Access**: View, download, and manage generated images
- **Metadata**: Generation parameters saved with each image

## 🔧 Configuration

### **Local Generation Settings**
- **Model ID**: Change Stable Diffusion model in `app.py`
- **Resolution Limits**: Adjust based on your VRAM
- **Default Parameters**: Modify steps, guidance, etc.

### **Cloud Generation Settings**
- **API Key Storage**: Stored in `api_keys.json`
- **Model Selection**: Updated via Leonardo.ai API
- **Polling Settings**: Timeout and retry intervals

### **Desktop App Settings**
- **Window Size**: Default 1200x900, resizable
- **Auto-Start Backend**: Enabled by default
- **Error Handling**: Automatic recovery and logging

## 📚 API Documentation

### **Web API Endpoints**

#### **GET `/`**
Root endpoint - returns basic API information.

#### **GET `/status`**
Returns system status including:
- Device type (CUDA/CPU)
- Model loading status
- VRAM usage
- Available generators
- System resources

#### **POST `/generate`**
Generate an image from text prompt.

**Request Body:**
```json
{
    "prompt": "A beautiful landscape with mountains",
    "negative_prompt": "blurry, low quality",
    "num_inference_steps": 20,
    "guidance_scale": 7.5,
    "width": 512,
    "height": 512,
    "seed": -1,
    "model": "stable-diffusion-1.5",
    "leonardo_model": "phoenix-1-0",
    "aspect_ratio": "16:9",
    "preset_style": "CREATIVE",
    "quality": "standard"
}
```

**Response:**
```json
{
    "image": "base64-encoded-image-data",
    "generation_time": 12.34,
    "vram_used": 6.78
}
```

#### **POST `/load_model`**
Pre-load a model into memory.

## 🛠️ Troubleshooting

### **Common Issues**

#### **"Backend failed to start"**
- **Check Python version**: Ensure Python 3.8+
- **Verify virtual environment**: Activate venv_gtx1070
- **Install dependencies**: Run `pip install -r requirements.txt`
- **Check CUDA**: Ensure CUDA 11.8+ is installed

#### **"Out of Memory Errors"**
- **Reduce resolution**: Use 512x512 instead of 768x768
- **Lower steps**: Use 15-20 steps instead of 30+
- **Close other apps**: Free up VRAM by closing other GPU applications
- **Restart app**: Clear cached memory

#### **"Cloud generation failed"**
- **Check API keys**: Verify your Replicate, Azure AI, and Leonardo.ai API keys are valid
- **Check internet**: Ensure stable internet connection
- **Verify model**: Make sure selected model is available
- **Check credits/balance**: Ensure you have sufficient credits or balance
- **Replicate specific**: Check model availability and rate limits
- **Azure AI specific**: Verify deployment endpoint and API version
- **Leonardo.ai specific**: Check credit balance and model access

#### **"Desktop app won't open"**
- **Run as administrator**: May need elevated permissions
- **Check antivirus**: Ensure the app isn't blocked
- **Install PyWebView**: Run `pip install pywebview`
- **Use command line**: Try `python simple_desktop.py`

### **Performance Optimization**

#### **For Faster Generation**
- **Use local models**: Faster for simple generations
- **Optimal settings**: 20 steps, 7.5 guidance
- **Lower resolution**: 512x512 is most efficient
- **Enable XFormers**: If available for memory efficiency

#### **For Better Quality**
- **Use Leonardo.ai**: Higher quality models
- **Increase steps**: 30-50 steps for more detail
- **Higher resolution**: 768x768 or 1024x1024 if VRAM allows
- **Experiment with styles**: Try different presets and models

## 🔄 Memory Optimization Techniques

This application uses several advanced techniques to minimize VRAM usage:

1. **FP16 Precision**: Uses half-precision floating point to reduce memory usage by ~50%
2. **CPU Offloading**: Offloads model components to CPU when not in use
3. **VAE Slicing**: Processes VAE in slices to reduce peak memory usage
4. **XFormers**: Memory-efficient attention mechanism (when available)
5. **Sequential CPU Offload**: Gradually moves components between GPU and CPU
6. **Automatic Cleanup**: Garbage collection and memory management
7. **Model Unloading**: Releases memory when switching models

## 🎯 Supported Models

### **Replicate API Models**
- **FLUX.1 Schnell**: Fast generation, 1-4 steps, $0.003/image
- **FLUX.1.1 Pro**: Premium quality, professional grade, $0.015/image
- **Stable Diffusion XL**: High-quality generation with version hash support
- **SDXL Turbo**: Fast generation with jyoung105 model
- **Kandinsky 2.2**: Artistic style generation

### **Azure AI Models**
- **FLUX-1.1-pro**: Enterprise-grade generation (1024x1024)
- **Azure OpenAI Endpoint**: Reliable production deployment

### **Local Models (Stable Diffusion)**
- **Stable Diffusion 1.5**: Default, most VRAM-efficient
- **Custom Fine-tuned Models**: Any SD 1.5-based models
- **Optimized for 8GB VRAM**: All models tested on GTX 1070

### **Leonardo.ai Models**
- **Phoenix 1.0**: Universal model for all image types
- **Phoenix 0.9**: Previous version, good for specific styles
- **Universal**: General purpose model

### **Aspect Ratios**
- **1:1**: Square (1024x1024)
- **16:9**: Widescreen (1344x768)
- **9:16**: Portrait (768x1344)
- **4:3**: Standard (1024x768)
- **3:4**: Vertical (768x1024)
- **2:3**: Tall (832x1216)
- **3:2**: Wide (1216x832)

## 📊 Performance Benchmarks

### **GTX 1070 (8GB VRAM) Local Performance**
- **512x512**: ~8-12 seconds (20 steps)
- **768x768**: ~15-20 seconds (20 steps)
- **1024x1024**: ~25-30 seconds (20 steps)
- **VRAM Usage**: 4-6GB typical, 7GB peak

### **Replicate API Performance**
- **FLUX.1 Schnell**: ~2-5 seconds (1-4 steps)
- **FLUX.1.1 Pro**: ~8-15 seconds (25-50 steps)
- **SDXL**: ~5-10 seconds (20-30 steps)
- **Cost**: Most economical FLUX Schnell (~1,666 images/$5)

### **Azure AI Performance**
- **FLUX-1.1-pro**: ~10-20 seconds
- **Quality**: Enterprise-grade, consistent results
- **Reliability**: Production deployment with SLA

### **Leonardo.ai Performance**
- **Generation Time**: 30-90 seconds (depends on queue)
- **Quality**: Superior to local generation
- **Models**: Access to latest professional models
- **No VRAM Usage**: All processing in cloud

## 📝 File Structure

```
windsurf-project/
├── app.py                      # Main FastAPI application
├── simple_desktop.py           # Desktop application launcher
├── robust_desktop.py           # Advanced desktop app with debugging
├── modern_generators.py        # Cloud API integrations
├── image_gallery.py            # Gallery management
├── static/
│   ├── index.html             # Web interface
│   ├── logo.png               # Application logo
│   └── output.css             # Tailwind CSS
├── venv_gtx1070/              # Virtual environment
├── api_keys.json              # API key storage
├── gallery/                   # Generated images storage
└── requirements.txt           # Python dependencies
```

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- **Report issues**: Bug reports and feature requests
- **Submit pull requests**: Code improvements and new features
- **Suggest models**: Recommend new models to support
- **Share optimizations**: Performance improvements

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For support and questions:
- **Check the troubleshooting section** above
- **Review the API documentation**
- **Test with different settings** if encountering issues
- **Ensure system requirements** are met

---

**VisionCraft Pro** - Professional AI Image Generation for Everyone

*Optimized for creators, designed for professionals, built for the future.*
