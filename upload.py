"""
Sieve workflow to upload a video to Pinecone and run CLIP on it.
"""
from typing import Dict, List

import sieve

from embeddings import PineconeUploadImages
from splitter import video_splitter


@sieve.workflow(name="copilot_upload")
def copilot_upload(video: sieve.Video, name: str, user_id: str) -> Dict:
    images = video_splitter(video, name)
    response = PineconeUploadImages()(images, user_id)
    return response
