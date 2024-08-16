import os
from typing import Dict, Any
from image_processor import Action, log_message

class RenameFile(Action):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.prefix = config['prefix']
        log_message(f"Initialized RenameFile with prefix: {self.prefix}")

    def execute(self, filepath: str, metadata: Dict[str, Any]) -> str:
        directory, filename = os.path.split(filepath)
        new_filename = self.prefix + filename
        new_filepath = os.path.join(directory, new_filename)
        os.rename(filepath, new_filepath)
        log_message(f"Renamed {filepath} to {new_filepath}")
        return new_filepath