# 05. 내가 만든 함수로 필드 검사하기

[전체 안내](../../README.md) · [코드](field_validation.py) · [입력 데이터](../../input_data/field_validation.json)

## 1. 왜 별도의 함수가 필요한가요?

Field는 길이와 숫자 범위 같은 조건을 표현하기 좋습니다. 하지만 “이름 양끝 공백을 없애고 admin이라는 이름은 사용하지 못하게 한다”는 규칙은 별도의 코드가 필요합니다. 이렇게 검증 과정에 참여하는 함수를 **검증기(validator)**라고 합니다.

## 2. 처음 보는 Python 문법

| 표현 | 뜻 |
| --- | --- |
| `@데코레이터` | 바로 아래 함수에 특별한 역할을 부여하는 문법 |
| `@field_validator("username", ...)` | 이 함수를 username 필드의 검증 과정에 등록 |
| `@classmethod` | 객체가 아닌 클래스에 속한 메서드로 만듦 |
| `cls` | 그 메서드에 전달되는 클래스, 여기서는 Signup |
| `value` | 현재 검사하는 값 |
| `Any` | 아직 타입을 한 종류로 정하지 않았다는 표기 |
| `-> str` | 함수가 문자열을 반환한다는 타입 힌트 |
| `raise ValueError(...)` | 값이 규칙에 어긋난다는 오류 발생 |

데코레이터 문법 전체를 먼저 외울 필요는 없습니다. 여기서는 “Pydantic이 언제 이 함수를 실행할지 등록한다”고 읽으세요. trim/check_name은 우리가 붙인 함수 이름입니다.

## 3. before와 after의 차이

```text
원본 username
→ trim: before 검증기
→ Pydantic의 str 타입 검사
→ check_name: after 검증기
→ 최종 username 저장
```

**before**는 기본 타입 검사 **전**입니다. 입력이 문자열일 수도, 숫자일 수도 있으므로 trim은 먼저 `isinstance(value, str)`로 문자열인지 검사합니다. 문자열이면 `strip()`으로 양끝 공백을 지웁니다. 숫자에는 strip이 없으므로 그대로 넘겨 기본 타입 검사가 오류를 내도록 합니다.

**after**는 기본 타입 검사 **후**입니다. check_name은 문자열인 값에 대해 글자 수와 금지 이름을 검사합니다. `len(value)`는 글자 수, `value.lower()`는 소문자로 만든 문자열입니다. lower는 여기서 비교에만 쓰므로 정상 이름을 소문자로 저장하는 것은 아닙니다.

## 4. 모델과 함수별 역할

| 이름 | 입력 → 출력 |
| --- | --- |
| Signup | username이 문자열인 가입 데이터의 규칙 |
| trim(cls, value) | 원본 값 → 공백 제거한 문자열 또는 원본 비문자열 |
| check_name(cls, value) | 문자열 → 규칙을 통과한 동일 문자열, 실패하면 오류 |
| run(data) | 입력 딕셔너리 → Signup 검증 → 결과 딕셔너리 |

`model_validate(data)`가 등록한 함수를 자동 실행하므로 run에서 trim이나 check_name을 따로 호출하지 않습니다.

**return이 중요합니다.** 검증기가 반환한 값이 다음 단계에 전달됩니다. return을 빼면 Python은 None을 반환합니다. 단순히 “오류가 없으니 알아서 원래 값을 쓰겠지”라고 생각하면 안 됩니다.

## 5. 사례를 따라가기

| 입력의 username | 처리 과정 | 결과 |
| --- | --- | --- |
| `"  minsu  "` | 공백 제거 → "minsu" → 길이/금지 이름 검사 | `{"username": "minsu"}` |
| `" admin "` | 공백 제거 → "admin" → 금지 이름 | value_error |
| `123` | before는 그대로 전달 → str 타입 검사 실패 | string_type |

ValueError는 Pydantic이 받아 ValidationError에 담아 줍니다. runner에서는 그 안의 오류 종류가 value_error로 보입니다.

## 6. 실행과 연습

`python main.py 05`를 실행합니다.

정상 이름도 소문자로 저장하고 싶다면 check_name의 마지막 줄을 `return value.lower()`로 바꿉니다. "Minsu" 입력의 결과는 "minsu"가 됩니다. 금지 이름 검사는 그대로 유지합니다.

확인 질문: 숫자 입력에서도 check_name이 실행될까요?  
답: 아니요. 이 예제에서는 그 전에 str 타입 검사에서 실패합니다.


[이전 장](../04/README.md) · [다음 장](../06/README.md)
