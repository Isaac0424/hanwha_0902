# 20260916 — LangChain 출력 파서 실습

LLM 응답을 JSON, 리스트, Pydantic 객체 등으로 변환하는 출력 파서를 학습했습니다. 프롬프트로 출력 형식을 안내하는 방법과 `with_structured_output()`을 비교하고, 형식이 맞지 않는 응답을 전처리하거나 추가 LLM 호출로 복구했습니다.

노트북 코드와 저장된 실행 결과를 기준으로 정리한 학습 기록입니다.

## 파일 구성

| 파일 | 실습 내용 |
|---|---|
| [pydantic_output_parser_test.ipynb](pydantic_output_parser_test.ipynb) | 이메일 정보 추출, Pydantic 스키마, 구조화 출력 비교 |
| [josn_output_parser.ipynb](josn_output_parser.ipynb) | 설명과 해시태그를 JSON으로 추출 |
| [comma_separated_list_output_parser.ipynb](comma_separated_list_output_parser.ipynb) | 쉼표로 구분된 응답을 리스트로 변환 |
| [structured_output_parser.ipynb](structured_output_parser.ipynb) | `ResponseSchema`로 답변과 출처 필드 정의 |
| [pandas_data_frame_output_parser.ipynb](pandas_data_frame_output_parser.ipynb) | 타이타닉 데이터 조회·평균 계산·출력 전처리 |
| [date_enum_output_parser.ipynb](date_enum_output_parser.ipynb) | 날짜 형식 지정과 Enum 파싱 |
| [current_output_parser.ipynb](current_output_parser.ipynb) | 기존 파서 예제를 Pydantic + 구조화 출력으로 구현 |
| [OutputFixingParser.ipynb](OutputFixingParser.ipynb) | 잘못된 JSON 형식의 응답 복구 |
| [data/titanic.csv](data/titanic.csv) | Pandas 실습용 데이터 |

## 1. 출력 파서의 공통 흐름

출력 파서는 모델 응답을 후속 코드에서 다루기 쉬운 형태로 변환합니다. 스키마는 필요한 필드와 타입을 정의하며, 실습에서는 `BaseModel`과 `Field(description=...)`를 사용했습니다.

```python
parser = PydanticOutputParser(pydantic_object=EmailSummary)
prompt = prompt.partial(format=parser.get_format_instructions())
chain = prompt | llm | parser
```

- `get_format_instructions()`: 모델에 전달할 출력 형식 안내 생성
- `partial()` / `partial_variables`: 형식 안내를 프롬프트에 미리 주입
- `prompt | model | parser`: 프롬프트 생성 → 모델 호출 → 결과 변환
- `parser.parse(text)`: 이미 생성된 문자열을 직접 파싱
- `chain.invoke(...)`: 입력을 전달해 체인 실행

## 2. Pydantic으로 이메일 정보 추출

`EmailSummary`에 `person`, `email`, `subject`, `summary`, `date` 필드를 정의했습니다.

1. 일반 요약 응답을 스트리밍으로 확인했습니다.
2. 형식 안내를 추가하고, 모은 응답 문자열을 `parser.parse()`로 변환했습니다.
3. 체인 마지막에 파서를 연결해 `EmailSummary` 객체를 바로 반환받았습니다.
4. `with_structured_output(EmailSummary)`으로 같은 스키마를 사용하는 방법을 비교했습니다.

결과는 `response.person`처럼 속성으로 접근합니다. 이 예제의 `date`는 `str`이므로 날짜 타입을 검증하지 않습니다. 저장된 응답에는 원문에 없는 연도가 추가된 사례도 있어, 형식 검증과 내용의 정확성 확인은 구분해야 합니다.

## 3. JSON · 리스트 · 필드 기반 출력

| 파서 | 예제 | 저장된 결과 형태 |
|---|---|---|
| `JsonOutputParser` | 지구 온난화 설명과 해시태그 | `description`, `hashtags` 키를 가진 `dict` |
| `CommaSeparatedListOutputParser` | 대한민국 관광명소 5개 | 문자열 요소를 가진 `list` |
| `StructuredOutputParser` | 대한민국 수도와 출처 | `answer`, `source` 키를 가진 `dict` |

JSON 실습에서는 `Topic` 모델로 출력 스키마를 안내하고 `answer["description"]`으로 값을 꺼냈습니다. Pydantic 파서 예제처럼 모델 객체를 반환받는 방식과 결과 형태를 비교했습니다.

`StructuredOutputParser`와 `ResponseSchema`는 `langchain_classic.output_parsers`에서 가져와 사용했습니다. `source`는 모델이 생성한 문자열이며, 이 노트북에서 해당 웹페이지를 조회하거나 출처를 검증한 것은 아닙니다.

## 4. Pandas 조회와 출력 전처리

`PandasDataFrameOutputParser(dataframe=df)`에 타이타닉 데이터를 전달하고 자연어로 연산을 요청했습니다.

