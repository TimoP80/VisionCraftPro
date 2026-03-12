"""
VisionCraft Pro GUI Setup Script
Creates an installable package for the VisionCraft GUI Manager
"""

from setuptools import setup, find_packages
import os
import sys

# Read README if it exists
def read_readme():
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    return "VisionCraft Pro GUI Manager - Manage Modal and Backend servers with an easy-to-use interface"

# Read requirements
def read_requirements():
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="visioncraft-gui",
    version="1.3.0",
    description="VisionCraft Pro GUI Manager - Manage Modal and Backend servers",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="VisionCraft Team",
    author_email="support@visioncraft.pro",
    url="https://github.com/timop80/visioncraft-pro",
    py_modules=["visioncraft_gui"],
    include_package_data=True,
    install_requires=[
        "requests",
        "pillow",
        "torch",
        "torchvision",
        "diffusers",
        "transformers",
        "accelerate",
        "fastapi",
        "uvicorn",
        "modal",
        "huggingface-hub",
        "python-dotenv",
        "google-generativeai",
        "anthropic",
        "openai"
    ],
    entry_points={
        "console_scripts": [
            "visioncraft-gui=visioncraft_gui:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: System :: Distributed Computing",
    ],
    keywords="ai image-generation gui modal stable-diffusion",
    python_requires=">=3.8",
    project_urls={
        "Bug Reports": "https://github.com/timop80/visioncraft-pro/issues",
        "Source": "https://github.com/timop80/visioncraft-pro",
        "Documentation": "https://github.com/timop80/visioncraft-pro#readme",
    },
)
