from pydoc import text
from turtle import mode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import HumanMessage
from dotenv import load_dotenv
import base64
load_dotenv()


gemini3 = 'gemini-3.1-pro-preview'
model = ChatGoogleGenerativeAI(
    model=gemini3,
    thinking_level='high',
    include_thoughts=True,
)
# humanMessage = HumanMessage(
#     [
#         {
#             'type': 'text',
#             'text': 'Explain the image in simple terms'
#         },
#         {
#             'type': 'image_url',
#             'image_url': {
#                 'url': 'https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png'
#             }
#         }
#     ]
# )

# response = model.invoke([humanMessage])
# print(response.text)

# Image Analysis
# mimeType = 'image/png'
# imageBytes = open('data/images/panda.png', 'rb').read()
# base64Bytes = base64.b64encode(imageBytes).decode('utf-8')

systemMessage = "You are a helpful assistant"
# humanMessage = HumanMessage (
#     [
#         {
#             'type': 'text',
#             'text': 'Describe the Image provided'
#         },
#         {
#             'type': 'image',
#             'base64': base64Bytes,
#             'mime_type': mimeType
#         }
#     ]
# )

# response = model.invoke([systemMessage, humanMessage])
# print(response.text)

# PDF Analysis
pdfBytes = open('data/rag-data/pdfs/apple/apple 10-q q1 2024.pdf', 'rb').read()
pdf_base64 = base64.b64encode(pdfBytes).decode('utf-8')
mimeType = "application/pdf"

humanMessage = HumanMessage (
    [
        {
            'type': 'text',
            'text': 'Summarize the Key insights from the quarterly Gemini report'
        },
        {
            'type': 'file',
            'base64': pdf_base64,
            mimeType: mimeType
        }
    ]
)

response = model.invoke([systemMessage, humanMessage])
print(response.usage_metadata)