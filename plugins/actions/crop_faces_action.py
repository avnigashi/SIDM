import os
from typing import Dict, Any
from image_processor import Action, log_message
from deepface import DeepFace
from PIL import Image
import numpy as np
import cv2

class CropFacesAction(Action):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.output_dir = config.get('output_dir', 'cropped_faces')
        self.detector_backend = config.get('detector_backend', 'opencv')
        self.enforce_detection = config.get('enforce_detection', True)
        self.align = config.get('align', True)
        self.target_size = config.get('target_size', (224, 224))

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        log_message(f"Initialized CropFacesAction with output_dir: {self.output_dir}, "
                    f"detector: {self.detector_backend}, align: {self.align}")

    def execute(self, filepath: str, metadata: Dict[str, Any]) -> str:
        try:
            # Extract faces from the image
            face_objs = DeepFace.extract_faces(
                img_path=filepath,
                detector_backend=self.detector_backend,
                enforce_detection=self.enforce_detection,
                align=self.align
            )

            # Process each detected face
            for i, face_obj in enumerate(face_objs):
                face = face_obj['face']
                confidence = face_obj.get('confidence', 'N/A')

                # Ensure the face is in the correct format (0-255 uint8)
                if face.max() <= 1.0:
                    face = (face * 255).astype(np.uint8)
                else:
                    face = face.astype(np.uint8)

                # Convert BGR to RGB if necessary
                if face.shape[2] == 3:
                    face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)

                # Convert the face array to a PIL Image
                face_image = Image.fromarray(face)

                # Resize the face image if necessary
                if face_image.size != self.target_size:
                    face_image = face_image.resize(self.target_size, Image.LANCZOS)

                # Generate output filename
                base_name = os.path.splitext(os.path.basename(filepath))[0]
                output_filename = f"{base_name}_face_{i+1}.jpg"
                output_path = os.path.join(self.output_dir, output_filename)

                # Save the cropped face
                face_image.save(output_path)

                log_message(f"Cropped face {i+1} from {filepath} saved to {output_path} "
                            f"(Confidence: {confidence})")

            return filepath  # Return original filepath as this action doesn't modify the original file

        except Exception as e:
            error_message = f"Error cropping faces from {filepath}: {str(e)}"
            log_message(error_message)
            return filepath  # Return original filepath in case of error