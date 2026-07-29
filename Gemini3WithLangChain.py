from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from dotenv import load_dotenv
load_dotenv()

gemini3 = 'gemini-3.1-pro-preview'
gemini2 = 'gemini-3.5-flash'

system_msg = SystemMessage("You are a helpful AI Assistant")
query = HumanMessage("Explain the theory of relativity in simple terms")

messages = [system_msg, query]

llm = ChatGoogleGenerativeAI(model=gemini3)

humanMessage = HumanMessage(
    [
        {
            'type': 'text',
            'text': 'Explain the image in simple terms'
        },
        {
            'type': 'image_url',
            'image_url': {
                'url': 'https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png'
            }
        }
    ]
)

response = llm.invoke([humanMessage, system_msg])

print(response.text)
print(response.usage_metadata)

for chunk in llm.stream([humanMessage, system_msg]):
    print(chunk.content, end="", flush=True)
