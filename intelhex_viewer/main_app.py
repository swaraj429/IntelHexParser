"""
Main Application Module

This module contains the main application class that coordinates all other modules
to provide the Intel HEX Viewer functionality.

Classes:
    HexViewerApp: Main application class
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional, Any, Union
import os

from .hex_parser import HexDataParser
from .structure_parser import CStructureParser, StructField, Endianness
from .symbol_manager import SymbolManager, Symbol
from .gui_components import (
    StructureDialog, StructureValuesDialog, SettingsDialog, SearchDialog,
    show_error_dialog, show_info_dialog, choose_file, choose_save_file
)
from . import __version__


class HexViewerApp:
    """
    Main Intel HEX Viewer application.
    
    This class coordinates all the components to provide a complete hex viewing
    and analysis application with GUI interface.
    
    Attributes:
        root (tk.Tk): Main application window
        hex_parser (HexDataParser): Handles hex file operations
        structure_parser (CStructureParser): Handles C structure parsing
        symbol_manager (SymbolManager): Handles symbol/tag management
        tree (ttk.Treeview): Main hex display widget
        tag_list (tk.Listbox): Symbol list widget
        highlighted_items (List): Track highlighted items for cleanup
    """
    
    def __init__(self, root: tk.Tk) -> None:
        """
        Initialize the main application.
        
        Args:
            root (tk.Tk): Root Tkinter window
        """
        self.root = root
        self.root.title("Intel HEX Viewer")
        
        # Initialize components
        self.hex_parser = HexDataParser()
        self.structure_parser = CStructureParser()
        self.symbol_manager = SymbolManager()
        
        # GUI state
        self.tree: Optional[ttk.Treeview] = None
        self.tag_list: Optional[tk.Listbox] = None
        self.status_label: Optional[ttk.Label] = None
        self.highlighted_items: List[tuple] = []
        self.current_struct_fields: Dict[str, StructField] = {}
        
        # Application settings
        self.settings = {
            'bytes_per_row': 16,
            'endianness': 'little',
            'auto_refresh': True
        }
        
        # Setup GUI
        self._create_menu()
        self._create_layout()
        self._create_status_bar()
        
        # Update status
        self._update_status("Ready - Load a HEX file to begin")
    
    def _create_menu(self) -> None:
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open HEX File", command=self._open_hex_file)
        file_menu.add_separator()
        file_menu.add_command(label="Load Map File", command=self._load_map_file)
        file_menu.add_command(label="Load Header File", command=self._load_header_file)
        file_menu.add_separator()
        file_menu.add_command(label="Export as CSV", command=self._export_csv)
        file_menu.add_command(label="Export as Binary", command=self._export_binary)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Settings", command=self._show_settings)
        view_menu.add_separator()
        view_menu.add_command(label="Memory Statistics", command=self._show_memory_stats)
        view_menu.add_command(label="Symbol Statistics", command=self._show_symbol_stats)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Parse C Structure", command=self._parse_structure)
        tools_menu.add_command(label="Search", command=self._search_data)
        tools_menu.add_command(label="Jump to Address", command=self._jump_to_address)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def _create_layout(self) -> None:
        """Create the main application layout."""
        # Create paned window for resizable layout
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True)
        
        # Left panel: Symbol list
        self._create_symbol_panel(paned)
        
        # Right panel: Hex display
        self._create_hex_panel(paned)
    
    def _create_symbol_panel(self, parent: ttk.PanedWindow) -> None:
        """Create the left panel with symbol list."""
        left_frame = ttk.Frame(parent, width=250)
        
        # Symbol list header
        ttk.Label(left_frame, text="Symbols", font=("Arial", 10, "bold")).pack(
            anchor="w", padx=5, pady=(5, 0)
        )
        
        # Symbol list with scrollbar
        list_frame = tk.Frame(left_frame)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tag_list = tk.Listbox(list_frame, font=("Consolas", 9))
        self.tag_list.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tag_list.yview)
        self.tag_list.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.tag_list.bind('<<ListboxSelect>>', self._on_symbol_select)
        
        parent.add(left_frame, weight=1)
    
    def _create_hex_panel(self, parent: ttk.PanedWindow) -> None:
        """Create the right panel with hex display."""
        right_frame = ttk.Frame(parent)
        
        # Create hex display treeview
        self._create_hex_treeview(right_frame)
        
        parent.add(right_frame, weight=4)
    
    def _create_hex_treeview(self, parent: ttk.Frame) -> None:
        """Create the hex display treeview widget."""
        # Calculate columns based on bytes per row
        bytes_per_row = self.settings['bytes_per_row']
        columns = ["Address"] + [f"+{i:02X}" for i in range(bytes_per_row)] + ["ASCII", "Tags", "Struct Values"]
        
        self.tree = ttk.Treeview(parent, columns=columns, show='headings')
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            
            if col == "Address":
                width = 80
            elif col == "ASCII":
                width = max(80, bytes_per_row * 8)
            elif col in ["Tags", "Struct Values"]:
                width = 200
            else:
                width = 40
            
            self.tree.column(col, width=width, anchor="center")
        
        # Configure tags for highlighting
        self.tree.tag_configure('highlight', background='yellow')
        self.tree.tag_configure('tagged', background='lightblue')
        
        # Pack with scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
    
    def _create_status_bar(self) -> None:
        """Create the status bar at the bottom."""
        self.status_label = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor="w")
        self.status_label.pack(side="bottom", fill="x")
    
    def _update_status(self, message: str) -> None:
        """Update the status bar message."""
        if self.status_label:
            self.status_label.config(text=message)
    
    def _open_hex_file(self) -> None:
        """Open and load a HEX file."""
        filetypes = [
            ("Intel HEX files", "*.hex"),
            ("Intel HEX files", "*.ihx"),
            ("All files", "*.*")
        ]
        
        filepath = choose_file(self.root, "Open HEX File", filetypes)
        if not filepath:
            return
        
        try:
            success = self.hex_parser.load_hex_file(filepath)
            if success:
                self._refresh_hex_display()
                filename = self.hex_parser.get_filename() or "Unknown"
                row_count = len(self.hex_parser.rows)
                self._update_status(f"Loaded {filename} - {row_count} rows")
                self.root.title(f"Intel HEX Viewer - {filename}")
            else:
                show_error_dialog(self.root, "Error", "Failed to load HEX file")
                
        except Exception as e:
            show_error_dialog(self.root, "Error", f"Failed to load HEX file:\n{e}")
    
    def _load_map_file(self) -> None:
        """Load symbols from a map file."""
        filetypes = [
            ("Map files", "*.map"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]
        
        filepath = choose_file(self.root, "Load Map File", filetypes)
        if not filepath:
            return
        
        try:
            count = self.symbol_manager.load_map_file(filepath)
            self._refresh_symbol_list()
            
            if self.hex_parser.is_loaded():
                self._refresh_hex_display()
            
            filename = os.path.basename(filepath)
            self._update_status(f"Loaded {count} symbols from {filename}")
            
        except Exception as e:
            show_error_dialog(self.root, "Error", f"Failed to load map file:\n{e}")
    
    def _load_header_file(self) -> None:
        """Load symbols from a C header file."""
        filetypes = [
            ("Header files", "*.h"),
            ("C++ Header files", "*.hpp"),
            ("All files", "*.*")
        ]
        
        filepath = choose_file(self.root, "Load Header File", filetypes)
        if not filepath:
            return
        
        try:
            count = self.symbol_manager.load_header_file(filepath)
            self._refresh_symbol_list()
            
            if self.hex_parser.is_loaded():
                self._refresh_hex_display()
            
            filename = os.path.basename(filepath)
            self._update_status(f"Loaded {count} symbols from {filename}")
            
        except Exception as e:
            show_error_dialog(self.root, "Error", f"Failed to load header file:\n{e}")
    
    def _export_csv(self) -> None:
        """Export hex data to CSV format."""
        if not self.hex_parser.is_loaded():
            show_info_dialog(self.root, "No Data", "Please load a HEX file first")
            return
        
        filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
        filepath = choose_save_file(self.root, "Export CSV", ".csv", filetypes)
        
        if filepath:
            try:
                success = self.hex_parser.export_to_csv(filepath)
                if success:
                    self._update_status(f"Exported to {os.path.basename(filepath)}")
                else:
                    show_error_dialog(self.root, "Error", "Failed to export CSV")
            except Exception as e:
                show_error_dialog(self.root, "Error", f"Export failed:\n{e}")
    
    def _export_binary(self) -> None:
        """Export hex data to binary format."""
        if not self.hex_parser.is_loaded():
            show_info_dialog(self.root, "No Data", "Please load a HEX file first")
            return
        
        filetypes = [("Binary files", "*.bin"), ("All files", "*.*")]
        filepath = choose_save_file(self.root, "Export Binary", ".bin", filetypes)
        
        if filepath:
            try:
                success = self.hex_parser.export_to_binary(filepath)
                if success:
                    self._update_status(f"Exported to {os.path.basename(filepath)}")
                else:
                    show_error_dialog(self.root, "Error", "Failed to export binary")
            except Exception as e:
                show_error_dialog(self.root, "Error", f"Export failed:\n{e}")
    
    def _show_settings(self) -> None:
        """Show the settings dialog."""
        dialog = SettingsDialog(self.root, self.settings.copy())
        result = dialog.show()
        
        if result:
            # Update settings
            old_bytes_per_row = self.settings['bytes_per_row']
            self.settings.update(result)
            
            # Update structure parser endianness
            endianness = Endianness.LITTLE if result['endianness'] == 'little' else Endianness.BIG
            self.structure_parser.set_endianness(endianness)
            
            # Recreate hex display if bytes per row changed
            if result['bytes_per_row'] != old_bytes_per_row:
                self.hex_parser.set_bytes_per_row(result['bytes_per_row'])
                self._recreate_hex_treeview()
                
                if self.hex_parser.is_loaded():
                    self._refresh_hex_display()
            
            # Refresh structure values if endianness changed
            elif result['endianness'] != self.settings['endianness'] and self.current_struct_fields:
                self._refresh_hex_display()
            
            self._update_status(f"Settings updated - {result['bytes_per_row']} bytes per row, {result['endianness']} endian")
    
    def _recreate_hex_treeview(self) -> None:
        """Recreate the hex treeview with new column layout."""
        if not self.tree:
            return
        
        parent = self.tree.master
        
        # Destroy old treeview and scrollbar
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Create new treeview
        self._create_hex_treeview(parent)
    
    def _show_memory_stats(self) -> None:
        """Show memory statistics dialog."""
        if not self.hex_parser.is_loaded():
            show_info_dialog(self.root, "No Data", "Please load a HEX file first")
            return
        
        stats = self.hex_parser.get_memory_stats()
        if stats:
            message = (
                f"File: {stats['filename']}\n"
                f"Start Address: {stats['min_address_hex']}\n"
                f"End Address: {stats['max_address_hex']}\n"
                f"Total Range: {stats['total_range']:,} bytes\n"
                f"Used Bytes: {stats['used_bytes']:,}\n"
                f"Unused Bytes: {stats['unused_bytes']:,}\n"
                f"Usage: {stats['used_bytes']/stats['total_range']*100:.1f}%"
            )
            show_info_dialog(self.root, "Memory Statistics", message)
    
    def _show_symbol_stats(self) -> None:
        """Show symbol statistics dialog."""
        stats = self.symbol_manager.get_statistics()
        
        if stats['total'] == 0:
            show_info_dialog(self.root, "Symbol Statistics", "No symbols loaded")
            return
        
        lines = [f"Total Symbols: {stats['total']}"]
        
        # Show breakdown by type
        for symbol_type, count in sorted(stats.items()):
            if symbol_type != 'total':
                lines.append(f"{symbol_type.replace('_', ' ').title()}: {count}")
        
        # Show loaded files
        files = self.symbol_manager.get_loaded_files()
        if files:
            lines.append("")
            lines.append("Loaded Files:")
            for filepath in files:
                lines.append(f"  {os.path.basename(filepath)}")
        
        message = "\n".join(lines)
        show_info_dialog(self.root, "Symbol Statistics", message)
    
    def _parse_structure(self) -> None:
        """Show the structure parsing dialog."""
        dialog = StructureDialog(self.root)
        dialog.set_view_values_callback(self._view_structure_values)
        
        result = dialog.show()
        if result:
            try:
                struct_text = result['structure_text']
                address = result['address']
                
                # Parse the structure
                fields = self.structure_parser.parse_structure(struct_text, address)
                if fields:
                    # Store fields for display
                    self.current_struct_fields = {f.name: f for f in fields}
                    
                    # Refresh hex display
                    self._refresh_hex_display()
                    
                    self._update_status(f"Parsed structure with {len(fields)} fields at 0x{address:08X}")
                else:
                    show_error_dialog(self.root, "Error", "Failed to parse structure")
                    
            except Exception as e:
                show_error_dialog(self.root, "Error", f"Structure parsing failed:\n{e}")
    
    def _view_structure_values(self, struct_text: str, address_text: str) -> None:
        """View structure values in a separate dialog."""
        try:
            if not struct_text.strip() or not address_text.strip():
                show_error_dialog(self.root, "Error", "Please provide both structure definition and address")
                return
            
            # Parse address
            if address_text.startswith('0x'):
                address = int(address_text, 16)
            else:
                address = int(address_text)
            
            # Parse structure
            fields = self.structure_parser.parse_structure(struct_text, address)
            if not fields:
                show_error_dialog(self.root, "Error", "Failed to parse structure")
                return
            
            # Prepare values data
            values_data = []
            for field in sorted(fields, key=lambda f: f.offset):
                # Get interpreted value
                if self.hex_parser.is_loaded():
                    raw_data = self.hex_parser.get_data_at_address(field.address, field.size)
                    if raw_data:
                        value = self.structure_parser.interpret_value(raw_data, field.type_name)
                    else:
                        value = "No data available"
                else:
                    value = "No HEX file loaded"
                
                values_data.append({
                    'field_name': field.name,
                    'address': f"0x{field.address:08X}",
                    'type_name': field.type_name,
                    'size': str(field.size),
                    'value': value
                })
            
            # Show values dialog
            values_dialog = StructureValuesDialog(self.root, f"Structure Values @ 0x{address:08X}")
            values_dialog.set_values(values_data)
            values_dialog.show()
            
        except Exception as e:
            show_error_dialog(self.root, "Error", f"Failed to show structure values:\n{e}")
    
    def _search_data(self) -> None:
        """Show the search dialog and perform search."""
        if not self.hex_parser.is_loaded():
            show_info_dialog(self.root, "No Data", "Please load a HEX file first")
            return
        
        dialog = SearchDialog(self.root)
        result = dialog.show()
        
        if result:
            try:
                query = result['query']
                search_type = result['search_type']
                
                matches = self.hex_parser.search_value(query, search_type)
                
                if matches:
                    # Jump to first match
                    self._jump_to_address_direct(matches[0])
                    
                    count = len(matches)
                    self._update_status(f"Found {count} match{'es' if count != 1 else ''} for '{query}'")
                else:
                    show_info_dialog(self.root, "Search Results", f"No matches found for '{query}'")
                    
            except Exception as e:
                show_error_dialog(self.root, "Error", f"Search failed:\n{e}")
    
    def _jump_to_address(self) -> None:
        """Show dialog to jump to a specific address."""
        if not self.hex_parser.is_loaded():
            show_info_dialog(self.root, "No Data", "Please load a HEX file first")
            return
        
        # Simple input dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Jump to Address")
        dialog.geometry("250x120")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (250 // 2)
        y = (dialog.winfo_screenheight() // 2) - (120 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        tk.Label(dialog, text="Address (hex):").pack(pady=10)
        entry = tk.Entry(dialog, width=20)
        entry.pack(pady=5)
        entry.focus()
        
        def go():
            try:
                addr_text = entry.get().strip()
                if addr_text.startswith('0x'):
                    address = int(addr_text, 16)
                else:
                    address = int(addr_text, 16)
                
                self._jump_to_address_direct(address)
                dialog.destroy()
                
            except ValueError:
                show_error_dialog(dialog, "Invalid Input", "Please enter a valid hexadecimal address")
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Jump", command=go).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)
        
        entry.bind('<Return>', lambda e: go())
    
    def _jump_to_address_direct(self, address: int) -> None:
        """Jump directly to the specified address."""
        if not self.tree:
            return
        
        bytes_per_row = self.settings['bytes_per_row']
        base = address - (address % bytes_per_row)
        item_id = f"row_{base:08X}"
        
        # Find and select the item
        for item in self.tree.get_children():
            if item == item_id:
                self.tree.see(item)
                self.tree.selection_set(item)
                self._update_status(f"Jumped to address 0x{address:08X}")
                return
        
        # Try alternative search
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            if values:
                try:
                    item_addr = int(values[0], 16)
                    if item_addr <= address < item_addr + bytes_per_row:
                        self.tree.see(item)
                        self.tree.selection_set(item)
                        self._update_status(f"Jumped to address 0x{address:08X}")
                        return
                except ValueError:
                    continue
        
        show_info_dialog(self.root, "Address Not Found", f"Address 0x{address:08X} not found in loaded data")
    
    def _show_about(self) -> None:
        """Show the about dialog."""
        message = (
            "Intel HEX Viewer v1.0.0\n"
            "\n"
            "A comprehensive tool for viewing and analyzing Intel HEX files\n"
            "with support for C structure parsing and symbol navigation.\n"
            "\n"
            "Features:\n"
            "• Intel HEX file loading and display\n"
            "• Symbol navigation via map files\n"
            "• C structure parsing and interpretation\n"
            "• Customizable display options\n"
            "• Search and export capabilities\n"
            "\n"
            "Open Source - MIT License\n"
            "Contributions welcome!"
        )
        show_info_dialog(self.root, "About Intel HEX Viewer", message)
    
    def _refresh_symbol_list(self) -> None:
        """Refresh the symbol list display."""
        if not self.tag_list:
            return
        
        self.tag_list.delete(0, tk.END)
        
        symbols = self.symbol_manager.get_all_symbols()
        for symbol in symbols:
            display_text = f"{symbol.name} @     {symbol.address:08X} ({symbol.size} bytes)"
            self.tag_list.insert(tk.END, display_text)
    
    def _refresh_hex_display(self) -> None:
        """Refresh the hex data display."""
        if not self.tree or not self.hex_parser.is_loaded():
            return
        
        # Clear existing data
        self.tree.delete(*self.tree.get_children())
        
        # Build address to symbols mapping
        addr_to_symbols = {}
        symbols = self.symbol_manager.get_all_symbols()
        for symbol in symbols:
            for addr in range(symbol.address, symbol.address + symbol.size):
                if addr not in addr_to_symbols:
                    addr_to_symbols[addr] = []
                addr_to_symbols[addr].append(symbol.name)
        
        bytes_per_row = self.settings['bytes_per_row']
        
        # Display each row
        for base, data in self.hex_parser.rows:
            # Create ASCII representation
            ascii_str = ''.join(
                chr(int(b, 16)) if b != "--" and 32 <= int(b, 16) <= 126 else '.'
                for b in data
            )
            
            # Find symbols for this row
            row_symbols = []
            for i in range(bytes_per_row):
                addr = base + i
                if addr in addr_to_symbols:
                    row_symbols.extend(addr_to_symbols[addr])
            
            # Format symbol display
            unique_symbols = list(set(row_symbols))
            symbol_display = ', '.join(unique_symbols[:3])
            if len(unique_symbols) > 3:
                symbol_display += f" (+{len(unique_symbols)-3} more)"
            
            # Find structure values for this row
            struct_values = []
            for field_name, field in self.current_struct_fields.items():
                if base <= field.address < base + bytes_per_row:
                    raw_data = self.hex_parser.get_data_at_address(field.address, field.size)
                    if raw_data:
                        value = self.structure_parser.interpret_value(raw_data, field.type_name)
                        struct_values.append(f"{field_name}: {value}")
            
            struct_display = '; '.join(struct_values[:2])
            if len(struct_values) > 2:
                struct_display += f" (+{len(struct_values)-2} more)"
            
            # Insert row
            item_id = f"row_{base:08X}"
            values = [f"{base:08X}"] + data + [ascii_str, symbol_display, struct_display]
            self.tree.insert('', 'end', iid=item_id, values=values)
            
            # Tag rows with symbols
            if row_symbols:
                self.tree.item(item_id, tags=('tagged',))
    
    def _on_symbol_select(self, event) -> None:
        """Handle symbol selection in the symbol list."""
        if not self.tag_list:
            return
        
        selection = event.widget.curselection()
        if not selection:
            return
        
        # Parse selected symbol
        text = event.widget.get(selection[0])
        name = text.split(' @')[0].strip()
        
        symbol = self.symbol_manager.get_symbol(name)
        if symbol:
            self._jump_to_address_direct(symbol.address)


def main() -> None:
    """Main entry point for the application."""
    import argparse
    import sys
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Intel HEX Viewer - A comprehensive GUI application for viewing and analyzing Intel HEX files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                     # Start with empty viewer
  %(prog)s firmware.hex        # Load firmware.hex file
  %(prog)s -h                  # Show this help message

For more information, visit: https://github.com/contributors/intel-hex-viewer
"""
    )
    
    parser.add_argument(
        "file",
        nargs="?",
        help="Intel HEX file to load on startup"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"Intel HEX Viewer {__version__}"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    # Create and run the application
    try:
        root = tk.Tk()
        app = HexViewerApp(root)
        
        # Set minimum window size
        root.minsize(800, 600)
        
        # Center window
        root.update_idletasks()
        width = 1200
        height = 800
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Load file if specified
        if args.file:
            if os.path.exists(args.file):
                # Load the hex file directly using the hex_parser
                try:
                    success = app.hex_parser.load_hex_file(args.file)
                    if success:
                        app._refresh_hex_display()
                        filename = os.path.basename(args.file)
                        row_count = len(app.hex_parser.rows)
                        app._update_status(f"Loaded {filename} - {row_count} rows")
                        root.title(f"Intel HEX Viewer - {filename}")
                        print(f"Loaded {args.file}")
                    else:
                        print(f"Error: Failed to load file '{args.file}'.", file=sys.stderr)
                        sys.exit(1)
                except Exception as e:
                    print(f"Error loading file '{args.file}': {e}", file=sys.stderr)
                    sys.exit(1)
            else:
                print(f"Error: File '{args.file}' not found.", file=sys.stderr)
                sys.exit(1)
        
        # Enable debug mode if requested
        if args.debug:
            print("Debug mode enabled")
        
        # Start the application
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 