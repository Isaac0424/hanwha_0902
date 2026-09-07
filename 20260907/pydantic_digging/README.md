# Pydantic을 처음 사용하는 사람을 위한 학습 예제

**처음에는 [01장 README](src/01/README.md)부터 읽으세요.** 코드만 읽다가 낯선 표현이 나오면 같은 폴더의 README에서 그 표현의 뜻과 입력·결과를 확인할 수 있습니다. Python 3.11 이상, Pydantic 2.11 이상 3 미만 기준이며 작성 환경은 Python 3.12 / Pydantic 2.13.5입니다.

## Pydantic은 무슨 일을 하나요?

외부에서 받은 데이터가 프로그램에서 요구하는 구조에 맞는지 검사하는 라이브러리입니다. 예를 들어 사용자 번호가 정수여야 한다고 정하면 문자열 "10"을 정수 10으로 바꾸거나, "hello"처럼 변환할 수 없는 값은 오류로 알려 줍니다.

```text
입력 데이터 → 정해 둔 규칙으로 검사·변환 → 프로그램에서 사용할 객체
```

여기서 규칙을 적은 클래스가 **모델**, 모델의 항목 하나가 **필드**입니다. BaseModel을 상속한 모델은 Pydantic의 검사 기능을 사용할 수 있습니다.

## 무엇부터 배우나요?

아래 표의 번호를 누르면 자세한 설명으로 이동합니다. 각 장은 사용 상황 → 문법·용어 → 모델과 함수 → 입력과 결과 → 오류 이유 → 연습 순서로 구성되어 있습니다.

| 장 | 주제 | 이 장을 읽고 답할 수 있는 질문 |
| --- | --- | --- |
| [01](src/01/README.md) | 모델, 필드, 기본값, None | None을 보내는 것과 키를 빼는 것은 어떻게 다른가? model_validate와 model_dump는 무엇을 반환하는가? |
| [02](src/02/README.md) | Field, Literal | 정수 타입 검사 외에 가격을 0 초과로 제한하려면? |
| [03](src/03/README.md) | 중첩 모델 | 주문 안의 여러 상품도 함께 검사하려면? |
| [04](src/04/README.md) | 별칭과 모델 설정 | 외부의 userId를 코드 안에서는 user_id로 쓰려면? |
| [05](src/05/README.md) | 필드 검증기 | 공백을 정리하거나 금지 이름을 검사하려면? |
| [06](src/06/README.md) | 모델 검증기 | 시작일과 종료일 두 값을 비교하려면? |
| [07](src/07/README.md) | 직렬화 | dict와 JSON 문자열은 무엇이 다르고 어떻게 내보내는가? |
| [08](src/08/README.md) | 부분 수정 | 소개를 유지하는 요청과 지우는 요청을 어떻게 구별하는가? |
| [09](src/09/README.md) | 엄격한 타입·재할당 | 문자열 숫자를 거부하거나 값을 바꿀 때도 검사하려면? |
| [10](src/10/README.md) | TypeAdapter | 최상위 데이터가 목록이면 어떻게 검사하는가? |
| [11](src/11/README.md) | 판별 필드가 있는 Union | 카드와 계좌처럼 종류별 입력 구조가 다르면? |
| [12](src/12/README.md) | 객체 속성 읽기 | 딕셔너리 대신 DB 조회 객체를 받았다면? |
| [13](src/13/README.md) | 제네릭·JSON Schema | 공통 페이지 구조에 상품/사용자 타입을 바꿔 넣으려면? |

01~03을 먼저 익힌 뒤 04~08로 넘어가세요. 09~13은 각 사용 상황을 이해하면서 진행하면 됩니다. 모르는 Python 문법도 각 장에서 함께 설명합니다.

## 설치와 실행

저장소 루트에서 다음 명령으로 이 학습 폴더로 이동합니다.

```powershell
cd 20260907/pydantic_digging
```

사용할 Python 환경에 Pydantic이 없다면 설치합니다. 이미 요구 버전이 있으면 생략합니다.

```powershell
python -m pip install -r requirements.txt
```

그다음 장을 골라 실행합니다.

```powershell
python main.py --list
python main.py 01
python main.py 05 06
python main.py all
```

--list는 목록 보기, 01은 1장 실행, 05 06은 두 장 실행, all은 전체 실행입니다. 인자를 쓰지 않아도 목록이 나옵니다. Windows에서 한글이 깨지면 `python -X utf8 main.py 01`로 실행하세요.

