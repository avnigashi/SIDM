from PIL import Image
from image_processor import Rule  # Ensure Rule is imported

class IsImage(Rule):  # Inherit from Rule
    def initialize(self, params):
        self.allowed_formats = params.get("allowed_formats", [".jpg", ".jpeg", ".png"])

    def apply(self, filepath, metadata):
        try:
            with Image.open(filepath) as img:
                img.verify()  # Verify that it is an image
            print(f"{filepath} is a valid image")
            return filepath.lower().endswith(tuple(self.allowed_formats))
        except (IOError, SyntaxError):
            print(f"{filepath} is not a valid image")
            return False
