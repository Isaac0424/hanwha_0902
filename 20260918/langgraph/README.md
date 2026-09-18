# LangChain legacy 메모리 → LangGraph 메모리 마이그레이션 정리

`../legacy/` 의 `langchain_classic.memory` 예제들을 **LangGraph / LangChain v1** 방식으로 다시 작성했습니다.
모든 노트북은 실행 결과(출력)까지 저장되어 있습니다.

> 확인 환경: `langchain 1.4.0`, `langchain-classic 1.0.8`, `langgraph 1.2.11`, `langgraph-checkpoint 4.2.0`, `langgraph-checkpoint-sqlite 3.1.1`, `langchain-openai 1.6.2`, 모델 `gpt-4o-mini`

---

## 1. 한 줄 요약

**"메모리 객체를 체인에 붙이던 방식"이 "그래프 상태(state)를 checkpointer / store 가 저장하는 방식"으로 바뀌었습니다.**

legacy 메모리 클래스를 쓰면 다음 경고가 나옵니다.

```
LangChainDeprecationWarning: The class `ConversationBufferMemory` was deprecated in LangChain 0.3.1
and will be removed in 2.0.0. Use `langchain.agents.create_agent` instead. For agents that need to
remember prior interactions, use `create_agent` with checkpointing or the `Store` API.
```

```
LangChainDeprecationWarning: RunnableWithMessageHistory is deprecated. Use LangGraph's built-in persistence instead.
```

## 2. 기억의 두 종류

| 구분 | LangGraph 구성요소 | 범위 | legacy 에서 대응되던 것 |
|---|---|---|---|
| **단기 기억** (대화 기록) | **Checkpointer** (`InMemorySaver`, `SqliteSaver`, `PostgresSaver`) | `thread_id` 하나 = 대화 하나 | Buffer / Window / TokenBuffer / Summary 메모리, `RunnableWithMessageHistory` |
| **장기 기억** (사실·프로필·지식) | **Store** (`InMemoryStore`, `PostgresStore`) | `namespace` (예: `("entities", user_id)`), **thread 를 넘어서 공유** | Entity / KG / VectorStoreRetriever 메모리 |

```python
graph = builder.compile(checkpointer=InMemorySaver(), store=InMemoryStore())
graph.invoke({"messages": [...]},
             config={"configurable": {"thread_id": "대화ID"}},   # 단기 기억 구분
             context={"user_id": "사용자ID"})                    # 장기 기억 네임스페이스 등에 사용
```

## 3. 파일 대응표

| legacy 노트북 | legacy 클래스 | 새 노트북 | LangGraph 대응 |
|---|---|---|---|
| `conversation_legacy.ipynb` | `ConversationBufferMemory`, `ConversationBufferWindowMemory` | [01_conversation_buffer_langgraph.ipynb](01_conversation_buffer_langgraph.ipynb) | `InMemorySaver` + `thread_id`, `trim_messages` / `RemoveMessage` |
| `conversation_tocken_buffer_legacy.ipynb` | `ConversationTokenBufferMemory` | [02_conversation_token_buffer_langgraph.ipynb](02_conversation_token_buffer_langgraph.ipynb) | `trim_messages(token_counter=llm)` + `@before_model` 미들웨어 |
| `conversation_summary_legacy.ipynb` | `ConversationSummaryMemory`, `ConversationSummaryBufferMemory` | [03_conversation_summary_langgraph.ipynb](03_conversation_summary_langgraph.ipynb) | 요약 노드 + `summary` state, `SummarizationMiddleware` |
| `conversation_entity_legacy.ipynb`, `conversation_knowledge_graph.ipynb` | `ConversationEntityMemory`, `ConversationKGMemory` | [04_entity_kg_memory_langgraph.ipynb](04_entity_kg_memory_langgraph.ipynb) | `Store` + `with_structured_output` 추출 |
| `vector_store_retriever_memory_legacy.ipynb` | `VectorStoreRetrieverMemory` | [05_vector_store_memory_langgraph.ipynb](05_vector_store_memory_langgraph.ipynb) | `InMemoryStore(index=...)` 시맨틱 검색 |
| `lcel_add_memory_legacy.ipynb` | `ConversationBufferMemory` + `RunnablePassthrough.assign` | [06_lcel_add_memory_langgraph.ipynb](06_lcel_add_memory_langgraph.ipynb) | LCEL 체인을 노드로 감싸기 |
| `memory_using_sql_legacy.ipynb` | `SQLChatMessageHistory` + `RunnableWithMessageHistory` | [07_memory_using_sql_langgraph.ipynb](07_memory_using_sql_langgraph.ipynb) | `SqliteSaver` (영속 checkpointer) |

## 4. 변경된 것 vs 변경되지 않은 것

### 변경된 것

