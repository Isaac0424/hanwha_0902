"""실행: python main.py --list / python main.py 01 / python main.py all"""
import argparse  # 터미널에서 적은 01, all, --list 같은 실행 인자를 읽는 도구
from importlib import import_module  # 문자열 경로로 Python 모듈(코드 파일)을 불러옵니다.
from src.runner import run_cases

# 숫자 폴더는 일반 from 문 대신 import_module로 불러온다.
# 직접 호출: run_cases("basic", import_module("src.01.basic").run)
# 딕셔너리의 키는 장 번호, 값은 (화면 제목, 코드 파일명) 튜플입니다.
LESSONS = {
    "01": ("기초: 타입 변환·기본값·None", "basic"),
    "02": ("기초: Field와 Literal 제약", "constraints"),
    "03": ("기초: 중첩 모델과 주문 목록", "nested"),
    "04": ("실무: 별칭과 알 수 없는 필드", "aliases"),
    "05": ("실무: 필드 검증기", "field_validation"),
    "06": ("실무: 모델 검증기", "model_validation"),
    "07": ("실무: 직렬화와 계산 필드", "serialization"),
    "08": ("실무: 부분 수정 PATCH", "partial_update"),
    "09": ("상황별: 엄격한 타입과 재할당", "strict_mode"),
    "10": ("상황별: TypeAdapter 목록 검증", "type_adapter"),
    "11": ("고급: 판별 필드로 모델 선택", "discriminated_union"),
    "12": ("상황별: ORM 속성 읽기", "from_attributes"),
    "13": ("고급: 제네릭 페이지 응답", "generics"),
}


def main():
    """실행 인자 읽기 → 장 선택 → 해당 장의 입력 사례 실행."""
    parser = argparse.ArgumentParser(description="Pydantic 기능별 학습")
    # lessons는 우리가 정한 인자 이름. nargs="*"는 장 번호를 0개 이상 받는다는 뜻입니다.
    parser.add_argument("lessons", nargs="*", help="예: 01 또는 01 05 08 또는 all")
    # store_true: --list를 붙이면 args.list가 True, 없으면 False가 됩니다.
    parser.add_argument("--list", action="store_true", help="학습 목록 보기")
    args = parser.parse_args()  # 예: 01 05 → args.lessons == ["01", "05"]
    if args.list or not args.lessons:
        for number, (title, _) in LESSONS.items():
            print(f"{number}. {title}")
        print("\n실행 예: python main.py 01 / python main.py 05 06 / python main.py all")
        return
    if args.lessons == ["all"]:
        selected = list(LESSONS)  # 딕셔너리의 모든 장 번호를 목록으로 가져옵니다.
    else:
        # zfill(2): "1"처럼 입력해도 앞에 0을 채워 "01"로 만듭니다.
        selected = [number.zfill(2) for number in args.lessons]
    if any(number not in LESSONS for number in selected):
        parser.error("01~13 또는 단독으로 all을 입력하세요.")
    count = 0
    for number in selected:
        title, name = LESSONS[number]
        # 예: "src.01.basic" → src/01/basic.py를 불러옵니다.
        module = import_module(f"src.{number}.{name}")
        print(f"\n=== {number}. {title} ===")
        # module.run은 해당 장의 run 함수 자체입니다. runner가 입력별로 호출합니다.
        count += run_cases(name, module.run)
    print(f"\n완료: {len(selected)}개 기능, {count}개 입력 사례 통과")


# 이 파일을 python main.py로 직접 실행할 때만 main()을 호출합니다.
if __name__ == "__main__":
    main()
