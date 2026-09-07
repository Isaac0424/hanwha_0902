# 07. 객체를 출력용 데이터로 바꾸기

[전체 안내](../../README.md) · [코드](serialization.py) · [입력 데이터](../../input_data/serialization.json)

## 1. 직렬화는 무엇인가요?

검증한 Receipt 객체를 다른 프로그램에 보내거나 파일에 저장하려면 전달 가능한 형태가 필요합니다. 객체를 딕셔너리나 JSON 같은 형태로 바꾸는 작업을 **직렬화(serialization)**라고 부릅니다.

JSON은 데이터를 주고받는 **텍스트 형식**입니다. Python 딕셔너리와 비슷하게 보이지만 같은 타입이 아닙니다. 딕셔너리는 Python 객체이고 JSON 문자열은 글자들의 모음인 str입니다.

## 2. 먼저 영수증 모델 이해하기

Receipt는 생성일(created_at), 단가(unit_price), 수량(quantity), 학습용 키(api_key)를 받습니다. 단가와 수량은 02장의 Field(gt=0)으로 양수만 허용합니다.

`SecretStr`은 문자열을 일반 출력에서 가려 주는 타입입니다. 암호화나 접근 제어 기능은 아닙니다. `Field(exclude=True)`는 해당 필드를 dump 결과에서 통째로 빼는 설정입니다. 이 프로젝트의 실행기는 **입력 원문도 출력**하므로 실제 비밀값 대신 제공된 가짜 키만 사용합니다.

## 3. 계산한 total은 어디서 나오나요?

```python
@computed_field
@property
def total(self) -> int:
    return self.unit_price * self.quantity
```

`@property`는 메서드를 `receipt.total()` 대신 `receipt.total`이라는 속성처럼 읽게 합니다. `@computed_field`는 이 계산값을 Pydantic의 출력 필드에도 포함시킵니다.

입력 JSON에는 total이 없습니다. 단가 1000, 수량 3이면 계산으로 total=3000이 나옵니다. self는 현재 Receipt 객체입니다.

## 4. 날짜 출력 함수를 읽기

```python
@field_serializer("created_at", when_used="json")
def serialize_date(self, value: datetime) -> str:
    return value.isoformat(timespec="seconds")
```

field_serializer는 검증기가 아니라 **출력 변환 함수**입니다. when_used="json"이면 JSON 모드 출력에만 적용합니다. isoformat은 날짜·시간을 표준적인 문자열로 만들고 timespec="seconds"는 초 단위까지 표현하게 합니다.

Pydantic은 기본적으로도 날짜를 JSON 문자열로 바꿀 수 있습니다. 여기서는 “출력 형식을 직접 지정하는 방법”을 연습하려고 함수를 둡니다.

## 5. 세 가지 출력 비교

run(data)는 Receipt.model_validate(data)로 먼저 검증한 뒤 아래 결과를 모두 반환합니다.

| 호출 | 전체 반환 타입 | created_at 값 | 용도 |
| --- | --- | --- | --- |
| model_dump() | dict | datetime 객체 | Python 안에서 계속 처리 |
| model_dump(mode="json") | dict | 문자열 | JSON 호환 값으로 구성된 딕셔너리 필요 |
| model_dump_json() | str | JSON 텍스트 안의 문자열 | JSON 텍스트를 저장/전달 |

첫 입력은 단가 1000, 수량 3, 날짜 "2026-09-07T12:30:00"입니다. JSON 문자열 결과는 다음과 같습니다.

```json
{"created_at":"2026-09-07T12:30:00","unit_price":1000,"quantity":3,"total":3000}
```

세 출력 모두 api_key는 빠지고 total은 포함됩니다. 전체 결과가 dict인지 str인지는 겉모양보다 `type(...)`으로 확인하는 것이 확실합니다.

## 6. 오류와 실행

`python main.py 07`을 실행합니다. quantity=0 사례는 greater_than 오류로 검증에 실패하므로 세 가지 출력 변환에 도달하지 않습니다.

수량을 4로 바꾸면 total=4000입니다. created_at에 소수 초를 추가하면 Python 딕셔너리에는 소수 초가 남을 수 있지만 JSON 출력 함수는 초 단위 문자열로 표현합니다.

확인 질문: mode="json"을 주면 전체가 문자열인가요?  
답: model_dump(mode="json")은 계속 dict입니다. model_dump_json()이 str을 반환합니다.


[이전 장](../06/README.md) · [다음 장](../08/README.md)
