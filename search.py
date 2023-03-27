"""
Sieve workflow to run CLIP on an image.
"""
from typing import Dict

import sieve

from clip_model import Clip
from splitter import VideoSplitter


@sieve.workflow(name="copilot_search")
def copilot_search(video: sieve.Video, name: str) -> Dict:
    images = VideoSplitter(video, name)
    clip_outputs = Clip()(images)
    return clip_outputs
