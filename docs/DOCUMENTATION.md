# Shinobi Image Tool (SiT) - Documentation

## 1. Overview
Shinobi Image Tool (SiT) is a command-line utility for batch image processing, supporting resizing, cropping, format conversion, and metadata management.

## 2. Features
### 2.1 Supported Formats
- **Input**: JPG, JPEG, PNG, JFIF, WebP.
- **Output**: JPG, PNG, WebP (multi-output supported).

### 2.2 Processing Features
- **Resizing**: Define exact pixel dimensions (`width x height`).
- **Aspect Ratio Control**: Crop while maintaining aspect ratio.
- **Quality Control**: Adjustable from 0-100 for lossy formats.
- **Cropping Methods**:
  - Fixed aspect cropping (`16:9`, `1:1`, etc.).
  - Pixel-based cropping (`crop_pixels`).
- **Metadata & EXIF**: Optionally preserve metadata.
- **DPI Configuration**: Specify DPI for print quality.

## 3. Using the Tool
### 3.1 Interactive Guide Mode
Run:
```sh
python cli.py --guide-mode
```
Key Features:
- Walkthrough with detailed descriptions.
- Format validation for input values.
- `back` functionality to correct previous inputs.
- A final summary before execution.

### 3.2 Command-Line Arguments
```sh
python cli.py -i input_folder -o output_folder -s 1080x1080 -a 16:9 -f jpg,png --quality 85
```

### Implementation Details

#### `image_optimizer.py`
Handles core image processing:
- Loads images and applies cropping based on aspect ratio.
- Resizes images to a specified size or fits them within max dimensions.
- Crops images based on pixel input.
- Saves output as WebP format with lossless compression.

#### `cli.py`
Provides the command-line interface:
- Loads settings from `config.json`.
- Parses user-defined parameters.
- Handles batch processing and directory management.

#### `requirements.txt`
Contains dependencies:
```
Pillow
rich
tqdm
```
