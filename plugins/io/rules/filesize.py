import os
from image_processor import Rule  # Ensure Rule is imported

class FileSize(Rule):  # Inherit from Rule
    def initialize(self, params):
        self.max_size = params.get("max_size", 1024 * 1024)  # Default 1MB

    def apply(self, filepath, metadata):
        file_size = os.path.getsize(filepath)
        print(f"Checking filesize for {filepath}: {file_size} bytes")
        return file_size <= self.max_size
