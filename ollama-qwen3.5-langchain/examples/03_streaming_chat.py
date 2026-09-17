"""토큰 스트리밍 예제."""
import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()

llm = ChatOllama(
    model=os.environ.get("CHAT_MODEL", "qwen3.5:9b"),
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
)

if __name__ == "__main__":
    for chunk in llm.stream("Qwen3.5 소형 모델 라인업의 특징을 3줄로 요약해줘."):
        print(chunk.content, end="", flush=True)
    print()
