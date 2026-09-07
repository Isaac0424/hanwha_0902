"""05. 기본 타입 검증 앞뒤에 내가 만든 검사 함수를 끼워 넣습니다."""
from typing import Any  # 아직 어떤 타입인지 정하지 않은 입력을 나타냅니다.
from pydantic import BaseModel, field_validator


class Signup(BaseModel):
    username: str

    # @...는 아래 함수에 역할을 부여하는 Python의 데코레이터 문법입니다.
    # username 필드의 "기본 타입 검사 전(before)"에 trim을 실행하도록 등록합니다.
    @field_validator("username", mode="before")
    @classmethod  # 객체가 아닌 클래스에 속한 메서드. 첫 인자 cls는 Signup 클래스입니다.
    def trim(cls, value: Any) -> Any:
        """원본이 문자열이면 양끝 공백을 제거합니다. -> Any는 반환 타입 표기입니다."""
        # before에는 숫자도 올 수 있습니다. 숫자에 strip()을 호출하지 않도록 확인합니다.
        if isinstance(value, str):
            return value.strip()  # "  minsu  " → "minsu"
        return value  # 문자열이 아니면 그대로 넘겨 Pydantic이 타입을 검사하게 합니다.

    @field_validator("username", mode="after")
    @classmethod
    def check_name(cls, value: str) -> str:
        """타입 검사 후(after)에는 문자열이라는 전제로 업무 규칙을 검사합니다."""
        # len은 글자 수, lower()는 소문자 변환입니다.
        if len(value) < 3 or value.lower() == "admin":
            # ValueError를 발생시키면 Pydantic이 ValidationError로 모아 알려 줍니다.
            raise ValueError("이름은 3자 이상이며 admin은 사용할 수 없습니다.")
        # 반환한 값이 필드에 저장됩니다. return을 빼면 Python은 None을 반환합니다.
        return value


def run(data):
    """model_validate가 trim → 문자열 타입 검사 → check_name 순으로 실행합니다."""
    signup = Signup.model_validate(data)
    return signup.model_dump()
