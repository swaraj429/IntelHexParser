"""
GUI Components Module

This module contains reusable GUI components and dialog windows for the Intel HEX Viewer,
including:
- Custom dialog windows
- Input validation helpers
- Common UI patterns
- Clipboard operations

Classes:
    BaseDialog: Base class for custom dialogs
    StructureDialog: Dialog for C structure input and viewing
    SettingsDialog: Settings configuration dialog
    SearchDialog: Search functionality dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Callable, Dict, Any, List
from abc import ABC, abstractmethod


class BaseDialog(ABC):
    """
    Base class for custom dialog windows.
    
    Provides common functionality for modal dialogs including:
    - Window setup and positioning
    - Result handling
    - Standard button layouts
    """
    
    def __init__(self, parent: tk.Tk, title: str, geometry: str = "400x300"):
        """
        Initialize the base dialog.
        
        Args:
            parent (tk.Tk): Parent window
            title (str): Dialog window title
            geometry (str): Window size as "WIDTHxHEIGHT"
        """
        self.parent = parent
        self.result: Optional[Any] = None
        
        # Create and configure window
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry(geometry)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the dialog
        self._center_window()
        
        # Setup UI
        self.create_widgets()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_cancel)
    
    def _center_window(self) -> None:
        """Center the dialog window over the parent."""
        self.window.update_idletasks()
        
        # Get window dimensions
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        # Get parent position and size
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate center position
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        
        self.window.geometry(f"+{x}+{y}")
    
    @abstractmethod
    def create_widgets(self) -> None:
        """Create the dialog's widgets. Must be implemented by subclasses."""
        pass
    
    def on_ok(self) -> None:
        """Handle OK button click. Should be overridden by subclasses."""
        self.window.destroy()
    
    def on_cancel(self) -> None:
        """Handle Cancel button click."""
        self.result = None
        self.window.destroy()
    
    def show(self) -> Optional[Any]:
        """
        Show the dialog and wait for result.
        
        Returns:
            Optional[Any]: Dialog result or None if cancelled
        """
        self.window.wait_window()
        return self.result


class StructureDialog(BaseDialog):
    """
    Dialog for inputting and viewing C structure definitions.
    
    Provides functionality for:
    - Text input for C structure definitions
    - Address specification
    - Structure validation
    - Value viewing in a separate dialog
    """
    
    def __init__(self, parent: tk.Tk, initial_address: str = "0x1000", 
                 initial_struct: str = ""):
        """
        Initialize the structure dialog.
        
        Args:
            parent (tk.Tk): Parent window
            initial_address (str): Default structure address
            initial_struct (str): Initial structure text
        """
        self.initial_address = initial_address
        self.initial_struct = initial_struct
        self.address_entry: Optional[tk.Entry] = None
        self.text_widget: Optional[tk.Text] = None
        self.on_view_values: Optional[Callable[[str, str], None]] = None
        
        super().__init__(parent, "Parse C Structure", "600x500")
    
    def create_widgets(self) -> None:
        """Create the structure dialog widgets."""
        # Address input frame
        addr_frame = tk.Frame(self.window)
        addr_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(addr_frame, text="Structure Address (hex):").pack(side="left")
        self.address_entry = tk.Entry(addr_frame, width=20)
        self.address_entry.pack(side="left", padx=5)
        self.address_entry.insert(0, self.initial_address)
        
        # Structure input
        tk.Label(self.window, text="C Structure Definition:").pack(
            anchor="w", padx=10, pady=(10, 0)
        )
        
        # Text area with scrollbar
        text_frame = tk.Frame(self.window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.text_widget = tk.Text(text_frame, height=20, width=70, wrap=tk.WORD)
        self.text_widget.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", 
                                command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Insert sample structure if no initial content
        if not self.initial_struct:
            sample_struct = """struct example_header {
    uint32_t magic;
    uint16_t version;
    uint16_t flags;
    uint32_t data_offset;
    uint32_t data_size;
    uint8_t reserved[8];
    char name[16];
};"""
            self.text_widget.insert("1.0", sample_struct)
        else:
            self.text_widget.insert("1.0", self.initial_struct)
        
        # Button frame
        self.create_button_frame()
    
    def create_button_frame(self) -> None:
        """Create the button frame with OK, View Values, and Cancel buttons."""
        button_frame = tk.Frame(self.window)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(button_frame, text="Parse & Apply", 
                 command=self.on_ok).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="View Values", 
                 command=self.on_view_values_click).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Cancel", 
                 command=self.on_cancel).pack(side="left", padx=5)
    
    def on_view_values_click(self) -> None:
        """Handle View Values button click."""
        if self.on_view_values:
            struct_text = self.get_structure_text()
            address_text = self.get_address_text()
            self.on_view_values(struct_text, address_text)
    
    def on_ok(self) -> None:
        """Handle OK button click."""
        try:
            struct_text = self.get_structure_text().strip()
            address_text = self.get_address_text().strip()
            
            if not struct_text or not address_text:
                messagebox.showerror("Error", 
                    "Please provide both structure definition and address")
                return
            
            # Validate address format
            if address_text.startswith('0x'):
                address = int(address_text, 16)
            else:
                address = int(address_text)
            
            self.result = {
                'structure_text': struct_text,
                'address': address,
                'address_text': address_text
            }
            
            self.window.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid address format: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse input: {e}")
    
    def get_structure_text(self) -> str:
        """Get the structure text from the text widget."""
        if self.text_widget:
            return self.text_widget.get("1.0", tk.END)
        return ""
    
    def get_address_text(self) -> str:
        """Get the address text from the entry widget."""
        if self.address_entry:
            return self.address_entry.get()
        return ""
    
    def set_view_values_callback(self, callback: Callable[[str, str], None]) -> None:
        """Set the callback for the View Values button."""
        self.on_view_values = callback


