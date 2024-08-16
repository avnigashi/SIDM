import os
from typing import Dict, Any
from image_processor import Rule, log_message

class IsPNG(Rule):
    def initialize(self, config: Dict[str, Any]) -> None:
        log_message("Initialized IsPNG rule")

    def apply(self, filepath: str, metadata: Dict[str, Any]) -> bool:
        _, ext = os.path.splitext(filepath)
        result = ext.lower() == '.png'
        log_message(f"IsPNG: {filepath} - {'Passed' if result else 'Failed'}")
        return result