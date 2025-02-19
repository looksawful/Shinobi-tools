import argparse
import os
import json
import sys
import shutil
from datetime import datetime
from image_optimizer import ImageOptimizer
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.panel import Panel

__version__ = "0.0.3"
console = Console()

LOGO = r"""
 ░▒▓███████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░ ░▒▓███████▓▒░   ░▒▓██████▓▒░  ░▒▓███████▓▒░  ░▒▓█▓▒░
░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░
░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░
 ░▒▓██████▓▒░  ░▒▓████████▓▒░ ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓███████▓▒░  ░▒▓█▓▒░
       ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░
       ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░
░▒▓███████▓▒░  ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░  ░▒▓██████▓▒░  ░▒▓███████▓▒░  ░▒▓█▓▒░

   Shinobi Image Tool (SiT) v{version}
""".format(version=__version__)

PRESETS = {
    "default": {"description": "Default settings.", "settings": {}},
    "social": {"description": "Optimized for social media (1080x1080, 1:1, quality 90, jpg).", "settings": {"size": "1080x1080", "aspect": "1:1", "quality": 90, "format": "jpg"}},
    "print": {"description": "Optimized for print (3000x3000, 1:1, quality 100, dpi 300, tiff).", "settings": {"size": "3000x3000", "aspect": "1:1", "quality": 100, "dpi": 300, "format": "tiff"}},
    "web": {"description": "Optimized for web (1920x1080, 16:9, quality 80, webp).", "settings": {"size": "1920x1080", "aspect": "16:9", "quality": 80, "format": "webp"}},
    "fast": {"description": "Faster processing with lower quality (quality 70).", "settings": {"quality": 70}}
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


def print_presets_info():
    console.print("\n[bold underline]Available Presets:[/bold underline]")
    for key, info in PRESETS.items():
        console.print(f"[bold]{key}[/bold]: {info['description']}")
    console.print(
        "Type the preset name or leave blank for no preset.\nType 'back' to return to previous step.\n")


def prompt_with_back(prompt_text, default_value=None, validator=None, allow_empty=True, choices=None):
    while True:
        try:
            default_str = f" ({default_value})" if default_value is not None and default_value != "" else ""
            user_input = input(f"{prompt_text}{default_str}: ").strip()
            if user_input.lower() == "back":
                return "back"
            if user_input == "" and allow_empty:
                return default_value if default_value != "" else None
            if choices and user_input.lower() not in [c.lower() for c in choices]:
                print(
                    f"Invalid input. Please enter one of: {', '.join(choices)}")
                continue
            if validator:
                is_valid, error_message, processed_value = validator(
                    user_input)
                if is_valid:
                    return processed_value
                else:
                    print(error_message)
                    continue
            return user_input
        except KeyboardInterrupt:
            print(
                "\nInterrupt detected. Type 'back' to return to previous step or press Enter to retry.")


def parse_size(size_str):
    try:
        width, height = map(int, size_str.lower().split("x"))
        if width > 4080 or height > 4080:
            raise ValueError("Dimensions must not exceed 4080px.")
        return (width, height)
    except Exception as e:
        console.print(f"[red]Invalid size format '{size_str}': {e}[/red]")
        return None


def validate_size(value):
    parsed = parse_size(value)
    if parsed is not None:
        return True, "", parsed
    else:
        return False, "Invalid size format.", None


def validate_aspect(value):
    parts = value.split(":")
    if len(parts) != 2:
        return False, "Aspect ratio must be in format 'width:height', e.g. 16:9.", None
    try:
        aspect_width, aspect_height = int(parts[0]), int(parts[1])
        if aspect_width <= 0 or aspect_height <= 0:
            return False, "Aspect ratio values must be positive.", None
        return True, "", f"{aspect_width}:{aspect_height}"
    except Exception:
        return False, "Invalid numbers in aspect ratio.", None


def validate_crop_position(value):
    short_map = {"c": "center", "t": "top",
                 "b": "bottom", "l": "left", "r": "right"}
    value_lower = value.lower()
    if value_lower in short_map:
        return True, "", short_map[value_lower]
    valid_positions = ["center", "top", "bottom", "left", "right"]
    if value_lower in valid_positions:
        return True, "", value_lower
    return False, ("Crop position must be one of: [C]enter, [T]op, [B]ottom, [L]eft, [R]ight."), None


def validate_crop_pixels(value, target_size=None):
    try:
        parts = list(map(int, value.split(",")))
        if len(parts) not in [1, 2, 4]:
            return False, "Crop_pixels must contain 1, 2, or 4 values.", None
        if target_size:
            width, height = target_size
            if len(parts) == 1:
                if 2 * parts[0] >= width or 2 * parts[0] >= height:
                    return False, "Crop_pixels value too high for the given size.", None
            elif len(parts) == 2:
                if 2 * parts[0] >= width or (parts[0] + parts[1]) >= height:
                    return False, "Crop_pixels values too high for the given size.", None
            elif len(parts) == 4:
                if (parts[3] + parts[1]) >= width or (parts[0] + parts[2]) >= height:
                    return False, "Crop_pixels values too high for the given size.", None
        return True, "", parts
    except Exception as e:
        return False, f"Invalid crop_pixels format: {e}", None


def validate_format(value):
    valid_formats = {"webp", "jpg", "png"}
    short_map = {"w": "webp", "j": "jpg", "p": "png"}
    formats = [v.strip() for v in value.split(",")]
    result = []
    for fmt in formats:
        fmt_lower = fmt.lower()
        if fmt_lower in short_map:
            result.append(short_map[fmt_lower])
        elif fmt_lower in valid_formats:
            result.append(fmt_lower)
        else:
            return False, "Output format must be one of: [W]ebp, [J]pg, [P]ng.", None
    result = list(dict.fromkeys(result))
    if len(result) == 1:
        return True, "", result[0]
    return True, "", result


def validate_int_range(value, min_val, max_val):
    try:
        num = int(value)
        if num < min_val or num > max_val:
            return False, f"Value must be between {min_val} and {max_val}.", None
        return True, "", num
    except Exception:
        return False, "Invalid integer value.", None


def validate_yes_no(value):
    if value.lower() in ['y', 'n']:
        return True, "", value.lower() == 'y'
    else:
        return False, "Please enter Y or N.", None


def validate_timestamp(value):
    short_map = {"n": "none", "d": "date", "dt": "datetime"}
    value_lower = value.lower()
    if value_lower in short_map:
        return True, "", short_map[value_lower]
    valid_options = ["none", "date", "datetime"]
    if value_lower in valid_options:
        return True, "", value_lower
    return False, "Timestamp option must be one of: [N]one, [D]ate, [DT]atetime.", None


def guide_mode(config):
    console.print(
        "[bold green]Guide Mode: Configure conversion settings (type 'back' to return to previous step)[/bold green]\n")
    responses = {}
    steps = [
        ("input_dir", "Enter input directory (relative paths allowed)",
         config.get("default_input_dir"), None),
        ("output_dir", "Enter output directory (relative paths allowed)",
         config.get("default_output_dir"), None),
        ("preset", "Choose a preset (default, social, print, web, fast) or type '-h' for details", "", None),
        ("size", "Enter size (e.g., 1080x1080) [Leave blank to keep original]", config.get(
            "default_size"), validate_size),
        ("aspect", "Enter aspect ratio (e.g., 1:1 or 16:9) [Leave blank to keep original]", config.get(
            "default_aspect"), validate_aspect),
        ("crop", "Enter crop position ([C]enter, [T]op, [B]ottom, [L]eft, [R]ight) [Leave blank to keep original]", config.get(
            "default_crop"), validate_crop_position),
        ("max_size",
         "Enter max size (e.g., 1920x1080) [Leave blank for no max size]", "", validate_size),
        ("crop_pixels", "Enter crop_pixels (e.g., 10 or 10,20,30,40) [Leave blank for no cropping]", "", lambda v: validate_crop_pixels(
            v, parse_size(responses.get("size")) if responses.get("size") else None)),
        ("format", "Enter output format ([W]ebp, [J]pg, [P]ng) [Leave blank to keep original; you can specify multiple separated by commas]", config.get(
            "default_format"), validate_format),
        ("quality", "Enter quality (0-100) [Leave blank to keep original]", str(
            config.get("default_quality")), lambda v: validate_int_range(v, 0, 100)),
        ("dpi", "Enter DPI (e.g., 300) [Leave blank to keep original]", "" if config.get(
            "default_dpi") is None else str(config.get("default_dpi")), lambda v: validate_int_range(v, 1, 10000)),
        ("delete_originals",
         "Delete original files after processing? [Y/N]", "n", validate_yes_no),
        ("keep_metadata",
         "Keep image metadata (EXIF)? [Y/N]", "n", validate_yes_no),
        ("timestamp", "Choose timestamp option ([N]one, [D]ate, [DT]atetime) [Leave blank for no change]", config.get(
            "default_timestamp"), validate_timestamp),
        ("group_by_format",
         "Group files by format? [Y/N]", "n", validate_yes_no),
        ("save_config",
         "Save current settings to config? [Y/N]", "n", validate_yes_no)
    ]
    i = 0
    while i < len(steps):
        key, prompt_text, default_value, validator = steps[i]
        if key == "preset":
            user_input = prompt_with_back(prompt_text, default_value, None)
            if user_input is None:
                user_input = default_value
            if user_input.lower() in ["-h", "help"]:
                print_presets_info()
                continue
            elif user_input.lower() == "back":
                if i > 0:
                    i -= 1
                    continue
                else:
                    console.print("This is the first step, cannot go back.")
                    continue
            responses[key] = user_input
            if user_input and user_input in PRESETS:
                preset_settings = PRESETS[user_input]["settings"]
                for k, v in preset_settings.items():
                    responses[k] = v
            i += 1
        else:
            response = prompt_with_back(prompt_text, default_value, validator)
            if response == "back":
                if i > 0:
                    i -= 1
                    continue
                else:
                    console.print("This is the first step, cannot go back.")
                    continue
            responses[key] = response
            i += 1
    if responses.get("size") and responses.get("aspect"):
        parsed = parse_size(responses["size"])
        if parsed:
            width, height = parsed
            asp_parts = responses["aspect"].split(":")
            if len(asp_parts) == 2:
                asp_width, asp_height = int(asp_parts[0]), int(asp_parts[1])
                actual_ratio = width / height
                given_ratio = asp_width / asp_height
                if abs(actual_ratio - given_ratio) > 0.01:
                    console.print(
                        "[red]Warning: The provided size and aspect ratio are inconsistent.[/red]")
                    confirm = prompt_with_back(
                        "Type 'back' to re-enter size/aspect or press Enter to continue", "", None)
                    if confirm == "back":
                        return guide_mode(config)
    return responses


def summary_confirmation(responses):
    console.print("\n[bold underline]Summary of Settings:[/bold underline]")
    console.print(f"Input directory: {responses.get('input_dir')}")
    console.print(f"Output directory: {responses.get('output_dir')}")
    console.print(f"Preset: {responses.get('preset')}")
    console.print(f"Size: {responses.get('size')}")
    console.print(f"Aspect Ratio: {responses.get('aspect')}")
    console.print(f"Crop Position: {responses.get('crop')}")
    console.print(f"Max Size: {responses.get('max_size')}")
    console.print(f"Crop Pixels: {responses.get('crop_pixels')}")
    console.print(f"Output Format: {responses.get('format')}")
    console.print(f"Quality: {responses.get('quality')}")
    console.print(f"DPI: {responses.get('dpi')}")
    console.print(f"Delete Originals: {responses.get('delete_originals')}")
    console.print(f"Keep Metadata: {responses.get('keep_metadata')}")
    console.print(f"Timestamp: {responses.get('timestamp')}")
    console.print(f"Group by Format: {responses.get('group_by_format')}")
    console.print(f"Save Config: {responses.get('save_config')}")
    confirm = prompt_with_back(
        "Proceed with processing? [Y/N]", "n", validate_yes_no)
    if confirm is not True:
        console.print("Operation cancelled by user.")
        sys.exit(0)


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
                        help="Output format (webp, jpg, png). For multiple formats separate with commas")
    parser.add_argument("-p", "--crop_pixels", type=str,
                        help="Crop pixels values (e.g., 10 or 10,20,30,40)")
    parser.add_argument("--quality", type=int, help="Output quality (0-100)")
    parser.add_argument("--dpi", type=int, help="Set DPI (e.g., 300)")
    parser.add_argument("--delete-originals", action="store_true",
                        help="Delete original files after processing")
    parser.add_argument("--keep-metadata", action="store_true",
                        help="Preserve image metadata (EXIF)")
    parser.add_argument("-m", "--max_size", type=str,
                        help="Max size (e.g., 1920x1080)")
    parser.add_argument("-v", "--version", action="version",
                        version=f"SiT v{__version__}")
    args = parser.parse_args()
    if args.guide_mode:
        responses = guide_mode(config)
        summary_confirmation(responses)
        args_dict = responses
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
    if isinstance(quality, str):
        try:
            quality = int(quality)
        except:
            quality = config.get("default_quality")
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
