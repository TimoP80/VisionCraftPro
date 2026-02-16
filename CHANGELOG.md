# VisionCraft Pro - Changelog

**Author:** Timo Pitkänen (tpitkane@gmail.com)

All notable changes to VisionCraft Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-16

### 🚀 Major Replicate API Integration

#### ✨ Added
- **Replicate API Support** - Full integration with 5+ high-quality models
- **FLUX Models** - FLUX.1 Schnell, FLUX.1.1 Pro with advanced capabilities
- **Stable Diffusion XL** - High-quality generation with version hash support
- **SDXL Turbo** - Fast generation with jyoung105 model
- **Kandinsky 2.2** - Artistic style generation
- **Aspect Ratio Controls** - Complete aspect ratio support (1:1, 16:9, 9:16, 4:3, 3:4, 2:3, 3:2)
- **Resolution Controls** - 5 quality levels (512x512 to 2048x2048)
- **Smart Dimension Calculation** - Real-time aspect ratio and resolution mapping
- **Model-Specific Optimization** - Tailored parameters for each Replicate model
- **Enhanced Debugging** - Comprehensive logging for troubleshooting
- **Binary Data Handling** - Support for models returning binary image data
- **Fallback Logic** - Automatic fallback to working models when issues occur

#### 🎨 Features
- **Replicate Model Portfolio**
  - FLUX.1 Schnell ($0.003) - Fastest generation, 1-4 steps
  - FLUX.1.1 Pro ($0.015) - Premium quality, professional grade
  - Stable Diffusion XL ($0.005) - High quality, reliable
  - SDXL Turbo ($0.003) - Fast generation with jyoung105 model
  - Kandinsky 2.2 ($0.008) - Artistic style generation

- **Aspect Ratio System**
  - 7 aspect ratios: 1:1, 16:9, 9:16, 4:3, 3:4, 2:3, 3:2
  - Smart mapping to FLUX Schnell supported ratios
  - Real-time dimension calculation and display
  - Resolution dropdown shows actual output dimensions

- **Enhanced UI Controls**
  - Dynamic resolution dropdown with aspect ratio preview
  - Real-time width/height field updates
  - Model-specific parameter optimization
  - Comprehensive error handling and user feedback

#### 🛠️ Technical
- **Replicate Python Library Integration**
  - Advanced error handling and retry logic
  - Model-specific parameter validation
  - Binary data processing for direct image returns
  - Version hash support for stable model access

- **Smart Aspect Ratio Mapping**
  - Mathematical mapping to nearest supported ratio
  - Support for FLUX Schnell's 11 predefined aspect ratios
  - Debug logging for mapping decisions
  - Fallback to 1:1 for unsupported ratios

- **Model Management**
  - Individual model routing and handling
  - Temporary disablement for problematic models
  - Enhanced debugging for model-specific issues
  - Cost-effective model selection guidance

#### 🔧 Model Status
- **✅ Working Models (5/8)**
  - FLUX.1 Schnell - Full aspect ratio support
  - FLUX.1.1 Pro - Premium quality (square only)
  - Stable Diffusion XL - High quality
  - SDXL Turbo - Fast generation
  - Kandinsky 2.2 - Artistic styles

- **🔄 Temporarily Disabled (3/8)**
  - Nano Banana Pro - UTF-8/binary data issues
  - Realistic Vision v5.1 - Binary data truncation
  - Ideogram V3 Turbo - Binary data truncation

#### 🎯 User Experience
- **Intuitive Controls** - Easy aspect ratio and resolution selection
- **Real-time Feedback** - Immediate dimension calculation and preview
- **Error Prevention** - Smart fallbacks and validation
- **Cost Transparency** - Clear pricing information for each model

#### 📦 Performance
- **Cost Analysis**
  - Most Economical: FLUX Schnell & SDXL Turbo (~1,666 images/$5)
  - Best Value: Stable Diffusion XL, Kandinsky (~625 images/$5)
  - Premium Quality: FLUX 1.1 Pro (~333 images/$5)

- **Generation Speed**
  - FLUX Schnell: 1-4 steps, fastest
  - SDXL Turbo: 10 steps, fast
  - Others: 25 steps, standard

---

## [1.0.0] - 2026-02-07

### 🎉 Initial Release

#### ✨ Added
- **Professional Desktop Application** - Native desktop window with PyWebView
- **Dual Generation Engine** - Local Stable Diffusion + Leonardo.ai cloud integration
- **Modern Web Interface** - Responsive UI with gradient effects and animations
- **VRAM Optimization** - Advanced memory management for 8GB GPUs
- **Persistent Gallery** - Automatic image saving and management
- **API Key Management** - Secure storage and GUI input for cloud services
- **Model Selection** - Multiple models and aspect ratios
- **Real-time Monitoring** - VRAM usage, generation time, system status
- **One-Click Launch** - Easy desktop app launcher

