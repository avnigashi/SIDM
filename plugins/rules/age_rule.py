from typing import Dict, Any
from image_processor import Rule, log_message
from deepface import DeepFace

class AgeRule(Rule):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.age_range = config.get('age_range', (0, 100))
        self.detector_backend = config.get('detector_backend', 'opencv')
        log_message(f"Initialized AgeRule with age_range: {self.age_range}, detector: {self.detector_backend}")

    def apply(self, filepath: str, metadata: Dict[str, Any]) -> bool:
        try:
            result = DeepFace.analyze(img_path=filepath, actions=['age'], detector_backend=self.detector_backend, enforce_detection=False)
            if not result:
                log_message(f"No face detected in {filepath}")
                return False

            age = result[0]['age']
            is_in_range = self.age_range[0] <= age <= self.age_range[1]
            log_message(f"Age {age} for {filepath} - In range: {is_in_range}")
            return is_in_range
        except Exception as e:
            log_message(f"Error analyzing age in {filepath}: {str(e)}")
            return False