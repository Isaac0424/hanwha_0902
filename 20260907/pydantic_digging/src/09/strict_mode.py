"""09. 문자열 숫자를 정수로 바꾸지 않고, 입력 타입 자체를 엄격히 검사합니다."""
from pydantic import BaseModel, ConfigDict, Field


class Inventory(BaseModel):
    model_config = ConfigDict(
        strict=True,  # 이 예제에서 정수 3은 허용하지만 문자열 "3"은 거부합니다.
        extra="forbid",  # quantity 이외의 필드를 보내면 오류
        validate_assignment=True,  # 객체 생성 후 값을 다시 대입할 때도 검사
    )
    quantity: int = Field(ge=0)  # 재고는 0 이상


def run(data):
    """initial로 재고를 만든 뒤, assign 키가 있으면 수량을 바꿔 봅니다."""
    inventory = Inventory.model_validate(data["initial"])
    if "assign" in data:  # 키가 있는지 확인합니다. 값이 0이어도 실행합니다.
        inventory.quantity = data["assign"]  # 음수나 문자열이면 여기서 오류가 납니다.
    return inventory.model_dump()
