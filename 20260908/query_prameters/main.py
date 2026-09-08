from fastapi import FastAPI

app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"},{"item_name": "Baz"}]

''' 
쿼리는 url에서 "?" 후에 나오고 "&" 로 구분되는 key-value 쌍의 집합입니다. 
http://127.0.0.1:8000/items/?skip=0&limit=10 에서는 skip = 0 을  limit은 10을 가집니다.
fake_items_db에서 슬라이싱 하여 return  
'''

#http://127.0.0.1:8000/items/?skip=0&limit=10
@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]
'''
#http://127.0.0.1:8000/items/{"item_id : str"}?q={q: str}
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}
'''
#http://127.0.0.1:8000/items/{"item_id : str"}?q={q: str}|None&short=1|True|true|on|yes
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description" : "This is an amazing item that has a long description"}
        )
    return item


#http://127.0.0.1:8000/items/2/foo?needy=TEST&skip=3&limit=5
@app.get("/items/2/{item_id}")
async def read_user_item(
    item_id: str, needy: str, skip: int = 0, limit: int | None = None):
    item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
    return item