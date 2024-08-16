from typing import Dict, Any
from image_processor import Rule, log_message

class CheckFileSize(Rule):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.max_size = config['max_size']
        log_message(f"Initialized CheckFileSize with max size: {self.max_size} bytes")

    def apply(self, filepath: str, metadata: Dict[str, Any]) -> bool:
        file_size = metadata['size']
        result = file_size <= self.max_size
        log_message(f"CheckFileSize: {filepath} ({file_size} bytes) - {'Passed' if result else 'Failed'}")
        return result