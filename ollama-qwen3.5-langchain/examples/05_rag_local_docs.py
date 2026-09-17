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
from langchain_core.runnables import RunnablePassthrough
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

splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
text = DATA_PATH.read_text(encoding="utf-8")
docs = splitter.create_documents([text])

vectorstore = Chroma.from_documents(docs, embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

prompt = ChatPromptTemplate.from_template(
    """다음 컨텍스트만 근거로 질문에 한국어로 답해줘. 컨텍스트에 없으면 모른다고 답해.

[컨텍스트]
{context}

[질문]
{question}
"""
)


def format_docs(retrieved_docs) -> str:
    return "\n\n".join(d.page_content for d in retrieved_docs)


chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

if __name__ == "__main__":
    question = "RTX 2070 Max-Q에 가장 적합한 Qwen3.5 모델 크기는?"
    print(chain.invoke(question))
