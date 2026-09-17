"""ChatPromptTemplate + LCEL 체인 예제."""
import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

load_dotenv()

llm = ChatOllama(
    model=os.environ.get("CHAT_MODEL", "qwen3.5:9b"),
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "너는 {role} 역할의 어시스턴트야. 답변은 한국어로 간결하게 해."),
        ("human", "{question}"),
    ]
)

chain = prompt | llm | StrOutputParser()

if __name__ == "__main__":
    result = chain.invoke(
        {
            "role": "GPU 하드웨어 전문가",
            "question": "RTX 2070 Max-Q의 VRAM 용량에 맞는 로컬 LLM 크기는 어느 정도가 적당해?",
        }
    )
    print(result)
