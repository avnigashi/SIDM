from typing import Dict, Any
from image_processor import Rule, log_message
from deepface import DeepFace
import os
import traceback
import sys

class SimilarityRule(Rule):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.threshold = config.get('threshold', 0.6)
        self.model_name = config.get('model_name', 'VGG-Face')
        self.distance_metric = config.get('distance_metric', 'cosine')
        self.reference_img_path = config.get('reference_img_path')
        self.negate = config.get('negate', False)
        if not self.reference_img_path or not os.path.exists(self.reference_img_path):
            raise ValueError(f"A valid reference image path must be provided. Current path: {self.reference_img_path}")

        log_message(f"Initialized SimilarityRule with threshold: {self.threshold}, "
                    f"model: {self.model_name}, metric: {self.distance_metric}, "
                    f"reference image: {self.reference_img_path}")

    def apply(self, filepath: str, metadata: Dict[str, Any]) -> bool:
        try:
            print(f"Checking similarity for {filepath}")
            if not os.path.exists(filepath):
                print(f"File not found: {filepath}")
                log_message(f"File not found: {filepath}")
                return False

            result = DeepFace.verify(
                img1_path=self.reference_img_path,
                img2_path=filepath,
                model_name=self.model_name,
                distance_metric=self.distance_metric,
                enforce_detection=False
            )
            print(result)
            is_similar = result['verified']
            distance = result['distance']

            print(f"Similarity check for {filepath}: "
                        f"{'Passed' if is_similar else 'Failed'} "
                        f"(Distance: {distance}, Threshold: {self.threshold})")

            log_message(f"Similarity check for {filepath}: "
                        f"{'Passed' if is_similar else 'Failed'} "
                        f"(Distance: {distance}, Threshold: {self.threshold})")

            return is_similar if not self.negate else not is_similar

        except Exception as e:
            error_message = f"Error in similarity check for {filepath}: {str(e)}\n"
            error_message += f"Reference image: {self.reference_img_path}\n"
            error_message += f"Traceback:\n{traceback.format_exc()}"
            log_message(error_message)
            print(error_message)
            return False  # Assume not similar if there's an error