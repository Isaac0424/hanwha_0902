"""01. 처음 배우는 Pydantic: 자세한 설명은 같은 폴더의 README.md를 읽으세요."""
from datetime import datetime  # 날짜와 시간을 함께 표현하는 Python 타입
from pydantic import BaseModel, Field  # 검증 기능의 기반 클래스 / 필드 설정 함수


# 모델은 "사용자 데이터에 어떤 항목과 규칙이 필요한가"를 적은 설계도입니다.
# BaseModel을 상속하면 아래 타입 선언을 이용해 입력을 검사할 수 있습니다.
class User(BaseModel):
    # id는 필드 이름, int는 정수 타입입니다. 기본값이 없어 입력에서 필수입니다.
    # 기본 설정에서는 "10" 같은 문자열 숫자도 정수 10으로 바꿔 줍니다.
    id: int

    # = "익명"은 name을 보내지 않았을 때 대신 사용할 기본값입니다.
    # name=None을 보낸 경우는 생략한 것이 아니므로 문자열 타입 오류가 납니다.
    name: str = "익명"

    # "2026-09-07T09:00:00" 같은 문자열을 날짜·시간 객체로 변환합니다.
    joined_at: datetime

    # |는 "또는"입니다. 값으로 문자열 또는 None(값 없음)을 받습니다.
    # {"nickname": None}은 항목을 보낸 것이므로 성공합니다.
    # nickname 키 자체가 없으면 기본값이 없으므로 missing 오류입니다.
    # 생략까지 허용하려면 nickname: str | None = None으로 적습니다.
    nickname: str | None

    # list[str]: 문자열을 담는 목록. 예: ["python", "study"]
    # Field(): 이 필드의 기본값이나 추가 조건을 지정하는 함수입니다.
    # default_factory=list: tags를 생략하면 list()를 호출하여 새 []를 만듭니다.
    # list는 "나중에 호출할 함수"를 전달하므로 여기에는 괄호를 붙이지 않습니다.
    tags: list[str] = Field(default_factory=list)


def run(data):
    """입력 딕셔너리 한 개를 받아 검증 결과를 반환합니다. main에서 호출합니다."""
    # model_validate는 Pydantic이 제공하는 메서드(클래스에 속한 함수)입니다.
    # 성공: 검사·변환한 User 객체 반환. 실패: ValidationError 발생.
    # 원본 data는 딕셔너리지만 user는 user.id처럼 값을 읽는 User 객체입니다.
    user = User.model_validate(data)

    # model_dump는 User 객체의 값을 일반 Python 딕셔너리로 꺼냅니다.
    # 원본 입력을 돌려주는 것이 아니라 변환된 값과 채워진 기본값을 담습니다.
    result = user.model_dump()

    # type(user.id)는 값의 타입, .__name__은 타입 이름인 "int"를 뜻합니다.
    return {"결과": result, "id 타입": type(user.id).__name__}
