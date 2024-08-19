from typing import Dict, Any
from image_processor import Rule, log_message
from PIL import Image

class IsSmallImage(Rule):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.min_width = config.get('min_width', 100)
        self.min_height = config.get('min_height', 100)
        log_message(f"Initialized IsSmallImage with min_width: {self.min_width}, min_height: {self.min_height}")

    def apply(self, filepath: str, metadata: Dict[str, Any]) -> bool:
        try:
            with Image.open(filepath) as img:
                width, height = img.size
            is_small = width < self.min_width or height < self.min_height
            log_message(f"IsSmallImage for {filepath}: {'Small' if is_small else 'Not small'}")
            return is_small
        except Exception as e:
            log_message(f"Error checking image size for {filepath}: {str(e)}")
            return False