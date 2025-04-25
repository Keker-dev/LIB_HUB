import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Book(SqlAlchemyBase):
    __tablename__ = 'books'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    pages = orm.relationship("Page", back_populates='book')
    about = sqlalchemy.Column(sqlalchemy.String, default="")
    reg_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    likes = sqlalchemy.Column(sqlalchemy.JSON, default=[])
    views = sqlalchemy.Column(sqlalchemy.JSON, default=[])
    likes_count = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    views_count = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    in_favorites = sqlalchemy.Column(sqlalchemy.JSON, default=[])
    tags = sqlalchemy.Column(sqlalchemy.JSON, default=[])
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    author = orm.relationship('User')

    def __repr__(self):
        return f"<Book> {self.id} {self.name}"
