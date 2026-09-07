"""10. 최상위 입력이 딕셔너리가 아닌 목록일 때 전체 목록을 검증합니다."""
from typing import Annotated  # 기본 타입 옆에 추가 정보를 붙이는 표기
from pydantic import BaseModel, Field, TypeAdapter


class Row(BaseModel):
    """목록에 들어갈 한 행의 구조입니다. sku는 상품을 구분하는 코드입니다."""
    sku: str
    # Annotated[기본 타입, 추가 조건]: 정수이며 0보다 커야 합니다.
    # 여기서는 quantity: int = Field(gt=0)과 같은 검증 목적입니다.
    quantity: Annotated[int, Field(gt=0)]


# Row는 한 행의 규칙. TypeAdapter(list[Row])는 "Row 목록 전체"의 검증 도구입니다.
# 함수 밖에서 한 번 만들면 run을 여러 번 실행해도 도구를 재사용합니다.
rows_adapter = TypeAdapter(list[Row])


def run(data):
    """목록을 받아 각 행을 검증한 후 일반 딕셔너리들의 목록을 반환합니다."""
    # TypeAdapter에는 model_validate 대신 validate_python이라는 메서드가 있습니다.
    rows = rows_adapter.validate_python(data)  # 결과는 list[Row]
    # Row 객체들을 JSON에 담을 수 있는 일반 값으로 바꿉니다. 전체 결과는 list입니다.
    result = rows_adapter.dump_python(rows, mode="json")
    return result
