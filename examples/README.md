# Intel HEX Viewer Examples

This directory contains examples and sample files for the Intel HEX Viewer application.

## Files

### `basic_usage.py`
Demonstrates programmatic usage of the Intel HEX Viewer components without the GUI:
- Loading and parsing hex files
- C structure parsing and interpretation
- Symbol management
- Configuration options

Run with:
```bash
python basic_usage.py
```

### `sample.hex`
A sample Intel HEX file that you can use for testing the application. Contains:
- Various data patterns for testing
- Example firmware structure data
- ASCII text for search functionality testing

## Running the Examples

1. **Basic Usage Example**:
   ```bash
   cd examples
   python basic_usage.py
   ```

2. **GUI with Sample File**:
   ```bash
   python hex_viewer.py
   # Then use File → Open HEX File to load examples/sample.hex
   ```

3. **Testing with Sample File**:
   ```bash
   python hex_viewer.py examples/sample.hex
   ```

## Creating Your Own Examples

To create additional examples:

1. Copy the `basic_usage.py` template
2. Modify the imports and example code
3. Add appropriate documentation
4. Include sample data files if needed

## Example Use Cases

- **Firmware Analysis**: Load firmware hex files and analyze structure
- **Data Visualization**: View memory layouts and data patterns
- **Structure Parsing**: Parse C structures at specific memory addresses
- **Symbol Management**: Track and navigate between named memory locations
- **Data Export**: Export hex data to CSV or binary formats

## Notes

- The `basic_usage.py` example is designed to work without requiring actual hex files
- For real usage, replace the example data with actual hex file paths
- All examples assume the Intel HEX Viewer is installed or available in the parent directory 