"""
Test Modal connection from VisionCraft
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_modal_connection():
    """Test if Modal function can be called"""
    try:
        # Import Modal function
        import modal_server
        from modal_server import generate_image
        
        print("[TEST] Modal function imported successfully")
        print(f"[TEST] Function object: {generate_image}")
        
        # Test call
        print("[TEST] Testing Modal function call...")
        result = await generate_image.remote.aio("test prompt", "runwayml/stable-diffusion-v1-5")
        print(f"[TEST] Success! Got {len(result)} bytes")
        
        return True
        
    except Exception as e:
        print(f"[TEST] Error: {e}")
        print(f"[TEST] Error type: {type(e).__name__}")
        import traceback
        print(f"[TEST] Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("[TEST] Testing Modal connection...")
    success = asyncio.run(test_modal_connection())
    
    if success:
        print("[TEST] ✅ Modal connection successful!")
    else:
        print("[TEST] ❌ Modal connection failed!")
    
    print("[TEST] Done.")
