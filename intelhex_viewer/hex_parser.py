"""
Intel HEX Data Parser Module

This module handles parsing and processing Intel HEX files, including:
- Loading Intel HEX files
- Converting hex data to displayable rows
- Managing memory addresses and data
- Export functionality

Classes:
    HexDataParser: Main class for hex file operations
"""

from typing import Dict, List, Tuple, Optional, Union
from collections import defaultdict
import os
from intelhex import IntelHex


class HexDataParser:
    """
    Handles Intel HEX file parsing and data management.
    
    This class provides methods to load, parse, and process Intel HEX files
    for display and analysis in the hex viewer application.
    
    Attributes:
        ih (IntelHex): The loaded Intel HEX object
        filepath (str): Path to the currently loaded file
        rows (List[Tuple]): Parsed hex data organized by rows
        bytes_per_row (int): Number of bytes to display per row
    """
    
    def __init__(self) -> None:
        """Initialize the hex data parser."""
        self.ih: Optional[IntelHex] = None
        self.filepath: Optional[str] = None
        self.rows: List[Tuple[int, List[str]]] = []
        self.bytes_per_row: int = 16
    
    def load_hex_file(self, filepath: str) -> bool:
        """
        Load an Intel HEX file.
        
        Args:
            filepath (str): Path to the Intel HEX file
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is invalid
        """
        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")
            
            self.ih = IntelHex(filepath)
            self.filepath = filepath
            self.rows = self._parse_hex_to_rows()
            return True
            
        except Exception as e:
            raise ValueError(f"Failed to load HEX file: {e}")
    
    def _parse_hex_to_rows(self) -> List[Tuple[int, List[str]]]:
        """
        Parse hex data into rows for display.
        
        Returns:
            List[Tuple[int, List[str]]]: List of (base_address, data_list) tuples
        """
        if not self.ih:
            return []
        
        rows = defaultdict(lambda: ["--"] * self.bytes_per_row)
        
        for addr in self.ih.addresses():
            base = addr - (addr % self.bytes_per_row)
            offset = addr % self.bytes_per_row
            rows[base][offset] = f"{self.ih[addr]:02X}"
        
        return sorted(rows.items())
    
    def set_bytes_per_row(self, bytes_per_row: int) -> None:
        """
        Set the number of bytes to display per row.
        
        Args:
            bytes_per_row (int): Number of bytes per row (1-64)
            
        Raises:
            ValueError: If bytes_per_row is out of valid range
        """
        if not 1 <= bytes_per_row <= 64:
            raise ValueError("Bytes per row must be between 1 and 64")
        
        self.bytes_per_row = bytes_per_row
        
        # Reparse if data is loaded
        if self.ih:
            self.rows = self._parse_hex_to_rows()
    
    def get_data_at_address(self, address: int, size: int = 1) -> Optional[bytes]:
        """
        Get raw bytes at the specified address.
        
        Args:
            address (int): Starting address
            size (int): Number of bytes to read
            
        Returns:
            Optional[bytes]: Raw bytes if available, None otherwise
        """
        if not self.ih:
            return None
        
        try:
            data = []
            for i in range(size):
                if address + i in self.ih.addresses():
                    data.append(self.ih[address + i])
                else:
                    return None
            return bytes(data)
        except Exception:
            return None
    
    def export_to_csv(self, output_path: str) -> bool:
        """
        Export hex data to CSV format.
        
        Args:
            output_path (str): Path for the output CSV file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import csv
            
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write header
                header = ["Address"] + [f"+{i:02X}" for i in range(self.bytes_per_row)]
                writer.writerow(header)
                
                # Write data rows
                for base, data in self.rows:
                    writer.writerow([f"{base:08X}"] + data)
            
            return True
            
        except Exception:
            return False
    
    def export_to_binary(self, output_path: str) -> bool:
        """
        Export hex data to binary format.
        
        Args:
            output_path (str): Path for the output binary file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.ih:
                return False
            
            self.ih.tofile(output_path, format='bin')
            return True
            
        except Exception:
            return False
    
    def get_memory_stats(self) -> Optional[Dict[str, Union[int, str]]]:
        """
        Get memory statistics for the loaded hex file.
        
        Returns:
            Optional[Dict]: Dictionary with memory statistics or None if no data
        """
        if not self.ih:
            return None
        
        min_addr = self.ih.minaddr()
        max_addr = self.ih.maxaddr()
        total_range = max_addr - min_addr + 1
        used_bytes = len(self.ih.addresses())
        unused_bytes = total_range - used_bytes
        
        return {
            'min_address': min_addr,
            'max_address': max_addr,
            'total_range': total_range,
            'used_bytes': used_bytes,
            'unused_bytes': unused_bytes,
            'min_address_hex': f"0x{min_addr:08X}",
            'max_address_hex': f"0x{max_addr:08X}",
            'filename': os.path.basename(self.filepath) if self.filepath else "Unknown"
        }
    
    def search_value(self, query: str, search_type: str = "auto") -> List[int]:
        """
        Search for a value in the hex data.
        
        Args:
            query (str): Search query
            search_type (str): "hex", "ascii", or "auto"
            
        Returns:
            List[int]: List of addresses where the value was found
        """
        if not self.ih:
            return []
        
        matches = []
        
        # Determine search type
        if search_type == "auto":
            is_hex = all(c in "0123456789abcdefABCDEF" for c in query.replace(" ", ""))
            search_type = "hex" if is_hex else "ascii"
        
        for addr in self.ih.addresses():
            val = self.ih[addr]
            
            if search_type == "ascii":
                if chr(val) in query:
                    matches.append(addr)
            elif search_type == "hex":
                if f"{val:02X}".lower() in query.lower():
                    matches.append(addr)
        
        return matches
    
    def is_loaded(self) -> bool:
        """
        Check if a hex file is currently loaded.
        
        Returns:
            bool: True if a file is loaded, False otherwise
        """
        return self.ih is not None
    
    def get_filename(self) -> Optional[str]:
        """
        Get the filename of the currently loaded file.
        
        Returns:
            Optional[str]: Filename or None if no file is loaded
        """
        return os.path.basename(self.filepath) if self.filepath else None 