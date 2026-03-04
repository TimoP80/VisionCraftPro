# VisionCraft Pro GUI Manager

A comprehensive GUI application for managing VisionCraft Pro servers, allowing you to run both the Modal web server and backend simultaneously with an easy-to-use interface.

## Features

- 🚀 **Dual Server Management**: Start/stop Modal and Backend servers independently or together
- 🔧 **Configuration Management**: Securely store API keys for Leonardo.ai, OpenAI, Anthropic, and Gemini
- 📊 **Real-time Monitoring**: Live logs and status updates from both servers
- 🌐 **Web Access**: Direct links to open VisionCraft web UI and Modal status
- 💾 **Persistent Settings**: Saves configuration between sessions
- 🖥️ **Cross-platform**: Works on Windows, macOS, and Linux

## Installation

### Windows (Recommended)

1. **Download VisionCraft Pro** to your computer
2. **Run the installer**:
   ```batch
   install_gui.bat
   ```
3. **Create desktop shortcut** (optional):
   ```batch
   create_shortcut.bat
   ```
4. **Run the GUI**:
   ```batch
   run_gui.bat
   ```

### Manual Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install the GUI
pip install -e .

# Run the GUI
visioncraft-gui
```

## Usage

### First Time Setup

1. **Launch VisionCraft GUI** using `run_gui.bat` or `visioncraft-gui`
2. **Go to Configuration tab** and enter your API keys:
   - Leonardo.ai API Key
   - OpenAI API Key (optional)
   - Anthropic API Key (optional)
   - Gemini API Key (optional)
3. **Set the VisionCraft project directory** path
4. **Save configuration**

### Running Servers

1. **Server Control tab**:
   - Click "Start Backend" to start the VisionCraft backend server
   - Click "Start Modal" to start the Modal cloud server
   - Or click "Start All" to start both servers
2. **Monitor status** in the status indicators
3. **View logs** in the Logs tab for real-time output

### Accessing VisionCraft

- **Web UI**: Click "Open VisionCraft Web UI" to open http://localhost:8000
- **Modal Status**: Click "Open Modal Status" to check Modal cloud deployments

## Server Ports

- **Backend Server**: Runs on `http://localhost:8000`
- **Modal Server**: Runs on Modal cloud infrastructure

## Troubleshooting

### Backend Won't Start
- Check that the VisionCraft project directory path is correct
- Ensure Python executable path is valid
- Verify API keys are properly configured

### Modal Won't Start
- Ensure Modal CLI is installed: `pip install modal`
- Check that you're logged in: `modal token set`
- Verify Hugging Face token is configured

### GUI Won't Launch
- Make sure tkinter is available (usually included with Python)
- Try reinstalling: `pip install tk tkinter`

### Permission Errors
- On Windows, run as Administrator if needed
- On macOS/Linux, check file permissions

## Configuration File

Settings are saved to: `~/.visioncraft/config.json`

```json
{
  "api_keys": {
    "leonardo": "your-leonardo-key",
    "openai": "your-openai-key",
    "anthropic": "your-anthropic-key",
    "gemini": "your-gemini-key"
  },
  "paths": {
    "project_dir": "/path/to/visioncraft",
    "python_exe": "/path/to/python"
  }
}
```

## System Requirements

- **Python**: 3.8 or higher
- **RAM**: 8GB minimum, 16GB recommended
- **Disk Space**: 10GB free space
- **Network**: Internet connection for Modal and API services

## API Keys Setup

### Leonardo.ai
1. Sign up at https://leonardo.ai
2. Go to API settings
3. Generate an API key

### OpenAI
1. Sign up at https://platform.openai.com
2. Create an API key in your dashboard

### Anthropic
1. Sign up at https://console.anthropic.com
2. Create an API key

### Gemini
1. Go to https://ai.google.dev
2. Create a Gemini API key

## Development

### Project Structure
```
visioncraft-gui/
├── visioncraft_gui.py      # Main GUI application
├── setup.py               # Package installer
├── requirements.txt       # Dependencies
├── install_gui.bat       # Windows installer
├── run_gui.bat          # Windows runner
├── create_shortcut.bat  # Desktop shortcut creator
└── README.md            # This file
```

### Adding New Features

The GUI is built with tkinter and follows a modular design:

- `VisionCraftGUIManager`: Main application class
- Tab-based interface for different functions
- Subprocess management for server control
- Configuration persistence with JSON

## License

MIT License - See LICENSE file for details.

## Support

- **Issues**: https://github.com/timop80/visioncraft-pro/issues
- **Documentation**: https://github.com/timop80/visioncraft-pro#readme
- **Community**: Join our Discord server

---

**VisionCraft Pro** - AI-powered image generation made simple 🎨🤖
