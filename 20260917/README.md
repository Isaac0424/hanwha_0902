# 20260917 — LangChain 모델 활용 실습

LangChain에서 채팅 모델을 다루는 부가 기능을 학습했습니다. 응답 캐싱으로 같은 요청의 대기 시간을 줄이고, 체인을 직렬화해 파일로 저장·복원했습니다. 토큰 사용량과 비용을 콜백으로 확인하고, OpenAI 대신 Google Gemini 모델로 스트리밍·배치·멀티모달 호출을 실습했습니다.

노트북 코드와 저장된 실행 결과를 기준으로 정리한 학습 기록입니다.

## 파일 구성

| 파일 | 실습 내용 |
|---|---|
| [langchain_models.ipynb](langchain_models.ipynb) | `InMemoryCache`, `SQLiteCache`로 LLM 응답 캐싱 |
| [model_serialization.ipynb](model_serialization.ipynb) | `dumpd`/`dumps`로 체인 직렬화, pickle·JSON 저장 후 `load`로 복원 |
| [tocken_callback.ipynb](tocken_callback.ipynb) | `get_openai_callback()`으로 토큰 수와 비용 확인 |
| [google_generative_ai.ipynb](google_generative_ai.ipynb) | Gemini 스트리밍, 체인, 안전 설정, 배치, 이미지 기반 시 작성 |
| [cache/llm_cache.db](cache/llm_cache.db) | `SQLiteCache`가 생성한 캐시 DB |
| [data/fruit_chain.json](data/fruit_chain.json) · `data/fruit_chain.pkl` | 직렬화한 체인 파일 |
| [images/](images/) | 멀티모달 실습용 이미지 (`cross.png`, `isaac.png`) |

## 1. LLM 응답 캐싱

`"{country}에 대해서 200자 내외로 요약해줘."` 프롬프트와 `gpt-4o-mini`를 연결한 체인에 같은 입력(`한국`)을 반복 전달하고 `%%time`으로 시간을 비교했습니다.

```python
from langchain_core.globals import set_llm_cache
from langchain_core.caches import InMemoryCache

set_llm_cache(InMemoryCache())
```

| 단계 | Wall time | 비고 |
|---|---|---|
| 캐시 없이 호출 | 1.59 s | |
| `InMemoryCache` 설정 후 첫 호출 | 1.32 s | 캐시가 비어 있어 API 호출 |
| 같은 입력으로 재호출 | **7.39 ms** | 첫 호출과 동일한 응답을 캐시에서 반환 |
| `SQLiteCache` 설정 후 첫 호출 | 1.59 s | 새 캐시이므로 API 호출, 응답 내용도 새로 생성 |
| 같은 입력으로 재호출 | 시간 출력 미저장 | 직전과 동일한 응답 반환 |

- `InMemoryCache`: 프로세스 메모리에 저장하므로 커널을 재시작하면 사라집니다.
- `SQLiteCache(database_path="cache/llm_cache.db")`: 파일에 저장되어 커널을 재시작해도 유지됩니다.
- 캐시는 프롬프트와 모델 설정이 같을 때 적중합니다. 캐시된 응답이 반환되므로, 같은 질문에 새로운 답변이 필요하면 캐시를 끄거나 비워야 합니다.

## 2. 체인 직렬화와 복원

`"{fruit}의 색상이 무엇입니까?"` 프롬프트와 `ChatOpenAI(model="gpt-4o-mini", temperature=0)`로 만든 체인을 저장했습니다. `ChatOpenAI.is_lc_serializable()`과 `chain.is_lc_serializable()` 모두 `True`였습니다.

| 함수 | 반환 형태 | 용도 |
|---|---|---|
| `dumpd(chain)` | `dict` | pickle·JSON 파일로 저장 |
| `dumps(chain)` | `str` (JSON 문자열) | 문자열 그대로 저장·전송 |
| `load(obj)` | 복원된 Runnable | `dict`에서 객체 복원 |
| `loads(text)` | 복원된 Runnable | JSON 문자열에서 객체 복원 |

직렬화 결과는 `lc`, `type: "constructor"`, `id`(클래스 경로), `kwargs`(생성 인자)로 구성됩니다. API 키는 값 대신 `{"type": "secret", "id": ["OPENAI_API_KEY"]}` 형태로 기록되어 파일에 노출되지 않습니다.

```python
from langchain_core.load import dumpd, load

with open("data/fruit_chain.pkl", "wb") as f:
    pickle.dump(dumpd(chain), f)

with open("data/fruit_chain.pkl", "rb") as f:
    loaded_chain = pickle.load(f)

chain_from_file = load(loaded_chain, allowed_objects="all")
chain_from_file.invoke({"fruit": "사과"})
```

