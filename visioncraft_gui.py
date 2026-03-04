"""
VisionCraft Pro GUI Manager
A GUI application for managing Modal and Backend servers simultaneously
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import time
import os
import sys
import json
import signal
from pathlib import Path
import requests

class VisionCraftGUIManager:
    """Main GUI application for managing VisionCraft servers"""

    def __init__(self, root):
        self.root = root
        self.root.title("VisionCraft Pro - Server Manager")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)

        # Server processes
        self.backend_process = None
        self.modal_process = None

        # Status tracking
        self.backend_running = False
        self.modal_running = False

        # Configuration
        self.config_file = Path.home() / ".visioncraft" / "config.json"
        self.config = self.load_config()

        self.setup_ui()
        self.load_existing_config()

    def setup_ui(self):
        """Setup the main UI components"""
        # Create main notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Server Control Tab
        self.control_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.control_frame, text="Server Control")
        self.setup_control_tab()

        # Configuration Tab
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="Configuration")
        self.setup_config_tab()

        # Logs Tab
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text="Logs")
        self.setup_logs_tab()

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def setup_control_tab(self):
        """Setup the server control tab"""
        # Server Status Section
        status_frame = ttk.LabelFrame(self.control_frame, text="Server Status")
        status_frame.pack(fill=tk.X, padx=10, pady=10)

        # Backend Status
        ttk.Label(status_frame, text="Backend Server:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.backend_status_var = tk.StringVar(value="Stopped")
        ttk.Label(status_frame, textvariable=self.backend_status_var, foreground="red").grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        # Modal Status
        ttk.Label(status_frame, text="Modal Server:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.modal_status_var = tk.StringVar(value="Stopped")
        ttk.Label(status_frame, textvariable=self.modal_status_var, foreground="red").grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        # Control Buttons Section
        control_frame = ttk.LabelFrame(self.control_frame, text="Server Control")
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        # Backend Controls
        ttk.Button(control_frame, text="Start Backend", command=self.start_backend).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(control_frame, text="Stop Backend", command=self.stop_backend).grid(row=0, column=1, padx=5, pady=5)

        # Modal Controls
        ttk.Button(control_frame, text="Start Modal", command=self.start_modal).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(control_frame, text="Stop Modal", command=self.stop_modal).grid(row=1, column=1, padx=5, pady=5)

        # Quick Actions
        ttk.Button(control_frame, text="Start All", command=self.start_all).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(control_frame, text="Stop All", command=self.stop_all).grid(row=2, column=1, padx=5, pady=5)

        # Web Access Section
        web_frame = ttk.LabelFrame(self.control_frame, text="Web Access")
        web_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(web_frame, text="Open VisionCraft Web UI", command=self.open_web_ui).pack(pady=5)
        ttk.Button(web_frame, text="Ping Backend Server", command=self.ping_backend).pack(pady=5)
        ttk.Button(web_frame, text="Open Modal Status", command=self.open_modal_status).pack(pady=5)

    def setup_config_tab(self):
        """Setup the configuration tab"""
        # API Keys Section
        api_frame = ttk.LabelFrame(self.config_frame, text="API Keys")
        api_frame.pack(fill=tk.X, padx=10, pady=10)

        # Leonardo.ai API Key
        ttk.Label(api_frame, text="Leonardo.ai API Key:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.leonardo_key_var = tk.StringVar()
        ttk.Entry(api_frame, textvariable=self.leonardo_key_var, show="*").grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)

        # OpenAI API Key
        ttk.Label(api_frame, text="OpenAI API Key:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.openai_key_var = tk.StringVar()
        ttk.Entry(api_frame, textvariable=self.openai_key_var, show="*").grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)

        # Anthropic API Key
        ttk.Label(api_frame, text="Anthropic API Key:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.anthropic_key_var = tk.StringVar()
        ttk.Entry(api_frame, textvariable=self.anthropic_key_var, show="*").grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)

        # Gemini API Key
        ttk.Label(api_frame, text="Gemini API Key:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.gemini_key_var = tk.StringVar()
        ttk.Entry(api_frame, textvariable=self.gemini_key_var, show="*").grid(row=3, column=1, sticky=tk.EW, padx=5, pady=2)

        # Configure grid weights
        api_frame.columnconfigure(1, weight=1)

        # Paths Section
        path_frame = ttk.LabelFrame(self.config_frame, text="Paths")
        path_frame.pack(fill=tk.X, padx=10, pady=10)

        # Project Directory
        ttk.Label(path_frame, text="VisionCraft Directory:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.project_path_var = tk.StringVar()
        path_entry = ttk.Entry(path_frame, textvariable=self.project_path_var)
        path_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(path_frame, text="Browse", command=self.browse_project_path).grid(row=0, column=2, padx=5, pady=2)

        # Python Executable
        ttk.Label(path_frame, text="Python Executable:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.python_path_var = tk.StringVar(value=sys.executable)
        ttk.Entry(path_frame, textvariable=self.python_path_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)

        path_frame.columnconfigure(1, weight=1)

        # Save Button
        ttk.Button(self.config_frame, text="Save Configuration", command=self.save_config).pack(pady=10)

    def setup_logs_tab(self):
        """Setup the logs tab with colored text support"""
        # Log display with colored text support
        self.log_text = tk.Text(self.logs_frame, wrap=tk.WORD, height=20, font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(self.logs_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        # Pack the text widget and scrollbar
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

        # Configure color tags
        self.log_text.tag_configure("timestamp", foreground="#666666")
        self.log_text.tag_configure("backend", foreground="#00AA00", font=("Consolas", 9, "bold"))
        self.log_text.tag_configure("modal", foreground="#0077FF", font=("Consolas", 9, "bold"))
        self.log_text.tag_configure("error", foreground="#FF4444")
        self.log_text.tag_configure("warning", foreground="#FFAA00")
        self.log_text.tag_configure("success", foreground="#00AA00")
        self.log_text.tag_configure("info", foreground="#AAAAAA")
        
        # Make text widget read-only
        self.log_text.config(state=tk.DISABLED)

        # Log controls
        control_frame = ttk.Frame(self.logs_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Button(control_frame, text="Clear Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Save Logs", command=self.save_logs).pack(side=tk.LEFT)

        # Auto-scroll checkbox
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Auto-scroll", variable=self.auto_scroll_var).pack(side=tk.RIGHT)

    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.log_message(f"Error loading config: {e}")

        return {
            "api_keys": {
                "leonardo": "",
                "openai": "",
                "anthropic": "",
                "gemini": ""
            },
            "paths": {
                "project_dir": str(Path.cwd()),
                "python_exe": sys.executable
            }
        }

    def save_config(self):
        """Save configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            self.config = {
                "api_keys": {
                    "leonardo": self.leonardo_key_var.get(),
                    "openai": self.openai_key_var.get(),
                    "anthropic": self.anthropic_key_var.get(),
                    "gemini": self.gemini_key_var.get()
                },
                "paths": {
                    "project_dir": self.project_path_var.get(),
                    "python_exe": self.python_path_var.get()
                }
            }

            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)

            self.log_message("Configuration saved successfully")
            messagebox.showinfo("Success", "Configuration saved successfully")

        except Exception as e:
            self.log_message(f"Error saving config: {e}")
            messagebox.showerror("Error", f"Failed to save configuration: {e}")

    def load_existing_config(self):
        """Load existing configuration into UI"""
        # API Keys
        self.leonardo_key_var.set(self.config.get("api_keys", {}).get("leonardo", ""))
        self.openai_key_var.set(self.config.get("api_keys", {}).get("openai", ""))
        self.anthropic_key_var.set(self.config.get("api_keys", {}).get("anthropic", ""))
        self.gemini_key_var.set(self.config.get("api_keys", {}).get("gemini", ""))

        # Paths
        self.project_path_var.set(self.config.get("paths", {}).get("project_dir", str(Path.cwd())))
        self.python_path_var.set(self.config.get("paths", {}).get("python_exe", sys.executable))

    def browse_project_path(self):
        """Browse for project directory"""
        directory = filedialog.askdirectory(title="Select VisionCraft Project Directory")
        if directory:
            self.project_path_var.set(directory)

    def start_backend(self):
        """Start the backend server"""
        if self.backend_running:
            messagebox.showwarning("Warning", "Backend server is already running")
            return

        try:
            project_dir = self.project_path_var.get()
            python_exe = self.python_path_var.get()

            self.log_message(f"DEBUG: Project directory: {project_dir}")
            self.log_message(f"DEBUG: Python executable: {python_exe}")
            self.log_message(f"DEBUG: Command: {[python_exe, 'visioncraft_server.py']}")

            if not os.path.exists(project_dir):
                raise Exception(f"Project directory does not exist: {project_dir}")

            if not os.path.exists(os.path.join(project_dir, "visioncraft_server.py")):
                raise Exception(f"visioncraft_server.py not found in project directory: {project_dir}")

            # Create environment variables for API keys
            env = os.environ.copy()
            env.update({
                "LEONARDO_API_KEY": self.leonardo_key_var.get(),
                "OPENAI_API_KEY": self.openai_key_var.get(),
                "ANTHROPIC_API_KEY": self.anthropic_key_var.get(),
                "GEMINI_API_KEY": self.gemini_key_var.get()
            })

            self.log_message("DEBUG: Starting backend server subprocess...")

            # Start backend server with proper unicode handling for Windows
            self.backend_process = subprocess.Popen(
                [python_exe, "visioncraft_server.py"],
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',  # Explicitly set UTF-8 encoding
                errors='replace',  # Replace unencodable characters
                bufsize=1,  # Line buffered
                universal_newlines=True,
                env=env
            )

            self.log_message("DEBUG: Subprocess started, checking if alive...")

            # Give it a moment to start and check if it's still running
            time.sleep(0.5)
            if self.backend_process.poll() is not None:
                # Process has already exited
                return_code = self.backend_process.returncode
                self.log_message(f"ERROR: Backend server exited immediately with code {return_code}")
                # Try to read any error output
                try:
                    remaining_output = self.backend_process.stdout.read()
                    if remaining_output.strip():
                        self.log_message(f"ERROR OUTPUT: {remaining_output.strip()}")
                except:
                    pass
                raise Exception(f"Backend server process exited immediately with code {return_code}")

            self.backend_running = True
            self.backend_status_var.set("Running")
            self.status_var.set("Backend server started")
            self.log_message("Backend server started successfully")

            # Start monitoring thread
            threading.Thread(target=self.monitor_backend, daemon=True).start()

        except Exception as e:
            self.log_message(f"Failed to start backend: {e}")
            messagebox.showerror("Error", f"Failed to start backend server: {e}")

    def stop_backend(self):
        """Stop the backend server"""
        if not self.backend_running:
            return

        try:
            if self.backend_process:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                self.backend_process = None

            self.backend_running = False
            self.backend_status_var.set("Stopped")
            self.status_var.set("Backend server stopped")
            self.log_message("Backend server stopped")

        except Exception as e:
            self.log_message(f"Error stopping backend: {e}")
            # Force kill if necessary
            if self.backend_process:
                try:
                    self.backend_process.kill()
                except:
                    pass

    def start_modal(self):
        """Start the modal server"""
        if self.modal_running:
            messagebox.showwarning("Warning", "Modal server is already running")
            return

        try:
            project_dir = self.project_path_var.get()

            if not os.path.exists(project_dir):
                raise Exception(f"Project directory does not exist: {project_dir}")

            # Start modal server with proper unicode handling for Windows
            self.modal_process = subprocess.Popen(
                ["modal", "serve", "modal_web.py"],
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',  # Explicitly set UTF-8 encoding
                errors='replace',  # Replace unencodable characters
                bufsize=1,  # Line buffered
                universal_newlines=True
            )

            self.modal_running = True
            self.modal_status_var.set("Running")
            self.status_var.set("Modal server started")
            self.log_message("Modal server started")

            # Start monitoring thread
            threading.Thread(target=self.monitor_modal, daemon=True).start()

        except Exception as e:
            self.log_message(f"Failed to start modal: {e}")
            messagebox.showerror("Error", f"Failed to start modal server: {e}")

    def stop_modal(self):
        """Stop the modal server"""
        if not self.modal_running:
            return

        try:
            if self.modal_process:
                self.modal_process.terminate()
                self.modal_process.wait(timeout=5)
                self.modal_process = None

            self.modal_running = False
            self.modal_status_var.set("Stopped")
            self.status_var.set("Modal server stopped")
            self.log_message("Modal server stopped")

        except Exception as e:
            self.log_message(f"Error stopping modal: {e}")
            # Force kill if necessary
            if self.modal_process:
                try:
                    self.modal_process.kill()
                except:
                    pass

    def start_all(self):
        """Start both servers"""
        self.start_backend()
        time.sleep(2)  # Brief delay
        self.start_modal()

    def stop_all(self):
        """Stop both servers"""
        self.stop_modal()
        self.stop_backend()

    def monitor_backend(self):
        """Monitor backend server output"""
        if self.backend_process:
            try:
                for line in iter(self.backend_process.stdout.readline, ''):
                    if line.strip():
                        self.log_message(f"[BACKEND] {line.strip()}")

                    if not self.backend_running:
                        break
            except:
                pass

    def monitor_modal(self):
        """Monitor modal server output"""
        if self.modal_process:
            try:
                for line in iter(self.modal_process.stdout.readline, ''):
                    if line.strip():
                        self.log_message(f"[MODAL] {line.strip()}")

                    if not self.modal_running:
                        break
            except:
                pass

    def ping_backend(self):
        """Ping the backend server to check if it's responding to HTTP requests"""
        try:
            self.log_message("Pinging backend server at http://localhost:8000...")

            # Try to connect with a short timeout
            response = requests.get("http://localhost:8000", timeout=5)

            if response.status_code == 200:
                self.log_message(f"✅ Backend server is responding! Status: {response.status_code}")
                try:
                    # Try to get server info if available
                    info_response = requests.get("http://localhost:8000/info", timeout=5)
                    if info_response.status_code == 200:
                        info = info_response.json()
                        self.log_message(f"📊 Server info: {info.get('version', 'unknown version')}")
                except:
                    pass  # Info endpoint might not exist, that's ok
            else:
                self.log_message(f"⚠️ Backend server responded with status: {response.status_code}")

        except requests.exceptions.ConnectionError:
            self.log_message("❌ Backend server is not responding - connection refused")
            self.log_message("💡 Check if the backend server process is still running")

        except requests.exceptions.Timeout:
            self.log_message("⏰ Backend server ping timed out - server may be slow or unresponsive")

        except Exception as e:
            self.log_message(f"❌ Error pinging backend server: {e}")

    def open_web_ui(self):
        """Open the VisionCraft web UI"""
        try:
            webbrowser.open("http://localhost:8000")
        except Exception as e:
            self.log_message(f"Failed to open web UI: {e}")

    def open_modal_status(self):
        """Open modal status page"""
        try:
            webbrowser.open("https://modal.com/apps")
        except Exception as e:
            self.log_message(f"Failed to open modal status: {e}")

    def log_message(self, message):
        """Add message to log display with colored text and unicode support"""
        timestamp = time.strftime("%H:%M:%S")
        
        # Enable text widget for editing
        self.log_text.config(state=tk.NORMAL)
        
        # Insert timestamp
        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Determine message type and apply appropriate color
        message_lower = message.lower()
        
        if "[backend]" in message_lower:
            # Backend messages in green
            prefix = "[BACKEND] "
            self.log_text.insert(tk.END, prefix, "backend")
            remaining = message.replace("[BACKEND]", "").strip()
            if any(word in remaining.lower() for word in ["error", "failed", "exception"]):
                self.log_text.insert(tk.END, remaining + "\n", "error")
            elif any(word in remaining.lower() for word in ["warning", "warn"]):
                self.log_text.insert(tk.END, remaining + "\n", "warning")
            elif any(word in remaining.lower() for word in ["success", "complete", "started"]):
                self.log_text.insert(tk.END, remaining + "\n", "success")
            else:
                self.log_text.insert(tk.END, remaining + "\n", "info")
                
        elif "[modal]" in message_lower:
            # Modal messages in blue
            prefix = "[MODAL] "
            self.log_text.insert(tk.END, prefix, "modal")
            remaining = message.replace("[MODAL]", "").strip()
            if any(word in remaining.lower() for word in ["error", "failed", "exception"]):
                self.log_text.insert(tk.END, remaining + "\n", "error")
            elif any(word in remaining.lower() for word in ["warning", "warn"]):
                self.log_text.insert(tk.END, remaining + "\n", "warning")
            elif any(word in remaining.lower() for word in ["success", "complete", "started"]):
                self.log_text.insert(tk.END, remaining + "\n", "success")
            else:
                self.log_text.insert(tk.END, remaining + "\n", "info")
                
        elif any(word in message_lower for word in ["error", "failed", "exception", "traceback"]):
            # Error messages in red
            self.log_text.insert(tk.END, message + "\n", "error")
            
        elif any(word in message_lower for word in ["warning", "warn", "deprecated"]):
            # Warning messages in orange
            self.log_text.insert(tk.END, message + "\n", "warning")
            
        elif any(word in message_lower for word in ["success", "complete", "started", "ready", "✅"]):
            # Success messages in green
            self.log_text.insert(tk.END, message + "\n", "success")
            
        else:
            # Default messages in gray
            self.log_text.insert(tk.END, message + "\n", "info")
        
        # Make text widget read-only again
        self.log_text.config(state=tk.DISABLED)

        # Auto-scroll if enabled
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)

    def clear_logs(self):
        """Clear the log display"""
        self.log_text.delete(1.0, tk.END)

    def save_logs(self):
        """Save logs to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log_message(f"Logs saved to {filename}")
        except Exception as e:
            self.log_message(f"Failed to save logs: {e}")

    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to stop all servers before quitting?"):
            self.stop_all()

        self.root.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = VisionCraftGUIManager(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
