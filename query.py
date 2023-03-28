"""
Sieve workflow to query copilot for video editing.
"""
from typing import Dict, List

import sieve

from embeddings import PineconeQueryText
from gpt import get_gpt_commands


@sieve.function(name="create-sieve-videos")
def create_sieve_videos(videos: List) -> sieve.Video:
    for video in videos:
        print(f"Creating video {video['url']}")
        yield sieve.Video(url=video["url"])


@sieve.workflow(name="copilot_query")
def copilot_query(videos: List[Dict], instructions: str, user_id: str) -> Dict:
    videos = create_sieve_videos(videos)
    commands = get_gpt_commands(videos, instructions)
    response = PineconeQueryText()(commands, user_id)
    return response
