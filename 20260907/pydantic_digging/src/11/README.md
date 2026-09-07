# 11. 종류에 따라 다른 모델 선택하기

[전체 안내](../../README.md) · [코드](discriminated_union.py) · [입력 데이터](../../input_data/discriminated_union.json)

## 1. 모든 결제가 같은 항목을 받지는 않습니다

카드 결제는 card_token이 필요하고 계좌 결제는 bank_code가 필요합니다. 결제 종류를 먼저 확인한 다음 그 종류에 맞는 구조로 검증하면 규칙이 분명해집니다.

이번 장의 **union**은 “여러 타입 중 하나”이고, **discriminator(판별 필드)**는 “어느 타입을 고를지 알려 주는 항목”입니다. 02장의 Literal, 03장의 중첩 모델, 10장의 Annotated를 먼저 확인하세요.

## 2. 모델 세 개의 역할

| 모델 | 역할 | 필수 값 |
| --- | --- | --- |
| CardPayment | 카드 결제 내용 | type="card", 비어 있지 않은 card_token |
| BankPayment | 계좌 결제 내용 | type="bank", 숫자 세 자리 bank_code |
| Checkout | 결제 전체 요청 | 양수 amount, payment |

여기서 `type`은 우리가 정한 입력 필드 이름입니다. Python의 내장 함수 type()과는 별개입니다. card_token은 실제 카드번호가 아닌 학습용 문자열입니다.

## 3. 긴 타입 선언을 나눠 읽기

```python
payment: Annotated[
    CardPayment | BankPayment,
    Field(discriminator="type"),
]
```

1. CardPayment | BankPayment: payment가 둘 중 한 모델이어야 합니다.
2. Annotated: 타입에 추가 정보를 붙입니다.
3. discriminator="type": payment 안의 type 값을 보고 모델을 고릅니다.
4. 각 모델의 Literal 값을 대조해 "card"면 CardPayment, "bank"면 BankPayment를 사용합니다.

즉 “결제 종류를 골라 검사한다”는 목적을 타입 선언으로 표현한 것입니다.

## 4. bank_code의 pattern 문법

`Field(pattern=r"^\d{3}$")`는 문자열 모양을 검사하는 **정규표현식**을 사용합니다.

| 조각 | 의미 |
| --- | --- |
| r"..." | Python에서 역슬래시를 그대로 적기 위한 raw 문자열 |
| ^ | 문자열 시작 |
| \d | 숫자 문자(ASCII 0~9 외 유니코드 숫자도 포함 가능) |
| {3} | 앞의 숫자가 정확히 세 번 |
| $ | 문자열 끝 |

그래서 "001"은 성공하고 "01"이나 "ABC"는 실패합니다. 실제 은행 코드 목록에 존재하는지까지 확인하는 규칙은 아닙니다.

## 5. run(data)의 입력과 결과

```json
{"amount": 1000, "payment": {"type": "card", "card_token": "fake-token"}}
```

Checkout.model_validate는 payment를 CardPayment 객체로 만듭니다. run은 `type(checkout.payment).__name__`으로 객체의 클래스 이름을 읽어 "선택 모델"에 CardPayment를 담고, model_dump로 결제 내용도 반환합니다.

| 오류 사례 | 오류 종류 | 이유 |
| --- | --- | --- |
| type="cash" | union_tag_invalid | 두 모델 중 해당 분류가 없음 |
| type="card"인데 토큰 없음 | missing | CardPayment 선택 후 필수 항목 누락 |

카드 토큰 누락 위치의 `payment.card.card_token`은 payment 안에서 card 분기를 골랐고 그 안의 card_token이 없다는 뜻입니다.

## 6. 실행과 연습

`python main.py 11`로 카드·계좌 성공과 두 오류 사례를 비교합니다.

bank_code를 "01"로 바꾸면 string_pattern_mismatch 오류입니다. 이 사례의 expected_errors에도 해당 종류를 적습니다.

확인 질문: type="card"인데 bank_code만 보내면 성공하나요?  
답: 아니요. 선택된 CardPayment에 필요한 card_token이 없으므로 실패합니다.


[이전 장](../10/README.md) · [다음 장](../12/README.md)
