"""LangChain LLM 캐싱 예제.

같은 질문을 두 번 호출해서 1차(실제 추론)와 2차(캐시 히트)의 응답 속도를 비교한다.
캐시는 SQLite 파일에 저장되므로 스크립트를 재실행해도 캐시가 유지된다.
"""
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from langchain_ollama import ChatOllama

load_dotenv()

CACHE_PATH = Path(__file__).resolve().parent.parent / "data" / ".langchain_cache.db"
CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
set_llm_cache(SQLiteCache(database_path=str(CACHE_PATH)))

llm = ChatOllama(
    model=os.environ.get("CHAT_MODEL", "qwen3.5:9b"),
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
)

QUESTION = "LangChain에서 LLM 캐싱이 왜 유용한지 한 문장으로 설명해줘."

if __name__ == "__main__":
    start = time.perf_counter()
    first = llm.invoke(QUESTION)
    elapsed_first = time.perf_counter() - start
    print(f"[1차 호출 - 실제 추론] {elapsed_first:.2f}s\n{first.content}\n")

    start = time.perf_counter()
    second = llm.invoke(QUESTION)
    elapsed_second = time.perf_counter() - start
    print(f"[2차 호출 - 캐시 히트] {elapsed_second:.2f}s\n{second.content}\n")

    print(f"캐시 파일: {CACHE_PATH}")
    print(f"속도 차이: {elapsed_first - elapsed_second:.2f}s 단축")
