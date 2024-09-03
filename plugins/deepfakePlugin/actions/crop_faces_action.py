import os
from typing import Dict, Any
from image_processor import Action, log_message
from deepface import DeepFace
from PIL import Image
import numpy as np

class CropFacesAction(Action):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.output_dir = config.get('output_dir', 'cropped_faces')
        self.detector_backend = config.get('detector_backend', 'retinaface')
        self.enforce_detection = config.get('enforce_detection', True)
        self.padding_factor = config.get('padding_factor', 0.5)  # 50% padding by default
        self.max_size = config.get('max_size', 1024)  # Maximum dimension of output image

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        log_message(f"Initialized CropFacesAction with detector: {self.detector_backend}, "
                    f"padding_factor: {self.padding_factor}, max_size: {self.max_size}, "
                    f"output_dir: {self.output_dir}")

    def execute(self, filepath: str, metadata: Dict[str, Any]) -> str:
        try:
            print(f"Processing file: {filepath}")
            # Open image with PIL
            with Image.open(filepath) as img:
                # Convert to RGB
                img_rgb = img.convert('RGB')
                # Convert to numpy array for DeepFace
                img_array = np.array(img_rgb)

            # Extract faces from the image
            face_objs = DeepFace.extract_faces(
                img_path=img_array,
                detector_backend=self.detector_backend,
                enforce_detection=self.enforce_detection,
                align=True
            )

            # Process each detected face
            for i, face_obj in enumerate(face_objs):
                facial_area = face_obj['facial_area']
                confidence = face_obj.get('confidence', 'N/A')

                # Calculate padded crop area
                x, y, w, h = facial_area['x'], facial_area['y'], facial_area['w'], facial_area['h']
                padding_x = int(w * self.padding_factor)
                padding_y = int(h * self.padding_factor)

                left = max(0, x - padding_x)
                top = max(0, y - padding_y)
                right = min(img_rgb.width, x + w + padding_x)
                bottom = min(img_rgb.height, y + h + padding_y)

                # Crop the face with padding
                face_image = img_rgb.crop((left, top, right, bottom))

                # Resize if the cropped image is too large
                if max(face_image.size) > self.max_size:
                    face_image.thumbnail((self.max_size, self.max_size), Image.LANCZOS)

                # Generate output filename
                base_name = os.path.splitext(os.path.basename(filepath))[0]
                output_filename = f"{base_name}_face_{i+1}.jpg"
                output_path = os.path.join(self.output_dir, output_filename)

                # Save the cropped face
                face_image.save(output_path, format='JPEG', quality=95)

                log_message(f"Cropped face {i+1} from {filepath} saved to {output_path} "
                            f"(Confidence: {confidence})")

            return filepath  # Return original filepath as this action doesn't modify the original file

        except Exception as e:
            error_message = f"Error cropping faces from {filepath}: {str(e)}"
            log_message(error_message)
            return filepath  # Return original filepath in case of error
