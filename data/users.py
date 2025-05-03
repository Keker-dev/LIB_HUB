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
    notifs = sqlalchemy.Column(sqlalchemy.JSON, default={"read": [], "write": []})
    settings = sqlalchemy.Column(sqlalchemy.JSON, default={"font": "Arial", "font-size": 20, "font-color": "#ffffff",
                                                           "ignore": "Никакие", "len-last-seen": 100})
    books = orm.relationship("Book", back_populates='author')
    comments = orm.relationship("Comment", back_populates='author')
    tokens = orm.relationship("Token", back_populates='user')

    def __repr__(self):
        return f"<User> {self.id} {self.name}"

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
