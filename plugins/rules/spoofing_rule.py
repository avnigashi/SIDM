from typing import Dict, Any
from image_processor import Rule, log_message
from deepface import DeepFace

class SpoofingRule(Rule):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.detector_backend = config.get('detector_backend', 'opencv')
        self.negate = config.get('negate', False)
        self.model_name = config.get('model_name', 'FaceNet512')
        log_message(f"Initialized SpoofingRule with detector: {self.detector_backend}, "
                    f"negate: {self.negate}, model: {self.model_name}")

    def apply(self, filepath: str, metadata: Dict[str, Any]) -> bool:
        try:
            result = DeepFace.verify(
                img1_path=filepath,
                model_name=self.model_name,
                detector_backend=self.detector_backend,
                prog_bar=False,
                anti_spoofing=True
            )

            is_real = result['is_real']
            spoofing_result = "Real" if is_real else "Spoof"
            log_message(f"Spoofing check for {filepath}: {spoofing_result}")

            # Apply negation if configured
            final_result = is_real if not self.negate else not is_real
            log_message(f"Final result after negation: {final_result}")

            return final_result
        except Exception as e:
            log_message(f"Error in spoofing detection for {filepath}: {str(e)}")
            return False