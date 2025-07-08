import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from intelhex import IntelHex
from collections import defaultdict
import os
import csv
import binascii

class HexViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Intel HEX Viewer")
        self.rows = []
        self.ih = None
        self.filepath = None

        self.create_menu()
        self.create_widgets()
        self.create_status_bar()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open HEX File", command=self.open_file)
        filemenu.add_command(label="Export as CSV", command=self.export_csv)
        filemenu.add_command(label="Export as Binary", command=self.export_bin)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # Tools
        toolmenu = tk.Menu(menubar, tearoff=0)
        toolmenu.add_command(label="Jump to Address", command=self.jump_to_address)
        toolmenu.add_command(label="Search ASCII or HEX", command=self.search_value)
        toolmenu.add_command(label="Memory Stats", command=self.show_stats)
        menubar.add_cascade(label="Tools", menu=toolmenu)

        # View
        viewmenu = tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Toggle Dark Theme", command=self.toggle_theme)
        menubar.add_cascade(label="View", menu=viewmenu)

        self.root.config(menu=menubar)

    def create_widgets(self):
        # TreeView setup
        frame = ttk.Frame(self.root)
        frame.pack(fill="both", expand=True)

        columns = ["Address"] + [f"+{i:02X}" for i in range(16)] + ["ASCII"]
        self.tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            width = 80 if col == "Address" else 40
            if col == "ASCII":
                width = 140
            self.tree.column(col, width=width, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def create_status_bar(self):
        self.status = ttk.Label(self.root, text="Load a HEX file to begin.", anchor="w")
        self.status.pack(side="bottom", fill="x")

    def update_status(self, text):
        self.status.config(text=text)

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Intel HEX files", "*.hex")])
        if not path:
            return
        try:
            self.ih = IntelHex(path)
            self.filepath = path
            self.rows = self.parse_hex_to_rows(self.ih)
            self.display_data()
            self.update_status(f"Loaded {os.path.basename(path)} - {len(self.rows)} memory rows")
            self.root.title(f"Intel HEX Viewer - {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load HEX file:\n{e}")

    def parse_hex_to_rows(self, ih):
        rows = defaultdict(lambda: ["--"] * 16)
        for addr in ih.addresses():
            base = addr - (addr % 16)
            offset = addr % 16
            rows[base][offset] = f"{ih[addr]:02X}"
        return sorted(rows.items())

    def display_data(self):
        self.tree.delete(*self.tree.get_children())
        for base, data in self.rows:
            ascii_str = ''.join(chr(int(b, 16)) if b != "--" and 32 <= int(b, 16) <= 126 else '.' for b in data)
            self.tree.insert("", "end", values=[f"{base:08X}"] + data + [ascii_str])

    def export_csv(self):
        if not self.rows:
            return messagebox.showinfo("No Data", "Please open a HEX file first.")
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path:
            return
        with open(path, "w", newline='') as f:
            writer = csv.writer(f)
            header = ["Address"] + [f"+{i:02X}" for i in range(16)]
            writer.writerow(header)
            for base, data in self.rows:
                writer.writerow([f"{base:08X}"] + data)
        self.update_status(f"Exported CSV: {path}")

    def export_bin(self):
        if not self.ih:
            return messagebox.showinfo("No HEX Loaded", "Load a HEX file first.")
        path = filedialog.asksaveasfilename(defaultextension=".bin")
        if not path:
            return
        self.ih.tofile(path, format='bin')
        self.update_status(f"Exported BIN: {path}")

    def jump_to_address(self):
        if not self.rows:
            return
        def go():
            try:
                addr = int(entry.get(), 16)
                base = addr - (addr % 16)
                for iid in self.tree.get_children():
                    if self.tree.item(iid)["values"][0] == f"{base:08X}":
                        self.tree.see(iid)
                        self.tree.selection_set(iid)
                        popup.destroy()
                        return
                messagebox.showinfo("Not Found", f"Address {addr:08X} not found.")
            except:
                messagebox.showerror("Invalid", "Enter a valid hexadecimal address.")

        popup = tk.Toplevel()
        popup.title("Jump to Address")
        tk.Label(popup, text="Address (Hex):").pack(padx=10, pady=5)
        entry = tk.Entry(popup)
        entry.pack(padx=10)
        tk.Button(popup, text="Jump", command=go).pack(pady=5)
        entry.focus()

    def search_value(self):
        if not self.ih:
            return
        def go():
            query = entry.get()
            if not query:
                return
            is_hex = all(c in "0123456789abcdefABCDEF" for c in query.replace(" ", ""))
            matches = []
            for addr in self.ih.addresses():
                val = self.ih[addr]
                if (not is_hex and chr(val) in query) or (is_hex and f"{val:02X}".lower() in query.lower()):
                    matches.append(addr)
            if matches:
                base = matches[0] - (matches[0] % 16)
                for iid in self.tree.get_children():
                    if self.tree.item(iid)["values"][0] == f"{base:08X}":
                        self.tree.see(iid)
                        self.tree.selection_set(iid)
                        break
                popup.destroy()
            else:
                messagebox.showinfo("No Match", "Value not found.")

        popup = tk.Toplevel()
        popup.title("Search")
        tk.Label(popup, text="Search (ASCII or HEX byte):").pack(padx=10, pady=5)
        entry = tk.Entry(popup)
        entry.pack(padx=10)
        tk.Button(popup, text="Search", command=go).pack(pady=5)
        entry.focus()

    def show_stats(self):
        if not self.ih:
            return
        total = self.ih.maxaddr() - self.ih.minaddr() + 1
        used = len(self.ih.addresses())
        unused = total - used
        messagebox.showinfo("Memory Stats",
            f"Start Address: {self.ih.minaddr():08X}\n"
            f"End Address:   {self.ih.maxaddr():08X}\n"
            f"Total Range:   {total} bytes\n"
            f"Used Bytes:    {used}\n"
            f"Unused:        {unused}")

    def toggle_theme(self):
        style = ttk.Style()
        current_theme = style.theme_use()
        dark = current_theme != "alt"
        style.theme_use("alt" if dark else "default")
        self.update_status("Theme changed")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = HexViewerApp(root)
    root.mainloop()
