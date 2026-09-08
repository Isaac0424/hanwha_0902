# FastAPI 기초

오늘은 FastAPI에서 요청을 받는 기본적인 방법을 정리한다.

- `path_parameters/`: 경로 파라미터
- `query_prameters/`: 쿼리 파라미터
- `request_body/`: 요청 본문

## 1. 설치

```bash
pip install "fastapi[standard]"
```

`fastapi[standard]`를 설치하면 FastAPI와 함께 개발 서버 실행에 필요한 Uvicorn도 설치된다.

## 2. 서버 실행

```bash
# FastAPI 개발 서버 실행
fastapi dev main.py

# Uvicorn으로 실행
uvicorn main:app --reload
```

명령어의 구성은 다음과 같다.

| 항목 | 설명 |
|---|---|
| `main` | 파일명. `main.py`에서 `.py`를 제외한 부분 |
| `app` | FastAPI 인스턴스 변수명. 예: `app = FastAPI()` |
| `--reload` | 코드가 변경될 때 서버를 자동으로 재시작하는 개발용 옵션 |
| `--host 0.0.0.0` | 외부에서도 접속할 수 있도록 서버 주소를 설정 |
| `--port 8000` | 서버 포트 지정. 기본값은 `8000` |

예를 들어 파일명이 `main.py`이고 인스턴스 이름이 `app`이면 `uvicorn main:app --reload`로 실행한다.

## 3. API 문서 확인

서버를 실행한 뒤 아래 주소로 접속한다.

<http://localhost:8000/docs>

FastAPI는 작성된 API를 바탕으로 Swagger UI 문서를 자동 생성한다. Swagger UI에서 각 API의 요청을 직접 보내고 응답을 확인할 수 있어 개발과 테스트에 유용하다.

FastAPI는 Pydantic을 내부적으로 사용하므로 요청 데이터의 타입과 형식을 자동으로 검증하고, 검증 결과를 API 문서에도 반영한다.

## 4. API 설계 순서

API를 구현하기 전에 다음 내용을 먼저 정리하면 개발 중 혼선을 줄일 수 있다.

1. 어떤 리소스를 다룰지 결정한다.
2. HTTP 메서드와 URL을 설계한다.
3. 경로 파라미터, 쿼리 파라미터, 요청 본문을 구분한다.
4. 요청과 응답의 데이터 형식을 문서로 작성한다.
5. API를 구현하고 Swagger UI에서 테스트한다.

## 5. 요청 데이터의 위치

### 경로 파라미터

URL 경로에 포함되는 값이다.

```text
/users/10
```

위 URL에서 `10`이 사용자 식별자를 나타내는 경로 파라미터다.

### 쿼리 파라미터

URL에서 경로 뒤의 `?`로 시작하는 값이다. 각 값은 `key=value` 형태로 작성하며, 여러 값은 `&`로 구분한다.

```text
/users?page=1&limit=10
```

위 예시의 `page=1`과 `limit=10`이 쿼리 파라미터다.

### 요청 본문

클라이언트가 서버로 보내는 데이터를 요청 본문에 담는 방식이다. JSON 데이터를 보내는 `POST`, `PUT`, `PATCH` 요청에서 자주 사용한다.

```json
{
  "name": "Daeyoung"
}
```

쿼리 파라미터는 URL에 표시되므로 검색·필터·페이지 번호 등에 적합하다. 요청 본문은 데이터 구조를 담기 좋으며, URL에 직접 표시되지 않는다. 단, 데이터를 숨기기 위한 목적이라면 HTTPS와 적절한 인증·인가를 함께 사용해야 한다.

## 6. HTTP 메서드 비교

| Method | 주 용도 | 서버 데이터 변경 | Idempotent | Body | FastAPI 중요도 |
|---|---|:---:|:---:|:---:|:---:|
| `GET` | 조회 | ❌ | ✅ | 보통 ❌ | ★★★★★ |
| `POST` | 생성 / 작업 실행 | ✅ | ❌ | ✅ | ★★★★★ |
| `PUT` | 전체 수정 / 교체 | ✅ | ✅ | ✅ | ★★★★☆ |
| `PATCH` | 일부 수정 | ✅ | 설계에 따라 다름 | ✅ | ★★★★★ |
| `DELETE` | 삭제 | ✅ | ✅ | 보통 ❌ | ★★★★☆ |
| `HEAD` | GET의 헤더만 조회 | ❌ | ✅ | ❌ | ★★☆☆☆ |
| `OPTIONS` | 지원 메서드 / CORS 확인 | ❌ | ✅ | 보통 ❌ | ★★★☆☆ |
| `TRACE` | 요청 경로 진단 | ❌ | ✅ | ❌ | ★☆☆☆☆ |

### 핵심 정리

- **GET**: 데이터를 조회할 때 사용
- **POST**: 새로운 리소스를 생성하거나 작업을 실행할 때 사용
- **PUT**: 리소스 전체를 교체하거나 수정할 때 사용
- **PATCH**: 리소스의 일부 필드만 수정할 때 사용
- **DELETE**: 리소스를 삭제할 때 사용
- **HEAD**: GET과 유사하지만 Response Body 없이 헤더만 확인
- **OPTIONS**: 서버가 지원하는 HTTP Method 확인, CORS Preflight에서 자주 사용
- **TRACE**: 요청 경로 진단용. 일반적인 REST API에서는 거의 사용하지 않음

## 7. 멱등성(Idempotent)

같은 요청을 여러 번 보내더라도 **최종 서버 상태가 동일한 성질**을 멱등성이라고 한다.

예:

```http
PUT /users/10

{
  "name": "Daeyoung"
}
```

위 요청을 여러 번 보내더라도 최종적으로 `name = Daeyoung`이라는 서버 상태는 같다.

반면:

```http
POST /orders
```

를 여러 번 보내면 주문이 여러 개 생성될 수 있으므로 일반적으로 멱등적이지 않다.
