"""가장 기본적인 ChatOllama 호출 예제."""
import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()

llm = ChatOllama(
    model=os.environ.get("CHAT_MODEL", "qwen3.5:9b"),
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
    temperature=0.3,
)

if __name__ == "__main__":
    response = llm.invoke("로컬 LLM을 쓰는 이유를 한 문장으로 설명해줘.")
    print(response.content)