#### 🎨 Features
- **Local Generation**
  - Stable Diffusion 1.5 integration
  - Resolution support: 512x512 to 1024x1024
  - Adjustable steps (15-50) and guidance (1-20)
  - Seed control for reproducible results
  - Negative prompt support

- **Leonardo.ai Integration**
  - Model selection: Phoenix 1.0, Phoenix 0.9, Universal
  - Aspect ratios: 1:1, 16:9, 9:16, 4:3, 3:4, 2:3, 3:2
  - Style presets: Creative, Dynamic, Artistic, Photographic, Cinematic, etc.
  - Quality levels: Standard, High, Ultra
  - API polling with automatic error recovery
  - Real-time status tracking

- **Desktop Application**
  - Native window: 1200x900, resizable
  - Professional branding and logo
  - Automatic backend startup
  - Graceful error handling
  - Cross-platform compatibility

#### 🛠️ Technical
- **Memory Optimization**
  - FP16 precision (50% memory reduction)
  - CPU offloading for unused components
  - VAE slicing for reduced peak memory
  - XFormers integration when available
  - Automatic garbage collection

- **API Architecture**
  - FastAPI backend with automatic documentation
  - RESTful API endpoints
  - Base64 image encoding
  - Real-time status monitoring
  - Error handling and logging

- **File Management**
  - Persistent gallery storage
  - Metadata preservation
  - API key secure storage
  - Configuration management

#### 🔧 Configuration
- **System Requirements**
  - NVIDIA GPU with 8GB+ VRAM
  - CUDA 11.8+ support
  - Python 3.8+ compatibility
  - 16GB+ RAM recommended

- **Performance**
  - GTX 1070 optimized
  - 512x512: ~8-12 seconds
  - 768x768: ~15-20 seconds
  - 1024x1024: ~25-30 seconds
  - VRAM usage: 4-6GB typical, 7GB peak

#### 📦 Installation
- **Easy Setup**
  - One-click desktop launcher
  - Automatic dependency installation
  - Virtual environment management
  - Windows batch file support

- **Multiple Launch Methods**
  - Desktop application (recommended)
  - Command line interface
  - Traditional web server

#### 🎯 Target Audience
- **Content Creators** - Professional image generation
- **Artists** - Creative AI assistance
- **Developers** - API integration and customization
- **Hobbyists** - Accessible AI image generation

#### 🌟 Highlights
- **Professional Grade** - Desktop application quality
- **Dual Engine** - Best of both local and cloud
- **Optimized** - Specifically for 8GB VRAM GPUs
- **User Friendly** - No command line knowledge required
- **Feature Complete** - All essential generation tools included

---

## Version History

### Development Phase
- **Initial Concept** - Web-based image generator
- **VRAM Optimization** - Memory management techniques
- **Desktop Conversion** - PyWebView integration
- **Cloud Integration** - Leonardo.ai API support
- **UI Enhancement** - Professional interface design
- **Bug Fixes** - Unicode encoding, connection issues
- **Documentation** - Comprehensive guides and API docs

### Key Milestones
1. **Basic Generator** - Local Stable Diffusion only
2. **Memory Optimization** - 8GB VRAM compatibility
3. **Web Interface** - Modern responsive UI
4. **Cloud Integration** - Leonardo.ai support
5. **Desktop Application** - Native desktop experience
6. **Professional Polish** - Branding, documentation, launcher

---

## Known Issues

### Resolved in v1.0.0
- ✅ Unicode encoding errors on Windows
- ✅ Backend connection issues
- ✅ Model selection problems
- ✅ API key management
- ✅ Desktop app startup failures

### Current Limitations
- **Leonardo.ai Credits** - Requires paid credits for cloud generation
- **Internet Dependency** - Cloud generation needs internet connection
- **Model Size** - Limited to models compatible with 8GB VRAM
- **Windows Focus** - Primarily tested on Windows (should work on other platforms)

---

## Future Roadmap

### v1.1.0 (Planned)
- **Additional Cloud Providers** - More API integrations
- **Model Management** - Download and manage custom models
- **Batch Generation** - Generate multiple images simultaneously
- **Advanced Settings** - More granular control options

### v1.2.0 (Planned)
- **Image Editing** - Basic editing tools
- **Prompt History** - Save and reuse prompts
- **Export Options** - More format choices
- **Performance Metrics** - Detailed analytics

### v2.0.0 (Future)
- **SDXL Support** - Next-gen model compatibility
- **Video Generation** - Moving image creation
- **Plugin System** - Extensible architecture
- **Cloud Sync** - Cross-device synchronization

---

## Support

### Getting Help
- **Documentation** - Comprehensive README and API docs
- **Troubleshooting** - Common issues and solutions
- **Community** - Issue tracking and discussions
- **Updates** - Regular improvements and fixes

### Contributing
- **Bug Reports** - Help us improve stability
- **Feature Requests** - Suggest new capabilities
- **Code Contributions** - Help us build better features
- **Documentation** - Improve guides and examples

---

**VisionCraft Pro** - Professional AI Image Generation

*Version 1.0.0 - The Beginning of Something Beautiful*
