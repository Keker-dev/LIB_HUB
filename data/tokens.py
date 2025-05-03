from datetime import datetime, timedelta
import sqlalchemy
import base64, os
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase, create_session


class Token(SqlAlchemyBase):
    __tablename__ = 'tokens'

    token = sqlalchemy.Column(sqlalchemy.String(32), primary_key=True, unique=True)
    expiration = sqlalchemy.Column(sqlalchemy.DateTime)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')

    def get_token(self):
        now = datetime.now()
        if self.token and self.expiration > now:
            return self.token
        elif self.token and self.expiration <= now:
            self.revoke_token()
        self.token, self.expiration = Token.generate_token()
        return self.token

    def revoke_token(self):
        self.expiration = datetime.now() - timedelta(seconds=10)

    @staticmethod
    def generate_token():
        sess = create_session()
        tk, exp = base64.b64encode(os.urandom(24)).decode('utf-8'), datetime.now() + timedelta(seconds=31536000)
        while sess.query(Token).get(tk):
            tk, exp = base64.b64encode(os.urandom(24)).decode('utf-8'), datetime.now() + timedelta(seconds=31536000)
        return tk, exp

    @staticmethod
    def get_user(tk):
        sess = create_session()
        token = sess.query(Token).get(tk)
        if not token or not token.get_token():
            return None
        return token.user

    def __repr__(self):
        return f"<Token> {self.token} {self.expiration} {self.user_id}"