저장소 루트에서 이동 없이 실행할 수도 있습니다.

```powershell
python 20260907/pydantic_digging/main.py 01
```

## 어떤 파일을 읽고 고치나요?

```text
pydantic_digging/
├── README.md                 # 지금 읽는 전체 안내
├── main.py                   # 실행할 장 선택
├── input_data/
│   ├── README.md             # JSON 문법과 사례 수정 방법
│   ├── basic.json            # 01장 입력·예상 오류·해설
│   └── ...                   # 기능별 JSON 입력
├── src/
│   ├── README.md             # main/runner의 실행 흐름과 함수 설명
│   ├── 01/
│   │   ├── README.md         # 초보자용 상세 설명
│   │   └── basic.py          # 주석을 따라 읽는 모델·run 함수
│   ├── ...
│   ├── 13/
│   │   ├── README.md
│   │   └── generics.py
│   └── runner.py             # JSON 읽기, 사례 실행, 결과 비교
└── requirements.txt          # 필요한 외부 라이브러리
```

- **규칙을 바꾸려면** src/번호/기능명.py를 수정합니다.
- **검사할 값을 바꾸려면** input_data/기능명.json을 수정합니다.
- **왜 그런 결과가 나오는지 보려면** 같은 번호 폴더의 README를 읽습니다.

입력과 소스는 분리되어 있습니다. main과 runner를 먼저 완전히 이해할 필요는 없습니다. 실행 도구가 궁금해지면 [공통 실행 코드 안내](src/README.md)를 읽으세요.

## 입력 한 건은 어떻게 실행되나요?

```text
python main.py 01
→ main이 src/01/basic.py를 선택
→ runner가 input_data/basic.json을 읽음
→ 각 사례의 input만 basic.run(data)에 전달
→ User.model_validate로 검사
→ 성공하면 model_dump 결과, 실패하면 오류 위치 출력
```

run은 우리가 정한 학습용 함수 이름입니다. Pydantic에서 제공하는 메서드는 model_validate, model_dump 등입니다.

## 오류가 나왔는데 왜 PASS인가요?

학습에는 일부러 실패하도록 만든 입력도 있습니다. JSON의 expected_errors에 그 입력에서 예상한 오류 종류를 적어 둡니다.

| 표시 | 의미 |
| --- | --- |
| expected_errors가 [] | 성공을 기대하는 입력 |
| expected_errors가 ["missing"] | 필수 값 누락으로 실패할 것을 기대 |
| [PASS] | 실제 성공 여부와 오류 종류가 예상과 일치 |
| AssertionError | 예상한 성공·실패 또는 오류 종류와 실제가 다름 |

[PASS]는 모든 결과 값을 자동 검사했다는 뜻은 아닙니다. 출력 값과 오류 위치는 해설을 함께 읽으며 확인하세요. ValidationError는 Pydantic의 입력 검증 오류이고, AssertionError는 이 실행기의 “예상과 다르다”는 오류입니다.

## 추천하는 공부 방법

1. 01장 README를 읽고 각 필드의 뜻을 자신의 말로 설명해 봅니다.
2. basic.py의 주석을 따라 읽습니다.
3. basic.json의 입력을 보고 결과를 예상합니다.
4. 실행 결과와 “해설”을 비교합니다.
5. 한 번에 입력 하나만 바꿉니다. 성공/실패 의도를 바꿨다면 expected_errors도 수정합니다.

JSON에는 주석을 적을 수 없습니다. 메모는 각 사례의 explanation 문자열에 적을 수 있습니다. 구체적인 방법은 [입력 데이터 안내](input_data/README.md)에 있습니다.

## 다시 찾아볼 공식 문서

아래는 이 예제의 API를 확인할 때 참고한 Pydantic 공식 문서입니다. 처음부터 공식 문서 전체를 읽기보다 각 장에서 배운 기능을 다시 확인하는 용도로 사용하세요.

- [필드와 기본값](https://docs.pydantic.dev/latest/concepts/fields/)
- [모델](https://docs.pydantic.dev/latest/concepts/models/)
- [검증기](https://docs.pydantic.dev/latest/concepts/validators/)
- [직렬화](https://docs.pydantic.dev/latest/concepts/serialization/)
- [Union](https://docs.pydantic.dev/latest/concepts/unions/)
- [TypeAdapter](https://docs.pydantic.dev/latest/concepts/type_adapter/)
