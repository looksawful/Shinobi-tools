import argparse
import os
import json
import sys
from datetime import datetime
from image_optimizer import ImageOptimizer
import shutil
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.panel import Panel

__version__ = "0.0.1"

console = Console()

LOGO = r"""
 ░▒▓███████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░ ░▒▓███████▓▒░   ░▒▓██████▓▒░  ░▒▓███████▓▒░  ░▒▓█▓▒░
░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░
░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░
 ░▒▓██████▓▒░  ░▒▓████████▓▒░ ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓███████▓▒░  ░▒▓█▓▒░
       ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░
       ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░
░▒▓███████▓▒░  ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░  ░▒▓██████▓▒░  ░▒▓███████▓▒░  ░▒▓█▓▒░

   Shinobi Image Tool (SiT) v{}
""".format(__version__)

PRESETS = {
    "default": {},
    "social": {"size": "1080x1080", "aspect": "1:1", "quality": 90, "format": "jpg"},
    "print": {"size": "3000x3000", "aspect": "1:1", "quality": 100, "dpi": 300, "format": "tiff"},
    "web": {"size": "1920x1080", "aspect": "16:9", "quality": 80, "format": "webp"},
    "fast": {"quality": 70}
}


def print_logo():
    console.print(Panel(LOGO, style="bold magenta", expand=False))


def load_config(config_path="config.json"):
    default_config = {
        "default_input_dir": "input",
        "default_output_dir": "output",
        "default_size": "1080x1080",
        "default_aspect": "1:1",
        "default_crop": "center",
        "default_format": "webp",
        "default_quality": 100,
        "default_dpi": None,
        "default_keep_metadata": False,
        "default_timestamp": "datetime",
        "default_group_by_format": False
    }
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            console.print(f"[red]Error loading config file: {e}[/red]")
    else:
        config = default_config
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    for key, value in default_config.items():
        if key not in config:
            config[key] = value
    return config


def parse_size(size_str):
    try:
        width, height = map(int, size_str.lower().split("x"))
        if width > 4080 or height > 4080:
            raise ValueError("Dimensions must not exceed 4080px.")
        return (width, height)
    except Exception as e:
        console.print(f"[red]Invalid size format '{size_str}': {e}[/red]")
        return None


def parse_crop_pixels(crop_str):
    try:
        crop_values = list(map(int, crop_str.split(",")))
        if len(crop_values) not in [1, 2, 4]:
            raise ValueError("Crop_pixels must contain 1, 2, or 4 values.")
        return crop_values
    except Exception as e:
        console.print(
            f"[red]Invalid crop_pixels format '{crop_str}': {e}[/red]")
        return None


