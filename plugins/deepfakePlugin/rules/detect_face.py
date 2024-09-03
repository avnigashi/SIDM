from typing import Dict, Any
from image_processor import Rule, log_message
import cv2
import numpy as np

class DetectFace(Rule):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        log_message("Initialized DetectFace")

    def apply(self, filepath: str, metadata: Dict[str, Any]) -> bool:
        img = cv2.imread(filepath)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        result = len(faces) > 0
        log_message(f"DetectFace: {filepath} - {'Passed' if result else 'Failed'}")
        return result
