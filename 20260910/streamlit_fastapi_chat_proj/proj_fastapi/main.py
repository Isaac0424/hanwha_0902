import sqlite3
import secrets
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

DATABASE_DIR = Path(__file__).parent / "database"
DATABASE_DIR.mkdir(exist_ok=True)
CHAT_DB_PATH = DATABASE_DIR / "chat.db"

def init_db():
    with sqlite3.connect(CHAT_DB_PATH) as chat_db_connection:
        chat_db_connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                session_token TEXT,
                last_seen TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        for column, definition in (
            ("session_token", "TEXT"),
            ("last_seen", "TEXT"),
        ):
            try:
                chat_db_connection.execute(
                    f"ALTER TABLE users ADD COLUMN {column} {definition}"
                )
            except sqlite3.OperationalError:
                pass
        chat_db_connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

init_db()


class MessageRequest(BaseModel):
    name: str
    message: str
    session_token: str


class NameRequest(BaseModel):
    name: str


class SessionRequest(BaseModel):
    name: str
    session_token: str


@app.post("/init_name")
def init_name(request: NameRequest):
    name = request.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="이름을 입력해 주세요.")

    try:
        session_token = secrets.token_urlsafe(32)
        with sqlite3.connect(CHAT_DB_PATH) as chat_db_connection:
            chat_db_connection.execute(
                """
                INSERT INTO users (username, session_token, last_seen)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                (name, session_token),
            )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="이미 사용 중인 이름입니다.")

    return {"name": name, "session_token": session_token}


@app.post("/login_name")
def login_name(request: NameRequest):
    name = request.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="이름을 입력해 주세요.")

    with sqlite3.connect(CHAT_DB_PATH) as chat_db_connection:
        row = chat_db_connection.execute(
            "SELECT username, session_token, last_seen "
            "FROM users WHERE username = ?",
            (name,),
        ).fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="등록된 이름이 없습니다.")

        active_session = row[1] is not None and chat_db_connection.execute(
            "SELECT 1 FROM users WHERE username = ? "
            "AND last_seen > datetime('now', '-5 minutes')",
            (name,),
        ).fetchone()
        if active_session:
            raise HTTPException(
                status_code=409,
                detail="이미 다른 세션에서 사용 중인 이름입니다.",
            )

        session_token = secrets.token_urlsafe(32)
        chat_db_connection.execute(
            "UPDATE users SET session_token = ?, last_seen = CURRENT_TIMESTAMP "
            "WHERE username = ?",
            (session_token, name),
        )

    return {"name": row[0], "session_token": session_token}


def refresh_session(request: SessionRequest):
    with sqlite3.connect(CHAT_DB_PATH) as chat_db_connection:
        cursor = chat_db_connection.execute(
            "UPDATE users SET last_seen = CURRENT_TIMESTAMP "
            "WHERE username = ? AND session_token = ? "
            "AND last_seen > datetime('now', '-5 minutes')",
            (request.name, request.session_token),
        )

    if cursor.rowcount == 0:
        raise HTTPException(status_code=401, detail="세션이 만료되었습니다.")

    return {"message": "세션이 갱신되었습니다."}


@app.post("/heartbeat")
def heartbeat(request: SessionRequest):
    return refresh_session(request)


@app.post("/logout")
def logout(request: SessionRequest):
    with sqlite3.connect(CHAT_DB_PATH) as chat_db_connection:
        chat_db_connection.execute(
            "UPDATE users SET session_token = NULL, last_seen = NULL "
            "WHERE username = ? AND session_token = ?",
            (request.name, request.session_token),
        )

    return {"message": "로그아웃되었습니다."}


@app.post("/send_messages")
def send_messages(request: MessageRequest):
    with sqlite3.connect(CHAT_DB_PATH) as chat_db_connection:
        cursor = chat_db_connection.execute(
            "UPDATE users SET last_seen = CURRENT_TIMESTAMP "
            "WHERE username = ? AND session_token = ? "
            "AND last_seen > datetime('now', '-5 minutes')",
            (request.name, request.session_token),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=401, detail="세션이 만료되었습니다.")

        chat_db_connection.row_factory = sqlite3.Row
        message_cursor = chat_db_connection.execute(
            "INSERT INTO messages (name, message) VALUES (?, ?)",
            (request.name, request.message),
        )
        row = chat_db_connection.execute(
            "SELECT id, name, message, created_at FROM messages WHERE id = ?",
            (message_cursor.lastrowid,),
        ).fetchone()

    return dict(row)


@app.get("/messages")
def get_messages():
    with sqlite3.connect(CHAT_DB_PATH) as chat_db_connection:
        chat_db_connection.row_factory = sqlite3.Row
        rows = chat_db_connection.execute(
            "SELECT id, name, message, created_at "
            "FROM messages ORDER BY id ASC"
        ).fetchall()

    return [dict(row) for row in rows]

@app.delete("/delete_messages")
def delete_messages():
    with sqlite3.connect(CHAT_DB_PATH) as chat_db_connection:
        chat_db_connection.execute("DELETE FROM messages")

    return {"message": "모든 메시지를 삭제했습니다."}

@app.get("/")
def read_root():
    return {"Hello":"World"}