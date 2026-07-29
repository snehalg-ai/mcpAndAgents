import os
from dotenv import load_dotenv

load_dotenv()

googleKey = os.getenv("GEMINI_API_KEY")
langsmithKey = os.getenv("LANGSMITH_API_KEY")

print(googleKey)
print(langsmithKey)

if googleKey:
    print("Gemini API Key loaded successfully")
else:
    print("Gemini API Key not found")

if langsmithKey:
    print("Langsmith API Key loaded successfully")
else:
    print("Langsmith API Key not found")