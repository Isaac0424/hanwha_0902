"""체인 실행 결과를 pickle / JSON으로 저장하고 다시 열어보는 예제.

JsonOutputParser로 딕셔너리 결과를 얻은 뒤 두 가지 방식으로 파일에 저장하고,
각 파일을 다시 읽어 내용이 같은지 확인한다.
"""
import json
import os
import pickle
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

load_dotenv()

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PKL_PATH = OUTPUT_DIR / "gpu_summary.pkl"
JSON_PATH = OUTPUT_DIR / "gpu_summary.json"

llm = ChatOllama(
    model=os.environ.get("CHAT_MODEL", "qwen3.5:9b"),
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
)

prompt = ChatPromptTemplate.from_template(
    "다음 GPU 사양을 JSON으로만 답해줘. 다른 설명은 붙이지 마.\n"
    "키는 gpu_name, vram_gb, recommended_model 세 개만 써.\n"
    "GPU: RTX 2070 with Max-Q Design, VRAM 8GB"
)

chain = prompt | llm | JsonOutputParser()


def save(result: dict) -> None:
    with open(PKL_PATH, "wb") as f:
        pickle.dump(result, f)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def load_and_print() -> None:
    with open(PKL_PATH, "rb") as f:
        from_pickle = pickle.load(f)
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        from_json = json.load(f)

    print("[pickle에서 읽은 값]", from_pickle)
    print("[json에서 읽은 값]  ", from_json)
    assert from_pickle == from_json, "pickle과 json 내용이 다릅니다"
    print("\n확인 완료: 두 파일의 내용이 일치합니다.")


if __name__ == "__main__":
    result = chain.invoke({})
    print("[체인 실행 결과]", result)

    save(result)
    print(f"저장 완료: {PKL_PATH} / {JSON_PATH}")

    load_and_print()
