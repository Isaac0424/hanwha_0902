import sqlite3
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.post("send_messages")
def send_messages():
    pass

@app.delete("delete_messages")
def delete_messages():
    pass

@app.get("init_message")
def init_message():
    pass

@app.get("/")
def read_root():
    return {"Hello":"World"}