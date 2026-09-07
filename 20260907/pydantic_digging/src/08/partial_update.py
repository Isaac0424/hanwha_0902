"""08. 이름/소개 중 사용자가 보낸 항목만 수정하는 요청을 처리합니다."""
from pydantic import BaseModel, ConfigDict, Field


class Profile(BaseModel):
    """실제로 저장할 최종 데이터의 규칙입니다."""
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1)  # 최종 이름은 None이나 빈 문자열이면 안 됩니다.
    bio: str | None = None  # 소개는 문자열/None 허용, 생략하면 기본값 None


class ProfilePatch(BaseModel):
    """일부 필드만 보내는 수정 요청입니다. 둘 다 생략할 수 있습니다."""
    model_config = ConfigDict(extra="forbid")
    # default=None은 생략 허용, min_length는 문자열이 들어온 경우에 적용됩니다.
    # 이 단계에서 받은 name=None은 마지막 Profile 재검증에서 거부합니다.
    name: str | None = Field(default=None, min_length=1)
    bio: str | None = None


def run(data):
    """원본 검증 → 요청 검증 → 보낸 항목만 합치기 → 최종 검증."""
    original = Profile.model_validate(data["original"])
    patch = ProfilePatch.model_validate(data["patch"])

    # unset은 "입력에서 지정하지 않음". 자동으로 채워진 기본값 필드를 제외합니다.
    # patch={}면 changes={}, patch={"bio": None}면 changes={"bio": None}입니다.
    changes = patch.model_dump(exclude_unset=True)

    # **는 딕셔너리의 항목을 펼칩니다. 같은 키는 오른쪽 changes 값으로 덮어씁니다.
    merged = {**original.model_dump(), **changes}

    # 합친 딕셔너리를 최종 저장 규칙으로 재검증합니다.
    # model_copy(update=...)는 수정 값을 검증하지 않으므로 이 과정의 대체가 아닙니다.
    updated = Profile.model_validate(merged)
    return {"실제 수정 필드": changes, "최종 프로필": updated.model_dump()}