| 요청 | 저장된 실행 결과 |
|---|---|
| `Age` 열 조회 | 나이 데이터 반환 |
| 첫 번째 행 조회 | 인덱스 0의 승객 정보 반환 |
| 0~4행 나이 평균 | `31.2` — 직접 계산한 `df["Age"].head().mean()`과 일치 |
| 전체 `Fare` 평균 | 파서 결과 `22.19937` |

모델이 `column:Age`를 `"column:Age"`처럼 따옴표로 감싸 반환하는 문제가 있어, 파서 앞에 문자열 추출과 전처리를 추가했습니다.

```python
def clean_output(text: str) -> str:
    return text.strip().strip('"').strip("'")

chain = (
    prompt
    | model
    | StrOutputParser()
    | RunnableLambda(clean_output)
    | parser
)
```

조회 결과는 `format_parser_output()`에서 `to_dict()`로 바꿔 출력하고, 평균처럼 스칼라 값이 반환되면 `print(parser_output)`으로 확인했습니다. 마지막 `df["Fare"].mean()` 셀에는 저장된 출력이 없습니다.

## 5. 날짜와 Enum

- `DatetimeOutputParser`: `format = "%Y-%m-%d"`로 형식을 지정하고, 결과를 `strftime()`으로 출력했습니다. 저장된 예제 응답은 `1998-09-04`입니다.
- `EnumOutputParser`: `Colors`에 빨간색·초록색·파란색을 정의하고 하늘의 색을 질문해 `Colors.BLUE`를 반환받았습니다. `.value`로 `"파란색"`을 꺼냈습니다.

## 6. Pydantic + `with_structured_output()` 비교

`current_output_parser.ipynb`에서는 다음 대응 관계를 구현했습니다. 아래 표는 오늘 실습한 비교이며, 모든 출력 파서를 일괄 대체한다는 의미는 아닙니다.

| 기존 실습 | 비교한 구현 | 확인한 결과 |
|---|---|---|
| `ResponseSchema` + `StructuredOutputParser` | `Person` + `with_structured_output(Person)` | 이름 `김철수`, 나이 `25` |
| `DatetimeOutputParser` | `Schedule.start_time: datetime` | 일정과 `datetime` 객체 |
| `EnumOutputParser` | `TaskResult.priority: Priority` | 서버 장애를 `Priority.HIGH`로 분류 |
| Enum 단일 값 | `TaskResult_EXP`에 이유·신뢰도 필드 추가 | `priority`, `reason`, `confidence` 반환 |
| DataFrame 관련 처리 | `People.rows: list[Person]` → `model_dump()` → `pd.DataFrame()` | 이름·나이·점수 테이블 생성 |

DataFrame 비교 예제는 텍스트에서 행 데이터를 추출해 표를 만드는 실습입니다. 타이타닉 예제의 기존 데이터 조회·집계와는 작업 범위가 다릅니다.

## 7. `OutputFixingParser`로 오류 복구

`Actor` 스키마에 배우 이름과 영화 목록을 정의한 뒤, 작은따옴표가 포함된 문자열을 파싱했습니다.

```python
misformatted = "{'name':'Tom Hanks', 'film_names': ['Forrest Gump']}"
parser.parse(misformatted)  # OutputParserException 발생
```

JSON 형식에 맞지 않아 예외가 발생했습니다. 기존 파서를 `OutputFixingParser`로 감싸 추가 LLM 호출로 수정한 뒤 다시 파싱했습니다.

```python
new_parser = OutputFixingParser.from_llm(parser=parser, llm=ChatOpenAI())
actor = new_parser.parse(misformatted)
# Actor(name='Tom Hanks', film_names=['Forrest Gump'])
```

단순한 앞뒤 따옴표 문제는 전처리 함수로 처리했고, JSON 형식 오류는 LLM 기반 복구로 처리했습니다. 저장된 예제에서는 복구 후 `Actor` 객체를 반환받았습니다.

## 실행 환경과 참고 사항

- 주요 패키지: `langchain-core`, `langchain-openai`, `langchain-classic`, `langchain-teddynote`, `pydantic`, `pandas`, `python-dotenv`
- 대부분 `gpt-4o-mini`를 지정하며, 날짜·Enum·오류 복구 예제 일부는 모델명을 지정하지 않은 `ChatOpenAI()`를 사용합니다.
- `load_dotenv()`로 환경변수를 로드합니다. OpenAI 호출에는 `OPENAI_API_KEY`가 필요하며, LangSmith 추적에는 관련 환경 설정이 필요합니다.
- Pandas 노트북은 `./data/titanic.csv`를 읽으므로 작업 디렉터리를 `20260916`으로 맞춥니다.
- 오류 복구 노트북의 첫 `parser.parse()` 셀은 의도적으로 예외를 발생시킵니다. 전체 실행이 중단되면 뒤의 복구 셀을 별도로 실행해 결과를 확인합니다.
