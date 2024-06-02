import sqlite3 as sql
import uuid

from data.model.user import User


class UserRepository:
    def __init__(self, filename: str):
        self._conn = sql.connect(filename, check_same_thread=False)

    async def authenticate(self, login: str, password: str) -> str | None:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM users WHERE login = ?", (login,))
        users = cur.fetchall()
        if users is None or len(users) == 0:
            token = str(uuid.uuid4())
            cur.execute(
                "INSERT INTO users (login, password, token) VALUES (?, ?, ?)",
                (login, password, token),
            )
            self._conn.commit()
            return token
        if users[0][2] == password:
            return users[0][3]
        return None

    async def get_user_by_token(self, token: str) -> User | None:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM users WHERE token = ?", (token,))
        user = cur.fetchone()
        if user is None:
            return None
        return User(id=user[0], name=user[1])

    def close(self):
        self._conn.close()
