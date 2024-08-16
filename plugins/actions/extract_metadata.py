import os
import json
from typing import Dict, Any
from image_processor import Action, log_message
from PIL import Image
from PIL.ExifTags import TAGS

class ExtractMetadata(Action):
    def initialize(self, config: Dict[str, Any]) -> None:
        log_message("Initialized ExtractMetadata")

    def execute(self, filepath: str, metadata: Dict[str, Any]) -> str:
        exif_data = {}
        with Image.open(filepath) as img:
            exif = img._getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_data[tag] = str(value)
        
        metadata_filepath = os.path.splitext(filepath)[0] + "_metadata.json"
        with open(metadata_filepath, 'w') as f:
            json.dump(exif_data, f, indent=4)
        
        log_message(f"Extracted metadata from {filepath} to {metadata_filepath}")
        return filepath