import datetime
from flask_login import UserMixin
import sqlalchemy
from sqlalchemy import orm
from database import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.inspection import inspect


class SerializerMixin(object):
    def serialize(self, filter_columns: list[str] = []):
        keys = filter(
            lambda key: len(filter_columns) == 0 or key in filter_columns,
            inspect(self).attrs.keys(),
        )
        return {key: getattr(self, key) for key in keys}

    @staticmethod
    def serialize_list(list, filter_columns: list[str]):
        return [model.serialize(filter_columns) for model in list]


class User(SqlAlchemyBase, SerializerMixin, UserMixin):
    __tablename__ = "user"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
