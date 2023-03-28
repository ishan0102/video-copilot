"""
Sieve workflow to query copilot for video editing.
"""
from typing import Dict, List

import sieve

from gpt import get_gpt_commands


@sieve.Model(
    name="pinecone-query-with-embedding",
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
class PineconeQueryWithEmbedding:
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

        for command in commands:
            if "query" not in command:
                yield command
                continue

            query = command["query"]
            for t in query:
                tokenized = clip.tokenize([t]).to("cpu")
                text_features = self.model.encode_text(tokenized)
                features = list(text_features.cpu().detach().numpy()[0])
                features = [float(x) for x in features]

            matches = index.query(
                vector=features,
                top_k=5,
                namespace=user_id,
                include_metadata=True,
            )["matches"]

            min_frame = float("inf")
            max_frame = float("-inf")

            for match in matches:
                frame_number = match["metadata"]["frame_number"]
                if frame_number < min_frame:
                    min_frame = frame_number
                if frame_number > max_frame:
                    max_frame = frame_number

            video_name = matches[0]["metadata"]["video_name"]
            fps = matches[0]["metadata"]["fps"]

            command["id"] = video_name
            command["start"] = round(min_frame / fps, 2)
            command["end"] = round(max_frame / fps, 2)
            del command["query"]
            yield command


@sieve.function(name="create-sieve-videos")
def create_sieve_videos(videos: List) -> sieve.Video:
    for video in videos:
        print(f"Creating video {video['url']}")
        yield sieve.Video(url=video["url"])


@sieve.workflow(name="copilot_query")
def copilot_query(videos: List[Dict], instructions: str, user_id: str) -> Dict:
    videos = create_sieve_videos(videos)
    commands = get_gpt_commands(videos, instructions)
    response = PineconeQueryWithEmbedding()(commands, user_id)
    return response
