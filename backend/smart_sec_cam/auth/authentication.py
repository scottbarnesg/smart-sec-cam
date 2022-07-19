import datetime
import os

import jwt

from smart_sec_cam.auth.database import AuthDatabase


class Authenticator:
    JWT_SECRET_LENGTH = 24
    TOKEN_DURATION_HOURS = 1

    def __init__(self, auth_db: AuthDatabase):
        self.auth_db = auth_db
        self.secret = os.urandom(self.JWT_SECRET_LENGTH)

    def authenticate(self, username: str, password: str) -> str:
        # Get user by id from database. If it doesn't exist, return error
        existing_user = self.auth_db.get_user_by_username(username)
        if not existing_user:
            raise ValueError(f"Failed to find user with username: {username}")
        # Verify that password matches
        if not existing_user.does_password_match(password):
            raise ValueError(f"Password mismatch for user: {username}")
        # Generate JWT and return it
        return self._generate_token(existing_user.user_id)

    def validate_token(self, token: str) -> bool:
        payload = jwt.decode(token, self.secret, algorithms=['HS256'])
        return payload['exp'] > datetime.datetime.utcnow().timestamp()

    def refresh_token(self, token: str) -> str:
        if self.validate_token(token):
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return self._generate_token(payload['sub'])

    def _generate_token(self, user_id: str) -> str:
        payload = {
            'exp': (datetime.datetime.utcnow() + datetime.timedelta(days=0, hours=self.TOKEN_DURATION_HOURS)).timestamp(),
            'iat': datetime.datetime.utcnow().timestamp(),
            'sub': user_id
        }
        return jwt.encode(payload, self.secret, algorithm='HS256')
