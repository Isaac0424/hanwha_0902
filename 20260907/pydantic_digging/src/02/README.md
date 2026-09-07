# 02. 타입이 맞아도 값이 적절한지 검사하기

[전체 안내](../../README.md) · [코드](constraints.py) · [입력 데이터](../../input_data/constraints.json)

## 1. 언제 필요한가요?

상품 가격이 정수라는 것만 확인하면 -100원도 통과합니다. 상품명도 문자열이기만 하면 빈 문자열을 받습니다. 이번 장에서는 **타입 조건에 길이·범위 조건을 더합니다.** 01장의 필드, 기본값, model_validate/model_dump를 먼저 읽으세요.

## 2. Field는 무엇인가요?

`Field(...)`는 필드의 추가 설정을 적는 함수입니다. 01장에서는 `default_factory`로 기본값 생성 방법을 설정했습니다. 여기서는 검증 조건을 설정합니다.

```python
name: str = Field(min_length=2, max_length=30)
price: int = Field(gt=0)
stock: int = Field(ge=0)
```

| 설정 | 풀어서 읽기 | 성공 예 | 실패 예 |
| --- | --- | --- | --- |
| min_length=2 | 길이가 2 이상 | "책장" | "책" |
| max_length=30 | 길이가 30 이하 | "파이썬 책" | 31자 문자열 |
| gt=0 | greater than, 0 초과 | 1 | 0, -1 |
| ge=0 | greater than or equal, 0 이상 | 0, 1 | -1 |

`= Field(gt=0)`에 등호가 있다고 기본값 0을 뜻하지는 않습니다. **gt는 제한값**입니다. default나 default_factory가 없으므로 price는 여전히 필수입니다.

## 3. Literal은 무엇인가요?

```python
category: Literal["book", "food"]
```

`Literal`은 Python typing에서 가져온 타입 표기이며, 대괄호 안에 적힌 **값 자체**만 허용합니다. category가 어떤 문자열이든 되는 것이 아니라 "book" 또는 "food"여야 합니다. "Book"도 다르므로 거부합니다.

## 4. 모델과 함수 읽기

`Product`는 상품 한 개의 규칙입니다. `run(data)`는 딕셔너리를 Product로 검증한 뒤 일반 딕셔너리로 반환합니다.

```python
product = Product.model_validate(data)  # 검사 성공 → Product 객체
result = product.model_dump()          # 객체 → dict
return result
```

검증 중 오류가 생기면 model_dump 줄은 실행되지 않고 runner가 오류를 출력합니다.

## 5. 입력과 결과 비교

정상 사례는 다음 입력을 사용합니다.

```json
{"name": "파이썬 책", "price": 20000, "stock": 3, "category": "book"}
```

모든 값이 조건을 만족하여 같은 값의 딕셔너리를 반환합니다.

오류 사례는 `{"name": "책", "price": 0, "stock": -1, "category": "toy"}`입니다. Pydantic은 여러 필드의 오류를 함께 보여 줍니다.

| 필드 | 오류 종류 | 이유 |
| --- | --- | --- |
| name | string_too_short | 한 글자여서 최소 2자 미달 |
| price | greater_than | 0 초과인데 0을 입력 |
| stock | greater_than_equal | 0 이상인데 -1을 입력 |
| category | literal_error | 허용 목록에 toy가 없음 |

## 6. 실행과 연습

`python main.py 02`로 실행합니다. 상품명과 가격을 정상 값으로 고치면 두 오류는 사라집니다. 그에 맞춰 입력 사례의 expected_errors에서도 해당 두 항목을 뺍니다.

stock 설정에 `le=100`을 추가해 보세요. le는 less than or equal, 즉 이하입니다. 100은 성공하고 101은 less_than_equal 오류가 됩니다.

확인 질문: 재고 0과 가격 0의 결과가 왜 다를까요?  
답: 재고는 ge=0으로 0을 포함하고 가격은 gt=0으로 0을 제외하기 때문입니다.


[이전 장](../01/README.md) · [다음 장](../03/README.md)
