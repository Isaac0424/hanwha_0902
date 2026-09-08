"""02. 타입에 더해 길이·숫자 범위·허용 값을 검사합니다."""
from typing import Literal  # 대괄호에 적힌 값 중 하나만 허용하는 타입 표기
from pydantic import BaseModel, Field


class Product(BaseModel):
    # str만 적으면 길이 제한이 없습니다. Field로 2~30자 조건을 더합니다.
    # Field에 default가 없으므로 = Field(...)라고 해도 필수 입력입니다.
    name: str = Field(min_length=2, max_length=30)
    # gt: greater than(초과). 0은 실패, 1은 성공. 가격은 원 단위 정수입니다.
    price: int = Field(gt=0)
    # ge: greater than or equal(이상). 재고 0은 허용합니다.
    stock: int = Field(ge=0)
    # str 타입이면서 정확히 "book" 또는 "food"인 값만 받습니다.
    category: Literal["book", "food"]


def run(data):
    """상품 입력 한 개를 검사하고 검증된 값을 딕셔너리로 반환합니다."""
    product = Product.model_validate(data)  # 실패하면 아래 줄로 진행하지 않습니다.
    result = product.model_dump()  # 성공한 Product 객체 → 딕셔너리
    return result
