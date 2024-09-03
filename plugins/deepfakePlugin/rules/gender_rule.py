from typing import Dict, Any
from image_processor import Rule, log_message
from deepface import DeepFace

class GenderRule(Rule):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.gender = config.get('gender', 'Female').lower()
        self.detector_backend = config.get('detector_backend', 'opencv')
        log_message(f"Initialized GenderRule with gender: {self.gender}, detector: {self.detector_backend}")

    def apply(self, filepath: str, metadata: Dict[str, Any]) -> bool:
        try:
            result = DeepFace.analyze(img_path=filepath, actions=['gender'], detector_backend=self.detector_backend, enforce_detection=False)
            if not result:
                log_message(f"No face detected in {filepath}")
                return False

            detected_gender = result[0]['dominant_gender'].lower()
            is_match = detected_gender == self.gender
            log_message(f"Gender {detected_gender} for {filepath} - Match: {is_match}")
            return is_match
        except Exception as e:
            log_message(f"Error analyzing gender in {filepath}: {str(e)}")
            return False
