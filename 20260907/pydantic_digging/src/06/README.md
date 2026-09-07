# 06. 여러 필드를 함께 검사하기

[전체 안내](../../README.md) · [코드](model_validation.py) · [입력 데이터](../../input_data/model_validation.json)

## 1. 필드 하나의 검사로 부족한 상황

시작일과 종료일이 각각 올바른 날짜라도 종료일이 더 빠르면 정상 예약이 아닙니다. **두 값을 비교하는 규칙**은 모델 전체를 보는 검증기가 이해하기 쉽습니다. 05장의 검증기와 예외 설명을 먼저 읽으세요.

## 2. date와 model_validator 읽기

`date`는 Python의 날짜 타입으로 연·월·일만 표현합니다. 01장의 datetime은 시간도 포함했습니다. "2026-09-07"이라는 문자열은 검증 후 date 객체가 되므로 날짜끼리 크기를 비교할 수 있습니다.

```python
@model_validator(mode="after")
def check_period(self) -> Self:
    if self.end <= self.start:
        raise ValueError("종료일은 시작일보다 뒤여야 합니다.")
    return self
```

| 표현 | 의미 |
| --- | --- |
| model_validator | 필드 하나가 아닌 모델 전체의 검증기 |
| mode="after" | 각 필드의 기본 검증이 성공한 뒤 실행 |
| self | 지금 검사하는 Reservation 객체 |
| self.start / self.end | 그 객체의 시작일 / 종료일 |
| Self | 자기 모델 타입을 반환한다는 타입 힌트. 여기서는 Reservation |
| <= | 앞 날짜가 뒤 날짜보다 이르거나 같은지 비교 |
| return self | 검사한 모델 객체를 다음 단계로 반환 |

05장의 cls는 클래스이고 여기의 self는 데이터가 채워진 객체입니다. 그래서 self를 통해 날짜 값을 읽습니다.

## 3. 모델과 함수의 흐름

Reservation은 start/end 두 필드를 정의합니다. check_period는 날짜 관계를 검사합니다. run(data)는 model_validate로 이 과정을 실행하고 model_dump로 결과 딕셔너리를 만듭니다.

```text
날짜 문자열 두 개
→ 각각 date 타입으로 변환
→ check_period가 두 날짜 비교
→ 성공하면 Reservation 반환
→ model_dump로 날짜 객체가 담긴 dict 반환
```

## 4. 입력과 결과

정상 입력:

```json
{"start": "2026-09-07", "end": "2026-09-09"}
```

반환 딕셔너리에는 start가 date(2026, 9, 7), end가 date(2026, 9, 9)에 해당하는 객체로 들어갑니다.

날짜를 반대로 입력하면 두 문자열 모두 날짜 변환은 성공하지만 check_period에서 value_error가 발생합니다. 오류 위치는 `(모델 전체)`로 표시됩니다. 어느 필드의 타입 하나가 잘못된 것이 아니라 두 필드의 관계가 잘못됐기 때문입니다.

## 5. 실행과 연습

`python main.py 06`으로 실행합니다. 종료일을 시작일과 같은 날짜로 바꾸면 현재 조건에서는 실패합니다.

같은 날짜를 허용하려면 `self.end <= self.start`를 `self.end < self.start`로 바꿉니다. 이제 더 빠른 종료일만 거부합니다. 성공으로 바뀐 사례의 expected_errors는 빈 목록으로 고칩니다.

확인 질문: 시작일이 "날짜아님"이면 기간 검사까지 갈까요?  
답: 날짜 필드 검증에서 실패하므로 이 after 모델 검증기는 실행되지 않습니다.


[이전 장](../05/README.md) · [다음 장](../07/README.md)
