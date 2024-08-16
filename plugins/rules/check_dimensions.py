from typing import Dict, Any
from image_processor import Rule, log_message
from PIL import Image

class CheckDimensions(Rule):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.min_width = config['min_width']
        self.min_height = config['min_height']
        log_message(f"Initialized CheckDimensions with minimum dimensions: {self.min_width}x{self.min_height}")

    def apply(self, filepath: str, metadata: Dict[str, Any]) -> bool:
        with Image.open(filepath) as img:
            width, height = img.size
        result = width >= self.min_width and height >= self.min_height
        log_message(f"CheckDimensions: {filepath} ({width}x{height}) - {'Passed' if result else 'Failed'}")
        return result