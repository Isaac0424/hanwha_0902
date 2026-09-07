# 12. 객체의 속성을 읽어 응답 모델 만들기

[전체 안내](../../README.md) · [코드](from_attributes.py) · [입력 데이터](../../input_data/from_attributes.json)

## 1. 딕셔너리와 속성 객체의 차이

앞의 예제들은 `data["id"]`처럼 키로 값을 읽는 딕셔너리를 받았습니다. 실제 프로그램에서는 `row.id`처럼 점으로 값을 읽는 객체를 받는 경우도 많습니다.

**속성(attribute)**은 객체에 붙어 있는 값의 이름입니다. **ORM**은 데이터베이스의 행을 Python 객체로 다루게 해 주는 도구입니다. 이번 예제는 DB에 연결하지 않고 그와 비슷한 속성 객체를 만들어 봅니다.

## 2. SimpleNamespace와 **data 이해하기

```python
row = SimpleNamespace(**data)
```

SimpleNamespace는 속성을 담기 위한 Python의 간단한 객체입니다. `**data`는 딕셔너리 항목을 함수의 이름 있는 인자로 펼칩니다.

입력이 `{"id": 1, "name": "민수"}`라면 `SimpleNamespace(id=1, name="민수")`처럼 전달되어 row.id가 1, row.name이 "민수"가 됩니다. 이때는 Pydantic 검증을 아직 하지 않았습니다.

08장에서는 중괄호 안에서 `**`로 딕셔너리를 합쳤고, 여기서는 함수 호출에서 인자를 전달합니다.

## 3. from_attributes=True가 하는 일

```python
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
```

from_attributes는 “속성에서 읽기”입니다. 이 설정을 켜면 UserResponse.model_validate(row)가 row.id와 row.name을 읽어 검증할 수 있습니다. 타입 검증을 생략하는 옵션이 아닙니다.

UserResponse는 응답으로 내보낼 사용자 정보의 규칙입니다. 이름에 Response를 붙인 것은 응답 용도를 나타내려는 개발자의 이름 선택이며 Pydantic의 예약어가 아닙니다.

## 4. run(data)의 흐름

```text
입력 JSON → 딕셔너리
→ SimpleNamespace(**data) → 속성 객체 row
→ UserResponse.model_validate(row) → 검증된 응답 객체 user
→ user.model_dump() → 응답 딕셔너리
```

입력:

```json
{"id": 1, "name": "민수", "internal_memo": "운영 메모"}
```

row에는 세 속성이 있지만 UserResponse에는 id/name만 선언되어 있습니다. 출력은 `{"id": 1, "name": "민수"}`입니다. 객체의 모든 속성을 통째로 출력하는 것이 아닙니다.

name이 없는 두 번째 사례는 필수 속성을 찾을 수 없어 missing 오류가 발생합니다.

## 5. 실행과 연습

`python main.py 12`를 실행합니다. 첫 사례의 id를 "10"으로 바꾸면 여기서는 엄격 모드를 켜지 않았으므로 정수 10으로 변환됩니다.

실제 ORM에서는 관계 속성을 읽는 동작이 추가 DB 조회를 일으킬 수 있습니다. 이 예제의 SimpleNamespace에는 그런 동작이 없습니다.

확인 질문: from_attributes=True면 없는 name도 만들어 주나요?  
답: 아니요. 어디서 값을 읽을지를 정할 뿐이며 기본값 없는 필수 name이 없으면 오류입니다.


[이전 장](../11/README.md) · [다음 장](../13/README.md)
