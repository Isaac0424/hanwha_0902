"""12. 딕셔너리 대신 점(.)으로 값을 읽는 객체를 모델로 바꿉니다."""
from types import SimpleNamespace  # 받은 값을 .id, .name처럼 읽을 수 있는 간단한 객체
from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    # from_attributes=True: 입력 객체의 속성(row.id, row.name)에서 값을 읽습니다.
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


def run(data):
    """DB 없이 일반 객체를 만들어 ORM 조회 결과를 변환하는 상황을 연습합니다."""
    # **data는 {"id": 1, "name": "민수"}를 id=1, name="민수" 인자로 펼칩니다.
    row = SimpleNamespace(**data)
    # 딕셔너리 키가 아니라 row.id와 row.name 속성을 읽어 검사합니다.
    user = UserResponse.model_validate(row)
    # 응답 모델에 선언한 id, name만 출력됩니다. internal_memo는 포함되지 않습니다.
    return user.model_dump()