class StructureValuesDialog(BaseDialog):
    """
    Dialog for displaying interpreted structure values in a table format.
    
    Shows structure fields with their addresses, types, sizes, and interpreted values.
    """
    
    def __init__(self, parent: tk.Tk, title: str = "Structure Values"):
        """
        Initialize the structure values dialog.
        
        Args:
            parent (tk.Tk): Parent window
            title (str): Dialog window title
        """
        self.tree: Optional[ttk.Treeview] = None
        self.values_data: List[Dict[str, Any]] = []
        
        super().__init__(parent, title, "700x400")
    
    def create_widgets(self) -> None:
        """Create the structure values display widgets."""
        # Create treeview for values
        columns = ["Field", "Address", "Type", "Size", "Value"]
        self.tree = ttk.Treeview(self.window, columns=columns, show='headings')
        
        # Configure columns
        column_widths = {"Field": 150, "Address": 80, "Type": 100, "Size": 60, "Value": 300}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", 
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Button frame
        self.create_button_frame()
    
    def create_button_frame(self) -> None:
        """Create the button frame."""
        button_frame = tk.Frame(self.window)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(button_frame, text="Copy to Clipboard", 
                 command=self.copy_to_clipboard).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Close", 
                 command=self.on_cancel).pack(side="left", padx=5)
    
    def set_values(self, values_data: List[Dict[str, Any]]) -> None:
        """
        Set the structure values to display.
        
        Args:
            values_data (List[Dict]): List of value dictionaries with keys:
                - field_name, address, type_name, size, value
        """
        self.values_data = values_data
        self._populate_tree()
    
    def _populate_tree(self) -> None:
        """Populate the treeview with structure values."""
        if not self.tree:
            return
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add new items
        for data in self.values_data:
            self.tree.insert("", "end", values=[
                data.get('field_name', ''),
                data.get('address', ''),
                data.get('type_name', ''),
                data.get('size', ''),
                data.get('value', '')
            ])
    
    def copy_to_clipboard(self) -> None:
        """Copy all structure values to clipboard."""
        try:
            if not self.values_data:
                return
            
            # Format output
            lines = ["Structure Values:"]
            lines.append("-" * 60)
            
            for data in self.values_data:
                field_name = data.get('field_name', '')
                address = data.get('address', '')
                type_name = data.get('type_name', '')
                size = data.get('size', '')
                value = data.get('value', '')
                
                lines.append(f"{field_name:20s} @ {address} ({type_name:10s}, {size:2s} bytes): {value}")
            
            output = "\n".join(lines)
            
            # Copy to clipboard
            self.window.clipboard_clear()
            self.window.clipboard_append(output)
            
            messagebox.showinfo("Copied", "Structure values copied to clipboard")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {e}")


