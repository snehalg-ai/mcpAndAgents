from langchain_ollama import ChatOllama
from langchain.messages import HumanMessage, SystemMessage

gemma4 = "gemma4:31b"

system_msg = SystemMessage("You are a helpful AI Assistant")
query = HumanMessage("Explain the theory of relativity in simple terms")

messages = [system_msg, query]

model = ChatOllama(model=gemma4)
response = model.invoke(messages)
print(response.content)
