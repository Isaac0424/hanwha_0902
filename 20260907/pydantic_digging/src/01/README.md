# 01. 입력을 검사하고 사용하기 편한 객체로 만들기

[전체 안내](../../README.md) · [코드](basic.py) · [입력 데이터](../../input_data/basic.json)

## 1. 무엇을 해결하나요?

사용자 데이터를 받았는데 id가 정수 `10`이 아니라 문자열 `"10"`일 수 있습니다. 날짜도 보통 `"2026-09-07T09:00:00"`처럼 글자로 들어옵니다. 이 값을 프로그램에서 쓰기 전에 “필요한 항목이 있는가, 타입이 맞는가, 변환할 수 있는가”를 확인하는 것이 **검증(validation)**입니다.

Pydantic은 우리가 적은 데이터 규칙을 읽고 이 작업을 해 줍니다. 아무 잘못된 값이나 고쳐 주는 것은 아닙니다. `"10"`은 정수로 바꿀 수 있지만 `"hello"`는 바꿀 수 없어 오류가 납니다.

## 2. 코드에서 쓰는 말부터 알아보기

| 표현 | 뜻 | 이 예제 |
| --- | --- | --- |
| 딕셔너리(dict) | 이름인 키와 값을 짝으로 저장 | `{"id": "10"}` |
| 필드(field) | 모델이 받는 데이터 항목 하나 | `id`, `name`, `nickname` |
| 타입(type) | 값의 종류 | `int` 정수, `str` 문자열 |
| 모델(model) | 항목과 규칙을 정의한 클래스 | `User` |
| 객체/인스턴스 | 모델을 바탕으로 만들어진 실제 데이터 | `user` |
| 메서드(method) | 클래스나 객체에 속한 함수 | `User.model_validate(...)` |
| 기본값(default) | 입력에서 항목을 빼면 대신 채울 값 | `name`의 `"익명"` |

`class User(BaseModel):`는 “Pydantic의 기본 검증 기능을 가진 User라는 클래스를 만든다”입니다. 괄호 안의 `BaseModel`을 **상속**하므로 우리가 직접 만들지 않은 `model_validate()`, `model_dump()`를 사용할 수 있습니다.

일반 Python에서 `id: int` 같은 타입 힌트만 적는다고 런타임 검증이 자동으로 되는 것은 아닙니다. 여기서는 Pydantic이 타입 힌트를 읽고 검증합니다.

## 3. 필드 선언을 왼쪽부터 읽기

```python
name: str = "익명"
```

- `name`: 데이터 항목 이름.
- `: str`: 이 항목의 값은 문자열이어야 한다.
- `= "익명"`: 항목이 입력에 없으면 이 값을 채운다.

`id: int`에는 기본값이 없습니다. 따라서 id를 보내야 합니다. `joined_at: datetime`의 datetime은 날짜와 시간을 표현하는 Python 타입입니다.

## 4. None을 보냈다는 것과 항목을 빼는 것은 어떻게 다른가요?

`None`은 Python에서 “값이 없음”을 나타내는 실제 값입니다. JSON 파일에서는 같은 의미로 `null`을 씁니다. JSON을 읽으면 `null`이 Python의 `None`으로 바뀝니다.

현재 코드는 다음과 같습니다.

```python
nickname: str | None
```

`|`는 **또는**입니다. “nickname의 값으로 문자열 또는 None을 받는다”입니다. 여기에 기본값은 없으므로 **nickname이라는 항목은 반드시 보내야 합니다.**

아래는 다른 필수 필드를 모두 보냈다고 가정하고 nickname 부분만 비교한 표입니다.

| 입력 JSON의 nickname 부분 | 키를 보냈나요? | 현재 선언의 결과 |
| --- | --- | --- |
| `"nickname": "민수"` | 예 | 문자열이므로 성공 |
| `"nickname": ""` | 예 | 빈 문자열도 str이므로 성공 |
| `"nickname": null` | 예 | None을 허용하므로 성공 |
| nickname 항목 자체를 삭제 | 아니요 | 대신 채울 기본값이 없어 missing 오류 |

**생략도 허용하려면 기본값을 추가합니다.**

```python
nickname: str | None = None
```

이제 nickname 키가 없어도 기본값 None을 채울 수 있습니다. `| None`은 **받을 수 있는 값**을, `= None`은 **보내지 않았을 때 채울 값**을 정합니다.

반대로 `name: str = "익명"`은 생략할 수 있지만 `name=None`은 허용하지 않습니다. 이미 None이라는 값을 보냈으므로 기본값을 적용하는 상황이 아니며, str 규칙을 위반합니다.

## 5. Field(default_factory=list)를 조각내서 읽기

```python
tags: list[str] = Field(default_factory=list)
```

