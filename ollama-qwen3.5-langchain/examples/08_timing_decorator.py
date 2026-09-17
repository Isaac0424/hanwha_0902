"""추론 시간을 재는 세 가지 방법 비교.

1) 직접 만든 @timed 데코레이터  - wall-clock 시간 (네트워크 왕복 포함)
2) LangChain 콜백(BaseCallbackHandler) - LLM 호출 구간만 자동 측정
3) ChatOllama 응답의 response_metadata - Ollama 서버가 실어보내는 정밀 타이밍
"""
import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama

from utils import LatencyCallbackHandler, print_ollama_durations, timed

load_dotenv()

llm = ChatOllama(
    model=os.environ.get("CHAT_MODEL", "qwen3.5:9b"),
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
)

QUESTION = "Docker와 WSL의 차이를 두 문장으로 설명해줘."


@timed("llm.invoke (wall-clock)")
def ask(question: str):
    return llm.invoke(question)


if __name__ == "__main__":
    # 1) 데코레이터 방식: 함수 호출을 감싸서 측정
    response = ask(QUESTION)
    print(response.content, "\n")

    # 2) 콜백 방식: invoke를 감싸지 않고 config로 꽂아 넣기만 하면 됨
    #    체인/에이전트처럼 내부에서 LLM이 여러 번 호출돼도 호출마다 자동으로 찍힌다.
    handler = LatencyCallbackHandler()
    llm.invoke(QUESTION, config={"callbacks": [handler]})

    # 3) LangChain을 거치지 않고도 Ollama 자체가 응답에 실어보내는 서버 측 정밀 타이밍
    #    (여기 값은 순수 추론 시간만 포함, 클라이언트<->서버 네트워크 왕복은 제외)
    print("\n[Ollama 서버 측 타이밍 - response_metadata]")
    print_ollama_durations(response.response_metadata)
