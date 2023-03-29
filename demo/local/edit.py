from moviepy.editor import concatenate_videoclips, VideoFileClip
import json


def edit_videos(json_file_path, videos_folder):
    # Read the JSON file
    with open(json_file_path, "r") as json_file:
        video_info = json.load(json_file)

    # Initialize an empty list to store the video clips
    video_clips = []

    # Loop through each item in the video editing information
    for item in video_info:
        # Extract video parameters from JSON
        video_id = item["id"]
        start = item["start"]
        end = item["end"]

        # Generate input file name
        input_file = f"{videos_folder}{video_id}"

        # Load the video clip using moviepy
        video_clip = VideoFileClip(input_file)

        # Ensure start and end times are within the duration of the video
        start = max(0, min(start, video_clip.duration))
        end = max(0, min(end, video_clip.duration))

        # Cut the video from the start position to the end position
        video_clip = video_clip.subclip(start, end)

        # Append the video clip to the list of video clips
        video_clips.append(video_clip)

    # Concatenate all video clips into a single video
    final_video = concatenate_videoclips(video_clips, method="compose")

    # Save the final output video
    final_output = f"{videos_folder}final_output.mp4"
    final_video.write_videofile(final_output, codec="libx264")

    # Close video clips
    for clip in video_clips:
        clip.close()


# Example usage (replace 'video_info.json' with the path to your JSON file and 'videos/' with the path to your videos folder)
# Note: Since the script needs to read a file, please run it locally on your machine.
edit_videos("video_info.json", "videos/")
