import base64

import requests
from langchain_ollama import ChatOllama
from langchain.messages import HumanMessage, SystemMessage

gemma4 = "gemma4:e2b"

system_msg = SystemMessage("You are a helpful AI Assistant")
query = HumanMessage("Explain ollama in simple terms")

messages = [system_msg, query]

model = ChatOllama(model=gemma4)

image_url = "https://upload.wikimedia.org/wikipedia/commons/6/6d/Audi_Q5_2.0_TDI_quattro_S_line_%28GU%29_%E2%80%93_f_13102025.jpg"
image_response = requests.get(image_url, headers={"User-Agent": "TestGemma4LocalConnection/1.0"})
image_response.raise_for_status()
image_b64 = base64.b64encode(image_response.content).decode("utf-8")

image_msg = HumanMessage(
    [
        {
            "type": "text",
            "text": "Explain the image provided",
        },
        {
            "type": "image_url",
            "image_url": f"data:image/jpeg;base64,{image_b64}",
        },
    ]
)

response = model.invoke([system_msg, image_msg])
print(response.content)

for chunk in model.stream([system_msg, image_msg]):
    print(chunk.content, end="", flush=True)

print()