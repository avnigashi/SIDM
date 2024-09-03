import os
from transformers import AutoModelForCausalLM, AutoProcessor
from PIL import Image
from image_processor import Rule, log_message
import torch

class FlorenceCaptionRule(Rule):
    def initialize(self, config):
        self.model_id = config.get('model_id', "thwri/CogFlorence-2.1-Large")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = AutoModelForCausalLM.from_pretrained(self.model_id, trust_remote_code=True).to(self.device).eval()
        self.processor = AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)
        self.prompt = config.get('prompt', "<MORE_DETAILED_CAPTION>")
        log_message(f"Initialized FlorenceCaptionRule with model {self.model_id}")

    def apply(self, filepath, metadata):
        try:
            image = Image.open(filepath)
            if image.mode != "RGB":
                image = image.convert("RGB")
            inputs = self.processor(text=self.prompt, images=image, return_tensors="pt").to(self.device)
            generated_ids = self.model.generate(
                input_ids=inputs["input_ids"],
                pixel_values=inputs["pixel_values"],
                max_new_tokens=1024,
                num_beams=3,
                do_sample=True
            )
            generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            parsed_answer = self.processor.post_process_generation(generated_text, task=self.prompt, image_size=(image.width, image.height))
            log_message(f"Generated caption for {filepath}: {parsed_answer}")
            return True  # You can customize this based on further logic
        except Exception as e:
            log_message(f"Error applying FlorenceCaptionRule to {filepath}: {str(e)}")
            return False
