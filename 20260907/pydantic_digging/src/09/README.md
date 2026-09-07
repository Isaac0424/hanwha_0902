# 09. 자동 변환을 끄고 타입을 엄격하게 검사하기

[전체 안내](../../README.md) · [코드](strict_mode.py) · [입력 데이터](../../input_data/strict_mode.json)

## 1. 01장과 무엇이 다른가요?

01장에서는 문자열 "10"을 정수 10으로 바꿨습니다. 외부 입력을 편하게 받는 데 도움이 됩니다. 하지만 어떤 데이터 흐름에서는 “정수로 보내야 하는데 문자열이 왔다”는 사실 자체를 오류로 보고 싶을 수 있습니다.

strict는 **엄격한**이라는 뜻입니다. 이번 Inventory 모델은 Python 입력의 quantity가 처음부터 정수인지 검사합니다.

## 2. 세 설정을 구분하기

```python
model_config = ConfigDict(
    strict=True,
    extra="forbid",
    validate_assignment=True,
)
```

| 설정 | 검사하는 것 | 이 코드의 예 |
| --- | --- | --- |
| strict=True | 타입 자동 변환 허용 여부 | "3"을 정수로 바꾸지 않고 거부 |
| extra="forbid" | 정의하지 않은 항목 유무 | quantity 외 키를 받으면 거부 |
| validate_assignment=True | 생성 뒤 새 값 대입도 검사할지 | inventory.quantity = -1에서 오류 |

`quantity: int = Field(ge=0)`은 타입 외에도 **0 이상**을 요구합니다. strict=True와 숫자 범위 제한은 다른 조건입니다.

## 3. 생성과 재할당이란?

`Inventory.model_validate(...)`는 객체를 처음 만드는 단계입니다. `inventory.quantity = ...`는 이미 만든 객체의 값을 바꾸는 **재할당**입니다.

기본적으로 일반적인 필드 재할당을 자동 검증하도록 설정되어 있지는 않으므로, 여기서는 validate_assignment=True를 켰습니다. 이 설정은 이 예제의 속성 대입을 검사합니다. 목록의 append처럼 내부 값을 직접 바꾸는 모든 동작까지 자동으로 검사한다는 뜻은 아닙니다.

## 4. run(data)와 입력 구조

Inventory의 필드는 quantity 하나입니다. 입력 JSON의 initial/assign은 학습용 run 함수가 쓰는 구분입니다.

```json
{"initial": {"quantity": 3}, "assign": 4}
```

run은 initial 딕셔너리를 검증해 재고를 만들고, assign 키가 있으면 그 값을 quantity에 대입합니다. 마지막에 model_dump로 `{"quantity": 4}`를 반환합니다.

`if "assign" in data`는 **키가 있는가**라는 검사입니다. 값이 0이어도 키가 있으면 대입합니다.

## 5. 성공과 실패 비교

| 입력 상황 | 실패 위치/종류 | 이유 |
| --- | --- | --- |
| initial 수량 3, assign 4 | 성공 | 둘 다 0 이상 정수 |
| initial 수량 "3" | 생성 때 int_type | 문자열을 정수로 변환하지 않음 |
| initial 수량 3, assign -1 | 대입 때 greater_than_equal | 재할당 검증에서 0 이상 조건 위반 |

JSON 파일을 json.loads로 읽은 후 Python 객체를 검증하는 예제입니다. strict 모드의 날짜 등 일부 타입 규칙은 JSON을 직접 검증할 때와 차이가 있을 수 있습니다.

## 6. 실행과 연습

`python main.py 09`를 실행합니다. assign을 0으로 바꾸면 성공하며 -1이면 실패합니다. assign을 `true`로 바꾸면 Python에서 True가 되지만 엄격한 int 검증에서는 int_type 오류가 됩니다.

확인 질문: strict=True가 음수를 막아 주나요?  
답: 음수는 정수 타입입니다. 음수를 막는 것은 Field(ge=0)입니다.


[이전 장](../08/README.md) · [다음 장](../10/README.md)
