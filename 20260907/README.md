# 2026-09-07 학습 기록

### 오늘 작성·수정한 내용

- `pydantic_ex.py`: `User` 모델로 데이터 타입 변환과 검증 오류 처리 예제 작성.
- `pydantic_ex2.py`: `Fruit` 모델의 값 제한과 `Meeting` 모델의 직렬화 옵션 비교 예제 작성.
- `pydantic_ex.ipynb`: 예제 코드와 실행 결과를 노트북에 정리.

### 학습 내용

- `BaseModel`과 타입 힌트로 데이터 구조를 정의하고, `**딕셔너리`로 값을 전달한다.
- 문자열을 `int`, `datetime` 등으로 자동 변환하며, `PositiveInt`로 양수 조건을 지정한다.
- `ValidationError.errors()`로 잘못된 타입과 필수 필드 누락을 확인하고, `try/except/else/finally`의 실행 흐름을 학습했다.
- `datetime | None`은 `None`을 허용하지만, 기본값이 없으면 필드를 생략할 수 없다.
- `Literal`로 허용 값을 제한하고, `Annotated[float, Gt(0)]`로 0보다 큰 값 조건을 지정한다.
- `model_dump()`는 딕셔너리, `model_dump_json()`은 JSON 문자열을 반환한다. `mode='json'`은 JSON에 맞게 값을 변환하되 딕셔너리를 반환한다.
- 직렬화 시 `exclude_unset`은 미입력 필드, `exclude`는 지정 필드, `exclude_defaults`는 기본값과 같은 값을 제외한다.

### 실행 방법

Pydantic이 설치된 환경에서 `20260907` 폴더로 이동한 뒤 실행한다.

```bash
python pydantic_ex.py
python pydantic_ex2.py
```

`Fruit` 예제를 실행하려면 `pydantic_ex2.py`의 `testTypeHint()` 호출 주석을 해제한다.
