import os
from typing import Dict, Any
from image_processor import Action, log_message
from PIL import Image

class ConvertFormatAction(Action):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.output_format = config.get('output_format', 'JPEG').upper()
        self.output_dir = config.get('output_dir', 'converted_images')
        self.quality = config.get('quality', 95)
        self.supported_formats = {'.webp', '.png', '.jpg', '.jpeg', '.gif'}

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        log_message(f"Initialized ConvertFormatAction with output_format: {self.output_format}, "
                    f"output_dir: {self.output_dir}, quality: {self.quality}")

    def execute(self, filepath: str, metadata: Dict[str, Any]) -> str:
        try:
            # Check if the input format is supported
            file_ext = os.path.splitext(filepath)[1].lower()
            if file_ext not in self.supported_formats:
                log_message(f"Unsupported input format for {filepath}")
                return filepath

            # Open the image
            with Image.open(filepath) as img:
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    bg = Image.new('RGB', img.size, (255, 255, 255))
                    bg.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else img.split()[1])
                    img = bg

                # Generate output filename
                base_name = os.path.splitext(os.path.basename(filepath))[0]
                output_filename = f"{base_name}.{self.output_format.lower()}"
                output_path = os.path.join(self.output_dir, output_filename)

                # Save the image in the new format
                img.save(output_path, format=self.output_format, quality=self.quality)

            log_message(f"Converted {filepath} to {output_path}")
            return output_path

        except Exception as e:
            error_message = f"Error converting format for {filepath}: {str(e)}"
            log_message(error_message)
            return filepath  # Return original filepath in case of error