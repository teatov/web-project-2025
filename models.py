import datetime
from flask_login import UserMixin
import sqlalchemy
from sqlalchemy import Column, ForeignKey, Table, orm
from database import Base
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.inspection import inspect
from slugify import slugify


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


class User(Base, SerializerMixin, UserMixin):
    __tablename__ = "user"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_admin = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


movie_studio_join = Table(
    "movie_studio_join",
    Base.metadata,
    Column("movie_id", ForeignKey("movie.id"), primary_key=True),
    Column("studio_id", ForeignKey("movie_studio.id"), primary_key=True),
)

movie_genre_join = Table(
    "movie_genre_join",
    Base.metadata,
    Column("movie_id", ForeignKey("movie.id"), primary_key=True),
    Column("genre_id", ForeignKey("movie_genre.id"), primary_key=True),
)

movie_staff_join = Table(
    "movie_staff_join",
    Base.metadata,
    Column("movie_id", ForeignKey("movie.id"), primary_key=True),
    Column("staff_id", ForeignKey("movie_staff.id"), primary_key=True),
)


class Movie(Base, SerializerMixin):
    __tablename__ = "movie"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    slug = sqlalchemy.Column(sqlalchemy.String, unique=True)
    release_date = sqlalchemy.Column(sqlalchemy.Date)
    poster_file = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def set_slug(self):
        self.slug = slugify(self.title)

    country_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("movie_country.id")
    )
    country = orm.relationship("MovieCountry")

    studios = orm.relationship(
        "MovieStudio", secondary=movie_studio_join, back_populates="movies"
    )
    genres = orm.relationship(
        "MovieGenre", secondary=movie_genre_join, back_populates="movies"
    )
    staff = orm.relationship(
        "MovieStaff", secondary=movie_staff_join, back_populates="movies"
    )


class MovieCountry(Base, SerializerMixin):
    __tablename__ = "movie_country"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True)

    movies = orm.relationship("Movie", back_populates="country")


class MovieStudio(Base, SerializerMixin):
    __tablename__ = "movie_studio"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True)

    movies = orm.relationship(
        "Movie", secondary=movie_studio_join, back_populates="studios"
    )


class MovieGenre(Base, SerializerMixin):
    __tablename__ = "movie_genre"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True)

    movies = orm.relationship(
        "Movie", secondary=movie_genre_join, back_populates="genres"
    )


class MovieStaff(Base, SerializerMixin):
    __tablename__ = "movie_staff"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True)

    movies = orm.relationship(
        "Movie", secondary=movie_staff_join, back_populates="staff"
    )
