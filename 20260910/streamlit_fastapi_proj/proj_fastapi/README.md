# FastAPI와 SQLite 요청 저장 예제

이 프로젝트는 Streamlit에서 입력한 이름과 나이를 FastAPI로 전달하고, FastAPI가 SQLite 데이터베이스에 저장하는 예제입니다.

## 전체 동작 흐름

```text
Streamlit 입력
    |
    | POST /predict
    | {"name": "홍길동", "age": 20}
    v
FastAPI의 predict()
    |
    | SQLite INSERT
    v
requests.db의 user_requests 테이블
    |
    v
request_id와 결과 메시지 반환
```

## 1. SQLite란?

SQLite는 별도의 데이터베이스 서버를 실행하지 않고 하나의 파일에 데이터를 저장하는 데이터베이스입니다.

이 코드가 실행되면 `main.py`와 같은 폴더에 다음 파일이 생성됩니다.

```text
requests.db
```

SQLite는 Python의 `sqlite3` 모듈로 사용할 수 있으므로 별도의 DB 서버나 설치 과정이 필요하지 않습니다. 작은 테스트나 학습용 프로젝트에 적합합니다.

## 2. 데이터베이스 구조

`init_db()` 함수는 다음 테이블을 만듭니다.

```sql
CREATE TABLE IF NOT EXISTS user_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL
)
```

| 열 | 설명 |
|---|---|
| `id` | 요청을 구분하는 고유 번호입니다. 자동으로 증가합니다. |
| `name` | 사용자 이름입니다. 문자열입니다. |
| `age` | 사용자 나이입니다. 정수입니다. |

- `PRIMARY KEY`: 각 데이터를 구분하는 대표 키입니다.
- `AUTOINCREMENT`: 새 데이터가 저장될 때 ID를 자동으로 증가시킵니다.
- `NOT NULL`: 비어 있는 값은 저장할 수 없습니다.
- `IF NOT EXISTS`: 테이블이 이미 있으면 다시 만들지 않습니다.

## 3. 서버 시작 생명주기

Uvicorn이 `main:app`을 실행하면 Python 파일이 위에서부터 실행됩니다.

```python
app = FastAPI()
DB_PATH = Path(__file__).with_name("requests.db")
```

- `FastAPI()`로 웹 애플리케이션을 만듭니다.
- `__file__`은 현재 `main.py`의 위치입니다.
- `DB_PATH`는 `requests.db`의 경로입니다.

그 다음 아래 코드가 실행됩니다.

```python
init_db()
```

`init_db()`는 DB 파일과 `user_requests` 테이블이 없으면 생성합니다. 이미 존재하면 기존 데이터를 유지합니다.

## 4. 요청 처리 생명주기

### 4-1. Streamlit에서 요청 전송

사용자가 이름과 나이를 입력하면 Streamlit은 다음과 같은 데이터를 만듭니다.

```python
payload = {
    "name": name,
    "age": age,
}
```

그리고 FastAPI에 `POST` 요청을 보냅니다.

```python
requests.post(
    "http://127.0.0.1:8000/predict",
    json=payload,
)
```

`payload`는 서버에 전달할 데이터 묶음이라는 뜻입니다.

### 4-2. FastAPI가 요청 검증

```python
class UserRequest(BaseModel):
    name: str
    age: int
```

FastAPI는 JSON을 `UserRequest` 형식으로 검증합니다.

- `name`이 없으면 오류가 발생합니다.
- `age`가 정수 형식이 아니면 오류가 발생합니다.
- 검증에 실패하면 함수가 실행되기 전에 `422` 응답을 반환합니다.

### 4-3. SQLite에 데이터 저장

```python
with sqlite3.connect(DB_PATH) as connection:
    cursor = connection.execute(
        "INSERT INTO user_requests (name, age) VALUES (?, ?)",
        (request.name, request.age),
    )
    request_id = cursor.lastrowid
```

동작 순서는 다음과 같습니다.

