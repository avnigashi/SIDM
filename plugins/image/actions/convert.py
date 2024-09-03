from PIL import Image
import os
from image_processor import Action  # Ensure Action is imported

class Convert(Action):  # Inherit from Action
    def initialize(self, params):
        self.output_format = params.get("output_format", "JPEG")
        self.output_dir = params.get("output_dir", "./converted_images")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def execute(self, filepath, metadata):
        base_name = os.path.basename(filepath)
        output_path = os.path.join(self.output_dir, f"{os.path.splitext(base_name)[0]}.{self.output_format.lower()}")
        with Image.open(filepath) as img:
            img.convert("RGB").save(output_path, self.output_format)
        print(f"Converted {filepath} to {output_path} in format {self.output_format}")
        return output_path
