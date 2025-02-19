# Shinobi Image Tool (SiT) - Release Notes

## Version 0.0.3
### 🔹 New Features:

✅ **Recursive Image Collection**:  
  - The `process_directory` function now uses `os.walk`, allowing all images in subdirectories to be processed automatically.

✅ **Bidirectional Format Conversion**:  
  - If no output format is specified, images retain their original format.  
  - If an output format is provided, all input files (regardless of format) are converted to the chosen format.

✅ **"No Change" Option in Guide Mode**:  
  - In guide mode, users can leave any field blank to keep its original value (e.g., image size, format, or cropping settings).

✅ **New Batch File for Guide Mode**:  
  - Added `run_guide.bat` for quick execution.  
  - Users can copy this file into any folder, and it will:  
    - Run Shinobi Image Tool in `guide-mode`.  
    - Use the folder it was executed in as the input directory.  
    - Automatically create an `output` folder in the same directory.

## Previous Releases:

### Version 0.0.3

- Bidirectional Format Conversion
- Return of Pixel-Based Cropping
- Recursive Image Collection
- "No Change" Option in Guide Mode
- New Batch File for Guide Mode

### Version 0.0.2
- Introduced interactive guide-mode.
- Basic input validation and "back" functionality.
- Initial support for WebP conversion.

### Version 0.0.1
- Core batch processing for JPG/PNG.
- CLI-based usage with predefined presets.
- Metadata preservation and quality settings.
