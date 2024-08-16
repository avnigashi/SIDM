import os
from typing import Dict, Any
from image_processor import Action, log_message
from PIL import Image

class ConvertToJPEG(Action):
    def initialize(self, config: Dict[str, Any]) -> None:
        log_message("Initialized ConvertToJPEG")

    def execute(self, filepath: str, metadata: Dict[str, Any]) -> str:
        with Image.open(filepath) as img:
            rgb_img = img.convert('RGB')
            new_filepath = os.path.splitext(filepath)[0] + '.jpg'
            rgb_img.save(new_filepath, 'JPEG')
        if filepath != new_filepath:
            os.remove(filepath)
            log_message(f"Converted {filepath} to {new_filepath}")
        else:
            log_message(f"File {filepath} is already a JPEG")
        return new_filepath