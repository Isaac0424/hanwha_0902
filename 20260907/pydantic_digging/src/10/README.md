# 10. 목록 전체를 TypeAdapter로 검사하기

[전체 안내](../../README.md) · [코드](type_adapter.py) · [입력 데이터](../../input_data/type_adapter.json)

## 1. 입력의 맨 바깥이 목록이라면?

03장 주문 입력은 `{"items": [...]}`라는 딕셔너리였습니다. 이번 입력은 바깥을 감싼 필드 없이 바로 목록입니다.

```json
[{"sku": "A", "quantity": "2"}, {"sku": "B", "quantity": 1}]
```

이 모양 그대로 검증하는 데 `TypeAdapter`를 씁니다. 타입 표기를 받아 **그 타입에 맞는 검증 도구를 만드는 클래스**라고 이해하면 됩니다.

## 2. Row와 Annotated 이해하기

Row는 한 행의 규칙입니다. sku는 상품 식별 코드, quantity는 양수 정수입니다.

```python
quantity: Annotated[int, Field(gt=0)]
```

`Annotated[기본 타입, 추가 정보]`는 타입 옆에 조건 같은 정보를 붙이는 Python 표기입니다. 여기서는 “int이고 0보다 커야 한다”입니다. 이 필드에서는 02장의 `quantity: int = Field(gt=0)`와 같은 검증 목적을 표현합니다.

Annotated 자체가 검증을 실행하는 것은 아닙니다. Pydantic이 여기에 붙인 Field 정보를 읽습니다.

## 3. 목록의 검증 도구 만들기

```python
rows_adapter = TypeAdapter(list[Row])
```

list[Row]는 “Row 여러 개를 담은 목록”이라는 타입입니다. rows_adapter는 실제 입력 목록이 아니라 **목록을 검사할 도구**입니다. 함수 밖에 만들어 run이 반복될 때 재사용합니다.

## 4. 메서드 이름 비교

| 대상 | 검사할 때 | 출력용 값으로 바꿀 때 |
| --- | --- | --- |
| BaseModel 기반 모델 | Model.model_validate(data) | model.model_dump() |
| TypeAdapter | adapter.validate_python(data) | adapter.dump_python(value) |

TypeAdapter는 BaseModel 객체가 아니므로 메서드 이름과 사용법이 다릅니다. dump_python에는 내보낼 **검증된 값 rows**를 직접 전달합니다.

## 5. run(data)의 흐름과 결과

```text
입력 list[dict]
→ rows_adapter.validate_python(data)
→ 검증된 list[Row]
→ rows_adapter.dump_python(rows, mode="json")
→ JSON 호환 값으로 된 list[dict]
```

첫 사례의 결과는 `[{"sku": "A", "quantity": 2}, {"sku": "B", "quantity": 1}]`입니다. "2"는 정수 2로 변환됩니다. 결과 전체는 **목록**이며 JSON 문자열이 아닙니다.

두 번째 행의 수량이 0이면 `1.quantity: ... [greater_than]`입니다. 맨 앞 1은 두 번째 행의 인덱스입니다. 바깥에 items라는 필드가 없어 03장과 달리 오류 위치도 items로 시작하지 않습니다.

## 6. 실행과 연습

`python main.py 10`을 실행합니다. CSV에서 읽은 행 목록이나 API가 반환한 배열을 검증하는 상황에 응용할 수 있습니다. 이 예제는 CSV 읽기 자체를 구현하지 않습니다.

세 번째 행에 quantity=0을 넣으면 위치는 2.quantity입니다.

확인 질문: Row.model_validate에 전체 목록을 바로 전달해도 되나요?  
답: Row는 한 행의 구조이므로 전체 목록을 검증하려면 여기처럼 TypeAdapter(list[Row])를 사용합니다.


[이전 장](../09/README.md) · [다음 장](../11/README.md)
