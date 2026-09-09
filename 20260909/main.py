from fastapi import FastAPI, HTTPException, Query
from typing import Annotated
import re
from pydantic import BaseModel, Field, StringConstraints

app = FastAPI()
PHONE_NUMBER_PATTERN = r"^(01[016789])-?(\d{3,4})-?(\d{4})$"

class UserInformation(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3)]
    age: int = Field(ge=0)
    phone_number: str | None = Field(
        default=None,
        pattern=PHONE_NUMBER_PATTERN,
    )


user_db = {
    1: UserInformation(name="isaac", age=31, phone_number="010-1234-1234"),
    2: UserInformation(name="dykim", age=25, phone_number=None),
    3: UserInformation(name="alice", age=28, phone_number="010-2345-6789"),
    4: UserInformation(name="bruce", age=35, phone_number="010-3456-7890"),
    5: UserInformation(name="chris", age=22, phone_number="011-456-7890"),
    6: UserInformation(name="diana", age=29, phone_number="016-567-8901"),
    7: UserInformation(name="eric", age=41, phone_number=None),
    8: UserInformation(name="fiona", age=26, phone_number="017-678-9012"),
    9: UserInformation(name="george", age=33, phone_number="018-789-0123"),
    10: UserInformation(name="helen", age=30, phone_number="019-890-1234"),
}
    

def normalize_phone_number(phone_number: str) -> str:
    match = re.fullmatch(PHONE_NUMBER_PATTERN, phone_number)
    if match is None:
        raise ValueError("올바른 전화번호 형식이 아닙니다.")
    area_code, middle, last = match.groups()
    return f"{area_code}-{middle}-{last}"


@app.get("/")
async def root():
    return {"message" : "hello world"}

@app.get("/user/")
async def read_user(name : str,q: Annotated[str | None, Query(max_length=50)] = None):
    results = {"name":name, "items":[{"item_id":"Foo"}, {"item_id":"Bar"}], "query":q}
    if q:
        results.update({"q":q})
    return results

@app.get("/user/{name_id}")
async def read_user(name_id:str, phone_number: Annotated[str | None, Query(pattern=PHONE_NUMBER_PATTERN)] = None):
    results = {"name":name_id, "items":[{"item_id":"Foo"}, {"item_id":"Bar"}]}
    if phone_number:
        results.update({"phone_number": normalize_phone_number(phone_number)})
    return results

@app.put("/update/")
async def update_user_inform(user:UserInformation):
    if user.phone_number:
        user = user.model_copy(
            update={"phone_number": normalize_phone_number(user.phone_number)}
        )

    user_id = max(user_db, default=0) + 1
    user_db[user_id] = user
    return {"message": "사용자가 추가되었습니다.", "user_id": user_id, "user": user}

@app.delete("/user-db/{user_id}")
async def delete_user(user_id: int):
    if user_id not in user_db:
        raise HTTPException(
            status_code=404,
            detail="사용자를 찾을 수 없습니다.",
        )
    
    delete_user = user_db.pop(user_id)
    
    return {
        "message": "사용자가 삭제되었습니다.",
        "user_id": user_id,
        "user": delete_user,
    }