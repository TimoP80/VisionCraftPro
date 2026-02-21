"""
Start Modal app in background for VisionCraft integration
"""

import subprocess
import time
import sys
import os

def main():
    print("[MODAL-START] Starting Modal app in background...")
    
    # Start Modal app in background
    try:
        # Use modal run with required parameters
        process = subprocess.Popen([
            "modal", "run", "modal_integration.py", 
            "--prompt", "keep_alive",  # Required parameter
            "--model-name", "runwayml/stable-diffusion-v1-5"  # Required parameter
        ], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
        )
        
        print("[MODAL-START] Modal app started with PID:", process.pid)
        print("[MODAL-START] Modal app is running in background...")
        print("[MODAL-START] Press Ctrl+C to stop")
        
        # Keep the process running and monitor output
        app_running = False
        while True:
            # Check if Modal app is running by looking for success message
            output = process.stdout.readline()
            if output:
                print(f"[MODAL-OUTPUT] {output.strip()}")
                if "Starting Modal app in server mode" in output or "App completed" in output:
                    app_running = True
                    print("[MODAL-START] ✅ Modal app is now running and ready!")
                elif "ERROR" in output or "Usage:" in output:
                    print(f"[MODAL-ERROR] Modal app error: {output.strip()}")
                    break
            
            # Check if process is still running
            if process.poll() is not None:
                print(f"[MODAL-START] Modal app exited with code: {process.returncode}")
                break
                
            # Small delay to prevent busy waiting
            time.sleep(0.5)
                    
    except KeyboardInterrupt:
        print("\n[MODAL-START] Stopping Modal app...")
        process.terminate()
        process.wait()
        print("[MODAL-START] Modal app stopped")
            
    except Exception as e:
        print(f"[MODAL-START] Error starting Modal app: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
