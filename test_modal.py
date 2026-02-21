"""
Test Modal Integration
Simple test to verify Modal is working
"""

import modal

try:
    # Test basic Modal import
    print("✅ Modal import successful")
    
    # Test app creation
    app = modal.App("test-modal")
    print("✅ Modal app created")
    
    # Test function
    @app.function()
    def test_function():
        return "Modal is working!"
    
    print("✅ Modal function defined")
    
    # Test remote call
    result = test_function.remote()
    print(f"✅ Modal remote call result: {result}")
    
except Exception as e:
    print(f"❌ Modal test failed: {e}")
    print(f"❌ Error type: {type(e).__name__}")
    import traceback
    print(f"❌ Traceback: {traceback.format_exc()}")
