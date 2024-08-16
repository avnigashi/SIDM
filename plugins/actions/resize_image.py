import os
from typing import Dict, Any
from image_processor import Action, log_message
from PIL import Image

class ResizeImage(Action):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.max_width = config['max_width']
        self.max_height = config['max_height']
        log_message(f"Initialized ResizeImage with max dimensions: {self.max_width}x{self.max_height}")

    def execute(self, filepath: str, metadata: Dict[str, Any]) -> str:
        with Image.open(filepath) as img:
            original_size = img.size
            img.thumbnail((self.max_width, self.max_height))
            if img.size != original_size:
                img.save(filepath)
                log_message(f"Resized {filepath} from {original_size} to {img.size}")
            else:
                log_message(f"No resize needed for {filepath}")
        return filepath