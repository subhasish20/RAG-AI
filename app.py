
###======================STEP 0 : Import the libraries===============================
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from  dotenv import  load_dotenv
from urllib.parse import urlparse, parse_qs
import streamlit as st
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") # for embedding


def get_youtube_id(url: str) -> str:

    #Extract the YouTube video ID from a given URL.
    #Returns:
        #str: YouTube video ID if found, otherwise None.

    # Break the URL into components: scheme, netloc, path, query, etc.
    parsed_url = urlparse(url)

    # --- Case 1: Shortened "youtu.be" links ---
    # Example: https://youtu.be/dQw4w9WgXcQ
    # The video ID is everything after the initial "/"
    if parsed_url.netloc == "youtu.be":
        return parsed_url.path.lstrip("/")  # Strip leading "/" from path

    # --- Case 2: Standard "youtube.com/watch" links ---
    # Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s
    # The video ID lives inside the "v=" query parameter
    if parsed_url.path == "/watch":
        query_params = parse_qs(parsed_url.query)  # Convert query string into dictionary
        return query_params.get("v", [None])[0]    # Get "v" param, fallback to None
    else:
        return  "Video url no found"
try:
    url = input("Enter the url :")
    video_id = get_youtube_id(url)
    # If you don’t care which language, this returns the “best” one
    transcript_list = YouTubeTranscriptApi().fetch(video_id, languages=['hi', 'en'])

    # Flatten it to plain text
    transcript = " ".join(chunk.text for chunk in transcript_list)
except TranscriptsDisabled:
    print("No captions available for this video.")



splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200) # using text splitter
chunks = splitter.create_documents([transcript])



# FREE local embedding model
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
# Build FAISS vector store
vector_store = FAISS.from_documents(chunks, embedding)


retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})


llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash')

prompt = PromptTemplate(
    template="""
You are an expert AI assistant specializing in answering questions based strictly on transcripts.

Instructions:
- Use only the information provided in the transcript context below.
- Be concise, accurate, and clear in your responses.
- If the transcript context does not contain the answer, say:
  "I don’t know based on the given transcript."
- Never make up facts or rely on outside knowledge.
- If relevant, provide brief direct quotes or summaries from the transcript.

---------------------
Transcript Context:
{context}
---------------------

Question: {question}

Answer:
    """,
    input_variables = ['context', 'question']
)
question = "what is java programming ?"
retrieved_docs = retriever.invoke(question)
context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)


final_prompt = prompt.invoke({"context": context_text, "question": question})

def format_docs(retrieved_docs):
  context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
  return context_text

parallel_chain = RunnableParallel({
    'context': retriever | RunnableLambda(format_docs),
    'question': RunnablePassthrough()
})

parser = StrOutputParser()

main_chain = parallel_chain | prompt | llm | parser

while True:
    user_input = input("User :")
    if user_input != "Exit" :
        answers = main_chain.invoke(user_input)
        print(f"AI : {answers}")
    else:
        break