| legacy | LangGraph / LangChain v1 |
|---|---|
| `ConversationChain(llm, memory=...)` | `create_agent(model, checkpointer=...)` 또는 직접 만든 `StateGraph` |
| `memory.save_context(inputs, outputs)` | 자동 저장 (노드가 반환한 메시지) / 수동: `graph.update_state(config, {"messages": [...]})` |
| `memory.load_memory_variables({})` | `graph.get_state(config).values["messages"]` |
| 메모리 객체 1개 = 대화 1개 | `thread_id` 1개 = 대화 1개 (checkpointer 하나가 여러 대화 관리) |
| `session_id` / `ConfigurableFieldSpec` / `history_factory_config` | `config={"configurable": {"thread_id": ...}}`, 사용자 정보는 `context=` |
| `input_messages_key`, `history_messages_key`, `memory_key` | 불필요 — `state["messages"]` 하나로 통일 |
| 요약·잘라내기가 메모리 클래스 안에 숨어 있음 | 노드 / 미들웨어로 **명시적으로** 작성 |
| Entity·KG 메모리 전용 클래스 | 전용 클래스 없음 → Store + 구조화 출력으로 직접 구현 (또는 `langmem` 패키지) |

### 변경되지 않은 것 (그대로 사용)

* **메시지 타입**: `HumanMessage`, `AIMessage`, `SystemMessage` (`langchain_core.messages`)
* **프롬프트/LCEL**: `ChatPromptTemplate`, `MessagesPlaceholder`, `prompt | llm | parser` — 노드 안에서 그대로 호출
* **유틸 함수**: `trim_messages`, `get_buffer_string`, `RemoveMessage`
* **벡터스토어·리트리버**: `FAISS`, `vs.as_retriever()`
* **대화 기록 클래스**: `SQLChatMessageHistory`, `ChatMessageHistory` 는 deprecated 아님 (기존 데이터를 읽어 이관할 때 유용 — 07번 마지막 섹션)

> ⚠️ 단, `langchain_community` 패키지를 import 하면 `langchain-community is being sunset` 경고가 나옵니다. `FAISS`, `SQLChatMessageHistory` 가 여기에 속하므로, 새 코드에서는 LangGraph 의 checkpointer / Store 로 옮기는 편이 장기적으로 안전합니다.

## 5. 기능별 설명

### 5.1 ConversationBufferMemory → Checkpointer (01)

```python
def chatbot(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"])]}     # 이전 대화가 자동으로 state 에 있음

graph = (StateGraph(MessagesState)
         .add_node("chatbot", chatbot).add_edge(START, "chatbot")
         .compile(checkpointer=InMemorySaver()))

config = {"configurable": {"thread_id": "bank-1"}}
graph.invoke({"messages": [HumanMessage("...")]}, config)     # 새 메시지만 넣으면 됨
graph.get_state(config).values["messages"]                    # = load_memory_variables
get_buffer_string(messages)                                   # = return_messages=False 형식
```

`create_agent(model=llm, tools=[], checkpointer=InMemorySaver())` 를 쓰면 그래프를 만들지 않아도 됩니다.

### 5.2 ConversationBufferWindowMemory(k) → `trim_messages` / `RemoveMessage` (01)

* **보낼 때만 자르기** (state 는 전체 보존): `trim_messages(msgs, token_counter=len, max_tokens=2*k, strategy="last", start_on="human")`
  → `token_counter=len` 으로 하면 "토큰 수" 대신 "메시지 개수" 기준이 됩니다.
* **실제로 삭제**: `return {"messages": [RemoveMessage(id=m.id) for m in old]}`
* 실행 결과: 두 방식 모두 첫 턴의 이름을 잊고, state 에 남은 메시지는 A=8개 / B=4개.

### 5.3 ConversationTokenBufferMemory → `trim_messages(token_counter=llm)` (02)

```python
@before_model
def keep_last_150_tokens(state, runtime):
    trimmed = trim_messages(state["messages"], max_tokens=150, token_counter=llm,
                            strategy="last", start_on="human")
    return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *trimmed]}

agent = create_agent(model=llm, tools=[], middleware=[keep_last_150_tokens], checkpointer=InMemorySaver())
```

* 실행 결과: 352 토큰(12개) → 113 토큰(4개). 처음에 말한 모델 번호 `XG-200` 을 기억하지 못함 (legacy 와 같은 동작).
* 로컬 모델(Ollama 등)이라면 `token_counter=count_tokens_approximately` 사용.

### 5.4 ConversationSummaryMemory / SummaryBufferMemory → 요약 노드 / `SummarizationMiddleware` (03)

