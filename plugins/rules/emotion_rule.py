from typing import Dict, Any
from image_processor import Rule, log_message
from deepface import DeepFace

class EmotionRule(Rule):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.emotion = config.get('emotion', 'happy').lower()
        self.detector_backend = config.get('detector_backend', 'opencv')
        log_message(f"Initialized EmotionRule with emotion: {self.emotion}, detector: {self.detector_backend}")

    def apply(self, filepath: str, metadata: Dict[str, Any]) -> bool:
        try:
            result = DeepFace.analyze(img_path=filepath, actions=['emotion'], detector_backend=self.detector_backend, enforce_detection=False)
            if not result:
                log_message(f"No face detected in {filepath}")
                return False

            detected_emotion = result[0]['dominant_emotion'].lower()
            is_match = detected_emotion == self.emotion
            log_message(f"Emotion {detected_emotion} for {filepath} - Match: {is_match}")
            return is_match
        except Exception as e:
            log_message(f"Error analyzing emotion in {filepath}: {str(e)}")
            return False