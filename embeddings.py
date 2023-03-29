from typing import Dict, List

import sieve


@sieve.Model(
    name="pinecone-upload-images",
    python_packages=[
        "pinecone-client==2.2.1",
        "python-dotenv==0.21.1",
        "torch==1.8.1",
        "git+https://github.com/openai/CLIP.git",
    ],
    run_commands=[
        "mkdir -p /root/.cache/clip",
        "wget -O /root/.cache/clip/ViT-B-32.pt https://openaipublic.azureedge.net/clip/models/40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af/ViT-B-32.pt",
    ],
    iterator_input=True,
)
class PineconeUploadImages:
    def __setup__(self):
        import clip

        self.model, self.preprocess = clip.load("ViT-B/32", device="cpu")

    def __predict__(self, images: sieve.Image, user_id: str):
        import os

        import pinecone
        from dotenv import load_dotenv

        load_dotenv()

        from PIL import Image

        clip_embeddings = []
        for image in images:
            metadata = {
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
            clip_embeddings.append({"id": image.id, "features": features, "metadata": metadata})

        api_key = os.getenv("PINECONE_API_KEY")
        pinecone.init(api_key=api_key, environment="us-west1-gcp")
        index_name = "video-copilot"
        index = pinecone.Index(index_name=index_name)

        vectors = []
        for clip_embedding in clip_embeddings:
            vectors.append((clip_embedding["id"], clip_embedding["features"], clip_embedding["metadata"]))

        # HACK: convert iterator input to string
        for user in user_id:
            user_id = user
            break

        response = index.upsert(vectors=vectors, namespace=user_id)
        if "upserted_count" in response:
            print(f"Successfully upserted {response['upserted_count']} vectors")
        else:
            print("Failed to upsert vectors")

        return clip_embeddings


@sieve.Model(
    name="pinecone-query-text",
    python_packages=[
        "pinecone-client==2.2.1",
        "python-dotenv==0.21.1",
        "torch==1.8.1",
        "git+https://github.com/openai/CLIP.git",
    ],
    run_commands=[
        "mkdir -p /root/.cache/clip",
        "wget -O /root/.cache/clip/ViT-B-32.pt https://openaipublic.azureedge.net/clip/models/40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af/ViT-B-32.pt",
    ],
    iterator_input=True,
)
class PineconeQueryText:
    def __setup__(self):
        import clip

        self.model, self.preprocess = clip.load("ViT-B/32", device="cpu")

    def __predict__(self, commands: Dict, user_id: str) -> Dict:
        import os

        import clip
        import pinecone
        from dotenv import load_dotenv

        load_dotenv()

        api_key = os.getenv("PINECONE_API_KEY")
        pinecone.init(api_key=api_key, environment="us-west1-gcp")
        index_name = "video-copilot"
        index = pinecone.Index(index_name=index_name)

        # HACK: convert iterator input to string
        for user in user_id:
            user_id = user
            break

        # Perform each required query
        for command in commands:
            if "query" not in command:
                print(f"Skipping {command} (no query)")
                yield command
                continue

            # Encode the query text with CLIP
            print(f"Querying for {command['query']}")
            query = command["query"]
            for t in query:
                tokenized = clip.tokenize([t]).to("cpu")
                text_features = self.model.encode_text(tokenized)
                features = list(text_features.cpu().detach().numpy()[0])
                features = [float(x) for x in features]

            print(features)

            # Get the top-k nearest neighbors
            matches = index.query(
                vector=features,
                top_k=10,
                namespace=user_id,
                include_metadata=True,
                include_values=True,
            )["matches"]

            # Keep the matches that win the majority vote by video name
            video_name_freqs = {}
            for match in matches:
                video_name = match["metadata"]["video_name"]
                if video_name not in video_name_freqs:
                    video_name_freqs[video_name] = 0
                video_name_freqs[video_name] += 1

            max_freq = float("-inf")
            max_freq_video_name = None
            for video_name, freq in video_name_freqs.items():
                if freq > max_freq:
                    max_freq = freq
                    max_freq_video_name = video_name

            matches = [match for match in matches if match["metadata"]["video_name"] == max_freq_video_name]

            # Find the min and max frame numbers
            min_frame = float("inf")
            max_frame = float("-inf")

            for match in matches:
                print(f"Found {match['id']} (frame_number={match['metadata']['frame_number']})")
                frame_number = match["metadata"]["frame_number"]
                if frame_number < min_frame:
                    min_frame = frame_number
                if frame_number > max_frame:
                    max_frame = frame_number

            print(f"Found {len(matches)} matches (min_frame={min_frame}, max_frame={max_frame})")
            print(f"The frames found are about {command['query']} (e.g. {matches[0]['id']})")

            # Update the command with the new start and end times
            video_name = matches[0]["metadata"]["video_name"]
            fps = matches[0]["metadata"]["fps"]

            command["id"] = video_name
            command["start"] = round(min_frame / fps, 2) * command["start"]
            command["end"] = round(max_frame / fps, 2) * command["end"]
            del command["query"]
            yield command
