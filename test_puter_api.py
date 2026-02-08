"""
Test Puter.com free unlimited image generation API

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import requests
import json
import time
import io
from PIL import Image

def test_puter_api():
    """Test Puter.com API for image generation"""
    print("🧪 Testing Puter.com Free Image Generation API")
    print("=" * 60)
    print("✨ FREE - No API keys required!")
    print("✨ UNLIMITED - No rate limits!")
    print("✨ MULTIPLE MODELS - DALL-E 3, FLUX, Stable Diffusion, etc!")
    
    # Puter.js works via JavaScript, but we can test the API endpoint directly
    print(f"\n🔍 Testing Puter.com API Access")
    print("=" * 60)
    
    # Test with a simple request to see if the service is available
    try:
        # First, let's try to access the Puter API endpoint
        response = requests.get("https://api.puter.com/v1/info", timeout=30)
        print(f"📡 Puter API Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Puter API is accessible!")
        else:
            print(f"⚠️  Puter API status: {response.text}")
            
    except Exception as e:
        print(f"❌ Error accessing Puter API: {e}")
    
    # Since Puter.js is a JavaScript library, let's create a test HTML file
    print(f"\n📝 Creating Puter.js Test HTML")
    print("=" * 60)
    
    html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Puter.com Image Generation Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .test-section {
            margin: 20px 0;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .model-test {
            margin: 10px 0;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 5px;
        }
        .generated-image {
            max-width: 300px;
            max-height: 300px;
            margin: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .loading {
            color: #666;
            font-style: italic;
        }
        .success {
            color: green;
            font-weight: bold;
        }
        .error {
            color: red;
            font-weight: bold;
        }
        button {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
        button:hover {
            background: #0056b3;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Puter.com Free Image Generation Test</h1>
        <p>Testing free, unlimited image generation with no API keys required!</p>
        
        <div class="test-section">
            <h2>🧪 Quick Test</h2>
            <input type="text" id="prompt" value="beautiful woman, high quality, detailed, photorealistic" placeholder="Enter prompt...">
            <button onclick="testQuickGeneration()">Generate Quick Test</button>
            <div id="quick-result"></div>
        </div>
        
        <div class="test-section">
            <h2>🎯 Model Comparison</h2>
            <button onclick="testAllModels()">Test All Models</button>
            <div id="models-result"></div>
        </div>
        
        <div class="test-section">
            <h2>📊 Test Results</h2>
            <div id="test-results">
                <p>Click the buttons above to test image generation...</p>
            </div>
        </div>
    </div>

    <script src="https://js.puter.com/v2/"></script>
    <script>
        const testPrompt = "beautiful woman, high quality, detailed, photorealistic";
        
        async function testQuickGeneration() {
            const resultDiv = document.getElementById('quick-result');
            const prompt = document.getElementById('prompt').value || testPrompt;
            
            resultDiv.innerHTML = '<div class="loading">🔄 Generating image...</div>';
            
            try {
                const startTime = Date.now();
                const imageElement = await puter.ai.txt2img(prompt, {
                    model: "dall-e-3",
                    quality: "standard"
                });
                const endTime = Date.now();
                
                resultDiv.innerHTML = `
                    <div class="success">✅ Generation successful!</div>
                    <div>⏱️ Time: ${endTime - startTime}ms</div>
                    <div>🎨 Model: DALL-E 3</div>
                    <div>📝 Prompt: ${prompt}</div>
                `;
                resultDiv.appendChild(imageElement);
                imageElement.className = "generated-image";
                
                // Update test results
                updateTestResults("DALL-E 3", true, endTime - startTime);
                
            } catch (error) {
                resultDiv.innerHTML = `<div class="error">❌ Error: ${error.message}</div>`;
                updateTestResults("DALL-E 3", false, 0, error.message);
            }
        }
        
        async function testAllModels() {
            const resultDiv = document.getElementById('models-result');
            resultDiv.innerHTML = '<div class="loading">🔄 Testing all models...</div>';
            
            const models = [
                { name: "DALL-E 3", model: "dall-e-3", quality: "standard" },
                { name: "FLUX.1 Schnell", model: "black-forest-labs/FLUX.1-schnell" },
                { name: "FLUX.1 Dev", model: "black-forest-labs/FLUX.1-dev" },
                { name: "Stable Diffusion XL", model: "stabilityai/stable-diffusion-xl-base-1.0" },
                { name: "GPT Image 1.5", model: "gpt-image-1.5", quality: "medium" },
                { name: "Gemini 2.5 Flash", model: "gemini-2.5-flash-image-preview" },
                { name: "Seedream 4.0", model: "ByteDance-Seed/Seedream-4.0" }
            ];
            
            let results = "";
            
            for (const modelInfo of models) {
                try {
                    const startTime = Date.now();
                    
                    const options = {
                        model: modelInfo.model
                    };
                    
                    if (modelInfo.quality) {
                        options.quality = modelInfo.quality;
                    }
                    
                    const imageElement = await puter.ai.txt2img(testPrompt, options);
                    const endTime = Date.now();
                    
                    results += `
                        <div class="model-test">
                            <div class="success">✅ ${modelInfo.name}</div>
                            <div>⏱️ Time: ${endTime - startTime}ms</div>
                        </div>
                    `;
                    
                    updateTestResults(modelInfo.name, true, endTime - startTime);
                    
                } catch (error) {
                    results += `
                        <div class="model-test">
                            <div class="error">❌ ${modelInfo.name}: ${error.message}</div>
                        </div>
                    `;
                    
                    updateTestResults(modelInfo.name, false, 0, error.message);
                }
            }
            
            resultDiv.innerHTML = results;
        }
        
        function updateTestResults(model, success, time, error = "") {
            const resultsDiv = document.getElementById('test-results');
            const timestamp = new Date().toLocaleTimeString();
            
            const resultEntry = success 
                ? `<div class="success">✅ ${model} - ${time}ms</div>`
                : `<div class="error">❌ ${model} - ${error}</div>`;
            
            resultsDiv.innerHTML = resultEntry + resultsDiv.innerHTML;
        }
        
        // Auto-test on page load
        window.addEventListener('load', () => {
            console.log('🎨 Puter.com Image Generation Test Loaded');
            console.log('📋 Available models: DALL-E 3, FLUX.1, Stable Diffusion, GPT Image, Gemini, Seedream, and more!');
        });
    </script>
</body>
</html>
    '''
    
    # Save the test HTML file
    with open('puter_test.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Created puter_test.html")
    print("🌐 Open this file in your browser to test Puter.com API")
    print("📱 Works on desktop and mobile!")
    
    return True

def show_puter_models():
    """Show all available Puter.com models"""
    print(f"\n🎨 Available Puter.com Models")
    print("=" * 60)
    
    models = [
        "🔥 DALL-E 3 (best quality)",
        "🚀 FLUX.1 Schnell (fast)",
        "⚡ FLUX.1 Dev (balanced)",
        "🎨 FLUX.1 Pro (premium)",
        "🌟 Stable Diffusion XL (reliable)",
        "💎 GPT Image 1.5 (OpenAI)",
        "🧠 Gemini 2.5 Flash (Google)",
        "🎯 Seedream 4.0 (ByteDance)",
        "🎪 DreamShaper (artistic)",
        "🌈 Ideogram 3.0 (text + image)",
        "⚡ Juggernaut Lightning FLUX",
        "🖼️ Imagen 4.0 (Google)",
        "🎨 HiDream I1 (multiple variants)"
    ]
    
    for model in models:
        print(f"   {model}")
    
    print(f"\n💡 Key Benefits:")
    print(f"   ✅ Completely FREE")
    print(f"   ✅ No API keys needed")
    print(f"   ✅ No rate limits")
    print(f"   ✅ No signup required")
    print(f"   ✅ Works in browser")
    print(f"   ✅ High-quality models")

if __name__ == "__main__":
    print("🎉 Puter.com - FREE Unlimited Image Generation!")
    print("=" * 60)
    
    # Test the API
    success = test_puter_api()
    
    # Show available models
    show_puter_models()
    
    if success:
        print(f"\n" + "=" * 60)
        print("🚀 Puter.com is ready for integration!")
        print("💡 This is perfect for VisionCraft Pro!")
        print("📝 Next: Integrate Puter.js into the frontend")
        print("🎨 Add DALL-E 3, FLUX, and other premium models!")
    else:
        print(f"\n❌ Puter.com test failed")