class SettingsDialog(BaseDialog):
    """Dialog for application settings configuration."""
    
    def __init__(self, parent: tk.Tk, current_settings: Dict[str, Any]):
        """
        Initialize the settings dialog.
        
        Args:
            parent (tk.Tk): Parent window
            current_settings (Dict): Current application settings
        """
        self.current_settings = current_settings.copy()
        self.widgets: Dict[str, tk.Widget] = {}
        
        super().__init__(parent, "Settings", "300x200")
    
    def create_widgets(self) -> None:
        """Create the settings dialog widgets."""
        # Bytes per row setting
        row_frame = tk.Frame(self.window)
        row_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(row_frame, text="Bytes per row (1-64):").pack(side="left")
        self.widgets['bytes_per_row'] = tk.Entry(row_frame, width=10)
        self.widgets['bytes_per_row'].pack(side="right")
        self.widgets['bytes_per_row'].insert(0, str(self.current_settings.get('bytes_per_row', 16)))
        
        # Endianness setting
        endian_frame = tk.Frame(self.window)
        endian_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(endian_frame, text="Endianness:").pack(side="left")
        self.widgets['endianness'] = tk.StringVar(value=self.current_settings.get('endianness', 'little'))
        
        endian_options = tk.Frame(endian_frame)
        endian_options.pack(side="right")
        
        tk.Radiobutton(endian_options, text="Little", 
                      variable=self.widgets['endianness'], 
                      value="little").pack(side="left")
        tk.Radiobutton(endian_options, text="Big", 
                      variable=self.widgets['endianness'], 
                      value="big").pack(side="left")
        
        # Button frame
        self.create_button_frame()
    
    def create_button_frame(self) -> None:
        """Create the button frame."""
        button_frame = tk.Frame(self.window)
        button_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        tk.Button(button_frame, text="Apply", 
                 command=self.on_ok).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", 
                 command=self.on_cancel).pack(side="left", padx=5)
    
    def on_ok(self) -> None:
        """Handle OK button click."""
        try:
            # Validate bytes per row
            bytes_per_row = int(self.widgets['bytes_per_row'].get())
            if not 1 <= bytes_per_row <= 64:
                raise ValueError("Bytes per row must be between 1 and 64")
            
            # Get endianness
            endianness = self.widgets['endianness'].get()
            
            self.result = {
                'bytes_per_row': bytes_per_row,
                'endianness': endianness
            }
            
            self.window.destroy()
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))


class SearchDialog(BaseDialog):
    """Dialog for searching values in hex data."""
    
    def __init__(self, parent: tk.Tk):
        """Initialize the search dialog."""
        self.search_entry: Optional[tk.Entry] = None
        self.search_type: Optional[tk.StringVar] = None
        
        super().__init__(parent, "Search", "300x150")
    
    def create_widgets(self) -> None:
        """Create the search dialog widgets."""
        # Search input
        search_frame = tk.Frame(self.window)
        search_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(search_frame, text="Search for:").pack(anchor="w")
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(fill="x", pady=5)
        self.search_entry.focus()
        
        # Search type
        type_frame = tk.Frame(self.window)
        type_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(type_frame, text="Search type:").pack(anchor="w")
        self.search_type = tk.StringVar(value="auto")
        
        type_options = tk.Frame(type_frame)
        type_options.pack(anchor="w")
        
        tk.Radiobutton(type_options, text="Auto detect", 
                      variable=self.search_type, value="auto").pack(anchor="w")
        tk.Radiobutton(type_options, text="Hex", 
                      variable=self.search_type, value="hex").pack(anchor="w")
        tk.Radiobutton(type_options, text="ASCII", 
                      variable=self.search_type, value="ascii").pack(anchor="w")
        
        # Button frame
        self.create_button_frame()
        
        # Bind Enter key
        self.search_entry.bind('<Return>', lambda e: self.on_ok())
    
    def create_button_frame(self) -> None:
        """Create the button frame."""
        button_frame = tk.Frame(self.window)
        button_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        tk.Button(button_frame, text="Search", 
                 command=self.on_ok).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", 
                 command=self.on_cancel).pack(side="left", padx=5)
    
    def on_ok(self) -> None:
        """Handle OK button click."""
        if self.search_entry and self.search_type:
            search_text = self.search_entry.get().strip()
            if search_text:
                self.result = {
                    'query': search_text,
                    'search_type': self.search_type.get()
                }
                self.window.destroy()
            else:
                messagebox.showwarning("No Input", "Please enter a search term")


def show_info_dialog(parent: tk.Tk, title: str, message: str) -> None:
    """
    Show an information dialog.
    
    Args:
        parent (tk.Tk): Parent window
        title (str): Dialog title
        message (str): Message to display
    """
    messagebox.showinfo(title, message, parent=parent)


def show_error_dialog(parent: tk.Tk, title: str, message: str) -> None:
    """
    Show an error dialog.
    
    Args:
        parent (tk.Tk): Parent window
        title (str): Dialog title
        message (str): Error message to display
    """
    messagebox.showerror(title, message, parent=parent)


def choose_file(parent: tk.Tk, title: str, filetypes: List[tuple]) -> Optional[str]:
    """
    Show a file chooser dialog.
    
    Args:
        parent (tk.Tk): Parent window
        title (str): Dialog title
        filetypes (List[tuple]): File type filters
        
    Returns:
        Optional[str]: Selected file path or None if cancelled
    """
    return filedialog.askopenfilename(parent=parent, title=title, filetypes=filetypes)


def choose_save_file(parent: tk.Tk, title: str, defaultextension: str, 
                    filetypes: List[tuple]) -> Optional[str]:
    """
    Show a save file dialog.
    
    Args:
        parent (tk.Tk): Parent window
        title (str): Dialog title
        defaultextension (str): Default file extension
        filetypes (List[tuple]): File type filters
        
    Returns:
        Optional[str]: Selected file path or None if cancelled
    """
    return filedialog.asksaveasfilename(
        parent=parent, 
        title=title,
        defaultextension=defaultextension,
        filetypes=filetypes
    ) 