"""13. 공통 응답 구조를 유지하며 목록에 들어갈 모델만 바꿉니다."""
from typing import Generic, TypeVar
from pydantic import BaseModel, Field

# T는 구체적인 타입을 나중에 채울 자리입니다. 실제 상품 데이터 변수가 아닙니다.
T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """여러 항목과 전체 검색 개수를 담는 응답. Generic[T]는 타입을 바꿔 쓰게 합니다."""
    items: list[T]  # Page[Product]에서는 list[Product]로 검증합니다.
    total: int = Field(ge=0)  # 전체 검색 결과 수. 현재 페이지 항목 수와 다를 수 있습니다.


class Product(BaseModel):
    """상품 페이지의 항목 한 개를 정의합니다."""
    id: int
    name: str


def run(data):
    """T 자리에 Product를 넣어 상품 목록의 각 항목도 검증합니다."""
    page = Page[Product].model_validate(data)
    result = page.model_dump()

    # JSON Schema는 실제 데이터가 아니라 "어떤 데이터 구조를 받는가"라는 설명입니다.
    # properties는 스키마의 필드 설명 사전입니다. list(사전)는 키 목록을 만듭니다.
    schema = Page[Product].model_json_schema()
    property_names = list(schema["properties"])
    return {"결과": result, "스키마 속성": property_names}
