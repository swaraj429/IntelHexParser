from intelhex import IntelHex
import csv
from collections import defaultdict

def hex_to_16byte_rows(hex_file_path, output_csv_path=None):
    ih = IntelHex(hex_file_path)

    # Group all used addresses by 16-byte row
    rows = defaultdict(lambda: ["--"] * 16)

    for addr in ih.addresses():
        base = addr - (addr % 16)
        offset = addr % 16
        rows[base][offset] = f"{ih[addr]:02X}"

    # Sort the rows by base address
    sorted_rows = sorted(rows.items())

    # Write to CSV
    if output_csv_path:
        with open(output_csv_path, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            header = ["Address"] + [f"+{i:02X}" for i in range(16)]
            writer.writerow(header)
            for base, data in sorted_rows:
                writer.writerow([f"{base:08X}"] + data)

    return sorted_rows

# Example usage
hex_file = "input.hex"
output_csv = "hex_16byte_table.csv"

table = hex_to_16byte_rows(hex_file, output_csv)
print(f"Converted {len(table)} rows. Output saved to {output_csv}")
