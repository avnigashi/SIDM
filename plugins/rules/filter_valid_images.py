import os
from typing import Dict, Any
from image_processor import Rule, log_message

class FilterValidImages(Rule):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.allowed_formats = config['allowed_formats']
        log_message(f"Initialized FilterValidImages with allowed formats: {self.allowed_formats}")

    def apply(self, filepath: str, metadata: Dict[str, Any]) -> bool:
        _, ext = os.path.splitext(filepath)
        result = ext.lower() in self.allowed_formats
        log_message(f"FilterValidImages: {filepath} - {'Passed' if result else 'Failed'}")
        return result