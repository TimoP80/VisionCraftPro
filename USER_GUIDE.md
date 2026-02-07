# VisionCraft Pro - User Guide

**Author:** Timo Pitkänen (tpitkane@gmail.com)

Welcome to VisionCraft Pro - your professional AI image generation suite! This comprehensive guide will help you get the most out of your image generation experience with both local Stable Diffusion and Leonardo.ai cloud integration.

## Table of Contents

- [Getting Started](#getting-started)
- [Interface Overview](#interface-overview)
- [Local Generation](#local-generation)
- [Cloud Generation](#cloud-generation)
- [Advanced Features](#advanced-features)
- [Gallery Management](#gallery-management)
- [Troubleshooting](#troubleshooting)
- [Tips and Best Practices](#tips-and-best-practices)

## Getting Started

### System Requirements

**Minimum Requirements:**
- NVIDIA GPU with 8GB+ VRAM (GTX 1070, RTX 3060, etc.)
- CUDA 11.8 or higher
- 16GB RAM recommended
- 10GB free disk space

**Optional for Cloud Generation:**
- Internet connection
- Leonardo.ai API key

### Installation and Launch

#### Method 1: One-Click Launch (Recommended)
1. Double-click `Launch_VisionCraft_Pro.bat`
2. Wait for automatic setup
3. Desktop window opens automatically

#### Method 2: Command Line
```bash
# Activate virtual environment
venv_gtx1070\Scripts\activate.bat

# Launch desktop app
python simple_desktop.py
```

### First Launch

When you first launch VisionCraft Pro:
1. **Backend starts automatically** - Wait for initialization
2. **Desktop window opens** - Professional interface appears
3. **System status displays** - Shows GPU and VRAM information
4. **Ready to generate** - Start creating images immediately

## Interface Overview

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────┐
│ VisionCraft Pro - Professional AI Image Generator        │
│ ───────────────────────────────────────────────────────── │
│                                                         │
│ [Logo] VisionCraft Pro                                   │
│ Professional AI-Powered Image Generation                  │
│                                                         │
│ ┌─ System Status ───────────────────────────────────────┐ │
│ │ 🚀 System Status                                     │ │
│ │ • Device: NVIDIA GeForce GTX 1070                    │ │
│ │ • VRAM: 4.2GB / 8.0GB used                          │ │
│ │ • Model: Stable Diffusion 1.5                        │ │
│ │ • Status: Ready                                      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                         │
│ ┌─ Generation Controls ────────────────────────────────┐ │
│ │ Model Selection: [Local Models ▼]                    │ │
│ │ Prompt: [Enter your image description here...]         │ │
│ │ Settings: [Advanced Options ▼]                        │ │
│ │ [Generate Button]                                      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                         │
│ ┌─ Gallery ──────────────────────────────────────────────┐ │
│ │ [Generated Images Display Area]                        │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### **Header Section**
- **Logo and branding** - Professional application identity
- **Status indicators** - Real-time system monitoring

#### **System Status Panel**
- **GPU Information** - Device type and VRAM usage
- **Model Status** - Currently loaded model
- **Generation Type** - Local or cloud mode
- **Performance Metrics** - Real-time monitoring

#### **Generation Controls**
- **Model Selection** - Choose between local and cloud models
- **Prompt Input** - Describe your desired image
- **Advanced Settings** - Fine-tune generation parameters
- **Generate Button** - Start image generation

#### **Gallery Section**
- **Image Display** - View generated images
- **Metadata** - Generation parameters and timestamps
- **Management Options** - Download, delete, organize

## Local Generation

### Overview

Local generation uses your GPU to run Stable Diffusion models directly on your computer. This provides:
- **Free generation** - No per-image costs
- **Privacy** - Images never leave your computer
- **Speed** - Fast generation for simple prompts
- **Offline capability** - No internet required

### Getting Started with Local Generation

#### Step 1: Select Local Model
1. Click the model dropdown
2. Choose from "Local Models (Stable Diffusion)"
3. Select "Stable Diffusion 1.5" (default)

#### Step 2: Configure Basic Settings
```
Resolution: 512x512 (recommended for 8GB VRAM)
Steps: 20 (good balance of speed/quality)
Guidance: 7.5 (standard setting)
Seed: -1 (random) or specific number
```

#### Step 3: Write Your Prompt
**Good Prompt Examples:**
- "A serene mountain landscape at sunrise"
- "A cute cat sitting on a windowsill"
- "Futuristic city with flying cars at night"
- "Beautiful flower garden with butterflies"

**Prompt Writing Tips:**
- **Be descriptive** - Include details about style, lighting, mood
- **Use specific terms** - "photorealistic," "oil painting," "anime style"
- **Consider composition** - "close-up," "wide angle," "bird's eye view"
- **Add atmosphere** - "misty morning," "golden hour," "dramatic lighting"

#### Step 4: Optional Negative Prompt
Tell the AI what to avoid:
```
blurry, low quality, distorted, ugly, bad anatomy, extra limbs
```

#### Step 5: Generate
1. Click the "Generate" button
2. Wait for generation (8-30 seconds depending on settings)
3. View your image in the gallery

### Advanced Local Settings

#### Resolution Options
- **512x512** - Fastest, good quality (recommended)
- **768x768** - Better detail, slower (requires more VRAM)
- **1024x1024** - Best quality, slowest (may cause VRAM issues)

#### Inference Steps
- **15 steps** - Fast, good for simple images
- **20 steps** - Balanced (recommended)
- **30 steps** - High detail, slower
- **50 steps** - Maximum detail, very slow

#### Guidance Scale
- **1.0-3.0** - More creative, less literal
- **7.5** - Standard (recommended)
- **10.0-15.0** - More literal, less creative
- **20.0** - Very strict interpretation

#### Seed Control
- **-1** - Random seed each time
- **Specific number** - Reproducible results
- **Copy seed** - From previous generation to recreate similar images

## Cloud Generation (Leonardo.ai)

### Overview

Leonardo.ai provides professional cloud-based generation with:
- **Higher quality** - State-of-the-art models
- **More models** - Specialized models for different styles
- **Professional features** - Advanced controls and presets
- **No VRAM limits** - All processing in the cloud

### Setting Up Leonardo.ai

#### Step 1: Get API Key
1. Visit [Leonardo.ai](https://leonardo.ai/)
2. Create an account or sign in
3. Navigate to API section
4. Generate or copy your API key

#### Step 2: Enter API Key in VisionCraft Pro
1. Look for "Leonardo.ai API Key" section
2. Enter your API key
3. Click "Save API Key"
4. Verify key shows as "API key set: ************1234"

#### Step 3: Select Leonardo.ai Model
1. Click model dropdown
2. Choose "Leonardo.ai"
3. Select specific model (Phoenix 1.0 recommended)

### Leonardo.ai Models

#### Phoenix 1.0 (Recommended)
- **Universal model** - Good for all image types
- **High quality** - Professional results
- **Versatile** - Works with most prompts

#### Phoenix 0.9
- **Previous version** - Slightly different style
- **Good for specific use cases** - Experimental results

#### Universal
- **General purpose** - Reliable all-around performer
- **Consistent results** - Predictable quality

### Aspect Ratios

Leonardo.ai provides multiple aspect ratios:

| Ratio | Resolution | Best For |
|-------|------------|-----------|
| 1:1 | 1024x1024 | Portraits, Instagram posts |
| 16:9 | 1344x768 | Landscapes, wallpapers |
| 9:16 | 768x1344 | Phone wallpapers, vertical content |
| 4:3 | 1024x768 | Traditional photos |
| 3:4 | 768x1024 | Vertical portraits |
| 2:3 | 832x1216 | Tall portraits |
| 3:2 | 1216x832 | Wide landscapes |

### Style Presets

Choose from professional style presets:

#### Creative Styles
- **Creative** - Balanced artistic output
- **Dynamic** - More dramatic and intense
- **Artistic** - Enhanced artistic style

#### Photographic Styles
- **Photographic** - Photorealistic output
- **Cinematic** - Movie-like quality
- **3D Render** - 3D rendered look

#### Themed Styles
- **Fantasy Art** - Fantasy themed images
- **Steampunk** - Victorian sci-fi aesthetic
- **Anime** - Anime/manga style
- **Comic Book** - Comic book appearance

### Quality Levels

| Level | Description | Speed | Quality |
|-------|-------------|-------|---------|
| Standard | Good quality, faster | Fast | Good |
| High | Better quality, moderate | Medium | Better |
| Ultra | Best quality, longer | Slow | Best |

### Cloud Generation Workflow

#### Step 1: Configure Leonardo.ai Settings
```
Model: Phoenix 1.0
Aspect Ratio: 16:9 (for landscapes)
Style: Photographic
Quality: High
```

#### Step 2: Write Prompt for Leonardo.ai
Leonardo.ai works well with detailed prompts:

**Example Prompts:**
- "Photorealistic portrait of a woman with flowing red hair, soft natural lighting, professional headshot"
- "Epic fantasy landscape with floating islands, waterfalls, dramatic clouds, cinematic lighting"
- "Steampunk mechanical dragon with brass and copper details, Victorian era, intricate design"

#### Step 3: Generate and Monitor
1. Click "Generate"
2. Monitor progress in console/log
3. Wait for completion (30-90 seconds typical)
4. Image appears in gallery when ready

## Advanced Features

### Model Switching

#### Switch Between Local and Cloud
1. Complete current generation or wait for completion
2. Select different model from dropdown
3. Configure settings for new model
4. Continue generating

#### Best Practices
- **Start local** for quick tests and iterations
- **Switch to cloud** for final high-quality images
- **Use both** to compare results

### Prompt Engineering

#### Basic Prompt Structure
```
[Subject] + [Style] + [Setting] + [Lighting] + [Details]
```

#### Example Breakdown
```
"A majestic lion" + "photorealistic" + "in an African savanna" + "golden hour lighting" + "detailed fur texture"
```

#### Advanced Techniques

#### Weighted Prompts
```
"Beautiful landscape:1.2 with mountains:0.8 and a lake:1.0"
```

#### Negative Prompts
```
"blurry, low quality, distorted, ugly, bad anatomy, watermark, text"
```

#### Style Modifiers
- **Photography terms**: "DSLR," "shot on 85mm lens," "f/1.4"
- **Art styles**: "oil painting," "watercolor," "pencil sketch"
- **Lighting**: "golden hour," "dramatic lighting," "soft natural light"

### Batch Generation

#### Sequential Generation
1. Generate first image
2. Modify prompt slightly
3. Use same seed for consistency
4. Compare variations

#### Parameter Sweeps
- Keep prompt constant
- Vary one parameter (steps, guidance, etc.)
- Compare results to find optimal settings

## Gallery Management

### Viewing Generated Images

#### Gallery Features
- **Automatic saving** - All images saved automatically
- **Metadata display** - Shows generation parameters
- **Thumbnail view** - Easy browsing of multiple images
- **Full-size view** - Click to see details

#### Image Information
Each image includes:
- **Prompt** - Original text description
- **Model** - Which model was used
- **Parameters** - Settings used for generation
- **Timestamp** - When image was created
- **Generation time** - How long it took

### Managing Your Gallery

#### Downloading Images
1. Click on any image in gallery
2. Look for download option
3. Save to desired location
4. Images are saved as PNG format

#### Deleting Images
1. Select image to remove
2. Use delete option
3. Confirm deletion
4. Image removed from gallery and disk

#### Organization Tips
- **Generate with descriptive prompts** for easier identification
- **Use consistent naming** in prompts for better organization
- **Regular cleanup** to manage disk space
- **Export favorites** to external storage

### Gallery Storage

#### File Location
- Images stored in `gallery/` folder
- Organized by date automatically
- PNG format for high quality
- Metadata embedded in filenames

#### Storage Management
- **Monitor disk space** - Images can be large (1-5MB each)
- **Regular cleanup** - Remove unwanted images
- **Export important images** - Save to external storage
- **Compress if needed** - For long-term storage

## Troubleshooting

### Common Issues

#### Generation Fails

**Local Generation Issues:**
- **"Out of memory"** - Reduce resolution or close other apps
- **"Model failed to load"** - Restart application
- **"CUDA error"** - Check GPU drivers and CUDA installation

**Cloud Generation Issues:**
- **"API key invalid"** - Verify Leonardo.ai API key
- **"Generation failed"** - Check internet connection and credits
- **"Model not available"** - Try different Leonardo.ai model

#### Performance Issues

**Slow Generation:**
- **Reduce resolution** - Use 512x512 instead of larger sizes
- **Lower steps** - Use 15-20 steps instead of 30+
- **Close other apps** - Free up VRAM and CPU resources
- **Check GPU usage** - Ensure GPU isn't overloaded

**Quality Issues:**
- **Improve prompts** - Be more specific and descriptive
- **Adjust guidance** - Try different guidance scales
- **Try different models** - Local vs cloud generation
- **Use negative prompts** - Specify what to avoid

#### Application Issues

**Desktop App Won't Start:**
- **Run as administrator** - May need elevated permissions
- **Check antivirus** - Ensure app isn't blocked
- **Install PyWebView** - Run `pip install pywebview`
- **Use command line** - Try `python simple_desktop.py`

**Backend Connection Issues:**
- **Wait longer** - Backend may need more time to start
- **Check console** - Look for error messages
- **Restart application** - Clear any stuck processes
- **Verify dependencies** - Ensure all packages installed

### Error Messages Explained

#### Common Error Messages

**"Backend failed to start"**
- Backend server encountered an error
- Check console for specific error details
- Usually related to missing dependencies or configuration

**"Model not available"**
- Selected model isn't accessible
- Try different model or check API key for cloud services

**"Insufficient VRAM"**
- Not enough GPU memory for requested settings
- Reduce resolution or close other GPU applications

**"Generation failed"**
- General generation error
- Check prompt for issues and try again

### Getting Help

#### Self-Service Resources
- **Console output** - Check for specific error messages
- **System status** - Verify GPU and VRAM availability
- **Documentation** - Review this guide and API docs

#### Common Solutions
1. **Restart application** - Clears temporary issues
2. **Reduce settings** - Lower resolution or steps
3. **Check dependencies** - Ensure all packages installed
4. **Verify system requirements** - GPU, CUDA, RAM

## Tips and Best Practices

### Prompt Writing

#### Do's
- **Be specific and descriptive**
- **Include style and mood**
- **Use artistic terminology**
- **Consider composition and lighting**
- **Experiment with different approaches**

#### Don'ts
- **Use vague descriptions**
- **Overcomplicate prompts**
- **Ignore negative prompts**
- **Forget about aspect ratio**
- **Skip parameter tuning**

### Parameter Optimization

#### Local Generation
- **Start with 512x512** for speed testing
- **Use 20 steps** for good balance
- **Keep guidance at 7.5** for most cases
- **Increase gradually** if you want more detail

#### Cloud Generation
- **Use Phoenix 1.0** for best results
- **Match aspect ratio to content**
- **Choose appropriate style preset**
- **Select quality based on needs**

### Workflow Recommendations

#### For Beginners
1. **Start with local generation** - Learn the basics
2. **Use simple prompts** - Get comfortable with interface
3. **Experiment with settings** - Understand parameter effects
4. **Try cloud generation** - Experience higher quality

#### For Professionals
1. **Use cloud generation** for final images
2. **Master prompt engineering** - Get consistent results
3. **Optimize parameters** - Find your perfect settings
4. **Organize gallery** - Manage large image collections

#### For Artists
1. **Experiment with styles** - Find your aesthetic
2. **Use reference images** - Guide the AI effectively
3. **Iterate on prompts** - Refine your vision
4. **Combine techniques** - Local + cloud generation

### Performance Optimization

#### Speed Tips
- **Lower resolution** for testing
- **Reduce steps** for faster generation
- **Use local generation** for quick iterations
- **Batch similar prompts** for efficiency

#### Quality Tips
- **Increase steps** for more detail
- **Use cloud generation** for best quality
- **Write detailed prompts** - Be specific
- **Use negative prompts** - Avoid unwanted elements

#### Resource Management
- **Monitor VRAM usage** - Stay within limits
- **Close unnecessary apps** - Free up resources
- **Regular cleanup** - Manage disk space
- **Export important images** - Long-term storage

---

**VisionCraft Pro** - Your Gateway to Professional AI Image Generation

*Happy Creating! 🎨*
