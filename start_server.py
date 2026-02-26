#!/usr/bin/env python3
"""
VisionCraft Pro Server Startup Script
Loads environment variables and starts the server
"""

import sys
import os
import subprocess
from pathlib import Path

def load_env_from_file(env_file="keys.txt"):
    """Load environment variables from a file"""
    env_path = Path(env_file)
    
    if not env_path.exists():
        print(f"❌ Environment file {env_file} not found")
        print(f"Please create {env_file} with your HF_TOKEN")
        return False
    
    print(f"🔑 Loading environment variables from {env_file}")
    
    with open(env_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#') or line.startswith('---'):
                continue
            
            # Parse KEY=VALUE format
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Set environment variable
                os.environ[key] = value
                print(f"✅ {key} loaded")
            else:
                print(f"⚠️  Line {line_num}: Invalid format (should be KEY=VALUE): {line}")
    
    print(f"🎉 Environment variables loaded successfully!")
    return True

def main():
    """Main startup function"""
    print("🚀 Starting VisionCraft Pro Server...")
    
    # Load environment variables
    if not load_env_from_file():
        sys.exit(1)
    
    # Check if HF_TOKEN is set
    hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
    if not hf_token or hf_token == "YOUR_HF_TOKEN_HERE":
        print("⚠️  HF_TOKEN is not set or is still the placeholder")
        print("Please edit keys.txt and replace YOUR_HF_TOKEN_HERE with your actual Hugging Face token")
        print("Get your token from: https://huggingface.co/settings/tokens")
        sys.exit(1)
    
    print(f"✅ HF_TOKEN is configured (length: {len(hf_token)} chars)")
    
    # Start the server
    print("🌐 Starting FastAPI server...")
    try:
        import uvicorn
        from visioncraft_server import app
        
        # Server configuration
        host = "0.0.0.0"
        port = 8000
        
        print(f"🌐 Server will be available at: http://{host}:{port}")
        print("📝 Press Ctrl+C to stop the server")
        
        uvicorn.run(app, host=host, port=port, reload=False)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
