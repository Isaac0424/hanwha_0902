# 20260911 실습 정리

## 1. 실습 주제

OpenAI와 Google Gemini 모델을 Python에서 직접 호출하고, LangChain의 Chat Model 인터페이스로 여러 모델의 응답과 토큰 사용량을 비교했다.

실습 파일:

- `ex_1.py`: OpenAI Responses API와 Google GenAI SDK 직접 호출
- `ex_langchain.ipynb`: LangChain으로 GPT와 Gemini 모델을 호출하고 응답 형식 및 토큰 사용량 비교
- `requirements.txt`: 기본 Python 패키지 목록

## 2. 환경 및 패키지 설치

노트북이 현재 사용 중인 Python 환경에 패키지를 설치하려면 `sys.executable`을 사용한다.

```python
import sys
print(sys.executable)
```

```python
!{sys.executable} -m pip install langchain-openai langchain-google-genai
```

`sys.executable`을 사용하면 터미널의 Python이 아니라 현재 Jupyter 커널이 사용하는 Python에 설치할 수 있다.

## 3. API 키 설정

API 키를 코드에 직접 작성하지 않고 환경변수로 설정한다.

```python
import os

openai_api_key = os.environ["OPENAI_API_KEY"]
google_api_key = os.environ["GOOGLE_API_KEY"]
```

환경변수가 없을 때는 다음처럼 오류를 명확하게 표시할 수 있다.

```python
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY가 설정되어 있지 않습니다.")
```

## 4. SDK로 직접 모델 호출하기

### OpenAI

```python
from openai import OpenAI

client = OpenAI()
response = client.responses.create(
    model="gpt-5-mini",
    input="파이썬의 장점 한 가지를 알려줘.",
)

print(response.output_text)
```

### Google Gemini

```python
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="사용 가능한 Gemini 모델명",
    contents="파이썬의 장점 한 가지를 알려줘.",
)

print(response.text)
```

사용 가능한 Gemini 모델은 계정과 API 버전에 따라 달라질 수 있으므로 호출 전에 목록을 확인한다.

```python
for model in client.models.list():
    actions = getattr(model, "supported_actions", [])
    if "generateContent" in actions:
        print(model.name, actions)
```

## 5. LangChain 모델 선언

```python
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

llm_gpt = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)

llm_gemini = ChatGoogleGenerativeAI(
    model="사용 가능한 Gemini 모델명",
    temperature=0,
)
```

모델명은 고정해서 추측하지 말고 `client.models.list()` 결과에서 `generateContent`를 지원하는 모델을 선택한다. 지원되지 않는 모델을 사용하면 `404 NOT_FOUND` 또는 `GoogleModelNotFoundError`가 발생한다.

일부 최신 모델은 sampling 기본값이 고정되어 `temperature`를 무시할 수 있다. 이 경우 경고가 표시되므로 해당 모델에서는 `temperature`를 지정하지 않는다.

```python
llm_gemini = ChatGoogleGenerativeAI(
    model="temperature를 지원하는 모델명",
)
```

## 6. 딕셔너리로 여러 모델 관리하기

모델을 딕셔너리에 넣으면 같은 질문을 여러 모델에 반복해서 보낼 수 있다.

```python
model_dict = {
    "llm_gpt": llm_gpt,
    "llm_gemini": llm_gemini,
}
```

딕셔너리의 key와 value를 함께 순회할 때는 `.items()`를 사용한다.

```python
question = "AI Agent를 공부할 때 가장 중요한 것은?"

for name, model in model_dict.items():
    response = model.invoke(question)
    print(name, response)
```

주요 순회 방법:

```python
for key in model_dict:
    print(key)

for model in model_dict.values():
    print(model)

for name, model in model_dict.items():
    print(name, model)
```

## 7. 응답 저장 및 딕셔너리 초기화

응답 하나를 모델 이름별로 저장할 때는 빈 딕셔너리를 사용한다.

```python
model_response_dict: dict[str, object] = {}

for name, model in model_dict.items():
    model_response_dict[name] = model.invoke(question)
```

모델별로 여러 응답을 리스트에 저장하려면 각 key를 빈 리스트로 초기화한다.

```python
model_response_dict: dict[str, list] = {
    name: []
    for name in model_dict
}

for name, model in model_dict.items():
    model_response_dict[name].append(model.invoke(question))
```

`model_response_dict[name].append(...)`를 사용하려면 해당 key에 리스트가 먼저 있어야 한다. 단순히 `dict()`만 호출한 상태에서는 key가 자동으로 만들어지지 않는다.

## 8. LangChain 응답 객체 확인

`model.invoke()`의 결과는 일반 문자열이 아니라 보통 `AIMessage` 객체다.

```python
response = llm_gpt.invoke(question)

print(type(response))
print(response.content)
```

일반적인 주요 필드는 다음과 같다.

