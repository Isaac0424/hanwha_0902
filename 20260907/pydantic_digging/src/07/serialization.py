"""07. 검증한 객체를 딕셔너리/JSON으로 바꿔 다른 곳에 전달합니다."""
from datetime import datetime
from pydantic import BaseModel, Field, SecretStr, computed_field, field_serializer


class Receipt(BaseModel):
    created_at: datetime
    unit_price: int = Field(gt=0)
    quantity: int = Field(gt=0)
    # SecretStr은 출력 시 값을 가려 보여 주는 타입이지 암호화가 아닙니다.
    # exclude=True는 model_dump / model_dump_json 결과에서 이 필드를 제외합니다.
    api_key: SecretStr = Field(exclude=True)

    @computed_field  # 입력에 없는 계산 결과도 Pydantic 출력에 포함시킵니다.
    @property  # receipt.total()이 아니라 receipt.total로 계산값을 읽게 합니다.
    def total(self) -> int:
        """self는 영수증 객체. 단가 × 수량을 계산하여 정수로 반환합니다."""
        return self.unit_price * self.quantity

    # 입력 검증기가 아니라 "출력 형식"을 정하는 함수입니다.
    # when_used="json"이므로 JSON 모드로 내보낼 때만 실행합니다.
    @field_serializer("created_at", when_used="json")
    def serialize_date(self, value: datetime) -> str:
        """날짜 객체를 '2026-09-07T12:30:00'처럼 초까지 표시한 문자열로 만듭니다."""
        return value.isoformat(timespec="seconds")


def run(data):
    """같은 영수증을 세 가지 방식으로 내보내 반환 타입과 날짜 표현을 비교합니다."""
    receipt = Receipt.model_validate(data)
    python_dict = receipt.model_dump()  # dict이며 안의 날짜는 datetime 객체
    json_dict = receipt.model_dump(mode="json")  # dict이며 안의 날짜는 문자열
    json_text = receipt.model_dump_json()  # 전체가 JSON 형식의 str
    return {
        "Python 딕셔너리": python_dict,
        "JSON용 딕셔너리": json_dict,
        "JSON 문자열": json_text,
    }
