from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api import TranscriptsDisabled
from dotenv import load_dotenv

load_dotenv()


from youtube_transcript_api import YouTubeTranscriptApi

# Replace 'video_id' with the actual ID of the YouTube video.
video_id = 'Gfr50f6ZBvo'

# Fetching the transcript
transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
print(transcript_list)

"""
video_id = "Gfr50f6ZBvo" # only the ID, not full URL
try:
    # If you don’t care which language, this returns the “best” one
    transcript_list = YouTubeTranscriptApi.get_tre(video_id, languages=["en"])

    # Flatten it to plain text
    transcript = " ".join(chunk["text"] for chunk in transcript_list)
    print(transcript)

except TranscriptsDisabled:
    print("No captions available for this video.")
    

model = ChatGoogleGenerativeAI(model='gemini-2.5-flash')

result = model.invoke('What is the capital of India')

print(result.content)"""
