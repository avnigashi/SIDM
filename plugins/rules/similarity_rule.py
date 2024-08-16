import os
from typing import Dict, Any
from image_processor import Rule, log_message
from deepface import DeepFace

class SimilarityRule(Rule):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.threshold = config.get('threshold', 0.6)
        self.model_name = config.get('model_name', 'VGG-Face')
        self.distance_metric = config.get('distance_metric', 'cosine')
        self.reference_img_path = config.get('reference_img_path')

        if not self.reference_img_path or not os.path.exists(self.reference_img_path):
            raise ValueError("A valid reference image path must be provided")

        log_message(f"Initialized SimilarityRule with threshold: {self.threshold}, "
                    f"model: {self.model_name}, metric: {self.distance_metric}")

    def apply(self, filepath: str, metadata: Dict[str, Any]) -> bool:
        try:
            result = DeepFace.verify(
                img1_path=self.reference_img_path,
                img2_path=filepath,
                model_name=self.model_name,
                distance_metric=self.distance_metric
            )

            is_similar = result['verified']
            distance = result['distance']

            log_message(f"Similarity check for {filepath}: "
                        f"{'Passed' if is_similar else 'Failed'} "
                        f"(Distance: {distance}, Threshold: {self.threshold})")

            return is_similar

        except Exception as e:
            error_message = f"Error in similarity check for {filepath}: {str(e)}"
            log_message(error_message)
            return False