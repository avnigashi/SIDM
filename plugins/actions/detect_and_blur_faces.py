import os
import cv2
import numpy as np
from typing import Dict, Any
from image_processor import Action, log_message
from deepface import DeepFace

class DetectAndBlurFaces(Action):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.detector_backend = config.get('detector_backend', 'retinaface')
        blur_factor = config.get('blur_factor', 30)
        # Ensure blur_factor is odd and greater than 1
        self.blur_factor = max(3, blur_factor + 1 if blur_factor % 2 == 0 else blur_factor)
        self.output_dir = config.get('output_dir', 'blurred_faces')
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        log_message(f"Initialized DetectAndBlurFaces with detector: {self.detector_backend}, "
                    f"blur_factor: {self.blur_factor}, output_dir: {self.output_dir}")

    def execute(self, filepath: str, metadata: Dict[str, Any]) -> str:
        try:
            # Read the image
            img = cv2.imread(filepath)
            if img is None:
                raise ValueError(f"Failed to read image: {filepath}")

            # Detect faces
            faces = DeepFace.extract_faces(img_path=img, 
                                           detector_backend=self.detector_backend, 
                                           enforce_detection=False)

            # Blur each detected face
            for face in faces:
                facial_area = face['facial_area']
                x, y, w, h = facial_area['x'], facial_area['y'], facial_area['w'], facial_area['h']
                
                # Ensure coordinates are within image boundaries
                x, y = max(0, x), max(0, y)
                w = min(w, img.shape[1] - x)
                h = min(h, img.shape[0] - y)
                
                face_region = img[y:y+h, x:x+w]
                blurred_face = cv2.GaussianBlur(face_region, (self.blur_factor, self.blur_factor), 0)
                img[y:y+h, x:x+w] = blurred_face

            # Generate output filename
            base_name = os.path.splitext(os.path.basename(filepath))[0]
            output_filename = f"{base_name}_blurred.jpg"
            output_path = os.path.join(self.output_dir, output_filename)

            # Save the image with blurred faces
            cv2.imwrite(output_path, img)

            log_message(f"Blurred {len(faces)} faces in {filepath}, saved to {output_path}")
            return output_path

        except Exception as e:
            error_message = f"Error blurring faces in {filepath}: {str(e)}"
            log_message(error_message)
            return filepath  # Return original filepath in case of error