# FastAPI 요청 본문과 데이터 검증

## 학습 내용

### 1. Pydantic 모델로 요청 본문 정의

FastAPI에서는 `BaseModel`을 상속한 클래스로 JSON 요청 본문의 구조와 검증 규칙을 선언한다.

```python
class UserInformation(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3)]
    age: int = Field(ge=0)
    phone_number: str | None = Field(
        default=None,
        pattern=PHONE_NUMBER_PATTERN,
    )
```

- `StringConstraints(strip_whitespace=True)`: 이름 앞뒤 공백 제거
- `min_length=3`: 이름 길이 제한
- `Field(ge=0)`: 나이가 0 이상인지 검증
- `Field(pattern=...)`: 문자열이 정규식 패턴과 일치하는지 검증
- 검증 실패 시 FastAPI가 자동으로 `422 Unprocessable Entity`를 반환

> 나이를 양수만 허용하려면 `Field(gt=0)`을 사용한다. `ge=0`은 0을 허용한다.

### 2. 전화번호 검증과 정규화

하이픈이 있거나 없어도 입력받되, 응답 또는 저장 시 하이픈 형식으로 통일할 수 있다.

```python
PHONE_NUMBER_PATTERN = r"^(01[016789])-?(\d{3,4})-?(\d{4})$"
```

```text
01012341234   -> 010-1234-1234
010-1234-1234 -> 010-1234-1234
```

`Field(pattern=...)`는 형식 검증만 담당한다. 실제 변환은 `normalize_phone_number()`처럼 별도 함수에서 처리한다.

### 3. PUT 요청

```python
@app.put("/update/")
async def update_user_inform(user: UserInformation):
    ...
```

Python의 `requests`로 JSON 본문을 보낼 때는 `json=`을 사용한다.

```python
requests.put(
    "http://127.0.0.1:8000/update/",
    json={
        "name": "isaac",
        "age": 31,
        "phone_number": "01012341234",
    },
)
```

## 오늘 발생한 실수와 해결

### 1. 정규식 마지막 숫자 부분 오타

잘못된 패턴:

```python
r"^01[016789]-?\d{3,4}-?{4}$"
```

`{4}` 앞에 숫자 패턴인 `\d`가 빠져 있었다. 따라서 다음처럼 작성해야 한다.

```python
r"^01[016789]-?\d{3,4}-?\d{4}$"
```

### 2. `Annotated` 사용법 오류

잘못된 형태:

```python
phone_number: Annotated(str | None)
```

`Annotated`는 타입과 메타데이터를 대괄호로 묶어야 한다.

```python
phone_number: Annotated[
    str | None,
    Field(pattern=PHONE_NUMBER_PATTERN),
] = None
```

Pydantic 모델에서는 다음처럼 `Field`를 타입 선언에 직접 사용할 수도 있다.

```python
phone_number: str | None = Field(
    default=None,
    pattern=PHONE_NUMBER_PATTERN,
)
```

### 3. 405 Method Not Allowed

요청 코드가 다음과 같았다.

```python
requests.post("http://127.0.0.1:8000/items/", json=data)
```

하지만 `/items/`는 `@app.get("/items/")`로 선언되어 있어 PUT을 받을 수 없다. PUT 요청은 PUT 라우트인 `/update/`로 보내야 한다.

```text
PUT /items/  -> 405
PUT /update/ -> 정상 처리
```

`405`는 URL은 존재하지만 해당 HTTP 메서드를 허용하지 않는다는 의미다.

### 4. 307 Temporary Redirect와 trailing slash

```text
GET /update  -> 307 Temporary Redirect
GET /update/ -> 405 Method Not Allowed
```

라우트가 `/update/`로 선언되어 있는데 `/update`로 요청해서 슬래시가 붙은 주소로 리다이렉트된 것이다. 또한 해당 라우트는 GET이 아니라 PUT 전용이므로, 주소뿐 아니라 메서드도 맞춰야 한다.

```python
requests.put("http://127.0.0.1:8000/update/", json=data)
```

### 5. 422 Unprocessable Entity

`422`는 서버가 살아 있지만 요청 데이터가 선언한 검증 규칙을 통과하지 못했다는 뜻이다.

확인할 항목:

- JSON 필드 이름이 모델 필드와 같은가?
- `name`의 길이가 최소 길이 이상인가?
- `age`가 `ge=0` 조건을 만족하는가?
- `phone_number`가 정규식에 맞는가?
- 요청 본문을 `data=`가 아니라 `json=`으로 보냈는가?

## 상태 코드 구분

| 상태 코드 | 의미 | 오늘의 사례 |
|---|---|---|
| `200` | 요청 성공 | 정상적인 PUT 응답 |
| `307` | 다른 URL로 임시 리다이렉트 | `/update` -> `/update/` |
| `405` | HTTP 메서드가 허용되지 않음 | PUT `/items/`, GET `/update/` |
| `422` | 요청 데이터 검증 실패 | 잘못된 전화번호, 이름, 나이 |

## 요청 전 체크리스트

1. URL 경로가 라우트 선언과 정확히 같은가?
2. HTTP 메서드가 `@app.get`, `@app.put`와 일치하는가?
3. trailing slash(`/`)를 일관되게 사용했는가?
4. JSON 요청은 `json=`으로 보냈는가?
5. 모델의 필드명과 요청 JSON의 키가 같은가?
6. `Field`, `Query`, 정규식 검증 조건을 만족하는가?
7. `/docs`에서 요청을 먼저 테스트했는가?

## 오늘의 최종 실습 구조

### `main.py`

`UserInformation` Pydantic 모델로 사용자 입력을 검증한다.

- `name`: 앞뒤 공백을 제거하고 3글자 이상인지 확인
- `age`: 0 이상인지 확인
- `phone_number`: 하이픈 유무를 허용하는 정규식으로 확인
- `normalize_phone_number()`: 응답 또는 저장 전에 `010-1234-5678` 형식으로 통일
- `user_db`: 학습용 인메모리 사용자 저장소

주요 엔드포인트:

| Method | URL | 역할 |
|---|---|---|
| `GET` | `/user/` | 쿼리 매개변수 예제 |
| `GET` | `/user/{name_id}` | 경로·쿼리 매개변수 예제 |
| `PUT` | `/update/` | 사용자 정보를 검증하고 저장 |
| `DELETE` | `/user-db/{user_id}` | 사용자 삭제 |

### `request.py`

서버 API를 단계별로 호출하는 CLI 클라이언트다.

1. `put` 또는 `delete` 선택
2. 기본값 사용 여부 선택
3. 직접 입력하는 경우 이름, 나이, 전화번호 입력
4. DELETE인 경우 사용자 ID 입력
5. 응답 출력 여부 선택

실행:

```bash
python request.py
```

Enter만 입력하면 기본값을 사용한다. 전화번호를 비워 두면 Python의 `None`이 JSON의 `null`로 전송된다.

## 실수에서 배운 점

- Python에서는 JSON의 `NULL`이 아니라 `None`을 사용한다.
- 요청 클라이언트의 URL과 서버의 HTTP 메서드가 정확히 일치해야 한다.
- `/update`와 `/update/`처럼 trailing slash를 일관되게 사용한다.
- `item`으로 시작한 예제를 `UserInformation`으로 바꿀 때 변수명, URL, 응답 key도 함께 사용자 기준으로 통일해야 한다.
- 인메모리 DB는 서버를 재시작하면 초기화되므로 실제 영속 저장소가 아니다.