```python
response.content          # 모델이 생성한 답변
response.usage_metadata   # 토큰 사용량
response.response_metadata # 모델별 추가 메타데이터
```

`response.text` 대신 `response.content`를 사용하는 이유는 LangChain의 표준 메시지 객체에서 실제 답변이 `content` 필드에 저장되기 때문이다.

## 9. GPT와 Gemini의 content 형식 차이

모델과 LangChain 버전에 따라 `response.content`가 문자열일 수도 있고, 텍스트 블록 리스트일 수도 있다.

```python
print(type(response.content))
print(response.content)
```

모델에 상관없이 텍스트만 출력하려면 다음처럼 정규화할 수 있다.

```python
def get_text(response) -> str:
    content = response.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, str):
                texts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                texts.append(block.get("text", ""))
        return "".join(texts)

    return str(content)

for name, response in model_response_dict.items():
    print(f"[{name}]")
    print(get_text(response))
```

## 10. 토큰 사용량 확인

`usage_metadata`가 없을 수 있으므로 빈 딕셔너리를 기본값으로 사용한다.

```python
usage = response.usage_metadata or {}

print("input tokens:", usage.get("input_tokens"))
print("output tokens:", usage.get("output_tokens"))
print("total tokens:", usage.get("total_tokens"))
print("reasoning tokens:", usage.get("reasoning_tokens", 0))
```

`or {}`는 왼쪽 값이 `None` 또는 빈 값이면 오른쪽의 빈 딕셔너리 `{}`를 사용한다는 뜻이다.

```python
value = None or {}
print(value)  # {}
```

`('reasoning_tokens', 0)`처럼 보이는 값은 key와 value로 이루어진 튜플이다. 해당 모델/API가 공개한 reasoning token 수가 0이라는 뜻이며, 모델의 모든 내부 추론이 없었다는 의미는 아니다.

## 11. 모델별 응답과 사용량 출력

```python
for name, response in model_response_dict.items():
    usage = response.usage_metadata or {}

    print("=" * 70)
    print(f"[{name}]")
    print(get_text(response))
    print("-" * 70)
    print("input tokens:", usage.get("input_tokens"))
    print("output tokens:", usage.get("output_tokens"))
    print("total tokens:", usage.get("total_tokens"))
    print("reasoning tokens:", usage.get("reasoning_tokens", 0))
```

## 12. temperature 실습에서 확인한 점

`temperature`는 답변의 무작위성과 다양성에 영향을 준다.

- 낮은 값: 비교적 일관되고 예측 가능한 답변
- 높은 값: 다양한 표현과 창의적인 답변
- 정답이 정해진 질문: temperature 차이가 작게 나타날 수 있음
- 창의적인 질문: temperature 차이가 더 뚜렷하게 나타날 수 있음
- 모델에 따라 허용 범위와 sampling 지원 여부가 다름

temperature를 바꾸면 답변 내용뿐 아니라 출력 토큰 수가 조금 달라질 수 있지만, 항상 증가한다고 단정할 수는 없다.

## 13. 자주 발생한 오류

### `NameError: name 'llm_gpt' is not defined`

모델 선언 셀이 실행되지 않았거나 커널이 재시작된 경우다. 노트북 셀을 위에서부터 순서대로 실행한다.

### `GoogleModelNotFoundError: 404 NOT_FOUND`

현재 API 버전이나 계정에서 해당 Gemini 모델을 지원하지 않는 경우다. 모델 목록을 조회한 뒤 `generateContent`를 지원하는 모델명을 사용한다.

### `AttributeError: 'AIMessage' object has no attribute 'reasoning_tokens'`

`reasoning_tokens`는 `AIMessage`의 직접 속성이 아니다. 다음처럼 `usage_metadata`에서 읽는다.

```python
usage = response.usage_metadata or {}
reasoning_tokens = usage.get("reasoning_tokens", 0)
```

### 출력이 `...`으로 생략되는 경우

노트북 출력 영역의 표시 제한일 수 있다. 필요한 값을 나누어 출력하거나 파일에 저장한다.

```python
from pathlib import Path

Path("model_output.txt").write_text(
    get_text(response),
    encoding="utf-8",
)
```

## 14. 전체 실습 예제

```python
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

question = "AI Agent를 공부할 때 가장 중요한 것은?"

model_dict = {
    "gpt": ChatOpenAI(model="gpt-4o-mini", temperature=0),
    "gemini": ChatGoogleGenerativeAI(model="사용 가능한 Gemini 모델명"),
}

model_response_dict = {
    name: model.invoke(question)
    for name, model in model_dict.items()
}

for name, response in model_response_dict.items():
    usage = response.usage_metadata or {}
    print(f"[{name}]\n{get_text(response)}")
    print("usage:", usage)
```

> Gemini 모델명과 temperature 지원 여부는 시간이 지나면서 달라질 수 있으므로, 실행 전 현재 API의 모델 목록과 공식 문서를 확인한다.
