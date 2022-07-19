import os
import sqlite3
from typing import List

from smart_sec_cam.auth.models import User


class AuthDatabase:
    DATABASE_DIR = "data/"
    FILE_TYPE = ".db"
    USER_TABLE = "users"

    def __init__(self, db_name: str = "smart-sec-cam"):
        self.db_name = db_name
        self.conn = sqlite3.connect(os.path.join(self.DATABASE_DIR, self.db_name + self.FILE_TYPE))

    def setup(self):
        cursor = self.conn.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.USER_TABLE} "
                       f"(id, username, salt, hash)")
        self.conn.commit()

    def add_user(self, user: User):
        cursor = self.conn.cursor()
        # Throw an error if this user already exists
        if self.get_user_by_username_or_id(user.user_id, user.username):
            raise ValueError("A user with this user id or username already exists")
        # Create User
        cursor.execute(f"INSERT INTO {self.USER_TABLE} VALUES (?, ?, ?, ?)",
                       (user.user_id, user.username, user.salt, user.password_hash))
        self.conn.commit()

    def get_user_by_id(self, user_id: str) -> User:
        cursor = self.conn.cursor()
        result = cursor.execute(f"SELECT * FROM {self.USER_TABLE} WHERE id = ?", (user_id,))
        if result:
            user_data = result.fetchone()
            return User(user_data[1], user_data[0], user_data[2], user_data[3])

    def get_user_by_username(self, username: str) -> User:
        cursor = self.conn.cursor()
        result = cursor.execute(f"SELECT * FROM {self.USER_TABLE} WHERE username= ?", (username,))
        if result:
            user_data = result.fetchone()
            return User(user_data[0], user_data[1], user_data[2], user_data[3])

    def get_user_by_username_or_id(self, user_id: str, username: str) -> List[User]:
        cursor = self.conn.cursor()
        users = []
        for row in cursor.execute(f"SELECT * FROM {self.USER_TABLE} WHERE id = ? OR username = ?", (user_id, username)):
            user = User(row[0], row[1], row[2], row[3])
            users.append(user)
        return users