* **직접 구현**: `class State(MessagesState): summary: str` → 메시지가 일정 개수를 넘으면 `summarize` 노드에서 요약 갱신 + 오래된 원문 `RemoveMessage`.
  실행 결과: 원문 14개 → 2개만 남고, 이미 지워진 대화의 내용(예약금 500유로, 조식 포함)을 요약만으로 답함.
  주의: 요약에 정보가 남아 있어도 조건이 복잡한 질문(예: "출발 20일 전 취소 시")은 모델이 잘못 추론할 수 있습니다. 실제로 테스트 중 "50% 청구"라는 틀린 답이 나왔습니다(정답: 예약금만 환불 불가).
* **내장 미들웨어** (SummaryBuffer 에 해당):

```python
SummarizationMiddleware(model=llm, trigger=("tokens", 200), keep=("messages", 4))
```

  실행 결과: 16개 메시지 → 요약 1개 + 최근 원문 5개. 기본 요약 프롬프트가 영어이므로 한국어 요약은 `summary_prompt=` 로 지정.

### 5.5 ConversationEntityMemory / ConversationKGMemory → Store (04)

* 추출: `llm.with_structured_output(MemoryExtraction)` (Pydantic: `entities: list[Entity]`, `triples: list[Triple]`)
* 저장: `runtime.store.put(("entities", user_id), 개체명, {"summary": ...})`, `runtime.store.put(("kg", user_id), "주어|관계|목적어", {...})`
* 조회: `store.search(("entities", user_id))` (= legacy `entity_store.store`)
* 실행 결과: **새 thread** 에서도 "셜리는 디자이너, 테디와 동료" 라고 답함. 다른 `user_id` 는 모름.
* 노드에서 Store/사용자 정보 접근: `def node(state, runtime: Runtime[Context])` → `runtime.store`, `runtime.context.user_id`

### 5.6 VectorStoreRetrieverMemory → Store 시맨틱 검색 (05)

```python
store = InMemoryStore(index={"embed": OpenAIEmbeddings(model="text-embedding-3-small"), "dims": 1536, "fields": ["text"]})
store.put(("interview", "user-1"), "turn-0", {"text": "Human: ...\nAI: ..."})   # = save_context
store.search(("interview", "user-1"), query="면접자 전공은?", limit=1)        # = load_memory_variables({"prompt": ...})
```

실행 결과: "전공" 질문 → 자기소개 턴, "역할" 질문 → 백엔드 개발 턴을 정확히 검색.

### 5.7 LCEL + 메모리 → 체인을 노드로 감싸기 (06)

```python
def call_chain(state: MessagesState):
    *chat_history, last = state["messages"]
    return {"messages": [chain.invoke({"chat_history": chat_history, "input": last.content})]}
```

`RunnablePassthrough.assign(...) | itemgetter(...)` 연결 코드와 호출 후 `memory.save_context(...)` 가 모두 필요 없어집니다.

### 5.8 SQLChatMessageHistory + RunnableWithMessageHistory → SqliteSaver (07)

```python
conn = sqlite3.connect("langgraph_checkpoints.db", check_same_thread=False)
graph = builder.compile(checkpointer=SqliteSaver(conn))

config = {"configurable": {"thread_id": f"{user_id}:{conversation_id}"}}   # ConfigurableFieldSpec 2개 대체
```

* 연결을 닫고 다시 열어도 대화가 남아 있음 (재시작 시뮬레이션으로 확인).
* **legacy 에 없던 기능**: `graph.get_state_history(config)` 로 체크포인트 이력 조회(time-travel), `checkpointer.list(None)` 로 thread 목록 조회.
* 기존 `../legacy/sqlite.db` 의 대화를 `SQLChatMessageHistory` 로 읽어 `update_state` 로 이관하는 예제 포함.
* 운영 환경에서는 `PostgresSaver` (`langgraph-checkpoint-postgres`) 사용.

## 6. legacy 노트북에서 발견된 점

* `lcel_add_memory_legacy.ipynb`: `ValueError: variable chat_history should be a list of base messages, got {'chat_history': []}`
  → `| itemgetter("chat_history")` 를 뺀 `runnable` 로 체인을 만들어서 생긴 오류입니다. `load_memory_variables` 는 딕셔너리를 반환하므로 리스트만 꺼내야 합니다. LangGraph 방식에서는 이 연결 코드 자체가 사라집니다.
* `vector_store_retriever_memory_legacy.ipynb`: 저장된 출력에 `NameError: name 'embedding_size' is not defined` 가 남아 있습니다. (셀을 수정하기 전에 실행된 결과로 보임)

## 7. 실행 방법

```bash
# 이 폴더 예제에 추가로 필요한 패키지 (07번)
pip install langgraph-checkpoint-sqlite
```

* `OPENAI_API_KEY` 환경변수 필요 (`load_dotenv()` 로도 가능)
* 07번은 실행할 때 `langgraph_checkpoints.db` 를 새로 만듭니다 (`.gitignore` 의 `*.db` 로 커밋 제외).
* 모든 노트북은 서로 독립적이며 순서대로 실행하면 됩니다.
