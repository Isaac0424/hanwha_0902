# 13. 항목 타입만 바꿔 쓰는 공통 페이지 모델

[전체 안내](../../README.md) · [코드](generics.py) · [입력 데이터](../../input_data/generics.json)

## 1. 제네릭이 필요한 상황

상품 목록과 사용자 목록의 응답이 둘 다 `{"items": [...], "total": 숫자}` 모양이라면 같은 바깥 구조를 반복해서 만들고 싶지 않을 수 있습니다. **제네릭(generic)**은 구조 일부의 타입을 나중에 지정해 재사용하는 방법입니다.

여기서는 Page의 items 안에 어떤 모델이 들어갈지 나중에 정합니다. 03장의 list[모델]과 10장의 타입 표기를 먼저 읽으세요.

## 2. T, TypeVar, Generic을 풀어서 읽기

```python
T = TypeVar("T")

class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(ge=0)
```

| 표현 | 의미 |
| --- | --- |
| TypeVar("T") | 나중에 구체적인 타입을 넣을 자리를 만듦 |
| T | 그 타입 자리에 붙인 이름. 상품 데이터 값이 아님 |
| Generic[T] | 이 모델이 T라는 타입을 바꿔 사용할 수 있다고 선언 |
| list[T] | T 타입의 항목 여러 개 |
| Page[Product] | T 자리에 Product 타입을 지정한 페이지 모델 |

Page[Product]는 값을 꺼내는 목록 인덱싱이 아닙니다. **페이지가 사용할 타입을 정하는 표기**입니다. 결과적으로 items는 list[Product] 규칙으로 검증됩니다.

## 3. 모델과 run(data)

Product는 상품 한 개의 id/name을 정의합니다. Page는 공통 바깥 구조를 정의합니다. run은 상품용 페이지 타입으로 입력을 검증합니다.

```python
page = Page[Product].model_validate(data)
result = page.model_dump()
```

입력:

```json
{"items": [{"id": 1, "name": "책"}], "total": 1}
```

page.items[0]은 Product 객체입니다. dump한 result에서는 같은 항목이 딕셔너리가 됩니다. id가 "bad"인 오류 사례는 `items.0.id`에서 int_parsing으로 실패합니다.

total은 **전체 검색 결과 수**로 사용할 수 있습니다. 현재 페이지에 상품이 10개 있어도 전체 결과는 100개일 수 있으므로 total과 len(items)가 같아야 한다는 규칙을 넣지 않았습니다.

## 4. model_json_schema는 model_dump와 무엇이 다른가요?

**스키마(schema)**는 데이터 구조를 설명하는 규칙 문서입니다. **JSON Schema**는 그 규칙을 표현하는 형식입니다.

| 메서드 | 알려 주는 것 |
| --- | --- |
| page.model_dump() | 실제 상품 값: id가 1이고 name이 "책" |
| Page[Product].model_json_schema() | 구조 규칙: items라는 목록과 total이라는 정수가 있음 |

model_json_schema()는 이름에 json이 있어도 Python **딕셔너리**를 반환합니다. run에서는 그 사전의 `["properties"]`에 접근해 필드 설명 부분을 꺼내고, `list(...)`로 키만 나열합니다. 결과의 “스키마 속성”은 `["items", "total"]`입니다.

## 5. 실행과 연습

`python main.py 13`으로 상품 페이지 성공과 안쪽 상품 id 오류를 확인합니다.

더 연습하려면 같은 파일에 사용자 모델을 추가하고 run에서 Page[Product]를 Page[User]로 바꿉니다. 스키마를 만드는 줄도 같은 타입으로 맞추고, 입력 JSON의 items도 사용자 필드로 수정해야 합니다. **실행 코드의 입력은 계속 JSON 파일에 둡니다.**

확인 질문: T가 상품 개수인가요?  
답: 아니요. T는 항목의 타입을 지정할 자리이며 개수는 total 같은 실제 필드로 표현합니다.


[이전 장](../12/README.md)
