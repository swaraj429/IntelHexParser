import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from intelhex import IntelHex
from collections import defaultdict
import csv
import os
import re
import struct

class HexViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Intel HEX Viewer")
        self.ih = None
        self.rows = []
        self.tags = {}  # name -> (address, size)
        self.addr_to_tags = {}  # address -> [tag_names]
        self.bytes_per_row = 16  # Default 16 bytes per row
        self.highlighted_items = []  # Track highlighted items for cleanup
        self.struct_fields = {}  # Store parsed structure fields
        self.endianness = 'little'  # Default endianness

        self.create_menu()
        self.create_layout()
        self.create_status_bar()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        # File menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open HEX File", command=self.open_file)
        filemenu.add_command(label="Export as CSV", command=self.export_csv)
        filemenu.add_command(label="Export as Binary", command=self.export_bin)
        filemenu.add_separator()
        filemenu.add_command(label="Load Map File", command=self.load_map_file_dialog)
        filemenu.add_command(label="Load Header File", command=self.load_header_file_dialog)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        
        # View menu
        viewmenu = tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Set Bytes Per Row", command=self.set_bytes_per_row)
        menubar.add_cascade(label="View", menu=viewmenu)
        
        # Tools menu
        toolsmenu = tk.Menu(menubar, tearoff=0)
        toolsmenu.add_command(label="Parse C Structure", command=self.parse_c_structure_dialog)
        toolsmenu.add_command(label="Set Endianness", command=self.set_endianness_dialog)
        menubar.add_cascade(label="Tools", menu=toolsmenu)
        
        self.root.config(menu=menubar)

    def create_layout(self):
        paned = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True)

        # Left pane: tag list
        left_frame = ttk.Frame(paned, width=200)
        ttk.Label(left_frame, text="Tags").pack(anchor="nw", padx=5, pady=5)
        self.tag_list = tk.Listbox(left_frame)
        self.tag_list.pack(fill="both", expand=True, padx=5, pady=5)
        self.tag_list.bind('<<ListboxSelect>>', self.on_tag_select)
        paned.add(left_frame, weight=1)

        # Right pane: hex table
        self.right_frame = ttk.Frame(paned)
        paned.add(self.right_frame, weight=4)
        
        # Create treeview (will be recreated when bytes_per_row changes)
        self.create_treeview()

    def create_treeview(self):
        # Remove existing treeview if it exists
        for widget in self.right_frame.winfo_children():
            widget.destroy()
            
        columns = ["Address"] + [f"+{i:02X}" for i in range(self.bytes_per_row)] + ["ASCII"] + ["Tags"] + ["Struct Values"]
        self.tree = ttk.Treeview(self.right_frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            width = 80 if col == "Address" else 40
            if col == "ASCII":
                width = max(80, self.bytes_per_row * 8)  # Adjust ASCII width based on bytes per row
            elif col == "Tags":
                width = 200
            elif col == "Struct Values":
                width = 300
            self.tree.column(col, width=width, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def create_status_bar(self):
        self.status = ttk.Label(self.root, text="Load a HEX file or map/header.", anchor="w")
        self.status.pack(side="bottom", fill="x")

    def update_status(self, text):
        self.status.config(text=text)

    def set_endianness_dialog(self):
        def apply_endianness():
            self.endianness = endian_var.get()
            popup.destroy()
            if self.struct_fields:
                self.refresh_struct_values()
            self.update_status(f"Endianness set to {self.endianness}")

        popup = tk.Toplevel(self.root)
        popup.title("Set Endianness")
        popup.geometry("200x120")
        
        tk.Label(popup, text="Data Endianness:").pack(pady=10)
        
        endian_var = tk.StringVar(value=self.endianness)
        tk.Radiobutton(popup, text="Little Endian", variable=endian_var, value="little").pack()
        tk.Radiobutton(popup, text="Big Endian", variable=endian_var, value="big").pack()
        
        tk.Button(popup, text="Apply", command=apply_endianness).pack(pady=10)

    def parse_c_structure_dialog(self):
        def parse_and_apply():
            try:
                struct_text = text_widget.get("1.0", tk.END).strip()
                address_str = address_entry.get().strip()
                
                if not struct_text or not address_str:
                    messagebox.showerror("Error", "Please provide both structure definition and address")
                    return
                
                # Parse address
                if address_str.startswith('0x'):
                    base_address = int(address_str, 16)
                else:
                    base_address = int(address_str)
                
                # Parse structure
                fields = self.parse_c_structure(struct_text)
                if not fields:
                    messagebox.showerror("Error", "Failed to parse structure")
                    return
                
                # Store parsed fields with their absolute addresses
                self.struct_fields = {}
                for field_name, (offset, size, type_name) in fields.items():
                    abs_address = base_address + offset
                    self.struct_fields[field_name] = (abs_address, size, type_name)
                
                # Refresh display
                self.refresh_struct_values()
                popup.destroy()
                self.update_status(f"Parsed structure with {len(fields)} fields at 0x{base_address:08X}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to parse structure: {e}")

        popup = tk.Toplevel(self.root)
        popup.title("Parse C Structure")
        popup.geometry("600x500")
        
        # Address input
        addr_frame = tk.Frame(popup)
        addr_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(addr_frame, text="Structure Address (hex):").pack(side="left")
        address_entry = tk.Entry(addr_frame, width=20)
        address_entry.pack(side="left", padx=5)
        address_entry.insert(0, "0x1000")
        
        # Structure input
        tk.Label(popup, text="C Structure Definition:").pack(anchor="w", padx=10, pady=(10,0))
        
        text_frame = tk.Frame(popup)
        text_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        text_widget = tk.Text(text_frame, height=20, width=70)
        text_widget.pack(side="left", fill="both", expand=True)
        
        text_scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=text_scrollbar.set)
        text_scrollbar.pack(side="right", fill="y")
        
        # Sample structure
        sample_struct = """struct example_header {
            uint32_t magic;
            uint16_t version;
            uint16_t flags;
            uint32_t data_offset;
            uint32_t data_size;
            uint8_t reserved[8];
            char name[16];
        };"""
        text_widget.insert("1.0", sample_struct)
        
        # Buttons
        button_frame = tk.Frame(popup)
        button_frame.pack(fill="x", padx=10, pady=10)
        tk.Button(button_frame, text="Parse & Apply", command=parse_and_apply).pack(side="left", padx=5)
        tk.Button(button_frame, text="View Values", command=lambda: self.view_struct_values_dialog(text_widget.get("1.0", tk.END).strip(), address_entry.get().strip())).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=popup.destroy).pack(side="left", padx=5)

    def view_struct_values_dialog(self, struct_text, address_str):
        """Show a dialog with the interpreted structure values"""
        try:
            if not struct_text or not address_str:
                messagebox.showerror("Error", "Please provide both structure definition and address")
                return
            
            # Parse address
            if address_str.startswith('0x'):
                base_address = int(address_str, 16)
            else:
                base_address = int(address_str)
            
            # Parse structure
            fields = self.parse_c_structure(struct_text)
            if not fields:
                messagebox.showerror("Error", "Failed to parse structure")
                return
            
            # Create values dialog
            values_popup = tk.Toplevel(self.root)
            values_popup.title("Structure Values")
            values_popup.geometry("700x400")
            
            # Create treeview for values
            columns = ["Field", "Address", "Type", "Size", "Value"]
            tree = ttk.Treeview(values_popup, columns=columns, show='headings')
            for col in columns:
                tree.heading(col, text=col)
                if col == "Field":
                    tree.column(col, width=150)
                elif col == "Address":
                    tree.column(col, width=80)
                elif col == "Type":
                    tree.column(col, width=100)
                elif col == "Size":
                    tree.column(col, width=60)
                elif col == "Value":
                    tree.column(col, width=300)
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(values_popup, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            # Pack tree and scrollbar
            tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            scrollbar.pack(side="right", fill="y", pady=10)
            
            # Populate with field values
            for field_name, (offset, size, type_name) in sorted(fields.items(), key=lambda x: x[1][0]):
                abs_address = base_address + offset
                
                # Get interpreted value
                if self.ih:
                    value = self.interpret_struct_value(abs_address, size, type_name)
                else:
                    value = "No hex data loaded"
                
                tree.insert("", "end", values=[
                    field_name,
                    f"0x{abs_address:08X}",
                    type_name,
                    size,
                    value
                ])
            
            # Add buttons
            button_frame = tk.Frame(values_popup)
            button_frame.pack(fill="x", padx=10, pady=10)
            
            def copy_to_clipboard():
                # Copy all values to clipboard
                output = f"Structure at 0x{base_address:08X}:\n"
                for field_name, (offset, size, type_name) in sorted(fields.items(), key=lambda x: x[1][0]):
                    abs_address = base_address + offset
                    if self.ih:
                        value = self.interpret_struct_value(abs_address, size, type_name)
                    else:
                        value = "No hex data loaded"
                    output += f"{field_name:20s} @ 0x{abs_address:08X} ({type_name:10s}, {size:2d} bytes): {value}\n"
                
                self.root.clipboard_clear()
                self.root.clipboard_append(output)
                messagebox.showinfo("Copied", "Structure values copied to clipboard")
            
            tk.Button(button_frame, text="Copy to Clipboard", command=copy_to_clipboard).pack(side="left", padx=5)
            tk.Button(button_frame, text="Close", command=values_popup.destroy).pack(side="left", padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show structure values: {e}")

    def parse_c_structure(self, struct_text):
        """Parse C structure definition and return field offsets and sizes"""
        fields = {}
        current_offset = 0
        
        # Remove comments and normalize whitespace
        struct_text = re.sub(r'//.*$', '', struct_text, flags=re.MULTILINE)
        struct_text = re.sub(r'/\*.*?\*/', '', struct_text, flags=re.DOTALL)
        struct_text = re.sub(r'\s+', ' ', struct_text).strip()
        
        # Extract struct body
        struct_match = re.search(r'struct\s+\w+\s*\{(.*?)\}', struct_text, re.DOTALL)
        if not struct_match:
            return None
        
        struct_body = struct_match.group(1).strip()
        
        # Parse field declarations
        field_lines = [line.strip() for line in struct_body.split(';') if line.strip()]
        
        for line in field_lines:
            if not line:
                continue
                
            # Handle arrays: uint8_t reserved[8];
            array_match = re.match(r'(\w+)\s+(\w+)\[(\d+)\]', line)
            if array_match:
                type_name, field_name, array_size = array_match.groups()
                element_size = self.get_type_size(type_name)
                total_size = element_size * int(array_size)
                fields[field_name] = (current_offset, total_size, f"{type_name}[{array_size}]")
                current_offset += total_size
                continue
            
            # Handle regular fields: uint32_t magic;
            field_match = re.match(r'(\w+)\s+(\w+)', line)
            if field_match:
                type_name, field_name = field_match.groups()
                size = self.get_type_size(type_name)
                fields[field_name] = (current_offset, size, type_name)
                current_offset += size
                continue
        
        return fields

    def get_type_size(self, type_name):
        """Get size in bytes for C data types"""
        type_sizes = {
            'uint8_t': 1, 'int8_t': 1, 'char': 1,
            'uint16_t': 2, 'int16_t': 2, 'short': 2,
            'uint32_t': 4, 'int32_t': 4, 'int': 4, 'long': 4,
            'uint64_t': 8, 'int64_t': 8, 'long long': 8,
            'float': 4, 'double': 8
        }
        return type_sizes.get(type_name, 1)

    def refresh_struct_values(self):
        """Refresh the hex view with interpreted structure values"""
        if not self.struct_fields or not self.ih:
            return
        
        # Clear existing display and rebuild
        if self.rows:
            self.display_data()

    def interpret_struct_value(self, address, size, type_name):
        """Interpret raw bytes as the specified data type"""
        if not self.ih:
            return "No data"
        
        try:
            # Read raw bytes
            raw_bytes = []
            for i in range(size):
                if address + i in self.ih.addresses():
                    raw_bytes.append(self.ih[address + i])
                else:
                    return "Missing data"
            
            if not raw_bytes:
                return "No data"
            
            # Convert to bytes object
            data = bytes(raw_bytes)
            
            # Determine endianness prefix
            endian_prefix = '<' if self.endianness == 'little' else '>'
            
            # Interpret based on type
            if type_name == 'uint8_t' or type_name == 'char':
                if type_name == 'char' and 32 <= data[0] <= 126:
                    return f"'{chr(data[0])}' (0x{data[0]:02X})"
                return f"0x{data[0]:02X} ({data[0]})"
            
            elif type_name == 'int8_t':
                val = struct.unpack('b', data)[0]
                return f"{val} (0x{data[0]:02X})"
            
            elif type_name == 'uint16_t':
                val = struct.unpack(f'{endian_prefix}H', data)[0]
                return f"0x{val:04X} ({val})"
            
            elif type_name == 'int16_t':
                val = struct.unpack(f'{endian_prefix}h', data)[0]
                return f"{val} (0x{val&0xFFFF:04X})"
            
            elif type_name == 'uint32_t':
                val = struct.unpack(f'{endian_prefix}I', data)[0]
                return f"0x{val:08X} ({val})"
            
            elif type_name == 'int32_t':
                val = struct.unpack(f'{endian_prefix}i', data)[0]
                return f"{val} (0x{val&0xFFFFFFFF:08X})"
            
            elif type_name == 'float':
                val = struct.unpack(f'{endian_prefix}f', data)[0]
                return f"{val:.6f}"
            
            elif type_name.startswith('char[') or type_name.startswith('uint8_t['):
                # Handle arrays as strings or hex
                if type_name.startswith('char['):
                    # Try to interpret as string
                    try:
                        null_idx = data.index(0)
                        text = data[:null_idx].decode('ascii', errors='ignore')
                        return f'"{text}"'
                    except:
                        text = data.decode('ascii', errors='ignore').rstrip('\x00')
                        return f'"{text}"'
                else:
                    # Show as hex array
                    hex_str = ' '.join(f'{b:02X}' for b in data)
                    return f"[{hex_str}]"
            
            else:
                # Default: show as hex
                hex_str = ' '.join(f'{b:02X}' for b in data)
                return f"[{hex_str}]"
                
        except Exception as e:
            return f"Error: {e}"

    def set_bytes_per_row(self):
        def apply_setting():
            try:
                new_bytes = int(entry.get())
                if new_bytes < 1 or new_bytes > 64:
                    raise ValueError("Value must be between 1 and 64")
                self.bytes_per_row = new_bytes
                self.create_treeview()
                if self.ih:
                    self.rows = self.parse_hex_to_rows(self.ih)
                    self.display_data()
                popup.destroy()
                self.update_status(f"Bytes per row set to {new_bytes}")
            except ValueError as e:
                messagebox.showerror("Invalid Input", f"Please enter a valid number (1-64): {e}")

        popup = tk.Toplevel(self.root)
        popup.title("Set Bytes Per Row")
        popup.geometry("250x120")
        
        tk.Label(popup, text="Bytes per row (1-64):").pack(pady=10)
        entry = tk.Entry(popup)
        entry.insert(0, str(self.bytes_per_row))
        entry.pack(pady=5)
        
        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Apply", command=apply_setting).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=popup.destroy).pack(side=tk.LEFT, padx=5)
        
        entry.focus()
        entry.select_range(0, tk.END)

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Intel HEX files", "*.hex;*.ihx"), ("All files", "*")])
        if not path:
            return
        try:
            self.ih = IntelHex(path)
            self.rows = self.parse_hex_to_rows(self.ih)
            self.display_data()
            self.update_status(f"Loaded {os.path.basename(path)} - {len(self.rows)} rows")
            self.root.title(f"Intel HEX Viewer - {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load HEX file:\n{e}")

    def parse_hex_to_rows(self, ih):
        rows = defaultdict(lambda: ["--"] * self.bytes_per_row)
        for addr in ih.addresses():
            base = addr - (addr % self.bytes_per_row)
            offset = addr % self.bytes_per_row
            rows[base][offset] = f"{ih[addr]:02X}"
        return sorted(rows.items())

    def build_addr_to_tags_map(self):
        """Build a map from addresses to tag names for display"""
        self.addr_to_tags.clear()
        for tag_name, (addr, size) in self.tags.items():
            # Add the tag to all addresses it covers
            for i in range(size):
                current_addr = addr + i
                if current_addr not in self.addr_to_tags:
                    self.addr_to_tags[current_addr] = []
                self.addr_to_tags[current_addr].append(tag_name)

    def display_data(self):
        self.tree.delete(*self.tree.get_children())
        # Configure highlight tag
        self.tree.tag_configure('highlight', background='yellow')
        self.tree.tag_configure('tagged', background='lightblue')
        
        # Build address to tags mapping
        self.build_addr_to_tags_map()
        
        for base, data in self.rows:
            ascii_str = ''.join(chr(int(b,16)) if b!='--' and 32<=int(b,16)<=126 else '.' for b in data)
            
            # Find tags for this row
            row_tags = []
            for i in range(self.bytes_per_row):
                addr = base + i
                if addr in self.addr_to_tags:
                    row_tags.extend(self.addr_to_tags[addr])
            
            # Remove duplicates and format
            unique_tags = list(set(row_tags))
            tag_display = ', '.join(unique_tags[:3])  # Show first 3 tags
            if len(unique_tags) > 3:
                tag_display += f" (+{len(unique_tags)-3} more)"
            
            # Find structure values for this row
            struct_values = []
            for field_name, (field_addr, field_size, field_type) in self.struct_fields.items():
                if base <= field_addr < base + self.bytes_per_row:
                    value = self.interpret_struct_value(field_addr, field_size, field_type)
                    struct_values.append(f"{field_name}: {value}")
            
            struct_display = '; '.join(struct_values[:2])  # Show first 2 fields
            if len(struct_values) > 2:
                struct_display += f" (+{len(struct_values)-2} more)"
            
            item_id = f"row_{base:08X}"
            self.tree.insert('', 'end', iid=item_id, 
                           values=[f"{base:08X}"] + data + [ascii_str] + [tag_display] + [struct_display])
            
            # Tag rows that have symbols
            if row_tags:
                self.tree.item(item_id, tags=('tagged',))

    def export_csv(self):
        if not self.rows:
            return messagebox.showinfo("No Data", "Please open a HEX file first.")
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not path:
            return
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            header = ["Address"] + [f"+{i:02X}" for i in range(self.bytes_per_row)]
            writer.writerow(header)
            for base, data in self.rows:
                writer.writerow([f"{base:08X}"] + data)
        self.update_status(f"CSV exported: {path}")

    def export_bin(self):
        if not self.ih:
            return messagebox.showinfo("No Data", "Please open a HEX file first.")
        path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("Binary files","*.bin")])
        if not path:
            return
        self.ih.tofile(path, format='bin')
        self.update_status(f"Binary exported: {path}")

    def load_map_file_dialog(self):
        path = filedialog.askopenfilename(filetypes=[("Map files","*.map;*.txt"), ("All files","*")])
        if path:
            self.load_map_file(path)

    def load_header_file_dialog(self):
        path = filedialog.askopenfilename(filetypes=[("Header files","*.h;*.hpp"), ("All files","*")])
        if path:
            self.load_header_file(path)

    def load_map_file(self, map_path):
        self.tags.clear()
        with open(map_path) as f:
            for line in f:
                m = re.match(r"\s*(0x[0-9A-Fa-f]+)\s+(\S+)", line)
                if m:
                    addr = int(m.group(1), 16)
                    name = m.group(2)
                    self.tags[name] = (addr, 1)
        self.refresh_tag_list()
        # Refresh the hex display to show tags
        if self.rows:
            self.display_data()
        self.update_status(f"Map loaded: {len(self.tags)} symbols")

    def load_header_file(self, hdr_path):
        with open(hdr_path) as f:
            current_struct = None
            offset = 0
            for line in f:
                line = line.strip()
                m = re.match(r"#define\s+(\w+)\s+(0x[0-9A-Fa-f]+)", line)
                if m:
                    name, val = m.groups()
                    self.tags[name] = (int(val,16), 1)
                    continue
                ms = re.match(r"struct\s+(\w+)\s*{", line)
                if ms:
                    current_struct = ms.group(1); offset = 0; continue
                if current_struct:
                    if line.startswith('};'):
                        current_struct = None; continue
                    mm = re.match(r"(uint(8|16|32)_t)\s+(\w+);", line)
                    if mm:
                        ctype, _, member = mm.groups()
                        size = {'uint8_t':1,'uint16_t':2,'uint32_t':4}[ctype]
                        fullname = f"{current_struct}.{member}"
                        self.tags[fullname] = (offset, size)
                        offset += size
        self.refresh_tag_list()
        # Refresh the hex display to show tags
        if self.rows:
            self.display_data()
        self.update_status(f"Header loaded: {len(self.tags)} tags")

    def refresh_tag_list(self):
        self.tag_list.delete(0, tk.END)
        for name in sorted(self.tags, key=lambda n: self.tags[n][0]):
            addr, size = self.tags[name]
            self.tag_list.insert(tk.END, f"{name} @     {addr:08X} ({size} bytes)")

    def on_tag_select(self, event):
        sel = event.widget.curselection()
        if not sel: 
            return
        text = event.widget.get(sel[0])
        name = text.split(' @ ')[0]
        addr, size = self.tags[name]
        self._jump_and_highlight(addr, size)

    def _clear_highlights(self):
        """Clear all previous highlights"""
        for item_id, original_values in self.highlighted_items:
            try:
                # Restore original values
                self.tree.item(item_id, values=original_values)
            except:
                pass
        self.highlighted_items.clear()

    def _jump_and_highlight(self, addr, size):
        if not self.rows:
            self.update_status("No hex data loaded")
            return
        
        # Clear previous highlights
        self._clear_highlights()
        
        # Find which row contains this address
        base = addr - (addr % self.bytes_per_row)
        item_id = f"row_{base:08X}"
        
        # Find the tree item
        if item_id in self.tree.get_children():
            # Jump to the item
            self.tree.see(item_id)
            self.tree.selection_set(item_id)
            
            # Highlight specific bytes
            self._highlight_bytes(item_id, addr, size)
            
            self.update_status(f"Jumped to 0x{addr:08X} (size: {size} bytes)")
        else:
            # Try to find any item that contains this address
            found = False
            for item in self.tree.get_children():
                values = self.tree.item(item, 'values')
                if values:
                    try:
                        item_addr = int(values[0], 16)
                        if item_addr <= addr < item_addr + self.bytes_per_row:
                            self.tree.see(item)
                            self.tree.selection_set(item)
                            
                            # Highlight specific bytes
                            self._highlight_bytes(item, addr, size)
                            
                            found = True
                            break
                    except ValueError:
                        continue
            
            if found:
                self.update_status(f"Jumped to 0x{addr:08X} (size: {size} bytes)")
            else:
                self.update_status(f"Address 0x{addr:08X} not found in loaded data")

    def _highlight_bytes(self, item_id, addr, size):
        """Highlight specific bytes in the hex view"""
        try:
            # Get the base address of this row
            values = self.tree.item(item_id, 'values')
            if not values:
                return
            
            base_addr = int(values[0], 16)
            
            # Store original values before any modification
            original_values = list(values)
            
            # Calculate which bytes to highlight in this row
            bytes_to_highlight = []
            bytes_highlighted = 0
            
            for i in range(size):
                current_addr = addr + i
                if current_addr < base_addr or current_addr >= base_addr + self.bytes_per_row:
                    # This byte is in a different row
                    if current_addr >= base_addr + self.bytes_per_row:
                        # Need to highlight bytes in the next row(s)
                        next_base = current_addr - (current_addr % self.bytes_per_row)
                        next_item_id = f"row_{next_base:08X}"
                        if next_item_id in self.tree.get_children():
                            remaining_size = size - bytes_highlighted
                            self._highlight_bytes(next_item_id, current_addr, remaining_size)
                    break
                
                # Calculate column index for this byte
                col_offset = current_addr - base_addr
                bytes_to_highlight.append(col_offset)
                bytes_highlighted += 1
            
            # Apply highlighting if there are bytes to highlight in this row
            if bytes_to_highlight:
                self._apply_cell_highlights(item_id, bytes_to_highlight, original_values)
                
        except Exception as e:
            print(f"Error highlighting bytes: {e}")

    def _apply_cell_highlights(self, item_id, byte_offsets, original_values):
        """Apply visual highlighting to specific byte positions"""
        try:
            # Create a copy of values to modify
            new_values = list(original_values)
            
            # Add brackets to the highlighted bytes
            for offset in byte_offsets:
                # Column index is offset + 1 (skip Address column)
                col_index = offset + 1
                if col_index < len(new_values):
                    current_val = new_values[col_index]
                    if current_val != "--":
                        new_values[col_index] = f"[{current_val}]"
            
            # Update the tree item with highlighted values
            self.tree.item(item_id, values=new_values)
            
            # Store original values for cleanup
            self.highlighted_items.append((item_id, original_values))
            
        except Exception as e:
            print(f"Error applying cell highlights: {e}")

if __name__ == '__main__':
    root = tk.Tk()
    app = HexViewerApp(root)
    root.mainloop()
