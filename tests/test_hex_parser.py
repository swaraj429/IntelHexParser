"""
Unit tests for the hex_parser module.

These tests verify the functionality of the HexDataParser class.
"""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock

# Import the module to test
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from intelhex_viewer.hex_parser import HexDataParser


class TestHexDataParser(unittest.TestCase):
    """Test cases for HexDataParser class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.parser = HexDataParser()
    
    def tearDown(self):
        """Clean up after each test method."""
        # Clean up any resources if needed
        pass
    
    def test_init(self):
        """Test HexDataParser initialization."""
        self.assertIsNone(self.parser.ih)
        self.assertIsNone(self.parser.filepath)
        self.assertEqual(self.parser.rows, [])
        self.assertEqual(self.parser.bytes_per_row, 16)
    
    def test_set_bytes_per_row_valid(self):
        """Test setting valid bytes per row values."""
        self.parser.set_bytes_per_row(8)
        self.assertEqual(self.parser.bytes_per_row, 8)
        
        self.parser.set_bytes_per_row(32)
        self.assertEqual(self.parser.bytes_per_row, 32)
    
    def test_set_bytes_per_row_invalid(self):
        """Test setting invalid bytes per row values."""
        with self.assertRaises(ValueError):
            self.parser.set_bytes_per_row(0)
        
        with self.assertRaises(ValueError):
            self.parser.set_bytes_per_row(65)
        
        with self.assertRaises(ValueError):
            self.parser.set_bytes_per_row(-1)
    
    def test_is_loaded_false(self):
        """Test is_loaded returns False when no file is loaded."""
        self.assertFalse(self.parser.is_loaded())
    
    def test_get_filename_none(self):
        """Test get_filename returns None when no file is loaded."""
        self.assertIsNone(self.parser.get_filename())
    
    def test_get_data_at_address_no_file(self):
        """Test get_data_at_address returns None when no file is loaded."""
        result = self.parser.get_data_at_address(0x1000, 4)
        self.assertIsNone(result)
    
    def test_export_to_csv_no_data(self):
        """Test CSV export fails when no data is loaded."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            result = self.parser.export_to_csv(temp_path)
            self.assertFalse(result)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_export_to_binary_no_data(self):
        """Test binary export fails when no data is loaded."""
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as f:
            temp_path = f.name
        
        try:
            result = self.parser.export_to_binary(temp_path)
            self.assertFalse(result)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_search_value_no_data(self):
        """Test search returns empty list when no data is loaded."""
        result = self.parser.search_value("test")
        self.assertEqual(result, [])
    
    def test_get_memory_stats_no_data(self):
        """Test memory stats returns None when no data is loaded."""
        result = self.parser.get_memory_stats()
        self.assertIsNone(result)
    
    @patch('intelhex_viewer.hex_parser.IntelHex')
    def test_load_hex_file_success(self, mock_intelhex):
        """Test successful hex file loading."""
        # Mock IntelHex behavior
        mock_ih = MagicMock()
        mock_ih.addresses.return_value = [0x1000, 0x1001, 0x1002]
        mock_ih.__getitem__.side_effect = lambda addr: addr & 0xFF
        mock_intelhex.return_value = mock_ih
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.hex', delete=False) as f:
            temp_path = f.name
            f.write(b":020000040000FA\n:10100000010203040506070809101112131415169E\n:00000001FF\n")
        
        try:
            result = self.parser.load_hex_file(temp_path)
            self.assertTrue(result)
            self.assertIsNotNone(self.parser.ih)
            self.assertEqual(self.parser.filepath, temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_load_hex_file_not_found(self):
        """Test loading non-existent file raises FileNotFoundError."""
        with self.assertRaises(ValueError):
            self.parser.load_hex_file("nonexistent_file.hex")


if __name__ == '__main__':
    unittest.main() 