# FastAPI CRUD 예제

이 디렉토리는 `dict`를 임시 데이터베이스처럼 사용해 FastAPI의 CRUD 흐름을 연습하는 예제다.

## 실행

프로젝트 루트 또는 이 디렉토리에서 실행한다.

```bash
uvicorn main:app --reload
```

실행 후 Swagger UI에서 확인한다.

```text
http://127.0.0.1:8000/docs
```

## 데이터 모델

```python
class ItemSchema(BaseModel):
    name: str
    price: float
    description: str | None = None
```

- `name`: 필수 문자열
- `price`: 필수 실수
- `description`: 선택 문자열

## 인메모리 저장소

```python
items_db: dict[int, dict] = {}
id_counter = 1
```

실제 DB 대신 Python 딕셔너리에 데이터를 저장한다. 서버를 재시작하면 데이터와 `id_counter`가 초기화된다.

## CRUD API

### Create: 생성

```http
POST /items/
```

요청 본문:

```json
{
  "name": "노트북",
  "price": 1500000,
  "description": "개발용 노트북"
}
```

`model_dump()`로 Pydantic 모델을 딕셔너리로 바꾼 뒤 ID를 추가하고 저장한다. 생성 성공 상태 코드는 `201`이다.

### Read: 조회

전체 조회:

```http
GET /items/
```

단일 조회:

```http
GET /items/1
```

존재하지 않는 ID를 조회하면 `HTTPException(status_code=404)`를 발생시킨다.

### Update: 전체 수정

```http
PUT /items/1
```

수정할 전체 데이터를 요청 본문으로 보낸다. 현재 예제는 전달받은 모델로 기존 데이터를 통째로 교체한다.

### Delete: 삭제

```http
DELETE /items/1
```

`dict.pop()`으로 데이터를 삭제하고 삭제된 데이터를 반환한다. 존재하지 않는 ID는 `404 Not Found`다.

## HTTP 메서드와 FastAPI

FastAPI 내부에서는 POST, GET, PUT, DELETE 모두 다음 흐름으로 처리된다.

```text
HTTP 메서드와 URL에 맞는 라우트 탐색
→ Path와 Request Body 검증
→ 함수 실행
→ 반환값을 JSON 응답으로 변환
```

POST, PUT, DELETE의 의미는 FastAPI가 자동으로 구현해 주는 것이 아니라 API 설계 약속이다.

- `POST`: 새 리소스 생성
- `GET`: 리소스 조회
- `PUT`: 특정 리소스 전체 수정
- `DELETE`: 특정 리소스 삭제

## 예외 처리

```python
if item_id not in items_db:
    raise HTTPException(
        status_code=404,
        detail="아이템을 찾을 수 없습니다.",
    )
```

요청 데이터가 Pydantic 모델을 통과하지 못하면 FastAPI가 자동으로 `422 Unprocessable Entity`를 반환한다. ID가 없으면 코드에서 직접 `404 Not Found`를 반환한다.

## 실무로 확장할 때

이 예제의 `items_db`는 학습용이다. 실무에서는 데이터베이스와 ORM을 사용하고, `id_counter` 대신 DB의 자동 증가 또는 UUID를 사용한다. 또한 요청 스키마, DB 모델, 응답 스키마를 분리하는 편이 유지보수에 유리하다.