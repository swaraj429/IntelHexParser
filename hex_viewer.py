#!/usr/bin/env python3
"""
Intel HEX Viewer - Main Entry Point

A comprehensive GUI application for viewing and analyzing Intel HEX files.

This is the main entry point for the restructured, modular version of the
Intel HEX Viewer application.

Usage:
    python hex_viewer.py

Features:
    - Intel HEX file loading and display
    - Symbol navigation through map files
    - C structure parsing and interpretation
    - Memory analysis and visualization
    - Export capabilities (CSV, Binary)
    - Search functionality
    - Customizable display options

Author: Open Source Contributors
License: MIT
Version: 1.0.0
"""

import sys
import os

# Add the intelhex_viewer directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'intelhex_viewer'))

try:
    import tkinter as tk
    from intelhex_viewer.main_app import HexViewerApp
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("\nRequired dependencies:")
    print("- tkinter (usually included with Python)")
    print("- intelhex (install with: pip install intelhex)")
    sys.exit(1)


def check_dependencies():
    """Check if all required dependencies are available."""
    missing_deps = []
    
    # Check for intelhex
    try:
        import intelhex
    except ImportError:
        missing_deps.append("intelhex")
    
    # Check for tkinter
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")
    
    if missing_deps:
        print("Missing required dependencies:")
        for dep in missing_deps:
            if dep == "intelhex":
                print(f"  {dep} - install with: pip install {dep}")
            elif dep == "tkinter":
                print(f"  {dep} - install with your system package manager")
                print("    Ubuntu/Debian: sudo apt install python3-tk")
                print("    CentOS/RHEL: sudo yum install tkinter")
                print("    Windows: included with Python from python.org")
        return False
    
    return True


def main():
    """Main application entry point."""
    # Check Python version
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    try:
        # Create and configure main window
        root = tk.Tk()
        
        # Initialize application
        app = HexViewerApp(root)
        
        # Set minimum window size
        root.minsize(800, 600)
        
        # Set default window size and center it
        root.update_idletasks()
        width = 1200
        height = 800
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Configure window icon if available
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
        if os.path.exists(icon_path):
            try:
                root.iconbitmap(icon_path)
            except tk.TclError:
                pass  # Icon loading failed, continue without it
        
        # Start the application main loop
        print("Starting Intel HEX Viewer...")
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 