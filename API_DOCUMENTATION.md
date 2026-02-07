# VisionCraft Pro - API Documentation

**Author:** Timo Pitkänen (tpitkane@gmail.com)

This document provides comprehensive API documentation for VisionCraft Pro, covering both the FastAPI backend endpoints and the Leonardo.ai integration.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Endpoints](#endpoints)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Rate Limits](#rate-limits)
- [Examples](#examples)

## Overview

VisionCraft Pro provides a RESTful API for AI image generation with both local Stable Diffusion and cloud-based Leonardo.ai integration. The API is built with FastAPI and provides automatic OpenAPI documentation.

### Key Features
- **Dual Generation Engines**: Local and cloud-based generation
- **Real-time Status**: System monitoring and VRAM usage
- **Gallery Management**: Persistent image storage
- **Configuration**: Dynamic model and parameter management

## Authentication

### Local Generation
No authentication required for local Stable Diffusion generation.

### Leonardo.ai Cloud Generation
API key required for Leonardo.ai integration. Set your API key using:
- **GUI**: In the application interface
- **API Key File**: Store in `api_keys.json`
- **Environment Variable**: `LEONARDO_API_KEY`

```json
{
  "leonardo-api": "your-api-key-here"
}
```

## Base URL

```
http://localhost:8000
```

## Endpoints

### GET `/`

Root endpoint - returns basic API information.

#### Response
```json
{
  "message": "VisionCraft Pro API",
  "status": "running",
  "version": "1.0.0"
}
```

---

### GET `/status`

Returns comprehensive system status including VRAM usage, available models, and system resources.

#### Response
```json
{
  "device": "cuda",
  "device_name": "NVIDIA GeForce GTX 1070",
  "vram_total": 8.0,
  "vram_used": 4.2,
  "vram_free": 3.8,
  "model_loaded": true,
  "current_model": "stable-diffusion-1.5",
  "current_generator_type": "local",
  "available_models": {
    "stable-diffusion-1.5": {
      "name": "Stable Diffusion 1.5",
      "quality": "Excellent",
      "vram_required": "4-6GB"
    }
  },
  "available_generators": {
    "leonardo-api": {
      "name": "Leonardo.ai API",
      "type": "api",
      "quality": "Professional"
    }
  },
  "system_info": {
    "python_version": "3.11.0",
    "cuda_available": true,
    "cuda_version": "12.1"
  }
}
```

---

### POST `/generate`

Generate an image from text prompt using either local Stable Diffusion or Leonardo.ai cloud generation.

#### Request Body

```json
{
  "prompt": "A beautiful landscape with mountains and a lake at sunset",
  "negative_prompt": "blurry, low quality, distorted",
  "num_inference_steps": 20,
  "guidance_scale": 7.5,
  "width": 512,
  "height": 512,
  "seed": -1,
  "model": "stable-diffusion-1.5",
  "leonardo_model": "phoenix-1.0",
  "aspect_ratio": "1:1",
  "preset_style": "CREATIVE",
  "quality": "standard"
}
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | Text description of the image to generate |
| `negative_prompt` | string | No | "" | Things to avoid in the generated image |
| `num_inference_steps` | integer | No | 20 | Number of denoising steps (15-50) |
| `guidance_scale` | float | No | 7.5 | How closely to follow the prompt (1-20) |
| `width` | integer | No | 512 | Image width in pixels |
| `height` | integer | No | 512 | Image height in pixels |
| `seed` | integer | No | -1 | Random seed (-1 for random) |
| `model` | string | No | "stable-diffusion-1.5" | Model to use for generation |
| `leonardo_model` | string | No | "phoenix-1.0" | Leonardo.ai specific model |
| `aspect_ratio` | string | No | "1:1" | Aspect ratio for Leonardo.ai |
| `preset_style` | string | No | "CREATIVE" | Style preset for Leonardo.ai |
| `quality` | string | No | "standard" | Quality level for Leonardo.ai |

#### Response

```json
{
  "image": "iVBORw0KGgoAAAANSUhEUgAA...base64-encoded-image-data...",
  "generation_time": 12.34,
  "vram_used": 4.2,
  "model": "stable-diffusion-1.5",
  "seed": 123456789,
  "parameters": {
    "prompt": "A beautiful landscape with mountains and a lake at sunset",
    "negative_prompt": "blurry, low quality, distorted",
    "num_inference_steps": 20,
    "guidance_scale": 7.5,
    "width": 512,
    "height": 512
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `image` | string | Base64-encoded PNG image data |
| `generation_time` | float | Time taken to generate in seconds |
| `vram_used` | float | VRAM used during generation in GB |
| `model` | string | Model used for generation |
| `seed` | integer | Seed used for generation |
| `parameters` | object | All parameters used for generation |

---

### POST `/load_model`

Load a specific model into memory. Useful for pre-loading models to reduce first-generation latency.

#### Request Body

```json
{
  "model": "stable-diffusion-1.5"
}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Model name to load |

#### Response

```json
{
  "message": "Model loaded successfully",
  "model": "stable-diffusion-1.5",
  "vram_used": 4.2,
  "load_time": 8.5
}
```

---

### GET `/models`

Get list of available models and their specifications.

#### Response

```json
{
  "local_models": {
    "stable-diffusion-1.5": {
      "name": "Stable Diffusion 1.5",
      "quality": "Excellent",
      "vram_required": "4-6GB",
      "max_resolution": [1024, 1024],
      "description": "High-quality general purpose model"
    }
  },
  "cloud_models": {
    "leonardo-api": {
      "models": {
        "phoenix-1-0": {
          "id": "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3",
          "name": "Phoenix 1.0",
          "description": "Universal model for all types of images"
        },
        "phoenix-0-9": {
          "id": "6b645e3a-d64f-4341-a6d8-7a3690fbf042",
          "name": "Phoenix 0.9",
          "description": "Previous version of Phoenix model"
        }
      },
      "aspect_ratios": [
        {"id": "1:1", "name": "Square", "resolution": [1024, 1024]},
        {"id": "16:9", "name": "Widescreen", "resolution": [1344, 768]}
      ],
      "preset_styles": [
        {"id": "CREATIVE", "name": "Creative", "description": "Balanced creative output"}
      ],
      "quality_levels": [
        {"id": "standard", "name": "Standard", "description": "Good quality, faster generation"}
      ]
    }
  }
}
```

---

### GET `/gallery`

Get list of generated images from the gallery.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 50 | Maximum number of images to return |
| `offset` | integer | No | 0 | Number of images to skip |
| `model` | string | No | - | Filter by model used |

#### Response

```json
{
  "images": [
    {
      "id": "img_123456789",
      "filename": "generated_image_20240207_123456.png",
      "prompt": "A beautiful landscape with mountains",
      "negative_prompt": "blurry, low quality",
      "model": "stable-diffusion-1.5",
      "seed": 123456789,
      "generation_time": 12.34,
      "vram_used": 4.2,
      "width": 512,
      "height": 512,
      "created_at": "2024-02-07T12:34:56Z",
      "image_data": "iVBORw0KGgoAAAANSUhEUgAA..."
    }
  ],
  "total_count": 25,
  "limit": 50,
  "offset": 0
}
```

---

### POST `/api-key`

Set or update API keys for cloud services.

#### Request Body

```json
{
  "service": "leonardo-api",
  "api_key": "your-leonardo-api-key-here"
}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `service` | string | Yes | Service name (currently "leonardo-api") |
| `api_key` | string | Yes | API key for the service |

#### Response

```json
{
  "message": "API key updated successfully",
  "service": "leonardo-api",
  "key_preview": "************9721"
}
```

---

## Data Models

### GenerationRequest

```python
class GenerationRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = ""
    num_inference_steps: Optional[int] = 20
    guidance_scale: Optional[float] = 7.5
    width: Optional[int] = 512
    height: Optional[int] = 512
    seed: Optional[int] = -1
    model: Optional[str] = "stable-diffusion-1.5"
    leonardo_model: Optional[str] = None
    aspect_ratio: Optional[str] = None
    preset_style: Optional[str] = None
    quality: Optional[str] = None
```

### GenerationResponse

```python
class GenerationResponse(BaseModel):
    image: str  # Base64 encoded
    generation_time: float
    vram_used: float
    model: str
    seed: int
    parameters: dict
```

### SystemStatus

```python
class SystemStatus(BaseModel):
    device: str
    device_name: str
    vram_total: float
    vram_used: float
    vram_free: float
    model_loaded: bool
    current_model: str
    current_generator_type: str
    available_models: dict
    available_generators: dict
    system_info: dict
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error information.

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid prompt provided",
    "details": {
      "field": "prompt",
      "issue": "Prompt cannot be empty"
    }
  }
}
```

### Common Error Codes

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 400 | VALIDATION_ERROR | Invalid request parameters |
| 401 | AUTHENTICATION_ERROR | Missing or invalid API key |
| 404 | NOT_FOUND | Resource not found |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests |
| 500 | INTERNAL_ERROR | Server error |
| 503 | SERVICE_UNAVAILABLE | Service temporarily unavailable |

### Specific Errors

#### Model Not Available
```json
{
  "error": {
    "code": "MODEL_NOT_AVAILABLE",
    "message": "Model 'invalid-model' not available",
    "available_models": ["stable-diffusion-1.5"]
  }
}
```

#### Insufficient VRAM
```json
{
  "error": {
    "code": "INSUFFICIENT_VRAM",
    "message": "Not enough VRAM for requested resolution",
    "vram_available": 3.2,
    "vram_required": 6.5
  }
}
```

#### Leonardo.ai API Error
```json
{
  "error": {
    "code": "LEONARDO_API_ERROR",
    "message": "Leonardo.ai generation failed",
    "details": {
      "api_error": "Invalid model ID",
      "suggestion": "Check available models"
    }
  }
}
```

## Rate Limits

### Local Generation
- **No strict rate limits**
- **Limited by VRAM and processing power**
- **Recommended**: 1-2 concurrent generations maximum

### Leonardo.ai Cloud Generation
- **Subject to Leonardo.ai rate limits**
- **Typical limits**: 10-20 generations per minute
- **Queue-based**: May experience delays during high demand

## Examples

### Basic Local Generation

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A serene mountain landscape at sunrise",
    "width": 512,
    "height": 512,
    "num_inference_steps": 20
  }'
```

### Leonardo.ai Cloud Generation

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A futuristic city with flying cars",
    "model": "leonardo-api",
    "leonardo_model": "phoenix-1-0",
    "aspect_ratio": "16:9",
    "preset_style": "CINEMATIC",
    "quality": "high"
  }'
```

### Python Example

```python
import requests
import base64
from PIL import Image
import io

# Generate image
response = requests.post("http://localhost:8000/generate", json={
    "prompt": "A beautiful garden with colorful flowers",
    "width": 768,
    "height": 768,
    "num_inference_steps": 25
})

data = response.json()

# Decode and save image
image_data = base64.b64decode(data["image"])
image = Image.open(io.BytesIO(image_data))
image.save("generated_image.png")

print(f"Generated in {data['generation_time']:.2f} seconds")
print(f"VRAM used: {data['vram_used']:.2f} GB")
```

### JavaScript Example

```javascript
async function generateImage(prompt) {
  const response = await fetch('http://localhost:8000/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt: prompt,
      width: 512,
      height: 512,
      num_inference_steps: 20
    })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    // Convert base64 to image
    const img = document.createElement('img');
    img.src = `data:image/png;base64,${data.image}`;
    document.body.appendChild(img);
    
    console.log(`Generated in ${data.generation_time}s`);
  } else {
    console.error('Generation failed:', data.error);
  }
}

// Usage
generateImage('A majestic dragon soaring through clouds');
```

## OpenAPI Documentation

When the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These provide interactive API documentation with testing capabilities.

## WebSocket Support

Currently, VisionCraft Pro uses HTTP polling for generation status. WebSocket support for real-time updates is planned for future versions.

## SDK and Libraries

Official SDKs are planned for:
- Python
- JavaScript/TypeScript
- Other languages based on community demand

## Support

For API-related questions:
- **Documentation**: Review this guide and OpenAPI docs
- **Issues**: Report bugs via GitHub issues
- **Community**: Join discussions for feature requests
- **Examples**: Check the repository for sample code

---

**VisionCraft Pro API** - Professional Image Generation at Your Fingertips

*Version 1.0.0 - Complete API Reference*
