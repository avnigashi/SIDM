import os
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
from image_processor import Rule, log_message

class VisionLanguageRule(Rule):
    def initialize(self, config):
        self.model_id = config.get('model_id', "vikhyatk/moondream2")
        self.revision = config.get('revision', "2024-05-20")
        self.question = config.get('question', "Describe this image.")
        self.expected_answer = config.get('expected_answer', None)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, revision=self.revision)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_id, trust_remote_code=True, revision=self.revision)
        log_message(f"Initialized VisionLanguageRule with model {self.model_id} and revision {self.revision}")

    def apply(self, filepath, metadata):
        try:
            image = Image.open(filepath)
            enc_image = self.model.encode_image(image)
            answer = self.model.answer_question(enc_image, self.question, self.tokenizer)
            log_message(f"Question: {self.question}")
            log_message(f"Model answer: {answer}")

            if self.expected_answer:
                result = self.expected_answer.lower() in answer.lower()
                log_message(f"Expected answer found: {result}")
                return result
            else:
                log_message(f"No expected answer provided, returning True by default")
                return True

        except Exception as e:
            log_message(f"Error applying VisionLanguageRule to {filepath}: {str(e)}")
            return False
