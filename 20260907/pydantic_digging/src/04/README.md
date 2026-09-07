# 04. 외부 이름과 코드 안의 이름 연결하기

[전체 안내](../../README.md) · [코드](aliases.py) · [입력 데이터](../../input_data/aliases.json)

## 1. 언제 필요한가요?

외부 서비스는 사용자 번호를 `userId`라고 보내는데 Python 코드에서는 `user_id`로 쓰고 싶을 수 있습니다. 같은 의미의 데이터 이름을 연결하는 기능이 **별칭(alias)**입니다. camelCase는 userId처럼 단어 중간을 대문자로, snake_case는 user_id처럼 밑줄로 구분하는 표기입니다.

## 2. Field(alias=...) 읽기

```python
user_id: int = Field(alias="userId")
```

“Python에서 필드 이름은 user_id이고 외부에서는 userId라는 이름도 사용한다”입니다. 객체에서는 `customer.user_id`로 읽습니다. `customer.userId` 속성을 만드는 기능은 아닙니다.

## 3. ConfigDict와 model_config는 무엇인가요?

`ConfigDict(...)`는 모델 전체의 동작 설정을 모으는 도구입니다. 이를 `model_config`라는 정해진 이름에 넣습니다. model_config는 사용자에게 받는 데이터 필드가 아닙니다.

| 설정 | 이 예제에서의 뜻 |
| --- | --- |
| validate_by_name=True | user_id처럼 Python에 선언한 이름으로 입력받기 허용 |
| validate_by_alias=True | userId처럼 alias로 지정한 이름으로 입력받기 허용 |
| extra="forbid" | 정의하지 않은 추가 필드를 받으면 거부 |

여기서는 두 종류의 이름을 모두 허용하도록 명시했습니다. 같은 필드의 두 이름을 동시에 보낼 필요는 없습니다.

## 4. Customer와 run(data)

Customer는 사용자 번호와 표시 이름을 정의합니다. run은 입력을 Customer 객체로 만들고 다음 두 딕셔너리를 반환합니다.

```python
internal = customer.model_dump()
external = customer.model_dump(by_alias=True)
```

`by_alias=True`는 “출력 키에 별칭을 써 달라”라는 옵션입니다. 입력 허용 설정과 출력 이름 선택은 별개입니다.

입력:

```json
{"userId": 1, "displayName": "민수"}
```

결과:

```python
{
    "내부 이름": {"user_id": 1, "display_name": "민수"},
    "외부 이름": {"userId": 1, "displayName": "민수"}
}
```

## 5. 왜 age를 보내면 오류인가요?

Customer에는 age가 없습니다. 입력에 age를 추가한 사례는 extra="forbid" 설정 때문에 `age: ... [extra_forbidden]`이 됩니다. 잘못된 키 이름을 조용히 놓치지 않으려는 설정입니다.

Pydantic의 기본 추가 필드 처리는 ignore이지만, 이 모델은 forbid로 선택했습니다. 외부 서비스가 새 필드를 자주 추가한다면 이 설정이 적합한지도 생각해야 합니다.

## 6. 실행과 연습

`python main.py 04`로 별칭 입력, 내부 이름 입력, 추가 필드 오류를 비교합니다.

정상 입력의 userId를 user_id로, displayName을 display_name으로 바꿔도 두 설정이 True라서 성공합니다. 결과 객체의 속성 이름은 계속 user_id/display_name입니다.

확인 질문: 입력에 userId를 썼으면 dump도 자동으로 userId가 되나요?  
답: 이 코드에서는 기본 dump가 user_id를 쓰고 by_alias=True를 지정한 dump가 userId를 씁니다.


[이전 장](../03/README.md) · [다음 장](../05/README.md)
