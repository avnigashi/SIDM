import os
import torch
from diffusers import AutoPipelineForText2Image
from typing import Dict, Any
from image_processor import Action, log_message

class SDXLImageGenerationAction(Action):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.prompt = config.get('prompt', "A cinematic shot of a baby racoon wearing an intricate italian priest robe.")
        self.model_id = config.get('model_id', 'stabilityai/sdxl-turbo')
        self.output_dir = config.get('output_dir', './generated_images_sdxl')
        self.num_inference_steps = config.get('num_inference_steps', 10)
        self.guidance_scale = config.get('guidance_scale', 0.0)
        self.height = config.get('height', 512)
        self.width = config.get('width', 512)

        # Create the output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Determine the device (CUDA if available, otherwise CPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        log_message(f"Using device: {self.device}")

        # Load the SDXL model
        self.pipe = AutoPipelineForText2Image.from_pretrained(
            self.model_id,
            torch_dtype=torch.float16,
            variant="fp16"
        )
        self.pipe.to(self.device)

        log_message(f"Initialized SDXLImageGenerationAction with model: {self.model_id}")
        log_message(f"Prompt: {self.prompt}")
        log_message(f"Output directory: {self.output_dir}")

    def execute(self, metadata: Dict[str, Any] = None) -> str:
        try:
            log_message("Starting image generation...")

            # Generate the image
            result = self.pipe(
                prompt=self.prompt,
                num_inference_steps=self.num_inference_steps,
                guidance_scale=self.guidance_scale,
                height=self.height,
                width=self.width,
            )

            image = result.images[0]

            # Define the output file path
            file_name = f"image_{self.seed}.png"
            file_path = os.path.join(self.output_dir, file_name)

            # Save the image
            image.save(file_path)

            log_message(f"Generated SDXL image saved to: {file_path}")

            # Return the file path
            return file_path

        except Exception as e:
            error_message = f"SDXLImageGenerationAction failed: {str(e)}"
            log_message(error_message)
            raise Exception(error_message)
