# Modal Setup Instructions

## Problem: Modal Generator Using Local GPU Instead of Remote

The issue is that Modal functions need to be properly deployed to run on Modal's cloud infrastructure, not locally.

## Solution: Proper Modal Setup

### 1. Install Modal
```bash
pip install modal
```

### 2. Authenticate with Modal
```bash
modal token
```

### 3. Start Modal App (IMPORTANT!)
In a **separate terminal**, run:
```bash
modal run modal_integration.py
```

This starts the Modal app and deploys the functions to Modal's cloud infrastructure.

### 4. Run VisionCraft Pro Server
In another terminal, run:
```bash
python visioncraft_server.py
```

### 5. Use Modal Generator
1. Open http://localhost:8000
2. Select "Modal H100 GPU" from the model dropdown
3. Enter a prompt and generate

## How It Works

- **Local**: VisionCraft Pro server runs locally
- **Remote**: When you select Modal, the `generate_image.remote()` call sends the request to Modal's cloud
- **Modal Cloud**: The function runs on Modal's A100/H100 GPUs in the cloud
- **Return**: Image bytes are sent back to your local server

## Debugging

Check the console output:
- `[MODAL-REMOTE]` messages indicate remote execution on Modal's infrastructure
- `[MODAL]` messages might indicate local execution (incorrect)

## Common Issues

1. **"Modal not installed"**: Install with `pip install modal`
2. **"Modal app not found"**: Run `modal run modal_integration.py` first
3. **"CUDA not available on Modal"**: Modal infrastructure issue, retry
4. **Local GPU usage**: Make sure Modal app is running before starting server

## Verification

When working correctly, you should see:
- Local server: `[MODAL] Calling remote Modal function...`
- Modal cloud: `[MODAL-REMOTE] Running on Modal cloud GPU (NOT local GPU)`
- Modal cloud: `[MODAL-REMOTE] Using GPU: NVIDIA A100` (or similar)

The generation will happen on Modal's cloud GPUs, NOT your local GPU!
