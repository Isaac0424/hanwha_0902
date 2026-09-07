"""04. 외부 데이터의 이름과 Python 코드의 이름을 연결합니다."""
from pydantic import BaseModel, ConfigDict, Field


class Customer(BaseModel):
    # model_config는 데이터 필드가 아니라 모델 전체의 동작 설정입니다.
    # ConfigDict는 그 설정을 모아 적는 도구입니다.
    model_config = ConfigDict(
        validate_by_name=True,   # Python 필드명 user_id로도 입력 가능
        validate_by_alias=True,  # 별칭 userId로도 입력 가능
        extra="forbid",          # 정의하지 않은 추가 필드는 오류로 처리
    )
    # alias는 "별칭". 외부의 userId를 받아 내부에서는 customer.user_id로 읽습니다.
    user_id: int = Field(alias="userId")
    display_name: str = Field(alias="displayName")


def run(data):
    """두 종류의 입력 이름을 받아 내부 이름/외부 이름 출력을 비교합니다."""
    customer = Customer.model_validate(data)
    internal = customer.model_dump()  # {"user_id": ..., "display_name": ...}
    external = customer.model_dump(by_alias=True)  # {"userId": ..., "displayName": ...}
    return {"내부 이름": internal, "외부 이름": external}
