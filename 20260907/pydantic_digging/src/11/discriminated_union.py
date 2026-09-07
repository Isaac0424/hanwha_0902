"""11. 결제 종류에 따라 서로 다른 필수 항목을 검사합니다."""
from typing import Annotated, Literal
from pydantic import BaseModel, Field


class CardPayment(BaseModel):
    # type은 이 입력의 분류 이름입니다. Python 내장 type() 호출과는 별개입니다.
    type: Literal["card"]
    card_token: str = Field(min_length=1)  # 실제 카드번호 대신 학습용 토큰 문자열


class BankPayment(BaseModel):
    type: Literal["bank"]
    # pattern은 문자열 모양을 검사하는 정규표현식입니다.
    # r은 역슬래시를 유지하는 문자열 표기, ^는 시작, \d는 숫자, {3}은 3번, $는 끝.
    bank_code: str = Field(pattern=r"^\d{3}$")


class Checkout(BaseModel):
    amount: int = Field(gt=0)
    # A | B는 A 또는 B 타입이라는 뜻입니다.
    # discriminator="type"은 payment 안의 type 값을 보고 사용할 모델을 고릅니다.
    # card면 CardPayment, bank면 BankPayment의 필수 필드를 검사합니다.
    payment: Annotated[CardPayment | BankPayment, Field(discriminator="type")]


def run(data):
    """선택된 결제 모델의 이름과 검증된 결제 내용을 함께 반환합니다."""
    checkout = Checkout.model_validate(data)
    selected_model = type(checkout.payment).__name__
    return {"선택 모델": selected_model, "결과": checkout.model_dump()}
