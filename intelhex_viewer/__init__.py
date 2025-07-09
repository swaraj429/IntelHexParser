"""
Intel HEX Viewer - A comprehensive GUI application for viewing and analyzing Intel HEX files.

This package provides tools for:
- Loading and viewing Intel HEX files
- Symbol navigation through map files
- C structure parsing and interpretation
- Memory analysis and visualization
- Export capabilities

Author: Open Source Contributors
License: MIT
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Open Source Contributors"
__license__ = "MIT"

from .main_app import HexViewerApp, main
from .hex_parser import HexDataParser
from .structure_parser import CStructureParser, StructField, Endianness
from .symbol_manager import SymbolManager, Symbol

__all__ = [
    "HexViewerApp",
    "main",
    "HexDataParser", 
    "CStructureParser",
    "StructField",
    "Endianness",
    "SymbolManager",
    "Symbol"
] 