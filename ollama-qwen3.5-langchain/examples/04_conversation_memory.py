"""대화 히스토리를 유지하는 RunnableWithMessageHistory 예제."""
import os

from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_ollama import ChatOllama

load_dotenv()

llm = ChatOllama(
    model=os.environ.get("CHAT_MODEL", "qwen3.5:9b"),
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "너는 친절한 한국어 어시스턴트야."),
        MessagesPlaceholder("history"),
        ("human", "{input}"),
    ]
)

chain = prompt | llm

store: dict[str, InMemoryChatMessageHistory] = {}


def get_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


chain_with_history = RunnableWithMessageHistory(
    chain,
    get_history,
    input_messages_key="input",
    history_messages_key="history",
)

if __name__ == "__main__":
    config = {"configurable": {"session_id": "demo"}}

    first = chain_with_history.invoke({"input": "내 GPU는 RTX 2070 Max-Q야. 기억해둬."}, config=config)
    print("AI:", first.content)

    second = chain_with_history.invoke({"input": "내 GPU 이름이 뭐라고 했지?"}, config=config)
    print("AI:", second.content)
