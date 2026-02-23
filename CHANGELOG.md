# VisionCraft Pro - Changelog

**Author:** Timo Pitkänen (tpitkane@gmail.com)

All notable changes to VisionCraft Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.2] - 2026-02-23

### 🚀 Improved
- **Hugging Face Token Delivery** - Resolved model download speed limitations on Modal by ensuring Hugging Face authentication tokens are correctly passed to all `from_pretrained` calls.

---

## [1.1.1] - 2026-02-23

### 🐛 Fixed
- **Modal GPU Memory Leaks** - Implemented a strict single-model VRAM cache across all Modal endpoint scripts (`modal_web.py`, `modal_integration.py`, `modal_server.py`, `modal_persistent.py`). This prevents out-of-memory (OOM) errors during rapid model switching by explicitly clearing the GPU cache and triggering garbage collection before loading new models.

---

## [1.1.0] - 2026-02-21

### ✨ Added
- **Extensive Leonardo.ai Model Support** - Added configuration mapping for all 33+ available Leonardo custom platform models. Now users can select from specialized models like FLUX variations, Anime XL, Pixel Art, RPG, and more.
- **Improved Error Logging** - Added detailed console logging for remote generation failures to capture the exact payload and endpoint details when a 500 error occurs.

### 🐛 Fixed
- **Leonardo API 500 Error Resolution** - Corrected a critical bug where human-readable model keys (e.g., `phoenix-1-0`) were transmitted instead of valid Leonardo.ai UUIDs, which previously caused image generations to fail with 500 Internal Server Errors.

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
