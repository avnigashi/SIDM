from PIL import Image, ImageFilter
import os
from typing import Dict, Any, List
from image_processor import Action, log_message

class BlurFacesAction(Action):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.blur_factor = config.get('blur_factor', 10)
        self.output_dir = config.get('output_dir', 'blurred_faces')

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        log_message(f"Initialized BlurFacesAction with blur_factor: {self.blur_factor}, output_dir: {self.output_dir}")

    def execute(self, filepath: str, metadata: Dict[str, Any] = None) -> List[str]:
        processed_files = []

        try:
            with Image.open(filepath) as img:
                blurred_img = img.filter(ImageFilter.GaussianBlur(self.blur_factor))
                base_name = os.path.splitext(os.path.basename(filepath))[0]
                output_path = os.path.join(self.output_dir, f"{base_name}_blurred.jpg")
                blurred_img.save(output_path, format='JPEG', quality=95)
                processed_files.append(output_path)
                log_message(f"Blurred image saved to {output_path}")

        except Exception as e:
            raise RuntimeError(f"Error blurring faces in {filepath}: {str(e)}") from e

        return processed_files
