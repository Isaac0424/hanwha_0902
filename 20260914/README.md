# 20260914 — LangChain & LangSmith 실습

LangChain, LangSmith 트레이싱, 그리고 로컬 로깅을 함께 사용해보는 실습 노트북입니다.

## 파일 구성

| 파일 | 설명 |
|---|---|
| [lang_smith_test.ipynb](lang_smith_test.ipynb) | 실습 메인 노트북 |
| [.env](.env) | API 키 등 환경변수 (git에는 커밋되지 않음, `.gitignore`로 제외) |
| [app.log](app.log) | 노트북 실행 중 `logging` 모듈로 기록된 로그 파일 |
| [images/LangSmith_Capture_image.png](images/LangSmith_Capture_image.png) | LangSmith 대시보드 트레이싱 결과 캡처 이미지 |

## 노트북 내용 ([lang_smith_test.ipynb](lang_smith_test.ipynb))

1. **환경 설정**: `python-dotenv`로 `.env`에 저장된 `OPENAI_API_KEY`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT` 로드
2. **기본 LLM 호출**: `ChatOpenAI`(`gpt-4o-mini`)로 간단한 질의응답
3. **에이전트 & 툴 사용**: `langchain.agents.create_agent`로 날씨 조회 툴(`get_weather`)을 연결한 에이전트 실행
4. **LangSmith 트레이싱**: `langchain_teddynote.logging.langsmith()`로 LangSmith 추적 활성화 (`langchain-study` 프로젝트)
5. **모델 응답 상세 정보**: `bind(logprobs=True)`로 로그 확률 등 응답 메타데이터 확인, 양자화/양자프로그래밍·그로버 알고리즘 질의 예제
6. **스트리밍 응답**: `llm.stream()`으로 토큰 단위 스트리밍 출력
7. **로컬 로깅 + 멀티모달**: Python `logging`으로 `app.log`에 실행 로그 기록, 이미지 URL을 포함한 멀티모달 프롬프트로 이미지 설명 요청

## 참고 사항

- `.env`에는 실제 API 키가 평문으로 들어 있습니다. 저장소에는 커밋되지 않지만, 파일을 공유하거나 캡처를 올릴 때 키 값이 노출되지 않도록 주의하세요.
- LangSmith 트레이싱 결과는 [images/LangSmith_Capture_image.png](images/LangSmith_Capture_image.png)에서 확인할 수 있습니다.
