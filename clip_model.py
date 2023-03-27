from typing import Dict, List

import sieve


@sieve.Model(
    name="clip",
    gpu=False,
    python_packages=[
        "git+https://github.com/openai/CLIP.git",
    ],
    python_version="3.9",
    persist_output=True,
)
class Clip:
    def __setup__(self):
        import torch
        import clip

        self.clip_device = "cpu"
        self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.clip_device)

    def __predict__(self, img: sieve.Image) -> List:
        import torch
        from PIL import Image

        image = self.clip_preprocess(Image.open(img.path)).unsqueeze(0).to(self.clip_device)

        with torch.no_grad():
            image_features = self.clip_model.encode_image(image)

        yield image_features
