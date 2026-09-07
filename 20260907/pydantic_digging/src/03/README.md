# 03. 주문 안의 상품 목록까지 검사하기

[전체 안내](../../README.md) · [코드](nested.py) · [입력 데이터](../../input_data/nested.json)

## 1. 중첩이라는 말부터 이해하기

주문 한 건에는 고객 번호와 상품 여러 개가 들어갑니다. 각 상품에는 상품 번호와 수량이 들어갑니다. 이처럼 데이터 안에 또 다른 데이터 구조가 들어 있는 것을 **중첩(nested)**이라고 합니다.

01~02장의 모델 한 개 검증을 알고 나면, 여기서는 “모델의 필드 타입으로 다른 모델도 쓸 수 있다”를 배우면 됩니다.

## 2. 입력의 모양 보기

```json
{
  "customer_id": 1,
  "items": [
    {"product_id": 10, "quantity": 2},
    {"product_id": 20, "quantity": 1}
  ]
}
```

바깥의 중괄호는 주문 딕셔너리입니다. items의 대괄호는 목록이고, 그 안의 각 중괄호는 상품 딕셔너리입니다.

## 3. 두 모델이 각각 담당하는 것

| 이름/선언 | 읽는 방법 |
| --- | --- |
| Item | 상품 한 개의 규칙: product_id는 정수, quantity는 양수 |
| Order | 주문 한 개의 규칙: customer_id와 items를 받음 |
| list[Item] | Item 객체 여러 개가 들어 있는 목록 |
| Field(min_length=1) | 목록에 항목이 최소 1개 있어야 함 |

```python
items: list[Item] = Field(min_length=1)
```

이 줄의 min_length는 **목록의 항목 수**입니다. 02장에서 문자열에 쓰면 글자 수를 셌지만, 여기서는 주문 상품의 개수를 셉니다. 상품 하나의 quantity 값과 목록의 길이는 다른 조건입니다.

## 4. run(data)의 실행 과정

```text
Order.model_validate(data)
→ 고객 번호 검사
→ items 목록 검사
→ 각 항목을 Item 규칙으로 검사하고 Item 객체로 만듦
→ Order 객체 반환
→ order.model_dump()로 안쪽 객체까지 딕셔너리로 반환
```

성공하면 `order.items[0]`은 첫 번째 Item 객체이고 `order.items[0].quantity`는 2입니다. 목록 인덱스는 **0부터** 시작합니다. dump 후에는 `result["items"][0]["quantity"]`로 읽습니다. 객체일 때는 점, 딕셔너리일 때는 키로 접근하는 차이입니다.

## 5. 오류 위치 읽기

두 번째 상품의 quantity를 0으로 바꾼 사례에서는 다음 위치가 나옵니다.

```text
items.1.quantity: ... [greater_than]
```

이를 “items 목록 → 인덱스 1, 즉 두 번째 상품 → quantity 필드”라고 읽습니다. 주문 전체의 수량이 아니라 그 상품의 수량이 0 초과 조건에 실패한 것입니다.

items가 빈 목록이면 `items: ... [too_short]`가 나옵니다. 상품 자체가 없으므로 Item 검사에 들어가기 전에 목록 길이에서 실패합니다.

## 6. 실행과 연습

`python main.py 03`으로 정상 주문, 두 번째 상품 오류, 빈 주문을 비교합니다.

세 번째 상품을 추가하고 수량을 0으로 보내면 위치는 `items.2.quantity`입니다. 오류 종류는 greater_than이며 위치만 달라집니다. 기존 runner는 오류 종류를 비교하므로 위치는 직접 출력에서 확인합니다.

확인 질문: Item을 직접 반복문으로 검증해야 하나요?  
답: 여기서는 list[Item] 선언을 읽은 Pydantic이 각 항목을 검증합니다.


[이전 장](../02/README.md) · [다음 장](../04/README.md)
