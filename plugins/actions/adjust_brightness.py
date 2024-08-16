from typing import Dict, Any
from image_processor import Action, log_message
from PIL import Image, ImageEnhance

class AdjustBrightness(Action):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.brightness_factor = config['brightness_factor']
        log_message(f"Initialized AdjustBrightness with factor: {self.brightness_factor}")

    def execute(self, filepath: str, metadata: Dict[str, Any]) -> str:
        with Image.open(filepath) as img:
            enhancer = ImageEnhance.Brightness(img)
            brightened_img = enhancer.enhance(self.brightness_factor)
            brightened_img.save(filepath)
        log_message(f"Adjusted brightness of {filepath}")
        return filepath