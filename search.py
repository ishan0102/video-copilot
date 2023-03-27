"""
Sieve workflow to run CLIP on an image.
"""
import sieve

from clip_model import Clip
from splitter import VideoSplitter


@sieve.workflow(name="copilot_search")
def copilot_search(video: sieve.Video) -> list:
    images = VideoSplitter(video)
    clip_outputs = Clip()(images)
    return clip_outputs
