import time
from dotenv import load_dotenv
from google import genai
from google.genai.types import CachedContent, CreateCachedContentConfig, Content, Part
from langchain_google_genai import ChatGoogleGenerativeAI
from IPython.display import Markdown, display
from Gemini3WithLangChain import gemini2

load_dotenv()

client = genai.Client()
files = [
    "data/rag-data/pdfs/apple/apple 10-q q1 2024.pdf",
    "data/rag-data/pdfs/apple/apple 10-q q2 2024.pdf"
]

uploadedFiles = []

for file in files:
    file = client.files.upload(file = file)
    while file.state.name == "PROCESSING":
        time.sleep(2)
        file = client.files.get(name = file.name)
    
    uploadedFiles.append(file)

# print(uploadedFiles)

parts = []
for f in uploadedFiles:
    part = Part.from_uri(file_uri=f.uri, mime_type=f.mime_type)
    parts.append(part)

# print(parts)

contents = [Content(role='user', parts=parts)]

cache = client.caches.create(
    model = gemini2,
    config = CreateCachedContentConfig(
        display_name = 'Apple Q1 Q2 2024 reports',
        system_instruction = "You are a financial analyst. Use these Apple quarterly reports to answer questions.",
        contents = contents,
        ttl = "1880s"
    )
)

model = ChatGoogleGenerativeAI (
    model = gemini2,
    cached_content = cache.name
)

query = "Compare the revenue growth between Q1 and Q2 2024"
response = model.invoke(query)
ñ

display(Markdown(response.text))