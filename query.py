"""
Sieve workflow to query copilot for video editing.
"""
from typing import Dict, List

import sieve


@sieve.function(
    name="get_commands",
    python_packages=[
        "openai==0.27.2",
        "python-dotenv==0.21.1",
    ],
    persist_output=True,
    iterator_input=True,
)
def get_commands(videos: sieve.Video, instructions: str) -> str:
    import json
    import os

    import openai
    from dotenv import load_dotenv

    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    videos_prompt = "VIDEOS:\n"
    for video in videos:
        video_metadata = f"ID - {video.url.split('/')[-1]}\nLENGTH - {video.frame_count / video.fps}s\n\n"
        videos_prompt += video_metadata

    # HACK: instructions is a string but iterator_input means it has to be iterated over to get the string
    instructions_prompt = "INSTRUCTIONS:\n"
    for instruction in instructions:
        instructions_prompt += instruction

    print(f"videos_prompt: {videos_prompt}")
    print(f"instructions_prompt: {instructions_prompt}")

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an agent controlling a video editing tool. You are given a list of videos available and a set of sentence instructions that tell you how to manipulate those videos."},
            {"role": "user", "content": "The VIDEOS given to you are given in a list:\n\nID - an ID or name denoting the video\nLENGTH - the length of the content in seconds\n\nThe available MANIPULATIONs are:\nDARKEN - darken the scene\nLIGHTEN - brighten the scene\nBLUR - blur the scene\nBG_REMOVE - remove the background\nBW - turn the clip to black and white\n\nThe INSTRUCTION is given to you as a list of sentences. Based on the sentences, you can issue a list of actions as shown below:\n\nIf the action is referencing a specific clip you know in the library, you will output the action as formatted below:\n\nID - the ID of the clip in the library\nSTART - start time in seconds of the clip to perform the actions\nEND - end time in seconds of the clip to perform the actions\nACTIONS - ordered, comma-separated list of MANIPULATIONS to perform\n\nIf the action doesn't seem to specify a specific video in the library, then you will issue a SEARCH command which will magically find the right clip based on their natural language description of it.\n\nQUERY - the query to search this clip by in natural language\nSTART - start time in fractional quantity of the part of the clip to perform the actions on\nEND - end time in fractional quantity of the part of the clip to perform the actions on\nACTIONS - ordered, comma-separated list of MANIPULATIONS to perform\n\nYou will return these actions in the order in which the user wants them to happen."},
            {"role": "user", "content": "Here are 4 examples:\n\n"},
            {"role": "user", "content": "VIDEOS:\nID - flower.mp4\nLENGTH - 500s\n\nID - 3453432342.mp4\nLENGTH - 2s\n\nID - shoot.mp4\nLENGTH - 145243s\n\nINSTRUCTIONS:\nCut the video of the dog to the first 10 seconds and remove its background."},
            {"role": "assistant", "content": 'COMMANDS:\nQUERY: "dog"\nSTART: 0\nEND: 1\nACTIONS: REMOVE_BG'},
            {"role": "user", "content": "VIDEOS:\nID - hello.avi\nLENGTH - 300041s\n\nINSTRUCTIONS:\nCut the first 500 seconds of the clip in the library, make it darker and black and white, and then add the part with the flowers right after it but make that clip a bit darker."},
            {"role": "assistant", "content": 'COMMANDS:\nID: hello.avi\nSTART: 0\nEND: 500s\nACTIONS: DARKEN, BW\n\nQUERY: "flowers"\nSTART: 0\nEND: 1\nACTIONS: DARKEN'},
            {"role": "user", "content": "VIDEOS:\nID - person.mp4\nLENGTH - 20s\n\nINSTRUCTIONS:\nadd the first 10s of the clip titled person and then add the same 10s after but darker."},
            {"role": "assistant", "content": "COMMANDS:\nID: person.mp4\nSTART: 0\nEND: 10s\nACTIONS:\n\nID: person.mp4\nSTART: 0\nEND: 10s\nACTIONS: DARKEN"},
            {"role": "user", "content": "VIDEOS:\nID: hello.mp4\nLENGTH - 500s\n\nID: hello1.mp4\nLENGTH - 20s\n\nINSTRUCTIONS:\nCreate a video with the original videos each with their backgrounds removed in order of shortest to longest. Then add the drone angle to the beginning."},
            {"role": "assistant", "content": 'COMMANDS:\nQUERY: "drone angle"\nSTART: 0\nEND: 1\nACTIONS:\n\nID: hello1.mp4\nSTART: 0\nEND: 20s\nACTIONS: BG_REMOVE\n\nID: hello.mp4\nSTART: 0\nEND: 500s\nACTIONS: BG_REMOVE'},
            {"role": "user", "content": f"VIDEOS:{videos_prompt}\n\nINSTRUCTIONS:{instructions_prompt}"},
        ],
    )

    print(response)
    commands = json.dumps(response.choices[0].message.content)
    commands = commands.replace(r"COMMANDS:\n", '"')
    commands = commands.strip('"').split(r"\n\n")
    print(commands)
    for command in commands:
        print(command)
        yield command


@sieve.function(name="create_videos")
def create_videos(videos: List) -> sieve.Video:
    for video in videos:
        print(f"Creating video {video['url']}")
        yield sieve.Video(url=video["url"])


@sieve.workflow(name="copilot_query")
def copilot_query(videos: List[Dict], instructions: str) -> str:
    # TODO: instead of asking for videos as input, we should be fetching them from the database based on the instructions
    videos = create_videos(videos)
    return get_commands(videos, instructions)
