import sqlite3
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
DB_PATH = Path(__file__).with_name("requests.db")


def init_db():
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL
            )
            """
        )


init_db()


class UserRequest(BaseModel):
    name: str
    age: int


@app.post("/predict")
def predict(request: UserRequest):
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute(
            "INSERT INTO user_requests (name, age) VALUES (?, ?)",
            (request.name, request.age),
        )
        request_id = cursor.lastrowid

    return {
        "request_id": request_id,
        "result_message": f"{request.name}님은 {request.age}세입니다.{"성인" if request.age>=20 else "미성년자"}입니다.",
    }


@app.get("/requests")
def get_requests():
    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT id, name, age FROM user_requests ORDER BY id DESC"
        ).fetchall()

    return [dict(row) for row in rows]

@app.get("/")
def read_root():
    return {"Hello":"World"}