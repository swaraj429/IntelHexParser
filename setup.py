#!/usr/bin/env python3
"""
Setup script for Intel HEX Viewer.

This setup.py file enables the Intel HEX Viewer to be installed as a 
standard Python package using pip.
"""

from setuptools import setup, find_packages
import os
import sys

# Ensure we're using Python 3.6+
if sys.version_info < (3, 6):
    sys.exit("Error: Python 3.6 or higher is required")

# Read version from package
def get_version():
    """Extract version from package __init__.py"""
    with open(os.path.join("intelhex_viewer", "__init__.py"), "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.0"

# Read long description from README
def get_long_description():
    """Get the long description from README.md"""
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "A comprehensive GUI application for viewing and analyzing Intel HEX files."

# Read requirements
def get_requirements():
    """Get requirements from requirements.txt"""
    try:
        with open("requirements.txt", "r") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return ["intelhex>=2.3.0"]

# Read development requirements
def get_dev_requirements():
    """Get development requirements"""
    try:
        with open("requirements-dev.txt", "r") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "pyinstaller>=4.0"
        ]

setup(
    # Package metadata
    name="intel-hex-viewer",
    version=get_version(),
    author="Intel HEX Viewer Contributors",
    author_email="contributors@intelhex-viewer.org",
    description="A comprehensive GUI application for viewing and analyzing Intel HEX files",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/contributors/intel-hex-viewer",
    
    # Package structure
    packages=find_packages(),
    package_data={
        "intelhex_viewer": ["*.txt", "*.md"],
    },
    include_package_data=True,
    
    # Requirements
    python_requires=">=3.6",
    install_requires=get_requirements(),
    extras_require={
        "dev": get_dev_requirements(),
        "build": ["pyinstaller>=4.0"],
    },
    
    # Entry points
    entry_points={
        "console_scripts": [
            "intel-hex-viewer=intelhex_viewer.main_app:main",
            "hex-viewer=intelhex_viewer.main_app:main",
        ],
        "gui_scripts": [
            "intel-hex-viewer-gui=intelhex_viewer.main_app:main",
        ],
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: System :: Hardware",
        "Topic :: Utilities",
        "Environment :: X11 Applications",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
    ],
    
    # Keywords
    keywords="intel hex firmware embedded systems gui viewer analyzer",
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/contributors/intel-hex-viewer/issues",
        "Source": "https://github.com/contributors/intel-hex-viewer",
        "Documentation": "https://github.com/contributors/intel-hex-viewer/blob/main/README.md",
        "Contributing": "https://github.com/contributors/intel-hex-viewer/blob/main/CONTRIBUTING.md",
    },
    
    # Additional options
    zip_safe=False,  # For GUI applications
    platforms=["any"],
) 