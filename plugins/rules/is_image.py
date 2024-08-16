import os
from typing import Dict, Any
from image_processor import Rule, log_message

class IsImage(Rule):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.allowed_formats = config['allowed_formats']
        log_message(f"Initialized IsImage with allowed formats: {self.allowed_formats}")

    def apply(self, filepath: str, metadata: Dict[str, Any]) -> bool:
        _, ext = os.path.splitext(filepath)
        result = ext.lower() in self.allowed_formats
        log_message(f"IsImage: {filepath} - {'Passed' if result else 'Failed'}")
        return result