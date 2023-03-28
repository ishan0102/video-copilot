"""
Sieve workflow to query copilot for video editing.
"""
from typing import Dict, List

import sieve

from gpt import get_gpt_commands


@sieve.function(name="create-sieve-videos")
def create_sieve_videos(videos: List) -> sieve.Video:
    for video in videos:
        print(f"Creating video {video['url']}")
        yield sieve.Video(url=video["url"])


@sieve.workflow(name="copilot_query")
def copilot_query(videos: List[Dict], instructions: str) -> Dict:
    # TODO: instead of asking for videos as input, we should be fetching them from the database based on the instructions
    videos = create_sieve_videos(videos)
    return get_gpt_commands(videos, instructions)
