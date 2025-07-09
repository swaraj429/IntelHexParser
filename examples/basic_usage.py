#!/usr/bin/env python3
"""
Basic usage example for Intel HEX Viewer.

This example shows how to use the Intel HEX Viewer components
programmatically without the GUI.
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from intelhex_viewer.hex_parser import HexDataParser
from intelhex_viewer.structure_parser import CStructureParser, Endianness
from intelhex_viewer.symbol_manager import SymbolManager


def main():
    """Demonstrate basic usage of Intel HEX Viewer components."""
    print("Intel HEX Viewer - Basic Usage Example")
    print("=" * 40)
    
    # Initialize components
    hex_parser = HexDataParser()
    structure_parser = CStructureParser()
    symbol_manager = SymbolManager()
    
    # Example 1: Parse a hex file (would need an actual hex file)
    print("\n1. HEX File Parsing Example")
    print("-" * 30)
    
    try:
        # This would work with an actual hex file
        # hex_parser.load_hex_file("example.hex")
        # print(f"Loaded hex file with {len(hex_parser.rows)} rows")
        print("(Would load actual hex file here)")
        
        # Show memory statistics
        # stats = hex_parser.get_memory_stats()
        # if stats:
        #     print(f"Memory range: {stats['min_address_hex']} - {stats['max_address_hex']}")
        #     print(f"Used bytes: {stats['used_bytes']:,}")
        
    except Exception as e:
        print(f"Error loading hex file: {e}")
    
    # Example 2: Parse a C structure
    print("\n2. C Structure Parsing Example")
    print("-" * 30)
    
    sample_structure = """
    struct firmware_header {
        uint32_t magic;
        uint16_t version;
        uint16_t flags;
        uint32_t data_offset;
        uint32_t data_size;
        uint8_t reserved[8];
        char name[16];
    };
    """
    
    try:
        # Parse the structure at address 0x1000
        fields = structure_parser.parse_structure(sample_structure, 0x1000)
        
        if fields:
            print(f"Successfully parsed structure with {len(fields)} fields:")
            for field in fields:
                print(f"  {field.name:15s} @ 0x{field.address:08X} ({field.size:2d} bytes, {field.type_name})")
            
            # Show total structure size
            total_size = structure_parser.get_structure_size(fields)
            print(f"\nTotal structure size: {total_size} bytes")
            
            # Example data interpretation (would use actual hex data)
            example_data = b'\x12\x34\x56\x78'  # Sample 4-byte data
            interpreted = structure_parser.interpret_value(example_data, 'uint32_t')
            print(f"Example uint32_t interpretation: {interpreted}")
            
        else:
            print("Failed to parse structure")
            
    except Exception as e:
        print(f"Error parsing structure: {e}")
    
    # Example 3: Symbol management
    print("\n3. Symbol Management Example")
    print("-" * 30)
    
    try:
        # Add some example symbols
        from intelhex_viewer.symbol_manager import Symbol
        
        symbols = [
            Symbol("main", 0x1000, 64, "function", "example"),
            Symbol("data_buffer", 0x2000, 256, "variable", "example"),
            Symbol("CONFIG_REGISTER", 0x3000, 4, "constant", "example"),
        ]
        
        for symbol in symbols:
            symbol_manager.add_symbol(symbol)
        
        print(f"Added {len(symbols)} symbols")
        
        # Get all symbols
        all_symbols = symbol_manager.get_all_symbols()
        print("All symbols:")
        for symbol in all_symbols:
            print(f"  {symbol}")
        
        # Search for symbols
        search_results = symbol_manager.search_symbols("data")
        print(f"\nSymbols containing 'data': {len(search_results)}")
        for symbol in search_results:
            print(f"  {symbol}")
        
        # Get symbols at specific address
        symbols_at_addr = symbol_manager.get_symbols_at_address(0x1000)
        print(f"\nSymbols at 0x1000: {len(symbols_at_addr)}")
        for symbol in symbols_at_addr:
            print(f"  {symbol}")
        
    except Exception as e:
        print(f"Error with symbol management: {e}")
    
    # Example 4: Configuration
    print("\n4. Configuration Example")
    print("-" * 30)
    
    # Change bytes per row
    hex_parser.set_bytes_per_row(32)
    print(f"Set bytes per row to: {hex_parser.bytes_per_row}")
    
    # Change endianness
    structure_parser.set_endianness(Endianness.BIG)
    print(f"Set endianness to: {structure_parser.endianness.value}")
    
    # Add custom type
    structure_parser.add_custom_type("custom_int", 3)
    print("Added custom type: custom_int (3 bytes)")
    
    print("\n" + "=" * 40)
    print("Example completed successfully!")
    print("To run the full GUI application:")
    print("  python hex_viewer.py")
    print("  or")
    print("  python -m intelhex_viewer")


if __name__ == "__main__":
    main() 