| 조각 | 의미 |
| --- | --- |
| `tags` | 관심사 목록이라는 필드 이름 |
| `list[str]` | 문자열 여러 개를 담는 목록. 예: `["python", "study"]` |
| `Field(...)` | 필드의 기본값이나 조건을 설정하는 Pydantic 함수 |
| `default_factory` | 기본값을 만들어 줄 함수 |
| `list` | 호출하면 새 목록을 만드는 Python 내장 타입/생성 함수 |

Python에서 `list()`를 호출하면 빈 목록 `[]`이 만들어집니다. 여기서는 **지금 호출한 결과**가 아니라 **필요할 때 호출할 함수 자체**를 전달하므로 `default_factory=list`라고 적습니다. `default_factory=list()`라고 적지 않습니다.

처리 흐름은 다음과 같습니다.

```text
tags를 보냈다 → 보낸 목록과 그 안의 문자열을 검증
tags를 생략했다 → list()를 호출 → 새로운 []를 기본값으로 사용
```

사용자를 두 명 만들면 각각 새 목록을 받습니다. 한 사용자의 tags에 항목을 추가해도 다른 사용자의 tags는 그대로입니다. Pydantic은 `tags: list[str] = []` 같은 변경 가능한 기본값도 복사해 처리하지만, 이 예제는 “객체마다 새 값을 만든다”는 의도를 명시하는 방식을 사용합니다.

## 6. model_validate와 model_dump는 방향이 다릅니다

```python
user = User.model_validate(data)
result = user.model_dump()
```

| 호출 | 받는 것 | 하는 일 | 돌려주는 것 |
| --- | --- | --- | --- |
| `User.model_validate(data)` | 입력 딕셔너리 | 필수 항목·타입 검사, 허용된 변환, 기본값 채우기 | User 객체 |
| `user.model_dump()` | 별도 입력 없이 user의 값 사용 | 객체에 담긴 값을 일반 구조로 꺼내기 | Python 딕셔너리 |

첫 줄은 성공하면 객체를 반환하며, 실패하면 `False` 대신 **ValidationError라는 예외**를 발생시킵니다. 예외는 정상 실행을 중단하는 오류 신호입니다. 이 프로젝트의 runner가 받아 오류 위치를 출력합니다.

둘째 줄은 원본 JSON으로 되돌리는 작업이 아닙니다. 변환된 값과 기본값을 담은 **딕셔너리**를 만듭니다. 날짜 객체는 날짜 객체로 남습니다. JSON 문자열로 바꾸는 방법은 07장에서 배웁니다.

## 7. 실제 입력이 어떻게 바뀌나요?

`basic.json`의 첫 사례에서 `input` 부분입니다.

```json
{"id": "10", "joined_at": "2026-09-07T09:00:00", "nickname": null}
```

```text
JSON 읽기 → Python 딕셔너리(null은 None으로 바뀜)
→ User.model_validate(data)
→ User 객체(user.id, user.name처럼 값에 접근)
→ user.model_dump()
→ Python 딕셔너리(result["id"]처럼 값에 접근)
```

검증 후 주요 값은 다음과 같습니다.

| 항목 | 결과 | 이유 |
| --- | --- | --- |
| id | 정수 `10` | 문자열 숫자를 변환 |
| name | `"익명"` | 입력에 없어 기본값 적용 |
| joined_at | `datetime(2026, 9, 7, 9, 0)`에 해당하는 객체 | 날짜 문자열 변환 |
| nickname | `None` | null을 보냈고 None을 허용 |
| tags | `[]` | 입력에 없어 새 목록 생성 |

`run(data)`는 우리가 만든 학습용 함수입니다. Pydantic의 특별한 함수 이름이 아닙니다. 입력 한 건을 받아 위 과정을 실행하고 결과를 main 쪽에 반환합니다.

## 8. 실행하고 오류까지 읽기

`pydantic_digging` 폴더에서 `python main.py 01`을 실행합니다. `missing`은 필수 항목 누락, `int_parsing`은 정수 변환 실패, `string_type`은 문자열 타입 불일치, `list_type`은 목록 타입 불일치입니다.

검증 오류 뒤에 `[PASS]`가 나올 수 있습니다. “이 입력은 실패해야 한다고 적어 두었고 실제로 그렇게 실패했다”는 뜻입니다.

## 9. 직접 확인하기

1. nickname 선언에 `= None`을 추가합니다. 키 누락 사례는 이제 성공하므로 그 사례의 `expected_errors`를 `[]`로 바꿉니다.
2. 첫 사례에 `"tags": ["python"]`을 추가합니다. 결과가 `[]` 대신 보낸 목록이 되는지 봅니다.
3. name을 생략한 경우와 `"name": null`인 사례를 비교합니다. 전자는 "익명", 후자는 string_type 오류입니다.

질문: “None을 허용하려면?”, “생략하면 None을 채우려면?”  
답: 각각 타입에 `| None`을 쓰고, 기본값으로 `= None`을 씁니다. 두 동작을 함께 원하면 둘 다 적습니다.


[다음 장](../02/README.md)
