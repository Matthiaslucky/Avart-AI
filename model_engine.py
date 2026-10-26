import torch
from diffusers import StableDiffusionPipeline, StableVideoDiffusionPipeline
from diffusers.utils import load_image, export_to_video
import os

class ModelEngine:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Initializing Avart AI Engine on device: {self.device}")
    def generate_image(self, prompt: str, output_path: str = "./outputs/generated_image.png"):
        """Generates an image from a text prompt using an open-source model."""
        #Ensure absolute path resolution for outputs directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if not os.path.isabs(output_path):
            output_path = os.path.join(base_dir, output_path.lstrip("./"))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Using a lightweight, fast model suitable for cloud deployment
        model_id = "segmind/small-sd"
        
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id, torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        )
        pipe.to(self.device)
        
        image = pipe(prompt).images[0]
        image.save(output_path)
        return output_path

    def process_background_removal(self, input_path: str, output_path: str):
        """Placeholder or utility method for background extraction on user uploads."""
        # This will link directly with your MediaProcessor asset workflows
        pass
