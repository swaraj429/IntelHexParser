"""
Symbol Manager Module

This module handles symbol and tag management for the Intel HEX Viewer, including:
- Loading and parsing map files
- Loading and parsing header files
- Symbol storage and retrieval
- Address-to-symbol mapping
- Symbol navigation support

Classes:
    Symbol: Data class for symbol information
    SymbolManager: Main class for symbol operations
"""

from typing import Dict, List, Tuple, Optional, Set
import re
import os
from dataclasses import dataclass


@dataclass
class Symbol:
    """
    Represents a symbol with its memory location and metadata.
    
    Attributes:
        name (str): Symbol name
        address (int): Memory address
        size (int): Size in bytes
        type (str): Symbol type (e.g., 'function', 'variable', 'constant')
        source (str): Source of the symbol (e.g., 'map_file', 'header_file')
    """
    name: str
    address: int
    size: int
    type: str = "unknown"
    source: str = "unknown"
    
    def __str__(self) -> str:
        """String representation of the symbol."""
        return f"{self.name} @ 0x{self.address:08X} ({self.size} bytes)"


class SymbolManager:
    """
    Manages symbols and tags for the hex viewer application.
    
    This class handles loading symbols from various sources (map files, header files)
    and provides functionality for symbol lookup and navigation.
    
    Attributes:
        symbols (Dict[str, Symbol]): Dictionary of symbols by name
        address_map (Dict[int, List[str]]): Mapping of addresses to symbol names
    """
    
    def __init__(self) -> None:
        """Initialize the symbol manager."""
        self.symbols: Dict[str, Symbol] = {}
        self.address_map: Dict[int, List[str]] = {}
        self._loaded_files: Set[str] = set()
    
    def clear_symbols(self) -> None:
        """Clear all loaded symbols."""
        self.symbols.clear()
        self.address_map.clear()
        self._loaded_files.clear()
    
    def add_symbol(self, symbol: Symbol) -> None:
        """
        Add a symbol to the manager.
        
        Args:
            symbol (Symbol): Symbol to add
        """
        # Store symbol by name
        self.symbols[symbol.name] = symbol
        
        # Update address mapping
        for addr in range(symbol.address, symbol.address + symbol.size):
            if addr not in self.address_map:
                self.address_map[addr] = []
            
            # Avoid duplicates
            if symbol.name not in self.address_map[addr]:
                self.address_map[addr].append(symbol.name)
    
    def remove_symbol(self, name: str) -> bool:
        """
        Remove a symbol by name.
        
        Args:
            name (str): Symbol name to remove
            
        Returns:
            bool: True if symbol was removed, False if not found
        """
        if name not in self.symbols:
            return False
        
        symbol = self.symbols[name]
        
        # Remove from address mapping
        for addr in range(symbol.address, symbol.address + symbol.size):
            if addr in self.address_map and name in self.address_map[addr]:
                self.address_map[addr].remove(name)
                
                # Clean up empty lists
                if not self.address_map[addr]:
                    del self.address_map[addr]
        
        # Remove from symbols
        del self.symbols[name]
        return True
    
    def get_symbol(self, name: str) -> Optional[Symbol]:
        """
        Get a symbol by name.
        
        Args:
            name (str): Symbol name
            
        Returns:
            Optional[Symbol]: Symbol if found, None otherwise
        """
        return self.symbols.get(name)
    
    def get_symbols_at_address(self, address: int) -> List[Symbol]:
        """
        Get all symbols at a specific address.
        
        Args:
            address (int): Memory address
            
        Returns:
            List[Symbol]: List of symbols at the address
        """
        symbol_names = self.address_map.get(address, [])
        return [self.symbols[name] for name in symbol_names if name in self.symbols]
    
    def get_symbols_in_range(self, start_address: int, end_address: int) -> List[Symbol]:
        """
        Get all symbols within an address range.
        
        Args:
            start_address (int): Start of range (inclusive)
            end_address (int): End of range (inclusive)
            
        Returns:
            List[Symbol]: List of symbols in the range
        """
        symbols = []
        seen_names = set()
        
        for addr in range(start_address, end_address + 1):
            symbol_names = self.address_map.get(addr, [])
            for name in symbol_names:
                if name not in seen_names:
                    seen_names.add(name)
                    if name in self.symbols:
                        symbols.append(self.symbols[name])
        
        return symbols
    
    def load_map_file(self, filepath: str) -> int:
        """
        Load symbols from a map file.
        
        Map file format expected:
        - Lines with pattern: "0xADDRESS SYMBOL_NAME"
        - Comments and empty lines are ignored
        
        Args:
            filepath (str): Path to the map file
            
        Returns:
            int: Number of symbols loaded
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Map file not found: {filepath}")
        
        symbols_loaded = 0
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#') or line.startswith('//'):
                        continue
                    
                    # Try to parse address and symbol
                    match = re.match(r'\s*(0x[0-9A-Fa-f]+)\s+(\S+)', line)
                    if match:
                        addr_str, name = match.groups()
                        address = int(addr_str, 16)
                        
                        # Create symbol (default size 1 for map file symbols)
                        symbol = Symbol(
                            name=name,
                            address=address,
                            size=1,
                            type="map_symbol",
                            source=f"map:{os.path.basename(filepath)}"
                        )
                        
                        self.add_symbol(symbol)
                        symbols_loaded += 1
                    
                    # Try alternative format: "SYMBOL_NAME = 0xADDRESS"
                    elif '=' in line:
                        match = re.match(r'\s*(\S+)\s*=\s*(0x[0-9A-Fa-f]+)', line)
                        if match:
                            name, addr_str = match.groups()
                            address = int(addr_str, 16)
                            
                            symbol = Symbol(
                                name=name,
                                address=address,
                                size=1,
                                type="map_symbol",
                                source=f"map:{os.path.basename(filepath)}"
                            )
                            
                            self.add_symbol(symbol)
                            symbols_loaded += 1
            
            self._loaded_files.add(filepath)
            return symbols_loaded
            
        except Exception as e:
            raise ValueError(f"Error parsing map file {filepath}: {e}")
    
    def load_header_file(self, filepath: str) -> int:
        """
        Load symbols from a C header file.
        
        Parses:
        - #define NAME VALUE
        - struct definitions with field offsets
        - enum definitions
        
        Args:
            filepath (str): Path to the header file
            
        Returns:
            int: Number of symbols loaded
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Header file not found: {filepath}")
        
        symbols_loaded = 0
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse #define statements
            symbols_loaded += self._parse_defines(content, filepath)
            
            # Parse struct definitions
            symbols_loaded += self._parse_structs(content, filepath)
            
            # Parse enum definitions
            symbols_loaded += self._parse_enums(content, filepath)
            
            self._loaded_files.add(filepath)
            return symbols_loaded
            
        except Exception as e:
            raise ValueError(f"Error parsing header file {filepath}: {e}")
    
    def _parse_defines(self, content: str, filepath: str) -> int:
        """Parse #define statements from header content."""
        symbols_loaded = 0
        
        # Find all #define statements with hex values
        define_pattern = r'#define\s+(\w+)\s+(0x[0-9A-Fa-f]+)'
        matches = re.findall(define_pattern, content, re.MULTILINE)
        
        for name, value_str in matches:
            try:
                address = int(value_str, 16)
                
                symbol = Symbol(
                    name=name,
                    address=address,
                    size=1,
                    type="constant",
                    source=f"header:{os.path.basename(filepath)}"
                )
                
                self.add_symbol(symbol)
                symbols_loaded += 1
                
            except ValueError:
                continue  # Skip invalid hex values
        
        return symbols_loaded
    
    def _parse_structs(self, content: str, filepath: str) -> int:
        """Parse struct definitions from header content."""
        symbols_loaded = 0
        
        # Find struct definitions
        struct_pattern = r'struct\s+(\w+)\s*\{([^}]+)\}'
        struct_matches = re.findall(struct_pattern, content, re.DOTALL)
        
        for struct_name, struct_body in struct_matches:
            offset = 0
            
            # Parse struct fields
            field_lines = [line.strip() for line in struct_body.split(';') if line.strip()]
            
            for line in field_lines:
                # Handle arrays
                array_match = re.match(r'(\w+)\s+(\w+)\[(\d+)\]', line)
                if array_match:
                    type_name, field_name, array_size = array_match.groups()
                    size = self._get_type_size(type_name) * int(array_size)
                    
                    symbol = Symbol(
                        name=f"{struct_name}.{field_name}",
                        address=offset,  # Relative offset
                        size=size,
                        type="struct_field",
                        source=f"header:{os.path.basename(filepath)}"
                    )
                    
                    self.add_symbol(symbol)
                    symbols_loaded += 1
                    offset += size
                    continue
                
                # Handle regular fields
                field_match = re.match(r'(\w+)\s+(\w+)', line)
                if field_match:
                    type_name, field_name = field_match.groups()
                    size = self._get_type_size(type_name)
                    
                    symbol = Symbol(
                        name=f"{struct_name}.{field_name}",
                        address=offset,  # Relative offset
                        size=size,
                        type="struct_field",
                        source=f"header:{os.path.basename(filepath)}"
                    )
                    
                    self.add_symbol(symbol)
                    symbols_loaded += 1
                    offset += size
        
        return symbols_loaded
    
    def _parse_enums(self, content: str, filepath: str) -> int:
        """Parse enum definitions from header content."""
        symbols_loaded = 0
        
        # Find enum definitions
        enum_pattern = r'enum\s+(\w+)?\s*\{([^}]+)\}'
        enum_matches = re.findall(enum_pattern, content, re.DOTALL)
        
        for enum_name, enum_body in enum_matches:
            value = 0
            
            # Parse enum values
            enum_lines = [line.strip() for line in enum_body.split(',') if line.strip()]
            
            for line in enum_lines:
                # Handle explicit values: NAME = VALUE
                explicit_match = re.match(r'(\w+)\s*=\s*(\d+)', line)
                if explicit_match:
                    name, value_str = explicit_match.groups()
                    value = int(value_str)
                else:
                    # Handle simple names: NAME
                    name_match = re.match(r'(\w+)', line)
                    if name_match:
                        name = name_match.group(1)
                
                if name_match or explicit_match:
                    symbol_name = f"{enum_name}.{name}" if enum_name else name
                    
                    symbol = Symbol(
                        name=symbol_name,
                        address=value,
                        size=4,  # Assume 4-byte enum
                        type="enum_value",
                        source=f"header:{os.path.basename(filepath)}"
                    )
                    
                    self.add_symbol(symbol)
                    symbols_loaded += 1
                    value += 1
        
        return symbols_loaded
    
    def _get_type_size(self, type_name: str) -> int:
        """Get size in bytes for C data types."""
        type_sizes = {
            'uint8_t': 1, 'int8_t': 1, 'char': 1, 'bool': 1,
            'uint16_t': 2, 'int16_t': 2, 'short': 2,
            'uint32_t': 4, 'int32_t': 4, 'int': 4, 'long': 4,
            'uint64_t': 8, 'int64_t': 8, 'long long': 8,
            'float': 4, 'double': 8
        }
        return type_sizes.get(type_name, 4)  # Default to 4 bytes
    
    def get_all_symbols(self) -> List[Symbol]:
        """
        Get all symbols sorted by address.
        
        Returns:
            List[Symbol]: All symbols sorted by address
        """
        return sorted(self.symbols.values(), key=lambda s: s.address)
    
    def get_symbols_by_type(self, symbol_type: str) -> List[Symbol]:
        """
        Get all symbols of a specific type.
        
        Args:
            symbol_type (str): Type to filter by
            
        Returns:
            List[Symbol]: Symbols of the specified type
        """
        return [s for s in self.symbols.values() if s.type == symbol_type]
    
    def search_symbols(self, query: str, case_sensitive: bool = False) -> List[Symbol]:
        """
        Search for symbols by name.
        
        Args:
            query (str): Search query
            case_sensitive (bool): Whether search should be case sensitive
            
        Returns:
            List[Symbol]: Matching symbols
        """
        if not case_sensitive:
            query = query.lower()
        
        matches = []
        for symbol in self.symbols.values():
            symbol_name = symbol.name if case_sensitive else symbol.name.lower()
            if query in symbol_name:
                matches.append(symbol)
        
        return sorted(matches, key=lambda s: s.address)
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get symbol statistics.
        
        Returns:
            Dict[str, int]: Statistics including total count and counts by type
        """
        stats = {'total': len(self.symbols)}
        
        # Count by type
        type_counts = {}
        for symbol in self.symbols.values():
            type_counts[symbol.type] = type_counts.get(symbol.type, 0) + 1
        
        stats.update(type_counts)
        return stats
    
    def get_loaded_files(self) -> List[str]:
        """
        Get list of loaded symbol files.
        
        Returns:
            List[str]: List of loaded file paths
        """
        return list(self._loaded_files) 