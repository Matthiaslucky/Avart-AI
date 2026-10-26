import os
import torch
from diffusers import StableDiffusionPipeline
from PIL import Image

class ModelEngine:
    def __init__(self):
        # Force CPU device explicitly for CPU EC2 instances
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Initializing Avart AI Engine on device: {self.device}")

    def generate_image(self, prompt: str, output_path: str = "./outputs/generated_image.png"):
        """Generates an image from a text prompt using an open-source model."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if not os.path.isabs(output_path):
            output_path = os.path.join(base_dir, output_path.lstrip("./"))
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        model_id = "segmind/small-sd"

        # Load pipeline using float32 for CPU stability
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float32
        )
        pipe = pipe.to(self.device)

        # Generate image
        image = pipe(prompt).images[0]
        image.save(output_path)
        return output_path

    def process_background_removal(self, input_path: str, output_path: str):
        pass

if __name__ == "__main__":
    engine = ModelEngine()
    engine.generate_image("City gate at night")