def reset_output_directory(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        console.print(
            f":warning: [yellow]Output directory {output_dir} has been reset.[/yellow]")
    else:
        console.print(
            f":information_source: [yellow]Output directory {output_dir} does not exist. Nothing to reset.[/yellow]")


def guide_mode(config):
    console.print(
        "[bold green]Guide Mode: Answer the questions to configure the conversion settings[/bold green]\n")
    args = {}
    args["input_dir"] = Prompt.ask(
        "Enter input directory", default=config.get("default_input_dir"))
    args["output_dir"] = Prompt.ask(
        "Enter output directory", default=config.get("default_output_dir"))
    preset_list = list(PRESETS.keys())
    preset_choice = Prompt.ask(
        "Choose a preset (" + ", ".join(preset_list) + ")", default="default")
    if preset_choice not in PRESETS:
        console.print(
            f"[red]Preset '{preset_choice}' not found. Using 'default'.[/red]")
        preset_choice = "default"
    preset_params = PRESETS[preset_choice]
    args["preset"] = preset_choice
    args["size"] = Prompt.ask("Enter size (e.g., 1080x1080)", default=preset_params.get(
        "size", config.get("default_size")))
    args["aspect"] = Prompt.ask("Enter aspect ratio (e.g., 1:1 or 16:9)",
                                default=preset_params.get("aspect", config.get("default_aspect")))
    args["crop"] = Prompt.ask(
        "Enter crop position (center, top, bottom, left, right)", default=config.get("default_crop"))
    args["max_size"] = Prompt.ask(
        "Enter max size (e.g., 1920x1080) or leave blank", default="")
    args["crop_pixels"] = Prompt.ask(
        "Enter crop_pixels (e.g., 10 or 10,20,30,40) or leave blank", default="")
    args["format"] = Prompt.ask("Enter output format (webp, jpg, png)",
                                default=preset_params.get("format", config.get("default_format")))
    quality_default = preset_params.get(
        "quality", config.get("default_quality"))
    args["quality"] = IntPrompt.ask(
        "Enter quality (0-100)", default=quality_default)
    dpi_default = preset_params.get("dpi", config.get("default_dpi"))
    args["dpi"] = IntPrompt.ask("Enter DPI (e.g., 300) or leave blank", default=dpi_default) if dpi_default is not None else Prompt.ask(
        "Enter DPI (e.g., 300) or leave blank", default="")
    args["delete_originals"] = Confirm.ask(
        "Delete original files after processing?", default=False)
    args["keep_metadata"] = Confirm.ask(
        "Keep image metadata (EXIF)?", default=False)
    args["timestamp"] = Prompt.ask(
        "Choose timestamp option (none, date, datetime)", default=config.get("default_timestamp"))
    args["group_by_format"] = Confirm.ask(
        "Group files by format?", default=config.get("default_group_by_format"))
    args["save_config"] = Confirm.ask(
        "Save current settings to config?", default=False)
    return args


def main():
    print_logo()
    config = load_config()
    parser = argparse.ArgumentParser(
        description="Shinobi Image Tool (SiT) - Batch image processor with presets and guide-mode.")
    parser.add_argument("--guide-mode", action="store_true",
                        help="Run interactive guide-mode (no flags required)")
    parser.add_argument("--preset", type=str, default="default", choices=list(
        PRESETS.keys()), help="Select a preset (default, social, print, web, fast)")
    parser.add_argument("-i", "--input", type=str, help="Input directory")
    parser.add_argument("-o", "--output", type=str, help="Output directory")
    parser.add_argument("-s", "--size", type=str,
                        help="Target size (e.g., 1080x1080)")
    parser.add_argument("-a", "--aspect", type=str,
                        help="Aspect ratio (e.g., 16:9)")
    parser.add_argument("-f", "--format", type=str,
                        help="Output format (webp, jpg, png)")
    parser.add_argument("--quality", type=int, help="Output quality (0-100)")
    parser.add_argument("--dpi", type=int, help="Set DPI (e.g., 300)")
    parser.add_argument("--delete-originals", action="store_true",
                        help="Delete original files after processing")
    parser.add_argument("--keep-metadata", action="store_true",
                        help="Preserve image metadata (EXIF)")
    parser.add_argument("-v", "--version", action="version",
                        version=f"SiT v{__version__}")
    args = parser.parse_args()
    if args.guide_mode:
        args_dict = guide_mode(config)
    else:
        args_dict = vars(args)
    input_dir = args_dict.get("input") or config.get("default_input_dir")
    output_dir = args_dict.get("output") or config.get("default_output_dir")
    size_str = args_dict.get("size") or config.get("default_size")
    aspect = args_dict.get("aspect") or config.get("default_aspect")
    _format = args_dict.get("format") or config.get("default_format")
    quality = args_dict.get("quality") if args_dict.get(
        "quality") is not None else config.get("default_quality")
    dpi = args_dict.get("dpi") if args_dict.get(
        "dpi") is not None else config.get("default_dpi")
    keep_metadata = args_dict.get("keep_metadata") if args_dict.get(
        "keep_metadata") is not None else config.get("default_keep_metadata")
    delete_originals = args_dict.get("delete_originals") if args_dict.get(
        "delete_originals") is not None else False
    parsed_size = parse_size(size_str)
    while parsed_size is None:
        console.print(
            "[red]Please enter a valid size (e.g., 1080x1080) that does not exceed 4080px.[/red]")
        size_str = Prompt.ask(
            "Enter new size", default=config.get("default_size"))
        parsed_size = parse_size(size_str)
    optimizer = ImageOptimizer(
        input_dir=input_dir,
        output_dir=output_dir,
        size=parsed_size,
        aspect_ratio=aspect,
        output_format=_format,
        quality=quality,
        dpi=dpi,
        keep_metadata=keep_metadata,
        delete_originals=delete_originals
    )
    optimizer.process_directory()


if __name__ == "__main__":
    main()
