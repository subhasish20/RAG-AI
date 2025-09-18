from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled  # Correct import for the error

video_id = "Gfr50f6ZBvo"  # Replace with your actual video ID

try:
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
    print(transcript_list)
except TranscriptsDisabled:
    print(f"Transcript is disabled for video {video_id}.")
except Exception as e:
    print(f"An error occurred: {e}")
