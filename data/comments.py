import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Comment(SqlAlchemyBase):
    __tablename__ = 'comms'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    number = sqlalchemy.Column(sqlalchemy.Integer)
    text = sqlalchemy.Column(sqlalchemy.String)
    reg_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    likes_count = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    likes = sqlalchemy.Column(sqlalchemy.JSON, default=[])
    page_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("pages.id"))
    page = orm.relationship('Page')
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    author = orm.relationship('User')

    def __repr__(self):
        return f"<Comment> {self.id} {self.author_id} {self.text}"

    def to_dict(self):
        return {"number": self.number, "text": self.text, "reg_date": self.reg_date, "likes": self.likes_count,
                "page": self.page.number, "author": self.author.name}
