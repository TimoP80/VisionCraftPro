"""
Leonardo.ai Quality Optimizer for SD 1.5
Maximizes image quality within the constraints of the basic Leonardo plan

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import requests
import json
import os
import time

def load_api_key():
    """Load Leonardo API key"""
    try:
        with open('api_keys.json', 'r') as f:
            keys = json.load(f)
            return keys.get('leonardo-api')
    except:
        return None

def create_premium_prompt_enhancer():
    """Create advanced prompt enhancement for SD 1.5 to maximize quality"""
    
    def enhance_prompt_for_sd15(prompt: str, style: str = "photorealistic") -> str:
        """Enhance prompt specifically for SD 1.5 to achieve premium quality"""
        
        # Base quality terms that work well with SD 1.5
        quality_base = [
            "high quality", "highly detailed", "sharp focus", "well-defined",
            "professional", "masterpiece", "best quality", "8k resolution"
        ]
        
        # Style-specific enhancements
        style_enhancements = {
            "photorealistic": [
                "photorealistic", "realistic", "lifelike", "professional photography",
                "DSLR", "shot on Sony A7R IV", "85mm lens", "f/1.4", "sharp details",
                "natural lighting", "studio lighting", "cinematic lighting"
            ],
            "portrait": [
                "photorealistic portrait", "detailed face", "realistic skin texture",
                "professional photography", "studio lighting", "soft lighting",
                "sharp eyes", "detailed hair", "natural expression", "high resolution"
            ],
            "cinematic": [
                "cinematic shot", "film still", "movie quality", "epic composition",
                "dramatic lighting", "cinematic color grading", "film grain",
                "anamorphic lens", "widescreen", "professional cinematography"
            ],
            "artistic": [
                "digital art", "concept art", "detailed illustration", "trending on artstation",
                "masterpiece", "award-winning", "highly detailed", "professional art",
                "sharp details", "vibrant colors", "perfect composition"
            ],
            "anime": [
                "high quality anime", "detailed anime art", "masterpiece", "best quality",
                "trending on pixiv", "sharp details", "vibrant colors", "professional anime art",
                "clean lines", "detailed background", "perfect anatomy"
            ]
        }
        
        # Determine content type and apply appropriate enhancements
        prompt_lower = prompt.lower()
        
        # Detect content type
        if "portrait" in prompt_lower or "woman" in prompt_lower or "man" in prompt_lower or "person" in prompt_lower:
            content_type = "portrait"
        elif "cinematic" in prompt_lower or "movie" in prompt_lower or "film" in prompt_lower:
            content_type = "cinematic"
        elif "anime" in prompt_lower or "manga" in prompt_lower:
            content_type = "anime"
        elif "art" in prompt_lower or "painting" in prompt_lower or "illustration" in prompt_lower:
            content_type = "artistic"
        else:
            content_type = "photorealistic"
        
        # Build enhanced prompt
        enhanced_parts = [prompt]
        
        # Add style-specific enhancements
        if content_type in style_enhancements:
            enhanced_parts.extend(style_enhancements[content_type])
        
        # Add base quality terms
        enhanced_parts.extend(quality_base)
        
        # Add technical photography terms for realism
        if content_type in ["photorealistic", "portrait", "cinematic"]:
            enhanced_parts.extend([
                "RAW photo", "no compression", "uncompressed", "high resolution",
                "professional grade", "commercial photography"
            ])
        
        return ", ".join(enhanced_parts)
    
    return enhance_prompt_for_sd15

def create_optimized_negative_prompt():
    """Create comprehensive negative prompt for SD 1.5"""
    return (
        "blurry, low quality, worst quality, low resolution, pixelated, "
        "jpeg artifacts, compression artifacts, noisy, grainy, distorted, "
        "deformed, disfigured, bad anatomy, bad proportions, extra limbs, "
        "missing limbs, fused fingers, too many fingers, watermark, signature, "
        "text, username, error, mutated, mutation, ugly, disgusting, "
        "cartoon, 3d, render, painting, drawing, sketch, amateur"
    )

def test_optimized_generation():
    """Test the optimized generation settings"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print("=" * 70)
    print("Testing Optimized Leonardo.ai Generation (SD 1.5)")
    print("=" * 70)
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Get the enhanced prompt function
    enhance_prompt = create_premium_prompt_enhancer()
    negative_prompt = create_optimized_negative_prompt()
    
    # Test different prompts with optimization
    test_prompts = [
        "beautiful woman with red hair",
        "stunning landscape with mountains",
        "cinematic city street at night",
        "anime character in fantasy setting"
    ]
    
    for i, base_prompt in enumerate(test_prompts):
        print(f"\n🧪 Test {i+1}: {base_prompt}")
        
        # Enhance the prompt
        enhanced_prompt = enhance_prompt(base_prompt, "photorealistic")
        print(f"📝 Enhanced: {enhanced_prompt[:100]}...")
        
        payload = {
            "prompt": enhanced_prompt,
            "width": 1024,
            "height": 1024,
            "num_images": 1,
            "presetStyle": "CREATIVE",  # Use creative style for better results
            "negative_prompt": negative_prompt,
            "num_inference_steps": 30,  # More steps for better quality
            "guidance_scale": 8.0,      # Higher guidance for better prompt adherence
            "contrast": 3.5
        }
        
        try:
            response = requests.post(
                "https://cloud.leonardo.ai/api/rest/v1/generations",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                generation_id = result.get('sdGenerationJob', {}).get('generationId')
                print(f"   ✅ Generation started: {generation_id}")
                
                # Wait and check
                time.sleep(8)
                gen_response = requests.get(
                    f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
                    headers=headers
                )
                
                if gen_response.status_code == 200:
                    gen_data = gen_response.json()
                    gen_info = gen_data.get('generations_by_pk', {})
                    status = gen_info.get('status')
                    
                    if status == 'COMPLETE':
                        print(f"   ✅ SUCCESS: Optimized generation completed!")
                        images = gen_info.get('generated_images', [])
                        if images:
                            img_url = images[0].get('url', '')
                            print(f"   🖼️  Image: {img_url}")
                    else:
                        print(f"   ⏳ Status: {status}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(2)  # Rate limiting

if __name__ == "__main__":
    test_optimized_generation()
