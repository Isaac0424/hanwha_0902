from fastapi import FastAPI

app = FastAPI()
#http://localhost:8888/
@app.get("/")
def read_root():
    return {"Hello" : "World"}

#http://localhost:8888/items/{555}
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id" : item_id, "q" : q}

#먼저 선언된 것이 호출된다. 
#http://localhost:8888/users
@app.get("/users")
async def read_users():
    return ["Rick", "Morty"]

@app.get("/users")
async def read_users2():
    return ["Bean", "Elfo"]

#따라서 다음과 같이 id로 들어온 것 보다 먼저 선언된 것에 의해 변수에 값이등록되지 않을 수도 있다.
#아래 두개의 예제는 read_user_me라는 함수가 호출된다. 
#http://localhost:8888/users/me
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}
#http://localhost:8888/users/{" ": str}
@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}

#enum class 
from enum import Enum

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"
#localhost:8000/models/{model_name}
@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    
    # model name Enum 멤버 비교 
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message" : "Deep Learning FTW"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    
    return {"model_name": model_name, "message": "Have some residuals"}

# file system 
#localhost:8000/files//home/johndoe/myfile.txt
#이런경우 2중 '/' 가 '//' 들어갈 수 있음

@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


# if __name__ == "__main__":
#     pass