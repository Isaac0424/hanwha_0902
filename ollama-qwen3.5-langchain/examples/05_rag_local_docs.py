"""로컬 텍스트 문서를 검색해 답변하는 간단한 RAG 예제.

data/sample.txt 를 청크로 나눠 nomic-embed-text 로 임베딩하고,
Chroma 인메모리 벡터스토어에서 유사도 검색 후 qwen3.5:9b 로 답변을 생성한다.
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample.txt"

embeddings = OllamaEmbeddings(
    model=os.environ.get("EMBED_MODEL", "nomic-embed-text"),
    base_url=BASE_URL,
)
llm = ChatOllama(model=os.environ.get("CHAT_MODEL", "qwen3.5:9b"), base_url=BASE_URL)

# add_start_index=True: 각 청크가 원본 텍스트의 몇 번째 글자에서 시작했는지를
# metadata["start_index"]에 정확히 기록한다. LLM에게 줄 번호를 추측시키지 않고,
# 이 값으로 실제 줄 번호를 계산해 답변과 별도로 출력하기 위함이다.
splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20, add_start_index=True)
text = DATA_PATH.read_text(encoding="utf-8")
docs = splitter.create_documents([text])

vectorstore = Chroma.from_documents(docs, embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

prompt = ChatPromptTemplate.from_template(
    """다음 컨텍스트만 근거로 질문에 한국어로 답해줘. 컨텍스트에 없으면 모른다고 답해.
    답변에서 어떤 문장을 참고했는지 [근거 N] 형태로 표시해줘.

[컨텍스트]
{context}

[질문]
{question}
"""
)

chain = prompt | llm | StrOutputParser()


def char_offset_to_line(offset: int) -> int:
    """원본 텍스트에서 글자 오프셋이 몇 번째 줄(1-based)에 해당하는지 계산한다."""
    return text.count("\n", 0, offset) + 1


def format_context(retrieved_docs) -> str:
    """각 청크에 [근거 N] 태그를 붙여 LLM이 답변에서 인용할 수 있게 한다."""
    return "\n\n".join(
        f"[근거 {i}]\n{d.page_content}" for i, d in enumerate(retrieved_docs, start=1)
    )


def print_sources(retrieved_docs) -> None:
    """[근거 N] 태그가 실제로 원본 문서의 몇 번째 줄인지 출력한다 (LLM 답변이 아닌 실측값)."""
    print("\n[참고한 근거 위치]")
    for i, d in enumerate(retrieved_docs, start=1):
        line = char_offset_to_line(d.metadata.get("start_index", 0))
        preview = d.page_content[:40].replace("\n", " ")
        print(f"  [근거 {i}] {DATA_PATH.name} {line}번째 줄 부근: \"{preview}...\"")


if __name__ == "__main__":
    question = "RTX 2070 Max-Q에 가장 적합한 Qwen3.5 모델 크기는?"
    retrieved_docs = retriever.invoke(question)

    answer = chain.invoke({"context": format_context(retrieved_docs), "question": question})
    print(answer)
    print_sources(retrieved_docs)
