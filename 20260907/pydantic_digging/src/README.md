# main과 runner는 어떻게 연결되나요?

[전체 안내](../README.md)

이 문서는 Pydantic 모델이 아닌 **학습용 실행 도구** 설명입니다. 처음에는 01장의 User부터 공부하고, 장 선택이나 JSON 읽기 동작이 궁금할 때 읽으세요.

## 전체 흐름

```text
터미널에서 python main.py 01
→ main()이 번호를 읽음
→ src.01.basic 모듈을 불러옴
→ run_cases("basic", basic.run) 호출
→ basic.json의 각 사례마다 basic.run(case["input"]) 호출
→ 결과 또는 오류 비교·출력
```

**모듈**은 여기서는 Python 코드 파일입니다. **함수를 전달한다**는 것은 그 함수를 나중에 호출할 수 있도록 함수 자체를 다른 함수의 인자로 주는 것입니다.

## main.py의 이름과 함수

| 이름 | 역할 |
| --- | --- |
| LESSONS | "01"을 화면 제목과 "basic" 파일명에 연결하는 딕셔너리 |
| main() | 실행 인자 읽기, 선택 확인, 모듈 로딩, 사례 실행 |
| argparse.ArgumentParser | 명령줄 인자를 해석하는 Python 표준 도구 |
| add_argument("lessons", nargs="*") | 장 번호를 0개 이상 받도록 등록 |
| add_argument("--list", action="store_true") | --list가 있으면 True가 되는 선택 항목 등록 |
| parse_args() | 실제 명령줄을 읽어 args에 저장 |
| import_module("src.01.basic") | 번호 폴더 안의 코드 모듈을 불러오기 |

숫자로만 된 폴더 이름은 일반적인 `from src.01.basic import User` 문법으로 쓸 수 없어 문자열 경로를 쓰는 import_module을 사용합니다.

args.lessons가 ["all"]이면 모든 번호를 선택하고, 그 외에는 zfill(2)로 "1"도 "01"로 맞춥니다. `if __name__ == "__main__"`은 파일을 직접 실행했을 때만 main()을 호출하는 Python 관례입니다.

main 안에서 직접 기능을 호출하려면 다음처럼 씁니다.

```python
basic = import_module("src.01.basic")
run_cases("basic", basic.run)
```

basic.run 뒤에 괄호가 없는 이유는 여기서 바로 실행하지 않고 run_cases에 **함수 자체를 전달**하기 때문입니다.

## runner.py의 함수

`run_cases(name, run)`은 기능 이름과 실행할 함수를 받습니다. 전체 처리한 사례 수(int)를 반환하여 main이 실행 건수를 합산할 수 있게 합니다.

| 코드 | 뜻 |
| --- | --- |
| Path(__file__).resolve() | 현재 runner.py의 절대 경로 |
| parents[1] / "input_data" | 학습 폴더 아래 input_data 경로 |
| read_text(encoding="utf-8") | 파일 내용을 한글을 포함한 문자열로 읽기 |
| json.loads(json_text) | JSON 문자열을 Python 값으로 읽기 |
| pprint(value) | 중첩 목록/딕셔너리를 보기 좋게 출력 |
| run(case["input"]) | 한 사례의 input만 해당 장 함수에 전달 |
| sorted(...) | 순서에 상관없이 오류 목록을 비교하려고 정렬 |

## 예외 처리 흐름

```text
try: 해당 장의 run 실행
├── ValidationError 발생 → except에서 예상 오류와 비교
└── 정상 반환 → else에서 성공을 기대했는지 확인하고 결과 출력
```

try/except/else는 Python의 오류 처리 문법입니다. Pydantic이 만든 ValidationError의 `errors()` 메서드는 오류 정보를 딕셔너리 목록으로 반환합니다.

- loc: 오류 위치. ("items", 1, "quantity")이면 두 번째 상품의 수량.
- type: 오류 종류. greater_than 등.
- msg: 사람이 읽는 설명.

runner는 위치를 점으로 연결해 출력하며, 비어 있는 위치는 "(모델 전체)"라고 표시합니다. 실제 성공 여부와 오류 종류가 예상과 다르면 AssertionError를 발생시킵니다.

## 각 장의 공통 run(data)

run은 우리가 만든 함수 이름입니다. Pydantic이 반드시 요구하는 이름이 아닙니다. 각 장을 동일한 방법으로 호출하기 위해 이렇게 맞췄습니다.

대부분의 장은 딕셔너리 한 개를 받고 딕셔너리를 반환합니다. 10장은 목록을 받고 목록을 반환합니다. 입력 파일 읽기는 runner가 맡으므로 모델 코드 안에 입력값을 적을 필요가 없습니다.
