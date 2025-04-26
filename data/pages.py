import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Page(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'pages'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    number = sqlalchemy.Column(sqlalchemy.Integer)
    text = sqlalchemy.Column(sqlalchemy.String)
    reg_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    book_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("books.id"))
    book = orm.relationship('Book')
    comments = orm.relationship("Comment", back_populates='page')

    def __repr__(self):
        return f"<Page> {self.id} {self.name}"
