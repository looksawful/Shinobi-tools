# Shinobi Image Tool (SiT)

![Shinobi Image Tool](https://your-image-url.com/banner.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)

## Overview

Shinobi Image Tool (SiT) is a command-line image processor for Windows written in Python. It provides a streamlined way to convert images to WebP format and back, as Windows does not have built-in support for WebP conversion. The tool is designed for handling batch image processing, supporting up to 600 images at once.

SiT allows for resizing, cropping, and optimizing images while maintaining high-quality output. It supports common image formats such as JPG, JPEG, PNG, and JFIF, and uses WebP for optimized storage.

## Features

✅ **Batch Processing**: Supports processing multiple images at once.  
✅ **Format Conversion**: Converts images to and from WebP format.  
✅ **Image Optimization**: Ensures high-quality images with lossless WebP compression.  
✅ **Cropping Options**: Supports various aspect ratios and cropping positions.  
✅ **Customizable Output**: Allows setting max dimensions, DPI, and aspect ratio.  
✅ **CLI Interface**: Provides a powerful command-line interface for easy automation.  

## Installation

SiT requires Python 3 and `Pillow` for image processing.

### Prerequisites

Ensure you have Python installed:

```sh
python --version
```

### Install Dependencies

Run the following command to install required dependencies:

```sh
pip install -r requirements.txt
```

## Configuration

The tool uses a `config.json` file to store default settings:

```json
{
  "default_input_dir": "input",
  "default_output_dir": "output",
  "default_size": "1080x1080",
  "default_aspect": "1:1",
  "default_crop": "center"
}
```

Modify these values to set default directories, image size, and cropping behavior.

## Usage

Run the CLI tool with the following options:

### Basic Usage

```sh
python cli.py -i input_folder -o output_folder
```

Processes images from `input_folder` and saves results in `output_folder`.

### Custom Image Size

```sh
python cli.py -s 1920x1080
```

Resizes images to 1920x1080.

### Set Aspect Ratio

```sh
python cli.py -a 16:9
```

Crops images to a 16:9 aspect ratio.

### Crop Position

```sh
python cli.py -c center
```

Other options: `top`, `bottom`, `left`, `right`.

### Set Maximum Size

```sh
python cli.py -m 1920x1080
```

Limits image dimensions while preserving the aspect ratio.

### Crop Pixels

```sh
python cli.py -p 10,20,30,40
```

Crops 10px from the top, 20px from the right, 30px from the bottom, and 40px from the left.

### Reset Output Directory

```sh
python cli.py -r
```

Deletes existing output before processing.

## Implementation Details

### `image_optimizer.py`

Handles core image processing:

- Loads images and applies cropping based on aspect ratio.
- Resizes images to a specified size or fits them within max dimensions.
- Crops images based on pixel input.
- Saves output as WebP format with lossless compression.

### `cli.py`

Provides the command-line interface:

- Loads settings from `config.json`.
- Parses user-defined parameters.
- Handles batch processing and directory management.

### `requirements.txt`

Contains dependencies:

```
Pillow
```

## Future Enhancements

- 🔹 **Drag-and-Drop Support**: Enhance usability for non-CLI users.
