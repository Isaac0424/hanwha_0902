from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ItemSchema(BaseModel):
    name: str
    price: float
    description: str | None = None
    
items_db: dict[int, dict] = {}
id_counter = 1


#C: Create 생성
#127.0.0.1:8000/items
@app.post("/items/", status_code=201)
async def create_item(item: ItemSchema):
    global id_counter
    new_item = item.model_dump()
    new_item["id"] = id_counter
    
    items_db[id_counter] = new_item
    id_counter += 1
    
    return {"message": "생성 완료", "data": new_item}
    

#R: Read 조회(전체) - Select
@app.get("/items/")
async def get_all_items():
    return {"message": "전체 목록 조회 완료", "data": items_db}

#R: Read 조회(단일) - Select
@app.get("/items/{item_id}")
async def get_single_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail= "아이템을 찾을 수 없습니다.")

    return {"message": f"{item_id}조회 완료", "data":items_db[item_id]}
    
#U: Update 수정
@app.put("/items/{item_id}")
async def modify_item(item_id: int, item: ItemSchema):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail= "아이템을 찾을 수 없습니다.")
    updated_data = item.model_dump()
    updated_data["id"] = item_id
    items_db[item_id] = updated_data
    
    return {"message": "수정 완료", "data": updated_data}

#D: Delete 삭제
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다.")
    
    deleted_item = items_db.pop(item_id)
    return {"message": "삭제 완료", "data": deleted_item}