import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Tag(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tags'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, default="")

    def __repr__(self):
        return f"<Tag> {self.id} {self.name}"
