from datetime import datetime, timedelta
import sqlalchemy
import base64, os
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase, create_session
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, default="Тут пока ничего нет...")
    reg_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)
    likes_count = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    likes = sqlalchemy.Column(sqlalchemy.JSON, default=[])
    favorite_authors = sqlalchemy.Column(sqlalchemy.JSON, default=[])
    favorite_books = sqlalchemy.Column(sqlalchemy.JSON, default=[])
    last_books = sqlalchemy.Column(sqlalchemy.JSON, default=[])
    notifs = sqlalchemy.Column(sqlalchemy.JSON, default=[])
    settings = sqlalchemy.Column(sqlalchemy.JSON,
                                 default={"font": "Arial", "font-size": 20, "font-color": "#fff", "ignore": "Никакие",
                                          "len-last-seen": 100})
    books = orm.relationship("Book", back_populates='author')
    comments = orm.relationship("Comment", back_populates='author')
    # Токен
    token = sqlalchemy.Column(sqlalchemy.String(32), unique=True)
    token_expiration = sqlalchemy.Column(sqlalchemy.DateTime)

    def get_token(self, expires_in=31536000):
        now = datetime.now()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.now() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        sess = create_session()
        user = sess.query(User).filter(User.token == token).first()
        if user is None or user.token_expiration < datetime.now():
            return None
        return user

    @staticmethod
    def generate_token():
        return base64.b64encode(os.urandom(24)).decode('utf-8'), datetime.now() + timedelta(seconds=31536000)

    def __repr__(self):
        return f"<User> {self.id} {self.name}"

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
