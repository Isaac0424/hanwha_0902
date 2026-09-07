# 입력 JSON 읽고 수정하기

[전체 안내](../README.md)

## JSON과 Python 표현의 차이

JSON은 데이터를 저장하는 텍스트 형식입니다. Python 소스 코드가 아니므로 문자열과 키에는 큰따옴표를 쓰고, 주석이나 마지막 항목 뒤의 쉼표를 넣지 않습니다.

| JSON 파일 | Python에서 읽은 값 |
| --- | --- |
| {"id": 1} | dict(딕셔너리) |
| ["python", "study"] | list(목록) |
| "10" | str(문자열) |
| 10 | int(정수) |
| null | None(값 없음) |
| true / false | True / False(불리언) |

runner의 json.loads가 텍스트를 이 Python 값들로 바꿉니다. 이 단계는 Pydantic 모델 검증과 다릅니다. 문자열 "10"은 이때 그대로 문자열이며, 이후 모델의 int 필드 검증에서 정수로 바뀔 수 있습니다.

## 사례 한 개의 구조

```json
{
  "title": "nickname을 생략한 입력",
  "input": {"id": 10, "joined_at": "2026-09-07T09:00:00"},
  "expected_errors": ["missing"],
  "explanation": "nickname은 기본값이 없어 키를 보내지 않으면 실패합니다."
}
```

| 항목 | 누가 사용하나요? |
| --- | --- |
| title | runner가 출력하는 사례 이름 |
| input | 이 값만 각 장의 run 함수에 전달 |
| expected_errors | runner가 실제 오류와 비교하는 예상 오류 종류 목록 |
| explanation | runner가 출력하는 학습용 해설 |

파일 바깥의 대괄호는 이런 사례 여러 개를 담은 목록입니다. **title이나 explanation을 모델 필드에 추가할 필요는 없습니다.**

## 값을 바꾸고 다시 실행하기

1. 해당 JSON의 input 값을 한 군데 바꿉니다.
2. 해당 장을 실행합니다. 예: python main.py 01
3. 출력된 오류의 위치와 이유를 읽습니다.
4. 바뀐 입력이 의도한 결과인지 확인한 뒤 expected_errors와 explanation을 맞춥니다.

예를 들어 nickname을 생략한 사례에 `"nickname": null`을 추가하면 성공합니다. 그 사례의 expected_errors는 []로 바꿉니다. 예상 목록을 고치는 것은 **검증 규칙을 바꾸는 일이 아니라 실행기의 기대를 바꾸는 일**입니다.

여러 필드가 실패하면 ["string_too_short", "greater_than"]처럼 여러 종류를 적습니다. 같은 종류의 오류가 두 번이면 목록에도 두 번 적어야 합니다. runner는 순서만 정렬하고 개수는 그대로 비교합니다.

## 자주 보는 오류

| 종류 | 뜻 |
| --- | --- |
| missing | 필요한 키 또는 속성이 없음 |
| int_parsing | 값을 정수로 변환할 수 없음 |
| int_type / string_type / list_type | 요구 타입에 맞지 않음 |
| greater_than | 초과 조건에 실패 |
| greater_than_equal | 이상 조건에 실패 |
| string_too_short | 문자열 길이가 최소보다 짧음 |
| too_short | 이 예제에서는 목록 길이가 부족함 |
| literal_error | 정해진 허용 값이 아님 |
| extra_forbidden | 모델에 없는 추가 필드를 보냄 |
| value_error | 작성한 검증기의 ValueError |
| union_tag_invalid | 분류 값에 해당하는 모델이 없음 |

오류 종류 이름을 외울 필요는 없습니다. “어느 값이 어떤 규칙을 위반했는지”부터 이해하세요.
