import datetime
import sqlalchemy
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, default="")
    reg_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    likes = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    favorite_authors = sqlalchemy.Column(sqlalchemy.String, default="[]")
    favorite_books = sqlalchemy.Column(sqlalchemy.String, default="[]")
    last_books = sqlalchemy.Column(sqlalchemy.String, default="[]")
    notifs = sqlalchemy.Column(sqlalchemy.String, default="[]")
    settings = sqlalchemy.Column(sqlalchemy.String, default='''{"font": "Arial", "font-size": 10, 
    "font-color": "black", "ignore": False, "len-last-seen": 100}''')
    books = orm.relationship("Book", back_populates='author')
    comments = orm.relationship("Comment", back_populates='author')

    def __repr__(self):
        return f"<User> {self.id} {self.name}"

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
