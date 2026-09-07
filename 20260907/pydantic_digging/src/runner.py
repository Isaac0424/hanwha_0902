"""각 장에 공통인 실행 도구입니다. Pydantic 개념은 src/01부터 먼저 읽으세요."""
import json  # JSON 텍스트를 Python dict/list로 바꿉니다.
from pathlib import Path  # 파일 경로를 다루는 Python 도구
from pprint import pprint  # 딕셔너리와 목록을 읽기 쉽게 출력
from pydantic import ValidationError  # Pydantic 검증 실패를 나타내는 예외 타입

# __file__은 현재 runner.py의 경로입니다.
# parents[0]은 src, parents[1]은 pydantic_digging 폴더입니다.
# 실행하는 터미널 위치가 달라도 같은 input_data 폴더를 찾습니다.
DATA_DIR = Path(__file__).resolve().parents[1] / "input_data"


def run_cases(name, run):
    """기능 이름과 그 기능의 run 함수를 받아 모든 입력 사례를 실행합니다.

    예: run_cases("basic", basic.run)
    두 번째 인자는 함수를 호출한 결과가 아니라 함수 자체입니다.
    이 함수 안에서 사례별로 run(입력)을 호출합니다.
    """
    input_path = DATA_DIR / f"{name}.json"
    json_text = input_path.read_text(encoding="utf-8")
    cases = json.loads(json_text)  # JSON null → None, true → True; 아직 모델 검증 전

    for case in cases:
        print(f"\n--- {case['title']} ---")
        print("입력:")
        pprint(case["input"], sort_dicts=False)
        # explanation은 학습용 설명이며 모델의 입력 필드가 아닙니다.
        if "explanation" in case:
            print(f"해설: {case['explanation']}")

        # expected_errors는 "실패해야 하는 오류 종류" 목록입니다. []면 성공을 기대합니다.
        # 오류 순서에 상관없이 비교하기 위해 두 목록을 sorted로 정렬합니다.
        expected = sorted(case["expected_errors"])
        try:
            result = run(case["input"])  # title/expected_errors는 모델에 전달하지 않습니다.
        except ValidationError as error:
            # errors()는 오류별 위치, 종류, 설명을 담은 딕셔너리 목록을 반환합니다.
            actual = sorted(item["type"] for item in error.errors())
            if actual != expected:
                # 이 오류는 Pydantic 입력 오류와 다릅니다. 학습용 예상과 실제가 다릅니다.
                raise AssertionError(f"예상 오류 {expected}, 실제 오류 {actual}") from error

            print("예상한 검증 오류:")
            for item in error.errors(include_url=False, include_input=False):
                # loc 예: ("items", 1, "quantity") → "items.1.quantity"
                location = ".".join(map(str, item["loc"])) or "(모델 전체)"
                print(f"  {location}: {item['msg']} [{item['type']}]")
        else:
            # try에서 ValidationError가 발생하지 않은 경우에만 실행합니다.
            if expected:
                raise AssertionError(f"오류 {expected}가 발생해야 하지만 성공했습니다.")
            print("결과:")
            pprint(result, sort_dicts=False)
        # 실패를 예상한 사례가 예상대로 실패한 경우도 PASS입니다.
        print("[PASS] 성공 여부와 오류 종류가 예상과 일치")
    return len(cases)  # main에서 전체 실행 사례 수를 합산하는 데 사용합니다.
