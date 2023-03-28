"""
Sieve workflow to upload a video to Pinecone and run CLIP on it.
"""
from typing import Dict

import sieve

from clip_model import Clip
from splitter import VideoSplitter


@sieve.workflow(name="copilot_upload")
def copilot_upload(video: sieve.Video, name: str) -> Dict:
    images = VideoSplitter(video, name)
    clip_outputs = Clip()(images)
    return clip_outputs
