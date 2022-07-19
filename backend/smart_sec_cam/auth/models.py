import os
import hashlib
import uuid


class User:
    SALT_LENGTH = 32
    HASH_ALGORITHM = 'sha256'
    PASSWORD_ENCODING = 'utf-8'
    HASH_ITERS = 100000

    def __init__(self, username: str, user_id: str = None, salt: bytes = None, password_hash: str = None):
        self.user_id = user_id
        self.username = username
        self.salt = salt
        self.password_hash = password_hash

    def generate_id(self):
        self.user_id = uuid.uuid4().hex

    def set_password(self, password: str):
        self.salt = os.urandom(32)
        self.password_hash = self._hash_password(self.salt, password)

    def does_password_match(self, password: str) -> bool:
        return self.password_hash == self._hash_password(self.salt, password)

    def _hash_password(self, salt: bytes, password: str):
        return hashlib.pbkdf2_hmac(self.HASH_ALGORITHM, password.encode(self.PASSWORD_ENCODING), salt, self.HASH_ITERS)
