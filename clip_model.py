import sieve


@sieve.Model(
    name="clip",
    gpu=False,
    python_packages=[
        "torch==1.8.1",
        "git+https://github.com/openai/CLIP.git",
    ],
    run_commands=[
        "mkdir -p /root/.cache/clip",
        "wget -O /root/.cache/clip/ViT-B-32.pt https://openaipublic.azureedge.net/clip/models/40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af/ViT-B-32.pt",
    ],
    iterator_input=True,
)
class Clip:
    def __setup__(self):
        import clip

        self.model, self.preprocess = clip.load("ViT-B/32", device="cpu")

    def __predict__(self, images: sieve.Image):
        from PIL import Image

        for image in images:
            metadata = {
                "id": image.id,
                "type": image.type,
                "video_name": image.video_name,
                "frame_number": image.frame_number,
                "frame_count": image.frame_count,
                "fps": image.fps,
                "x0": image.x0,
                "y0": image.y0,
                "x1": image.x1,
                "y1": image.y1,
                "video_path": image.video_path,
            }
            preprocessed_image = self.preprocess(Image.open(image.path)).unsqueeze(0).to("cpu")
            image_features = self.model.encode_image(preprocessed_image)
            features = list(image_features.cpu().detach().numpy()[0])
            features = [float(x) for x in features]
            print(type(features), type(features[0]), len(features))
            yield {"features": features, "metadata": metadata}
