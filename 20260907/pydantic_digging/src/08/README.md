# 08. 보낸 항목만 수정하기: 생략과 null의 실무 차이

[전체 안내](../../README.md) · [코드](partial_update.py) · [입력 데이터](../../input_data/partial_update.json)

## 1. PATCH란 무엇인가요?

API에서 PATCH는 자원의 일부를 수정할 때 쓰는 요청 방식입니다. 이 예제는 서버를 실행하지 않고 “현재 프로필에 수정 요청을 적용하는 과정”만 연습합니다.

이름만 바꾸고 싶으면 소개는 유지해야 합니다. 소개를 지우고 싶으면 “소개를 비우겠다”고 따로 알려야 합니다. 01장에서 배운 **생략과 None의 차이**가 여기서 중요해집니다.

## 2. 왜 모델이 두 개인가요?

| 모델 | 담당 | name 규칙 |
| --- | --- | --- |
| Profile | 최종 저장 데이터 | 반드시 문자열, 최소 1자 |
| ProfilePatch | 일부 항목만 담는 수정 요청 | 생략 가능. 이 단계에서는 None도 허용 |
 
ProfilePatch에서 `Field(default=None, min_length=1)`은 생략하면 None을 채우고, 문자열을 보냈으면 최소 1자를 검사합니다. name=None 요청을 실제 반영해도 되는지는 마지막 Profile 재검증에서 결정합니다.

## 3. exclude_unset=True는 무엇을 제외하나요?

unset은 **입력에서 지정하지 않은 상태**입니다. Patch 객체에는 기본값이 채워져 name과 bio가 모두 보일 수 있어도, Pydantic은 어떤 필드를 실제로 보냈는지 기억합니다.

```python
changes = patch.model_dump(exclude_unset=True)
```

“요청에서 보내지 않아 기본값으로 채운 필드는 빼고 딕셔너리로 꺼내라”입니다.

| 수정 요청 JSON | changes | 의미 |
| --- | --- | --- |
| `{}` | `{}` | 아무것도 바꾸지 않음 |
| `{"name": "지수"}` | `{"name": "지수"}` | 이름만 변경 |
| `{"bio": null}` | `{"bio": None}` | 소개를 비움 |

exclude_none=True는 **값이 None인 항목**을 빼므로 bio를 비우라는 요청도 사라집니다. 여기서는 exclude_unset이 목적에 맞습니다.

## 4. run(data)를 순서대로 읽기

입력은 original과 patch 두 딕셔너리를 담습니다.

```json
{"original": {"name": "민수", "bio": "개발자"}, "patch": {"name": "지수"}}
```

1. Profile로 original을 검증합니다.
2. ProfilePatch로 patch를 검증합니다.
3. exclude_unset으로 실제로 보낸 수정 필드만 꺼냅니다.
4. `{**original.model_dump(), **changes}`로 합칩니다.
5. 합친 값을 Profile로 다시 검증합니다.

`**`는 딕셔너리 항목을 펼치는 Python 문법입니다. 두 딕셔너리에 같은 키가 있으면 오른쪽 값이 이깁니다. 따라서 changes의 name이 기존 name을 덮어씁니다.

결과는 `{"name": "지수", "bio": "개발자"}`입니다. bio는 요청하지 않았으므로 유지됩니다.

## 5. 왜 마지막에 또 검증하나요?

name=null 요청은 ProfilePatch를 통과하지만 이를 합치면 최종 이름이 None이 됩니다. 최종 Profile의 name은 str이므로 string_type 오류로 거부합니다. 입력 요청 형태와 최종 저장 상태의 규칙이 다르기 때문입니다.

`model_copy(update=...)`는 복사하며 값을 바꾸는 메서드지만 변경 값을 재검증하지 않습니다. 여기서 사용하면 위 최종 검사 과정을 대신할 수 없습니다.

## 6. 실행과 연습

`python main.py 08`을 실행하여 네 사례를 비교하세요. 반환 결과의 “실제 수정 필드”가 changes이고 “최종 프로필”이 검증 후 저장할 값입니다.

original을 그대로 두고 patch를 `{}`, `{"bio": null}`로 번갈아 바꿉니다. 전자는 bio="개발자", 후자는 bio=None입니다.

확인 질문: patch에 name=""를 보내면 언제 실패하나요?  
답: 빈 문자열이 min_length=1을 위반하므로 ProfilePatch 검증에서 string_too_short로 실패합니다.


[이전 장](../07/README.md) · [다음 장](../09/README.md)
