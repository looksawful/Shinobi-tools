from PIL import Image
import os
from tqdm import tqdm


class ImageOptimizer:
    def __init__(self, input_dir, output_dir, size=(1080, 1080), aspect_ratio="1:1", crop_position="center", max_size=None, crop_pixels=None, output_format="webp", quality=100, dpi=None, keep_metadata=False, delete_originals=False):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.size = size
        self.aspect_ratio = aspect_ratio
        self.crop_position = crop_position
        self.max_size = max_size
        self.crop_pixels = crop_pixels
        self.output_format = output_format.lower()
        self.quality = quality
        self.dpi = dpi
        self.keep_metadata = keep_metadata
        self.delete_originals = delete_originals

    def crop_image(self, image, aspect_ratio):
        width, height = image.size
        try:
            aspect_width, aspect_height = map(int, aspect_ratio.split(":"))
        except Exception as e:
            print(
                f"Invalid aspect ratio format: {aspect_ratio}. Using full image.")
            return image
        aspect_value = aspect_width / aspect_height
        if width / height > aspect_value:
            new_width = int(height * aspect_value)
            new_height = height
        else:
            new_width = width
            new_height = int(width / aspect_value)
        if self.crop_position == "center":
            left = (width - new_width) // 2
            top = (height - new_height) // 2
        elif self.crop_position == "left":
            left = 0
            top = (height - new_height) // 2
        elif self.crop_position == "right":
            left = width - new_width
            top = (height - new_height) // 2
        elif self.crop_position == "top":
            left = (width - new_width) // 2
            top = 0
        elif self.crop_position == "bottom":
            left = (width - new_width) // 2
            top = height - new_height
        else:
            left = (width - new_width) // 2
            top = (height - new_height) // 2
        return image.crop((left, top, left + new_width, top + new_height))

    def resize_within_max_size(self, img):
        if self.max_size:
            width, height = img.size
            max_width, max_height = self.max_size
            aspect_ratio = width / height
            if width > max_width or height > max_height:
                if width / max_width > height / max_height:
                    new_width = max_width
                    new_height = int(new_width / aspect_ratio)
                else:
                    new_height = max_height
                    new_width = int(new_height * aspect_ratio)
                img = img.resize((new_width, new_height), Image.LANCZOS)
        return img

    def crop_by_pixels(self, img):
        if self.crop_pixels:
            width, height = img.size
            if len(self.crop_pixels) == 1:
                crop_top = crop_bottom = crop_left = crop_right = self.crop_pixels[0]
            elif len(self.crop_pixels) == 2:
                crop_top, crop_bottom = self.crop_pixels
                crop_left = crop_right = crop_top
            elif len(self.crop_pixels) == 4:
                crop_top, crop_right, crop_bottom, crop_left = self.crop_pixels
            else:
                print("Invalid crop_pixels format. Using no cropping.")
                return img
            img = img.crop((crop_left, crop_top, width -
                           crop_right, height - crop_bottom))
        return img

    def process_image(self, file_path, output_dir_for_file):
        try:
            with Image.open(file_path) as img:
                original_info = img.info if self.keep_metadata else {}
                img = self.crop_image(img, self.aspect_ratio)
                img = img.resize(self.size, Image.LANCZOS)
                img = self.resize_within_max_size(img)
                img = self.crop_by_pixels(img)
                base_name = os.path.splitext(os.path.basename(file_path))[
                    0] + "." + self.output_format
                output_path = os.path.join(output_dir_for_file, base_name)
                save_kwargs = {}
                if self.output_format in ['jpg', 'jpeg']:
                    save_kwargs["quality"] = self.quality
                    if self.keep_metadata and "exif" in original_info:
                        save_kwargs["exif"] = original_info["exif"]
                elif self.output_format == "webp":
                    if self.quality < 100:
                        save_kwargs["quality"] = self.quality
                        save_kwargs["lossless"] = False
                    else:
                        save_kwargs["quality"] = self.quality
                        save_kwargs["lossless"] = True
                if self.dpi:
                    save_kwargs["dpi"] = (self.dpi, self.dpi)
                img.save(output_path, self.output_format.upper(), **save_kwargs)
                print(f"Processed: {file_path} -> {output_path}")
            if self.delete_originals:
                os.remove(file_path)
                print(f"Deleted original: {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    def process_directory(self):
        image_files = []
        for root, dirs, files in os.walk(self.input_dir):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.jfif')):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(root, self.input_dir)
                    image_files.append((file_path, relative_path))
        for file_path, relative_path in tqdm(image_files, desc="Processing images"):
            output_dir_for_file = os.path.join(self.output_dir, relative_path)
            os.makedirs(output_dir_for_file, exist_ok=True)
            self.process_image(file_path, output_dir_for_file)
