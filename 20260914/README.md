# 20260914 — LangChain & LangSmith 실습

LangChain, LangSmith 트레이싱, 로컬 로깅, 그리고 LCEL의 Runnable 계열(`RunnableParallel` / `RunnablePassthrough` / `RunnableLambda`)을 다루는 실습 노트북 모음입니다.

## 파일 구성

| 파일 | 설명 |
|---|---|
| [lang_smith_test.ipynb](lang_smith_test.ipynb) | LangSmith 트레이싱 · 로깅 · 멀티모달 실습 노트북 |
| [langsmith_runnable_test.ipynb](langsmith_runnable_test.ipynb) | LCEL Runnable(`RunnableParallel`/`RunnablePassthrough`/`RunnableLambda`) 실습 노트북 |
| [runnablepassthrough사용이유.md](runnablepassthrough사용이유.md) | `RunnablePassthrough`의 동작 원리와 사용 이유 정리 |
| [.env](.env) | API 키 등 환경변수 (git에는 커밋되지 않음, `.gitignore`로 제외) |
| [app.log](app.log) | 노트북 실행 중 `logging` 모듈로 기록된 로그 파일 |
| [images/LangSmith_Capture_image.png](images/LangSmith_Capture_image.png) | LangSmith 대시보드 트레이싱 결과 캡처 이미지 |

## 1. lang_smith_test.ipynb

1. **환경 설정**: `python-dotenv`로 `.env`에 저장된 `OPENAI_API_KEY`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT` 로드
2. **기본 LLM 호출**: `ChatOpenAI`(`gpt-4o-mini`)로 간단한 질의응답
3. **에이전트 & 툴 사용**: `langchain.agents.create_agent`로 날씨 조회 툴(`get_weather`)을 연결한 에이전트 실행
4. **LangSmith 트레이싱**: `langchain_teddynote.logging.langsmith()`로 LangSmith 추적 활성화 (`langchain-study` 프로젝트)
5. **모델 응답 상세 정보**: `bind(logprobs=True)`로 로그 확률 등 응답 메타데이터 확인, 양자화/양자프로그래밍·그로버 알고리즘 질의 예제
6. **스트리밍 응답**: `llm.stream()`으로 토큰 단위 스트리밍 출력
7. **로컬 로깅 + 멀티모달**: Python `logging`으로 `app.log`에 실행 로그 기록, 이미지 URL을 포함한 멀티모달 프롬프트로 이미지 설명 요청

## 2. langsmith_runnable_test.ipynb — 함수별 정리

### 2.1 체인 기본 구성 요소

| 함수/클래스 | 역할 |
|---|---|
| `PromptTemplate.from_template("{country}...")` | 문자열 템플릿에 변수를 채워 프롬프트 생성 |
| `ChatOpenAI(model=..., max_completion_tokens=...)` | OpenAI 챗 모델 래퍼. `.bind(logprobs=True)`로 토큰별 로그확률 반환 옵션 추가 |
| `StrOutputParser()` | 모델의 `AIMessage` 응답에서 `content`(문자열)만 추출 |
| `prompt \| model \| parser` | `\|` 연산자로 Runnable들을 순차 파이프라인(체인)으로 연결 |
| `.invoke()` / `.batch()` | `.invoke()`는 단일 입력 실행, `.batch()`는 여러 입력을 리스트로 한 번에 실행 |

### 2.2 병렬 실행 — `RunnableParallel`

| 함수/클래스 | 역할 |
|---|---|
| `RunnableParallel(capital=chain_1, area=chain_2)` | 동일 입력을 여러 체인에 동시에 넣고, 각 결과를 key별 dict로 모아 반환 (`{"capital": ..., "area": ...}`) |
| `{"key": runnable}` (dict 자동 변환) | LCEL 파이프에 dict를 넣으면 내부적으로 `RunnableParallel`로 자동 변환(coerce)됨 |

### 2.3 입력 보존 — `RunnablePassthrough`

| 함수/클래스 | 역할 |
|---|---|
| `RunnablePassthrough()` | 입력을 변형 없이 그대로 다음 단계로 전달하는 항등(identity) Runnable. 병렬 체인에서 원본 입력(예: RAG의 `question`)을 잃지 않고 유지할 때 사용 |
| `RunnablePassthrough.assign(new_key=lambda x: ...)` | 입력이 dict일 때, 원본 dict를 유지한 채 새로 계산한 필드를 병합(merge)해서 반환. 입력이 dict가 아니면 에러 발생(`b9ee2757` 셀에서 확인) |

상세 원리는 [runnablepassthrough사용이유.md](runnablepassthrough사용이유.md) 참고.

### 2.4 임의 함수를 체인에 삽입 — `RunnableLambda`

| 함수/클래스 | 역할 |
|---|---|
| `get_today(a)` | 오늘 날짜를 `"Sep-14"` 형식 문자열로 반환하는 사용자 정의 함수. `RunnableLambda`가 인자를 하나 넘겨주므로 더미 매개변수(`a` 또는 관례상 `_`)가 필요 |
| `RunnableLambda(get_today)` | 일반 파이썬 함수를 Runnable로 감싸 체인 파이프라인(`\|`)에 끼워 넣을 수 있게 함 |
| `length_function(text)` | 문자열 길이를 반환하는 단순 함수 |
| `_multiple_length_function(text_1, text_2)` | 두 문자열 길이를 곱한 값을 반환 |
| `multiple_length_function(_dict)` | dict에서 `text_1`, `text_2`를 꺼내 `_multiple_length_function`에 전달하는 래퍼. `RunnableLambda`는 인자를 1개만 받을 수 있어 dict로 묶어 전달하는 패턴 |
| `itemgetter("word_1")` | `operator` 모듈 함수. dict/시퀀스에서 특정 key 값만 뽑아내는 Runnable로 동작 (`itemgetter("word_1") \| RunnableLambda(length_function)`처럼 파이프 가능) |

### 2.5 핵심 흐름 요약

`PromptTemplate → ChatOpenAI → StrOutputParser`로 기본 체인을 만들고, `RunnableParallel`로 여러 체인을 동시 실행하며, `RunnablePassthrough`(원본 입력 보존)와 `RunnableLambda`(임의 함수 삽입)를 조합해 복잡한 데이터 흐름(날짜 계산 → 프롬프트 주입, 두 단어 길이 곱셈 등)을 LCEL 파이프라인 안에서 처리하는 패턴을 학습했습니다.

## 참고 사항

- `.env`에는 실제 API 키가 평문으로 들어 있습니다. 저장소에는 커밋되지 않지만, 파일을 공유하거나 캡처를 올릴 때 키 값이 노출되지 않도록 주의하세요.
- LangSmith 트레이싱 결과는 [images/LangSmith_Capture_image.png](images/LangSmith_Capture_image.png)에서 확인할 수 있습니다.