1. `sqlite3.connect(DB_PATH)`로 DB 파일에 연결합니다.
2. `connection`을 통해 SQL을 실행합니다.
3. `INSERT INTO`로 새 행을 추가합니다.
4. `?`에는 뒤의 `(request.name, request.age)` 값이 순서대로 들어갑니다.
5. `lastrowid`로 방금 저장된 행의 ID를 가져옵니다.
6. `with` 블록이 끝나면 연결이 닫힙니다.

`?`를 사용하는 매개변수 바인딩은 값을 SQL 문자열에 직접 이어 붙이는 것보다 안전하며 SQL injection을 예방하는 데 도움이 됩니다.

### 4-4. FastAPI가 응답 반환

```python
return {
    "request_id": request_id,
    "result_message": f"{request.name}님은 {request.age}세입니다.",
}
```

예를 들어 다음과 같은 JSON을 Streamlit에 반환합니다.

```json
{
  "request_id": 1,
  "result_message": "홍길동님은 20세입니다."
}
```

## 5. 함수 설명

### `init_db()`

앱 시작 시 DB와 테이블을 준비합니다. 데이터를 저장하는 함수가 아니라 저장 공간을 준비하는 함수입니다.

### `predict(request: UserRequest)`

```python
@app.post("/predict")
def predict(request: UserRequest):
```

`POST /predict` 요청을 처리합니다.

1. 요청 JSON을 `UserRequest`로 받습니다.
2. 이름과 나이를 SQLite에 저장합니다.
3. 저장된 ID를 가져옵니다.
4. 결과를 JSON으로 반환합니다.

### `get_requests()`

```python
@app.get("/requests")
def get_requests():
```

저장된 요청 목록을 조회합니다.

```sql
SELECT id, name, age
FROM user_requests
ORDER BY id DESC
```

- `SELECT`: 데이터를 조회합니다.
- `FROM`: 조회할 테이블을 지정합니다.
- `ORDER BY id DESC`: 최신 ID부터 정렬합니다.
- `fetchall()`: 조회 결과 전체를 가져옵니다.

조회 결과는 `sqlite3.Row`를 Python `dict`로 바꾼 뒤 JSON 배열로 반환합니다.

### `read_root()`

```python
@app.get("/")
def read_root():
    return {"Hello": "World"}
```

서버가 실행 중인지 확인하기 위한 기본 엔드포인트입니다. DB와는 직접 관계가 없습니다.

## 6. 실행 방법

FastAPI 폴더에서 실행합니다.

```powershell
uvicorn main:app --reload
```

프로젝트 루트에서 실행할 때는 다음과 같이 실행할 수 있습니다.

```powershell
uvicorn 20260910.streamlit_fastapi_proj.proj_fastapi.main:app --reload
```

Streamlit은 다른 터미널에서 실행합니다.

```powershell
streamlit run 20260910/streamlit_fastapi_proj/proj_streamlit/app.py
```

## 7. 저장 테스트

1. Streamlit 화면에서 이름과 나이를 입력합니다.
2. `백엔드로 전송` 버튼을 누릅니다.
3. `FastAPI 응답성공!`이 표시되는지 확인합니다.
4. `저장된 요청 ID`가 표시되는지 확인합니다.
5. 브라우저에서 다음 주소를 엽니다.

```text
http://localhost:8000/requests
```

예시 응답:

```json
[
  {
    "id": 1,
    "name": "홍길동",
    "age": 20
  }
]
```

`/predict`는 POST 전용이므로 브라우저 주소창에서 열면 안 됩니다. 주소창은 GET 요청을 보내기 때문에 `Method Not Allowed`가 나옵니다. 저장 결과 확인은 GET 방식인 `/requests`에서 합니다.

## 핵심 요약

```text
connect()  : DB에 연결
execute()  : SQL 실행
INSERT     : 데이터 저장
lastrowid  : 방금 저장한 ID 확인
SELECT     : 데이터 조회
fetchall() : 조회 결과 전체 가져오기
with       : 작업 후 DB 연결 정리
```
