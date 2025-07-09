"""
C Structure Parser Module

This module handles parsing C structure definitions and interpreting raw memory data
according to those structures, including:
- Parsing C structure syntax
- Type size calculations
- Data interpretation with endianness support
- Value formatting for display

Classes:
    CStructureParser: Main class for C structure operations
    StructField: Data class for structure field information
"""

from typing import Dict, List, Tuple, Optional, Union, Any
import re
import struct
from dataclasses import dataclass
from enum import Enum


class Endianness(Enum):
    """Enumeration for byte order specifications."""
    LITTLE = "little"
    BIG = "big"


@dataclass
class StructField:
    """
    Represents a single field in a C structure.
    
    Attributes:
        name (str): Field name
        offset (int): Byte offset from structure start
        size (int): Size in bytes
        type_name (str): C type name (e.g., 'uint32_t', 'char[16]')
        address (int): Absolute memory address (when structure address is known)
    """
    name: str
    offset: int
    size: int
    type_name: str
    address: int = 0


class CStructureParser:
    """
    Handles C structure definition parsing and memory interpretation.
    
    This class can parse C structure syntax and interpret raw memory data
    according to the parsed structure definitions.
    
    Attributes:
        endianness (Endianness): Byte order for multi-byte values
        type_sizes (Dict[str, int]): Mapping of C types to their sizes
    """
    
    # Standard C type sizes (can be overridden if needed)
    DEFAULT_TYPE_SIZES = {
        'uint8_t': 1, 'int8_t': 1, 'char': 1, 'bool': 1,
        'uint16_t': 2, 'int16_t': 2, 'short': 2,
        'uint32_t': 4, 'int32_t': 4, 'int': 4, 'long': 4,
        'uint64_t': 8, 'int64_t': 8, 'long long': 8,
        'float': 4, 'double': 8, 'size_t': 4, 'ptrdiff_t': 4,
        'void*': 4, 'char*': 4  # Assuming 32-bit pointers
    }
    
    def __init__(self, endianness: Endianness = Endianness.LITTLE) -> None:
        """
        Initialize the structure parser.
        
        Args:
            endianness (Endianness): Byte order for interpretation
        """
        self.endianness = endianness
        self.type_sizes = self.DEFAULT_TYPE_SIZES.copy()
        self.parsed_structures: Dict[str, List[StructField]] = {}
    
    def set_endianness(self, endianness: Endianness) -> None:
        """
        Set the byte order for data interpretation.
        
        Args:
            endianness (Endianness): New byte order
        """
        self.endianness = endianness
    
    def add_custom_type(self, type_name: str, size: int) -> None:
        """
        Add a custom type definition.
        
        Args:
            type_name (str): Name of the custom type
            size (int): Size in bytes
        """
        self.type_sizes[type_name] = size
    
    def parse_structure(self, struct_text: str, base_address: int = 0) -> Optional[List[StructField]]:
        """
        Parse a C structure definition.
        
        Args:
            struct_text (str): C structure definition text
            base_address (int): Base address for calculating absolute addresses
            
        Returns:
            Optional[List[StructField]]: List of parsed fields or None if parsing failed
            
        Example:
            >>> parser = CStructureParser()
            >>> fields = parser.parse_structure('''
            ... struct example {
            ...     uint32_t magic;
            ...     uint16_t version;
            ...     char name[16];
            ... };
            ... ''', 0x1000)
        """
        try:
            # Clean up the input text
            cleaned_text = self._clean_struct_text(struct_text)
            
            # Extract structure body
            struct_body = self._extract_struct_body(cleaned_text)
            if not struct_body:
                return None
            
            # Parse individual fields
            fields = self._parse_fields(struct_body, base_address)
            
            # Store parsed structure for reuse
            struct_name = self._extract_struct_name(cleaned_text) or "anonymous"
            self.parsed_structures[struct_name] = fields
            
            return fields
            
        except Exception as e:
            print(f"Error parsing structure: {e}")
            return None
    
    def _clean_struct_text(self, text: str) -> str:
        """Remove comments and normalize whitespace."""
        # Remove single-line comments
        text = re.sub(r'//.*$', '', text, flags=re.MULTILINE)
        
        # Remove multi-line comments
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_struct_name(self, text: str) -> Optional[str]:
        """Extract structure name from definition."""
        match = re.search(r'struct\s+(\w+)', text)
        return match.group(1) if match else None
    
    def _extract_struct_body(self, text: str) -> Optional[str]:
        """Extract the body content between braces."""
        match = re.search(r'struct\s+\w*\s*\{(.*?)\}', text, re.DOTALL)
        return match.group(1).strip() if match else None
    
    def _parse_fields(self, struct_body: str, base_address: int) -> List[StructField]:
        """Parse individual field declarations."""
        fields = []
        current_offset = 0
        
        # Split into field declarations
        field_lines = [line.strip() for line in struct_body.split(';') if line.strip()]
        
        for line in field_lines:
            field = self._parse_field_line(line, current_offset, base_address)
            if field:
                fields.append(field)
                current_offset += field.size
        
        return fields
    
    def _parse_field_line(self, line: str, offset: int, base_address: int) -> Optional[StructField]:
        """Parse a single field declaration line."""
        # Handle arrays: uint8_t reserved[8];
        array_match = re.match(r'(\w+)\s+(\w+)\[(\d+)\]', line)
        if array_match:
            type_name, field_name, array_size = array_match.groups()
            element_size = self.type_sizes.get(type_name, 1)
            total_size = element_size * int(array_size)
            return StructField(
                name=field_name,
                offset=offset,
                size=total_size,
                type_name=f"{type_name}[{array_size}]",
                address=base_address + offset
            )
        
        # Handle regular fields: uint32_t magic;
        field_match = re.match(r'(\w+)\s+(\w+)', line)
        if field_match:
            type_name, field_name = field_match.groups()
            size = self.type_sizes.get(type_name, 1)
            return StructField(
                name=field_name,
                offset=offset,
                size=size,
                type_name=type_name,
                address=base_address + offset
            )
        
        return None
    
    def interpret_value(self, data: bytes, type_name: str) -> str:
        """
        Interpret raw bytes according to the specified type.
        
        Args:
            data (bytes): Raw byte data
            type_name (str): C type name
            
        Returns:
            str: Formatted interpretation of the data
        """
        if not data:
            return "No data"
        
        try:
            size = len(data)
            endian_prefix = '<' if self.endianness == Endianness.LITTLE else '>'
            
            # Handle single-byte types
            if type_name in ['uint8_t', 'char', 'bool']:
                return self._interpret_uint8(data[0], type_name)
            elif type_name == 'int8_t':
                return self._interpret_int8(data[0])
            
            # Handle multi-byte integers
            elif type_name == 'uint16_t':
                val = struct.unpack(f'{endian_prefix}H', data[:2])[0]
                return f"0x{val:04X} ({val})"
            elif type_name == 'int16_t':
                val = struct.unpack(f'{endian_prefix}h', data[:2])[0]
                return f"{val} (0x{val&0xFFFF:04X})"
            elif type_name == 'uint32_t':
                val = struct.unpack(f'{endian_prefix}I', data[:4])[0]
                return f"0x{val:08X} ({val})"
            elif type_name == 'int32_t':
                val = struct.unpack(f'{endian_prefix}i', data[:4])[0]
                return f"{val} (0x{val&0xFFFFFFFF:08X})"
            elif type_name == 'uint64_t':
                val = struct.unpack(f'{endian_prefix}Q', data[:8])[0]
                return f"0x{val:016X} ({val})"
            elif type_name == 'int64_t':
                val = struct.unpack(f'{endian_prefix}q', data[:8])[0]
                return f"{val} (0x{val&0xFFFFFFFFFFFFFFFF:016X})"
            
            # Handle floating point
            elif type_name == 'float':
                val = struct.unpack(f'{endian_prefix}f', data[:4])[0]
                return f"{val:.6f}"
            elif type_name == 'double':
                val = struct.unpack(f'{endian_prefix}d', data[:8])[0]
                return f"{val:.6f}"
            
            # Handle arrays
            elif type_name.startswith('char['):
                return self._interpret_char_array(data)
            elif '[' in type_name:
                return self._interpret_byte_array(data)
            
            # Default: show as hex array
            else:
                return self._interpret_byte_array(data)
                
        except Exception as e:
            return f"Error: {e}"
    
    def _interpret_uint8(self, value: int, type_name: str) -> str:
        """Interpret an 8-bit unsigned value."""
        if type_name == 'char' and 32 <= value <= 126:
            return f"'{chr(value)}' (0x{value:02X})"
        elif type_name == 'bool':
            return f"{'true' if value else 'false'} (0x{value:02X})"
        else:
            return f"0x{value:02X} ({value})"
    
    def _interpret_int8(self, value: int) -> str:
        """Interpret an 8-bit signed value."""
        signed_val = struct.unpack('b', bytes([value]))[0]
        return f"{signed_val} (0x{value:02X})"
    
    def _interpret_char_array(self, data: bytes) -> str:
        """Interpret byte array as a C string."""
        try:
            # Find null terminator
            null_idx = data.find(0)
            if null_idx != -1:
                text = data[:null_idx].decode('ascii', errors='ignore')
            else:
                text = data.decode('ascii', errors='ignore').rstrip('\x00')
            return f'"{text}"'
        except Exception:
            # Fall back to hex representation
            return self._interpret_byte_array(data)
    
    def _interpret_byte_array(self, data: bytes) -> str:
        """Interpret as hex byte array."""
        hex_str = ' '.join(f'{b:02X}' for b in data)
        return f"[{hex_str}]"
    
    def get_structure_size(self, fields: List[StructField]) -> int:
        """
        Calculate total size of a structure.
        
        Args:
            fields (List[StructField]): List of structure fields
            
        Returns:
            int: Total structure size in bytes
        """
        if not fields:
            return 0
        
        # Size is the end of the last field
        last_field = max(fields, key=lambda f: f.offset + f.size)
        return last_field.offset + last_field.size
    
    def format_structure_summary(self, fields: List[StructField], 
                                struct_name: str = "Structure") -> str:
        """
        Format a human-readable structure summary.
        
        Args:
            fields (List[StructField]): Structure fields
            struct_name (str): Name of the structure
            
        Returns:
            str: Formatted summary text
        """
        if not fields:
            return f"{struct_name}: Empty structure"
        
        lines = [f"{struct_name} (Size: {self.get_structure_size(fields)} bytes)"]
        lines.append("-" * 50)
        
        for field in fields:
            lines.append(
                f"{field.name:20s} @ +0x{field.offset:04X} "
                f"({field.type_name:12s}, {field.size:2d} bytes)"
            )
        
        return "\n".join(lines) 