import argparse
import os
import json
from datetime import datetime
from image_optimizer import ImageOptimizer
import shutil


def load_config(config_path="config.json"):
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            try:
                config = json.load(f)
            except Exception as e:
                print(f"Error loading config file: {e}")
    return config


def parse_size(size_str):
    try:
        width, height = map(int, size_str.lower().split("x"))
        if width > 4080 or height > 4080:
            raise ValueError(
                "Dimensions must not exceed 4080px in either direction.")
        return (width, height)
    except ValueError as ve:
        print(f"Error: {ve}")
        return None
    except Exception as e:
        print(f"Error parsing size: {e}")
        return None


def parse_crop_pixels(crop_str):
    try:
        crop_values = list(map(int, crop_str.split(",")))
        if len(crop_values) not in [1, 2, 4]:
            raise ValueError(
                "Invalid crop_pixels format. Should be 1, 2, or 4 values.")
        return crop_values
    except ValueError as ve:
        print(f"Error: {ve}")
        return None
    except Exception as e:
        print(f"Error parsing crop_pixels: {e}")
        return None


def reset_output_directory(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        print(f"Output {output_dir} has been reset.")
    else:
        print(
            f"Output {output_dir} does not exist. Nothing to reset.")


def main():
    config = load_config()

    default_input = config.get("default_input_dir", "input")
    default_output = config.get("default_output_dir", "output")
    default_size = config.get("default_size", "1080x1080")
    default_aspect = config.get("default_aspect", "1:1")
    default_crop = config.get("default_crop", "center")

    parser = argparse.ArgumentParser(
        description="High-performance image optimizer and WebP converter (CLI)")
    parser.add_argument("-i", "--input_dir", type=str, default=default_input,
                        help="Input directory (default from config)")
    parser.add_argument("-o", "--output_dir", type=str, default=default_output,
                        help="Output directory (default from config)")
    parser.add_argument("-s", "--size", type=str,
                        default=default_size, help="Target size (e.g., 1080x1080)")
    parser.add_argument("-a", "--aspect", type=str,
                        default=default_aspect, help="Aspect ratio (e.g., 1:1, 16:9)")
    parser.add_argument("-c", "--crop", type=str, default=default_crop,
                        choices=["center", "top", "bottom", "left", "right"], help="Crop position")
    parser.add_argument("-m", "--max_size", type=str, default=None,
                        help="Maximum size (e.g., 1920x1080), maintaining aspect ratio")
    parser.add_argument("-p", "--crop_pixels", type=str, default=None,
                        help="Crop pixels from edges (e.g., 10 for all sides, 10,20 for vertical and horizontal, 10,20,30,40 for all sides)")
    parser.add_argument("-r", "--reset", action="store_true",
                        help="Reset (clear) the output directory before processing")
    args = parser.parse_args()

    if args.reset:
        reset_output_directory(args.output_dir)
        return  # Exit the program after resetting

    size = None
    while not size:
        size = parse_size(args.size)
        if not size:
            print(
                "Please provide a valid size (e.g., 1080x1080) that does not exceed 4080px in either direction.")
            new_size = input("Enter a new size: ")
            args.size = new_size  # Update size for the next iteration

    max_size = parse_size(args.max_size) if args.max_size else None
    crop_pixels = parse_crop_pixels(
        args.crop_pixels) if args.crop_pixels else None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_output_dir = os.path.join(args.output_dir, timestamp)
    os.makedirs(final_output_dir, exist_ok=True)

    print(f"Input Directory: {args.input_dir}")
    print(f"Output Directory: {final_output_dir}")
    print(f"Target Size: {size}")
    print(f"Aspect Ratio: {args.aspect}")
    print(f"Crop Position: {args.crop}")
    print(f"Max Size: {max_size}")
    print(f"Crop Pixels: {crop_pixels}")

    optimizer = ImageOptimizer(args.input_dir, final_output_dir, size=size, aspect_ratio=args.aspect,
                               crop_position=args.crop, max_size=max_size, crop_pixels=crop_pixels)
    optimizer.process_directory()


if __name__ == "__main__":
    main()
