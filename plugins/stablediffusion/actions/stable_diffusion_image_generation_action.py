import os
import torch
from diffusers import StableDiffusionPipeline
from typing import Dict, Any, List
from image_processor import Action, log_message

class StableDiffusionImageGenerationAction(Action):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.model_id = config.get('model_id', 'runwayml/stable-diffusion-v1-5')
        self.prompt = config.get('prompt', "a photo of an astronaut riding a horse on mars")
        self.negative_prompt = config.get('negative_prompt', "")  # Optional negative prompt
        self.output_dir = config.get('output_dir', "./generated_images")
        self.guidance_scale = config.get('guidance_scale', 7.5)
        self.num_inference_steps = config.get('num_inference_steps', 50)
        self.height = config.get('height', 512)
        self.width = config.get('width', 512)
        self.seed = config.get('seed', 0)
        self.batch_size = config.get('batch_size', 1)  # Number of images to generate
        self.use_attention_slicing = config.get('use_attention_slicing', False)
        self.use_vae_slicing = config.get('use_vae_slicing', False)

        # Create the output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Determine the device (CUDA if available, otherwise CPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        log_message(f"Using device: {self.device}")

        # Load the model with appropriate dtype
        self.pipe = StableDiffusionPipeline.from_pretrained(
            self.model_id,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        )
        self.pipe = self.pipe.to(self.device)

        # Enable memory optimizations if configured
        if self.use_attention_slicing:
            self.pipe.enable_attention_slicing()
            log_message("Enabled attention slicing for memory optimization.")

        if self.use_vae_slicing:
            self.pipe.enable_vae_slicing()
            log_message("Enabled VAE slicing for memory optimization.")

        log_message(f"Initialized StableDiffusionImageGenerationAction with model: {self.model_id}")
        log_message(f"Output directory: {self.output_dir}")
        log_message(f"Prompt: {self.prompt}")
        log_message(f"Negative Prompt: {self.negative_prompt}")
        log_message(f"Batch size: {self.batch_size}")

    def execute(self, metadata: Dict[str, Any] = None) -> List[str]:
        try:
            generated_image_paths = []
            generator = torch.manual_seed(self.seed)

            log_message("Starting image generation...")

            for i in range(self.batch_size):
                # Generate the image
                result = self.pipe(
                    prompt=self.prompt,
                    negative_prompt=self.negative_prompt if self.negative_prompt else None,
                    height=self.height,
                    width=self.width,
                    guidance_scale=self.guidance_scale,
                    num_inference_steps=self.num_inference_steps,
                    generator=generator,
                    output_type="pil"  # Ensures PIL.Image output
                )

                image = result.images[0]

                # Define the output file path with a unique name
                file_name = f"image_{self.seed + i}.png"
                file_path = os.path.join(self.output_dir, file_name)

                # Save the image
                image.save(file_path)
                generated_image_paths.append(file_path)

                log_message(f"Generated image saved to: {file_path}")

            # Return the list of file paths
            return generated_image_paths

        except Exception as e:
            error_message = f"StableDiffusionImageGenerationAction failed: {str(e)}"
            log_message(error_message)
            raise Exception(error_message)
