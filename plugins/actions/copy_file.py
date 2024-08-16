import os
import shutil
from typing import Dict, Any
from image_processor import Action, log_message

class CopyFile(Action):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.output_dir = config['output_dir']
        log_message(f"Initialized CopyFile with output directory: {self.output_dir}")

    def execute(self, filepath: str, metadata: Dict[str, Any]) -> str:
        # Create the output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Generate the new filepath
        filename = os.path.basename(filepath)
        new_filepath = os.path.join(self.output_dir, filename)

        # Copy the file
        shutil.copy2(filepath, new_filepath)

        log_message(f"Copied {filepath} to {new_filepath}")
        return new_filepath