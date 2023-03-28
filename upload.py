"""
Sieve workflow to upload a video to Pinecone and run CLIP on it.
"""
from typing import Dict, List

import sieve

from clip_model import ClipImageEncoder
from splitter import video_splitter


@sieve.function(
    name="pinecone-upload",
    python_packages=[
        "pinecone-client==2.2.1",
        "python-dotenv==0.21.1",
    ],
    iterator_input=True,
)
def pinecone_upload(clip_embeddings: List, user_id: str):
    import os

    import pinecone
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("PINECONE_API_KEY")
    pinecone.init(api_key=api_key, environment="us-west1-gcp")

    index_name = "video-copilot"
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(name=index_name, dimension=512, metric="cosine")
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


@sieve.workflow(name="copilot_upload")
def copilot_upload(video: sieve.Video, name: str, user_id: str) -> Dict:
    images = video_splitter(video, name)
    clip_outputs = ClipImageEncoder()(images)
    response = pinecone_upload(clip_outputs, user_id)
    return clip_outputs
