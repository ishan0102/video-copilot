import time

import requests
from moviepy.editor import VideoFileClip, concatenate_videoclips
from rich.console import Console
from rich.panel import Panel

console = Console()


def edit_videos(video_info, videos_folder):
    console.print(Panel("Editing Videos", title="[bold blue]Edit Videos", expand=False, border_style="blue"))

    # Sort the video info by the order key
    video_info = sorted(video_info, key=lambda x: x["order"])

    video_clips = []
    for item in video_info:
        video_id = item["id"]
        start = item["start"]
        end = item["end"]

        input_file = f"{videos_folder}{video_id}"
        console.print(f"Loading video: {input_file}", style="bold yellow")
        video_clip = VideoFileClip(input_file)

        # Ensure start and end times are within the duration of the video
        start = max(0, min(start, video_clip.duration))
        end = max(0, min(end, video_clip.duration))
        video_clip = video_clip.subclip(start, end)
        video_clips.append(video_clip)

    # Concatenate all video clips into a single video
    console.print("Concatenating video clips...", style="bold yellow")
    final_video = concatenate_videoclips(video_clips, method="compose")

    # Save the final output video
    final_output = f"{videos_folder}final_output.mp4"
    console.print("Saving final output...", style="bold yellow")
    final_video.write_videofile(final_output, codec="libx264")

    # Close video clips
    for clip in video_clips:
        clip.close()

    console.print(Panel("Video Editing Complete", title="[bold blue]Edit Videos", expand=False, border_style="blue"))


def get_job_status(job_id):
    # Spin until the job is finished
    url = f"https://mango.sievedata.com/v1/jobs/{job_id}"
    headers = {
        "X-API-Key": "redacted",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    return response.json()["status"]


def push_data(prompt):
    console.print(Panel("Pushing Data", title="[bold blue]Push Data", expand=False, border_style="blue"))

    # Push a job to the Sieve API
    basketball = {
        "url": "https://storage.googleapis.com/sieve-public-videos/celebrity-videos/dwyane_basketball.mp4",
    }

    inputs = {
        "videos": [basketball],
        "instructions": prompt,
        "user_id": "ishan0102",
    }

    url = "https://mango.sievedata.com/v1/push"
    body = {"workflow_name": "copilot_query", "inputs": inputs}
    headers = {
        "X-API-Key": "redacted",
        "Content-Type": "application/json",
    }
    response = requests.post(url, json=body, headers=headers)
    job_id = response.json()["id"]

    # Spin until the job is finished
    console.print("Waiting for job to finish...", style="bold yellow")
    while get_job_status(job_id) != "finished":
        time.sleep(1)

    url = f"https://mango.sievedata.com/v1/jobs/{job_id}"
    headers = {
        "X-API-Key": "redacted",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    video_info = response.json()["data"]
    console.print(Panel("Data Push Complete", title="[bold blue]Push Data", expand=False, border_style="blue"))
    return video_info


if __name__ == "__main__":
    console.print(Panel("Video Editing Process Started", title="[bold green]Start", expand=False, border_style="green"))

    # Get the prompt
    prompt = "Put the basketball video first. Then query for and put the second half of the obama video."
    console.print(Panel(prompt, title="[bold blue]Instructions", expand=False, border_style="blue"))

    # Push data to the server and get the video editing information
    video_info = push_data(prompt)

    # Edit videos based on the received information
    edit_videos(video_info, "videos/")

    console.print(Panel("Video Editing Process Finished", title="[bold green]Finish", expand=False, border_style="green"))
