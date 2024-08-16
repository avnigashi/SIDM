from typing import Dict, Any
from image_processor import Action, log_message
from PIL import Image, ImageDraw, ImageFont

class AddWatermark(Action):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.watermark_text = config['watermark_text']
        log_message(f"Initialized AddWatermark with text: {self.watermark_text}")

    def execute(self, filepath: str, metadata: Dict[str, Any]) -> str:
        with Image.open(filepath) as img:
            draw = ImageDraw.Draw(img)
            width, height = img.size
            font = ImageFont.load_default()

            # Use textbbox instead of textsize
            left, top, right, bottom = draw.textbbox((0, 0), self.watermark_text, font=font)
            textwidth = right - left
            textheight = bottom - top

            x = width - textwidth - 10
            y = height - textheight - 10
            draw.text((x, y), self.watermark_text, font=font, fill=(255, 255, 255, 128))
            img.save(filepath)
        log_message(f"Added watermark to {filepath}")
        return filepath