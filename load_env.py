#!/usr/bin/env python3
"""
Load environment variables from keys.txt file
Run this before starting the VisionCraft server
"""

import os
from pathlib import Path

def load_env_from_file(env_file="keys.txt"):
    """Load environment variables from a file"""
    env_path = Path(env_file)
    
    if not env_path.exists():
        print(f"❌ Environment file {env_file} not found")
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

if __name__ == "__main__":
    load_env_from_file()
