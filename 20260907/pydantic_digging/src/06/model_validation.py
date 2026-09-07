"""06. 날짜 각각의 타입뿐 아니라 두 날짜 사이의 관계도 검사합니다."""
from datetime import date  # 시각 없이 연·월·일을 나타내는 타입
from typing import Self  # 이 메서드가 자신과 같은 모델 타입을 반환한다는 표기
from pydantic import BaseModel, model_validator


class Reservation(BaseModel):
    start: date  # 날짜 문자열을 date 객체로 바꿉니다.
    end: date

    # 필드 검사가 모두 성공한 뒤 완성된 모델을 한 번 더 검사합니다.
    @model_validator(mode="after")
    def check_period(self) -> Self:
        """self는 검사 중인 Reservation 객체입니다. 날짜 두 개를 함께 읽습니다."""
        if self.end <= self.start:
            raise ValueError("종료일은 시작일보다 뒤여야 합니다.")
        return self  # 검증한 모델 객체를 반환해야 합니다.


def run(data):
    """날짜 타입 변환 → 기간 관계 검증 → 딕셔너리 반환 순서입니다."""
    reservation = Reservation.model_validate(data)
    return reservation.model_dump()
