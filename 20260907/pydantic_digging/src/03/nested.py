"""03. 주문 안의 상품 목록까지 모델을 사용해 검사합니다."""
from pydantic import BaseModel, Field


class Item(BaseModel):
    """주문에 담긴 상품 한 개의 구조입니다."""
    product_id: int
    quantity: int = Field(gt=0)  # 한 개 이상 주문해야 합니다.


class Order(BaseModel):
    """주문 한 건: 고객 번호와 여러 상품으로 구성됩니다."""
    customer_id: int
    # list[Item]: Item 객체가 여러 개 들어 있는 목록이라는 뜻입니다.
    # 입력의 각 딕셔너리를 Pydantic이 Item 객체로 만들며 수량도 검사합니다.
    # 목록에 붙인 min_length=1은 "상품을 적어도 하나 담아야 한다"입니다.
    items: list[Item] = Field(min_length=1)


def run(data):
    """주문 전체를 한 번 검증하면 안쪽 Item도 함께 검증됩니다."""
    order = Order.model_validate(data)
    # order.items[0]은 첫 Item 객체이고 order.items[0].quantity로 수량을 읽습니다.
    # model_dump()는 안쪽 Item도 재귀적으로(안으로 들어가며) 딕셔너리로 바꿉니다.
    result = order.model_dump()
    return result