- `ChatOpenAI`처럼 `langchain_core` 밖(partner 패키지)의 클래스를 복원하려면 `allowed_objects`를 지정해야 했습니다. 신뢰할 수 없는 파일이라면 `"all"` 대신 필요한 클래스만 나열하는 편이 안전합니다.
- `secrets_map={"OPENAI_API_KEY": ...}`로 키를 직접 주입하거나, 생략하고 환경변수에서 읽도록 할 수 있습니다.
- pickle 파일과 JSON 파일 모두 복원 후 `invoke()`가 정상 동작해 사과 색상에 대한 `AIMessage`를 반환했습니다.
- `load`는 실행 시 `LangChainBetaWarning`(베타 API)을 출력합니다.

## 3. 토큰 사용량과 비용 확인

`langchain.callbacks`의 기존 경로 대신 `langchain_community.callbacks.manager`에서 `get_openai_callback`을 가져왔습니다. `with` 블록 안의 모든 호출이 합산됩니다.

```python
with get_openai_callback() as cb:
    result = llm.invoke("대한민국의 수도는 어디야?")
    print(cb)
```

| 실습 | 총 토큰 | 프롬프트 | 답변 | 비용 (USD) |
|---|---|---|---|---|
| 1회 호출 | 23 | 15 | 8 | 약 7.05e-06 |
| 같은 질문 2회 호출 | 46 | 30 | 16 | 약 1.41e-05 |

`cb.total_tokens`, `cb.prompt_tokens`, `cb.completion_tokens`, `cb.total_cost`로 개별 값을 꺼낼 수 있습니다. 2회 호출 결과는 1회의 정확히 두 배로 누적되었습니다.

> 저장된 출력에서는 비용 줄의 라벨이 `총 사용된 토큰수`로 찍혀 있습니다. 현재 코드는 `호출에 청구된 금액`으로 수정되어 있어, 다시 실행하면 라벨이 바뀝니다.

## 4. Google Gemini (`langchain_google_genai`)

`ChatGoogleGenerativeAI(model="gemini-3.5-flash")`를 사용했습니다. OpenAI 모델과 같은 Runnable 인터페이스(`stream`, `invoke`, `batch`, `|` 연결)로 호출합니다.

### 응답 형태 차이

Gemini 응답의 `content`는 문자열이 아니라 `[{'type': 'text', 'text': ..., 'index': 0}]` 형태의 콘텐츠 블록 리스트입니다. 첫 스트리밍 셀에서 `token.content`를 출력하자 딕셔너리 리스트가 그대로 찍혔습니다.

| 텍스트를 꺼내는 방법 | 사용한 곳 |
|---|---|
| `token.text` / `res.text` | 스트리밍 누적, 배치 결과 출력 |
| `answer.content[0]["text"]` | `prompt \| model` 체인의 `invoke` 결과 |
| 체인 끝에 `StrOutputParser()` 연결 | `"프롬프트 캐싱"` N행시 스트리밍 |

### 안전 설정과 배치

`safety_settings`로 성적 콘텐츠·혐오 발언·괴롭힘·위험 콘텐츠 카테고리의 차단 임계값을 `HarmBlockThreshold.BLOCK_NONE`으로 지정했습니다. 이 모델로 `llm.batch([...])`에 질문 두 개를 전달해 수도(`서울`)와 주요 관광지 5곳을 한 번에 받았습니다.

### 멀티모달

`langchain_teddynote.models.MultiModal`에 Gemini 모델과 시스템·사용자 프롬프트("시인"으로서 이미지에 대한 시 작성)를 전달했습니다.

```python
multimodal_gemini = MultiModal(llm, system_prompt=system_prompt, user_prompt=user_prompt)
answer = multimodal_gemini.stream("images/cross.png")
for token in answer:
    print(token.text)
```

`cross.png`로는 이미지 표시 후 「침묵의 온기」라는 시가 생성되었습니다. 토큰마다 `print()`로 줄을 바꿔 출력해 단어 중간에서 줄이 끊겨 보입니다. `isaac.png` 셀은 저장된 출력이 없습니다.

## 실행 환경과 참고 사항

- 주요 패키지: `langchain-core`, `langchain-openai`, `langchain-community`, `langchain-google-genai`, `langchain-teddynote`, `python-dotenv`
- `load_dotenv()`로 환경변수를 로드합니다. OpenAI 호출에는 `OPENAI_API_KEY`, Gemini 호출에는 `GOOGLE_API_KEY`가 필요하며, LangSmith 추적에는 관련 환경 설정이 필요합니다.
- 캐시 DB, 직렬화 파일, 이미지를 상대 경로로 읽고 쓰므로 작업 디렉터리를 `20260917`로 맞춥니다.
- `set_llm_cache()`는 전역 설정입니다. 캐시 노트북을 실행한 커널에서 다른 실습을 이어 하면 캐시된 응답이 반환될 수 있습니다.
