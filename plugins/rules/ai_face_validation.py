import cv2
import base64
import requests
from typing import Dict, Any
from image_processor import Rule, log_message

class AIFaceValidation(Rule):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.api_url = config['api_url']
        self.model = config.get('model', 'default')
        self.temperature = float(config.get('temperature', 0.2))
        self.max_tokens = int(config.get('max_tokens', 1000))
        self.top_p = float(config.get('top_p', 1))
        self.frequency_penalty = float(config.get('frequency_penalty', 0))
        self.presence_penalty = float(config.get('presence_penalty', 0))
        self.prompt = config.get('prompt', "Validate if this image contains a human face. Respond with only 'yes' or 'no' but then explain.")
        log_message(f"Initialized AIFaceValidation with model: {self.model}")
        log_message(f"Using prompt: {self.prompt}")

    def apply(self, filepath: str, metadata: Dict[str, Any]) -> bool:
        image = cv2.imread(filepath)
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        validation_result, response = self.validate_image(image_base64)

        if validation_result is None:  # This indicates an error occurred
            error_message = f"AI Face Validation failed: {response}"
            log_message(error_message)
            raise Exception(error_message)

        log_message(f"AI Face Validation for {filepath}: {'Passed' if validation_result else 'Failed'}")
        log_message(f"AI Response: {response}")

        return validation_result

    def validate_image(self, image_base64):
        payload = {
            "model": self.model,
            "prompt": self.prompt,
            "images": [image_base64],
            "options": {
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "top_p": self.top_p,
                "frequency_penalty": self.frequency_penalty,
                "presence_penalty": self.presence_penalty
            },
            "stream": False
        }

        try:
            response = requests.post(self.api_url, json=payload)
            if response.status_code == 200:
                ai_response = response.json().get('response', 'No response generated')
                # Check if the response starts with 'yes', ignoring case and leading/trailing whitespace
                validation_result = ai_response.strip().lower().startswith('yes')
                return validation_result, ai_response
            else:
                error_message = f"Error in AI request: {response.status_code} - {response.text}"
                log_message(error_message)
                return None, error_message
        except Exception as e:
            error_message = f"Exception in AI request: {str(e)}"
            log_message(error_message)
            return None, error_message