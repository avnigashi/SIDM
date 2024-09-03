from typing import Dict, Any
from image_processor import Rule, log_message
from deepface import DeepFace

class RaceRule(Rule):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.race = config.get('race', 'white').lower()
        self.detector_backend = config.get('detector_backend', 'opencv')
        log_message(f"Initialized RaceRule with race: {self.race}, detector: {self.detector_backend}")

    def apply(self, filepath: str, metadata: Dict[str, Any]) -> bool:
        try:
            result = DeepFace.analyze(img_path=filepath, actions=['race'], detector_backend=self.detector_backend, enforce_detection=False)
            if not result:
                log_message(f"No face detected in {filepath}")
                return False

            detected_race = result[0]['dominant_race'].lower()
            is_match = detected_race == self.race
            log_message(f"Race {detected_race} for {filepath} - Match: {is_match}")
            return is_match
        except Exception as e:
            log_message(f"Error analyzing race in {filepath}: {str(e)}")
            return False
