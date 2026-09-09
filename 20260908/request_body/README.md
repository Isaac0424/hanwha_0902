# Request Body

FastAPI에서 클라이언트가 JSON 데이터를 요청 본문(Request Body)에 담아 보내는 방법을 정리한다.

## 파일 구성

- `main.py`: FastAPI 서버
- `requests_post.py`: `POST` 요청 예제
- `requests_put.py`: `PUT` 요청 예제

## 클라이언트 설치

Python에서 요청을 보내려면 `requests` 라이브러리를 설치한다.

```bash
pip install requests
```

## 서버 실행

`request_body` 폴더에서 다음 명령을 실행한다.

```bash
fastapi dev main.py
```

서버가 실행되면 기본 주소는 `http://127.0.0.1:8000`이다.

## 데이터 모델

```python
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
```

`Item` 모델은 Pydantic으로 요청 본문의 형식과 타입을 검증한다.

- `name`: 필수 문자열
- `description`: 선택 문자열
- `price`: 필수 숫자
- `tax`: 선택 숫자

## POST 요청

`POST /items/`는 상품 데이터를 전달받아 처리한다.

```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/items/",
    json={
        "name": "노트북",
        "price": 1500000,
        "tax": 50000,
    },
)

print(response.status_code)
print(response.json())
```

서버를 실행한 상태에서 다음 명령으로 요청을 보낸다.

```bash
python requests_post.py
```

예상 응답은 다음과 같다.

```json
{
  "name": "노트북",
  "description": null,
  "price": 1500000.0,
  "tax": 50000.0,
  "price_with_tax": 1550000.0
}
```

## PUT 요청

`PUT /items/{item_id}`는 경로 파라미터인 `item_id`와 요청 본문의 상품 데이터를 함께 받는다. `q`는 선택적인 쿼리 파라미터다.

```python
response = requests.put(
    "http://127.0.0.1:8000/items/1?q=update",
    json={"name": "노트북", "price": 1800000},
)
```

실행 방법은 다음과 같다.

```bash
python requests_put.py
```

응답은 다음과 같은 형태다.

```json
{
  "item_id": 1,
  "name": "노트북",
  "description": null,
  "price": 1800000.0,
  "tax": null,
  "q": "update"
}
```

## 요청을 보내는 위치

| 요청 방법 | 요청을 보내는 곳 | 응답을 확인하는 곳 |
|---|---|---|
| 브라우저 주소창에 URL 입력 | 주로 `GET` | 브라우저 화면 |
| Swagger UI에서 실행 | `GET`, `POST`, `PUT` 등 | Swagger UI의 Response body |
| `requests.get()` 또는 `requests.post()` 실행 | Python 코드 | `response` 객체 또는 터미널 |

`GET`과 `POST`의 차이는 HTTP 메서드와 요청 데이터의 전달 방식이다. 어떤 화면에서 응답을 보는지는 요청을 보낸 클라이언트에 따라 달라진다. Python에서 `GET`을 호출하면 응답은 브라우저가 아니라 Python의 `response` 객체에 저장된다.

```python
response = requests.get("http://127.0.0.1:8000/items/")
print(response.text)
```

반대로 브라우저에서 URL을 열면 브라우저가 `GET` 요청을 보내고 응답을 화면에 표시한다.

## `**` 딕셔너리 언패킹

`**`는 딕셔너리의 키와 값을 풀어서 다른 딕셔너리에 합칠 때 사용한다.

```python
data = {"name": "노트북", "price": 1500000.0}

result = {"item": data}
# {"item": {"name": "노트북", "price": 1500000.0}}

result = {"id": 1, **data}
# {"id": 1, "name": "노트북", "price": 1500000.0}
```

따라서 다음 코드에서:

```python
result = {"item_id": item_id, **item.model_dump()}
```

`item.model_dump()`의 필드들이 `result`에 펼쳐져 추가된다.

## 참고

요청 본문에 데이터를 담는다고 해서 데이터가 보안상 숨겨지는 것은 아니다. 민감한 데이터를 전송할 때는 HTTPS와 인증·인가를 함께 사용해야 한다.